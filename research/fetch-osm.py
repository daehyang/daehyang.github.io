# -*- coding: utf-8 -*-
"""배경-osm.json — 고개 지도의 바탕이 될 재료를 OpenStreetMap 에서 받아 추린다.

    python3 fetch-osm.py            ← research/ 에서. 받고 추려 배경-osm.json 을 쓴다
    python3 fetch-osm.py --raw      ← 받아 둔 원본을 지우지 않고 남긴다(다시 받을 때 빠름)

**이 스크립트는 작업(Actions)이 돌리지 않습니다.** 그림을 그리는
make-positions.py 는 배경-osm.json 을 읽기만 하고, 그 파일은 저장소에 들어 있다.
바탕은 몇 해에 한 번 손으로 다시 받으면 되는 것이고, 그림을 그릴 때마다 남의
서버를 두드릴 일이 아니기 때문이다. 받는 길이 막히면 그림이 아예 안 나오게 되는
것도 피했다.

자료는 **OpenStreetMap 기여자**의 것이고 **ODbL** 이다. 그래서 그림 범례에
출처를 적는다 — 지우지 마십시오.

표준 라이브러리만 쓴다.
"""
import json, math, os, sys, time, urllib.parse, urllib.request

# **User-Agent 는 ASCII 로만 적는다.** HTTP 머리글은 latin-1 이라 한글을 그대로
# 넣으면 urllib 이 터지고, `?` 로 바꿔 넣으면 어떤 서버는 수상히 여겨 막는다
# (osm.ch 가 `????` 가 든 UA 에 HTML 오류 쪽을 돌려주었다 — 2026-10-02).
UA = 'daehyang-gogae-research/1.0 (toponym survey; github.com/daehyang)'

sys.setrecursionlimit(20000)

OUT = '배경-osm.json'
RAW = '.osm-raw'                     # 받아 둔 원본 (.gitignore 에 있다)
S, W, N, E = 36.065, 127.205, 36.525, 127.605     # 그림 범위보다 조금 넓게
BB = '%f,%f,%f,%f' % (S, W, N, E)
# 내(계류)는 띠로 갈라 받는다 — 한 번에 범위 전체를 달라고 하면 서버가 끊는다.
BANDS = [(36.065 + i * 0.1533, 36.065 + (i + 1) * 0.1533) for i in range(3)]

# 미러를 돌려 가며 쓴다. 공개 서버라 자주 끊기고, 끊기는 서버가 그때그때 다르다.
# 공개 서버는 돌아가며 멎으므로 하나에 매달리지 않는다. 다만 **아무 미러나
# 넣으면 안 된다** — 2026-10-02 에 `overpass.osm.ch` 는 200 에 올바른 JSON 을
# 돌려주면서 `elements` 가 늘 비어 있었다(자료가 안 올라간 빈 서버였다).
# 그래서 아래 check() 가 **자료 기준 시각**을 보고 그런 서버를 걸러 낸다.
# `overpass.openstreetmap.fr` 는 403 으로 막고, `overpass.osm.jp` 는 인증서가
# 맞지 않아 뺐다.
MIRRORS = ['https://overpass.private.coffee/api/interpreter',
           'https://overpass-api.de/api/interpreter']

# 켜마다 **띠로 갈라** 받는다. 범위 전체를 한 번에 달라고 하면 공개 서버가
# 끊는다(504 · connection reset). 띠 하나는 몇 초면 끝나고, 받은 띠는 쟁여 두므로
# 중간에 끊겨도 처음부터 다시 받지 않는다.
WAYS = {                                   # 받는 차례 = 중요한 차례
    'road':   'way[highway~"^(motorway|trunk|primary)$"]',
    'river':  'way[waterway=river]',
    'rail':   'way[railway=rail][usage!=industrial]',
    'water':  'way[natural=water];way[landuse=reservoir];'
              'rel[natural=water];rel[landuse=reservoir]',
    'stream': 'way[waterway=stream]',
}

# **큰 것 둘은 Overpass 가 아니라 Nominatim 에서 이름으로 받는다.**
# 대청호와 대전광역시 경계는 Overpass 로 받으면 토막 난 way 수십 개를 도로
# 꿰매야 하고, 관계를 통째로 달라고 하면 공개 서버가 끊는다. Nominatim 은
# 같은 OSM 자료를 **이미 꿰맨 다각형 하나**로 준다. 자료도 ODbL 로 같다.
NAMED = [('호수',   '대청호',      ['대청호']),
         ('시경계', '대전광역시',  ['대전광역시'])]
NODES = {
    'peak':  'node[natural=peak][name]',
    # 동(洞)·면 이름을 얻는다 — 급 C 고개의 자리는 이 점들의 중심에서 나온다.
    'place': 'node[place~"^(city|town|suburb|quarter|village|neighbourhood)$"][name]',
}


# 계류(stream)는 수가 많아 한 띠가 무겁다 — 다른 켜보다 **더 잘게** 자른다.
# 2026-10-02 에 세 띠로 받으려다 스무 번을 내리 끊겼다.
FINE = {'stream': 2}


def bands_for(name):
    k = FINE.get(name, 1)
    out = []
    for lo, hi in BANDS:
        for j in range(k):
            out.append((lo + (hi - lo) * j / k, lo + (hi - lo) * (j + 1) / k))
    return out


def jobs():
    # **중요한 켜부터 받는다.** 공개 서버가 막으면 오래 걸리므로, 중간에
    # 멈추더라도 손에 남는 것이 쓸모 있게 순서를 둔다 — 산·지명과 큰길이
    # 먼저고, 잔물줄기가 맨 뒤다.
    for name, sel in NODES.items():
        yield name, name, '(%s(%s););out;' % (sel, BB)
    for name, sel in WAYS.items():
        for k, (lo, hi) in enumerate(bands_for(name)):
            bb = '%f,%f,%f,%f' % (lo, W, hi, E)
            # 합집합 괄호 안은 **마지막에도 `;`** 가 있어야 한다. 빠뜨리면 서버가
            # 400 parse error 를 돌려주는데, 그 몸통이 HTML 이라 오류 글이 눈에
            # 띄지 않는다 — 2026-10-02 에 「서버가 죽었다」고 한참 헤맸다.
            q = '(%s;);out geom;' % ';'.join('%s(%s)' % (t, bb) for t in sel.split(';'))
            yield '%s-%d' % (name, k), name, q


EPS = 0.00022      # 980 px · 0.274° 에서 1 px 이 0.00028° — 그보다 잘게 둘 까닭이 없다
R = 4              # 소수 넷째 자리 ≈ 10 m


MISSING = []


def check(m, d):
    """돌려받은 것이 **진짜 자료인지** 본다.

    200 에 올바른 JSON 인데 속이 빈 서버가 있다. 그런 응답을 그대로 쟁여 두면
    「받기는 다 됐는데 그림이 텅 비는」 꼴이 되고, 까닭을 찾기가 아주 어렵다.
    자료 기준 시각(`timestamp_osm_base`)이 날짜 꼴이 아니면 그런 서버다.
    """
    ts = (d.get('osm3s') or {}).get('timestamp_osm_base', '')
    if not ts.startswith('20'):
        raise IOError('자료가 없는 서버로 보입니다 (기준 시각 %r)' % ts[:24])


# 한 조각을 몇 번까지 다시 물을 것인가. 공개 서버가 막으면 길게 기다려야 하므로
# 기본은 넉넉하다. 지금 당장 **받은 만큼만** 내놓아야 할 때는 `TRIES=3` 처럼 줄인다.
TRIES = int(os.environ.get('TRIES', '400'))


def grab(name, q, tries=TRIES):
    """한 켜를 받는다. 받아 둔 것이 있으면 그것을 쓴다."""
    cached = os.path.join(RAW, name + '.json')
    if os.path.exists(cached):
        return json.load(open(cached, encoding='utf-8'))
    for i in range(tries):
        m = MIRRORS[i % len(MIRRORS)]
        try:
            body = urllib.parse.urlencode({'data': '[out:json][timeout:90];' + q}).encode()
            req = urllib.request.Request(
                m, data=body, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=150) as r:
                d = json.loads(r.read().decode('utf-8'))
            check(m, d)
            time.sleep(1.5)           # 공개 서버에 몰아치지 않는다
            if not os.path.isdir(RAW):
                os.makedirs(RAW)
            json.dump(d, open(cached, 'w', encoding='utf-8'), ensure_ascii=False)
            return d
        except Exception as e:
            why = str(e)[:52]
            # 400 의 몸통에 **무엇이 틀렸는지**가 적혀 있다. 이것을 안 보면
            # 질의가 틀린 것을 서버 탓으로 돌리게 된다.
            body = getattr(e, 'read', None)
            if body:
                import re as _re
                txt = _re.sub(r'<[^>]+>', ' ', body().decode('utf-8', 'replace'))
                err = [t.strip() for t in txt.split('Error:') [1:]]
                if err:
                    why = 'Error: ' + err[0][:120]
            sys.stderr.write('  %-9s %-22s %s\n' % (name, m.split('/')[2], why))
            # 공개 서버는 몰아치면 막고(406), 얼마 뒤 다시 열린다. 그러니 간격을
            # 점점 늘리지 말고 **일정하게** 두드리는 편이 빨리 통과한다.
            # 받은 조각은 쟁여 두므로 오래 걸려도 처음부터 다시 받지 않는다.
            time.sleep(15)
    # **못 받았다고 멈추지 않는다.** 공개 서버는 몇 시간씩 막기도 하는데,
    # 그때마다 아무것도 못 내놓으면 쓸모가 없다. 못 받은 켜는 비워 두고
    # 그 사실을 파일에 적어 둔다 — 나중에 다시 돌리면 그 켜만 채워진다.
    MISSING.append(name)
    sys.stderr.write('  ! %s 를 못 받았습니다 — 이 켜는 비워 둡니다.\n' % name)
    return {'elements': []}


def nominatim(q, expect):
    """행정구역·호수 하나를 이름으로 받는다. 겉고리와 속고리(섬)를 갈라 돌려준다."""
    cached = os.path.join(RAW, 'nom-' + q + '.json')
    if os.path.exists(cached):
        d = json.load(open(cached, encoding='utf-8'))
    else:
        u = ('https://nominatim.openstreetmap.org/search?'
             + urllib.parse.urlencode({'q': q, 'format': 'json', 'limit': 5,
                                       'polygon_geojson': 1}))
        req = urllib.request.Request(u, headers={'User-Agent': UA})
        for i in range(8):
            try:
                d = json.loads(urllib.request.urlopen(req, timeout=180).read().decode())
                break
            except Exception as e:
                sys.stderr.write('  nominatim %-12s %s\n' % (q, str(e)[:50]))
                time.sleep(min(5 * 2 ** i, 120))
        else:
            MISSING.append(q)
            sys.stderr.write('  ! Nominatim 에서 「%s」 를 못 받았습니다 — '
                             '이 켜는 비워 둡니다.\n' % q)
            return [], []
        if not os.path.isdir(RAW):
            os.makedirs(RAW)
        json.dump(d, open(cached, 'w', encoding='utf-8'), ensure_ascii=False)
        time.sleep(1.5)                   # Nominatim 이용 규약 — 초당 하나
    for e in d:
        if all(w in e['display_name'] for w in expect):
            g = e.get('geojson') or {}
            polys_ = ([g['coordinates']] if g.get('type') == 'Polygon'
                      else g.get('coordinates', []) if g.get('type') == 'MultiPolygon'
                      else [])
            # 다각형은 **첫 고리가 겉, 나머지가 속(섬)**이다. 섬까지 물빛으로
            # 칠하면 호수 한가운데 섬이 사라진다.
            return ([pl[0] for pl in polys_ if pl],
                    [r for pl in polys_ for r in pl[1:]])
    MISSING.append(q)
    return [], []


def dp(pts, eps=EPS):
    """더글러스–포이커 — 1 px 안에서 움직이는 꼭짓점은 버린다."""
    if len(pts) < 3:
        return pts
    ax, ay = pts[0]
    bx, by = pts[-1]
    dx, dy = bx - ax, by - ay
    n = math.hypot(dx, dy)
    best, bi = -1.0, 0
    for i in range(1, len(pts) - 1):
        px, py = pts[i]
        d = (abs(dy * px - dx * py + bx * ay - by * ax) / n if n
             else math.hypot(px - ax, py - ay))
        if d > best:
            best, bi = d, i
    if best <= eps:
        return [pts[0], pts[-1]]
    return dp(pts[:bi + 1], eps)[:-1] + dp(pts[bi:], eps)


def rnd(pts):
    out = [[round(x, R), round(y, R)] for x, y in pts]
    return [p for i, p in enumerate(out) if i == 0 or p != out[i - 1]]


def rings(raw):
    """다각형 관계의 멤버 way 를 고리로 꿰맨다.

    큰 물(대청호)은 way 하나가 아니라 **토막 여럿으로 쪼개진 관계**다. 토막을
    저마다 닫아 버리면 호수를 가로지르는 금이 생긴다. 끝점이 맞는 토막끼리
    이어 붙여 고리를 만들어야 한다. `겉`(outer)과 `속`(inner, 섬)을 갈라 돌려
    준다 — 섬까지 물빛으로 칠하면 안 되기 때문이다.
    """
    out, inner = [], []
    for e in raw.get('elements', []):
        if e.get('type') == 'way':
            g = e.get('geometry') or []
            if len(g) > 3:
                out.append([(p['lon'], p['lat']) for p in g])
            continue
        for role, bucket in (('outer', out), ('inner', inner)):
            frags = [[(p['lon'], p['lat']) for p in m['geometry']]
                     for m in e.get('members', [])
                     if m.get('geometry') and (m.get('role') or 'outer') == role]
            while frags:
                cur = frags.pop(0)
                moved = True
                while moved and cur[0] != cur[-1]:
                    moved = False
                    for i, f in enumerate(frags):
                        if f[0] == cur[-1]:
                            cur += f[1:]
                        elif f[-1] == cur[-1]:
                            cur += f[-2::-1]
                        elif f[-1] == cur[0]:
                            cur = f[:-1] + cur
                        elif f[0] == cur[0]:
                            cur = f[:0:-1] + cur
                        else:
                            continue
                        frags.pop(i)
                        moved = True
                        break
                if len(cur) > 3:
                    bucket.append(cur)
    return out, inner


def polys(raw, eps=EPS):
    """way 는 제 geometry 를, relation 은 멤버 way 들의 geometry 를 쓴다."""
    out = []
    for e in raw.get('elements', []):
        chunks = ([e.get('geometry')] if e.get('type') == 'way'
                  else [m.get('geometry') for m in e.get('members', [])])
        for g in chunks:
            if not g or len(g) < 2:
                continue
            r = rnd(dp([(p['lon'], p['lat']) for p in g], eps))
            if len(r) > 1:
                out.append(r)
    return out


# `--named-only` — **Nominatim 에서 받는 큰 것 둘만** 다시 받아 기존 바탕에 끼운다.
# Overpass 가 막혀 있을 때, 이미 있는 바탕을 버리지 않고 호수·경계만 새로 넣을 때 쓴다.
if '--named-only' in sys.argv:
    doc = json.load(open(OUT, encoding='utf-8'))
    doc['물섬'] = [r for r in doc.get('물섬', []) if True]
    for key, q, expect in NAMED:
        out_r, in_r = nominatim(q, expect)
        if not out_r:
            continue
        if key == '시경계':
            doc['시도'] = [rnd(dp([tuple(c) for c in r])) for r in out_r]
        else:
            doc['호수'] = [rnd(dp([tuple(c) for c in r], EPS * 1.5)) for r in out_r]
            doc['물섬'] += [rnd(dp([tuple(c) for c in r], EPS * 1.5)) for r in in_r]
        print('  %-7s %s → 겉 %d 고리 · 속 %d 고리' % (key, q, len(out_r), len(in_r)))
    json.dump(doc, open(OUT, 'w', encoding='utf-8'),
              ensure_ascii=False, separators=(',', ':'))
    print('→ %s · %d KB (큰 것 둘만 고쳐 넣었습니다)' % (OUT, os.path.getsize(OUT) // 1024))
    raise SystemExit(0)

raw = {}
for key, name, q in jobs():
    d = grab(key, q)
    raw.setdefault(name, {'elements': []})['elements'] += d.get('elements', [])
    print('  %-11s %5d 건' % (key, len(d.get('elements', []))))
    sys.stdout.flush()

# 띠를 갈라 받으면 띠 경계에 걸친 것이 두 번 들어온다 — id 로 솎는다
for name, d in raw.items():
    seen, uniq = set(), []
    for e in d['elements']:
        k = (e.get('type'), e.get('id'))
        if k in seen:
            continue
        seen.add(k)
        uniq.append(e)
    d['elements'] = uniq
    print('  = %-9s %5d 건 (겹친 것 솎은 뒤)' % (name, len(uniq)))

doc = {
    '_': '© OpenStreetMap 기여자 · ODbL. research/fetch-osm.py 가 Overpass 에서 받아 '
         '추린 것입니다. 손으로 고치지 마십시오 — 고칠 일이 있으면 스크립트를 다시 '
         '돌리십시오. 그림의 출처 표시(범례)는 ODbL 이 요구하는 것이니 지우지 마십시오.',
    '강':     polys(raw['river']),
    '내':     polys(raw['stream']),
    '물':     [rnd(dp(r, EPS * 1.5)) for r in rings(raw['water'])[0]],
    '물섬':   [rnd(dp(r, EPS * 1.5)) for r in rings(raw['water'])[1]],
    '호수':   [],
    '고속':   [], '국도': [],
    '철도':   polys(raw['rail']),
    # 시·군·구 경계(admin_level=6)는 일부러 받지 않는다. 시·도 경계와 생김새가
    # 비슷해 둘을 함께 깔면 어느 쪽이 무슨 경계인지 읽히지 않는다. 이 그림에서
    # 뜻을 지는 것은 **대전광역시 경계** 하나다.
    '시도':   [],
    '봉우리': [], '마을': [],
}
for e in raw['road'].get('elements', []):
    key = '고속' if e.get('tags', {}).get('highway') == 'motorway' else '국도'
    doc[key] += polys({'elements': [e]})
for e in raw['peak'].get('elements', []):
    t = e['tags']
    try:
        h = float(str(t.get('ele', '')).split()[0])
    except Exception:
        h = 0.0
    doc['봉우리'].append({'이름': t['name'], '높이': round(h, 1),
                          '위도': round(e['lat'], R), '경도': round(e['lon'], R)})
for e in raw['place'].get('elements', []):
    t = e['tags']
    doc['마을'].append({'이름': t['name'], '갈래': t['place'],
                        '위도': round(e['lat'], R), '경도': round(e['lon'], R)})

# Nominatim 에서 받는 큰 것 둘
for key, q, expect in NAMED:
    out_r, in_r = nominatim(q, expect)
    if key == '시경계':
        doc['시도'] = [rnd(dp([tuple(c) for c in r])) for r in out_r]
    else:
        doc['호수'] = [rnd(dp([tuple(c) for c in r], EPS * 1.5)) for r in out_r]
        doc['물섬'] += [rnd(dp([tuple(c) for c in r], EPS * 1.5)) for r in in_r]
    print('  %-7s %s → 겉 %d 고리 · 속 %d 고리' % (key, q, len(out_r), len(in_r)))

if MISSING:
    doc['못받은켜'] = sorted(set(MISSING))

json.dump(doc, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('\n추린 것')
for k, v in doc.items():
    if k != '_':
        print('  %-7s %5d' % (k, len(v)))
print('\n→ %s · %d KB' % (OUT, os.path.getsize(OUT) // 1024))
if MISSING:
    print('\n⚠ 못 받은 켜 %d: %s' % (len(set(MISSING)), ' '.join(sorted(set(MISSING)))))
    print('  공개 서버가 막은 것입니다. **나중에 다시 돌리면 그 켜만 채워집니다** —')
    print('  받아 둔 켜는 %s 에 남아 다시 받지 않습니다.' % RAW)
if '--raw' not in sys.argv:
    for f in os.listdir(RAW) if os.path.isdir(RAW) else []:
        os.remove(os.path.join(RAW, f))
    if os.path.isdir(RAW):
        os.rmdir(RAW)
