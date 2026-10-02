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

sys.setrecursionlimit(20000)

OUT = '배경-osm.json'
RAW = '.osm-raw'                     # 받아 둔 원본 (.gitignore 에 있다)
S, W, N, E = 36.070, 127.223, 36.320, 127.537     # 그림 범위보다 조금 넓게
BB = '%f,%f,%f,%f' % (S, W, N, E)
MID = 36.195                         # 내(계류)는 둘로 갈라 받는다 — 한 번에 받으면 서버가 끊는다

# 미러를 돌려 가며 쓴다. 공개 서버라 자주 끊기고, 끊기는 서버가 그때그때 다르다.
MIRRORS = ['https://overpass.private.coffee/api/interpreter',
           'https://overpass-api.de/api/interpreter',
           'https://overpass.kumi.systems/api/interpreter',
           'https://overpass.osm.jp/api/interpreter']

LAYERS = [
    ('river',    '(way[waterway=river](%s););out geom;' % BB),
    ('stream_n', '(way[waterway=stream](%f,%f,%f,%f););out geom;' % (MID, W, N, E)),
    ('stream_s', '(way[waterway=stream](%f,%f,%f,%f););out geom;' % (S, W, MID, E)),
    ('water',    '(way[natural=water](%s);way[landuse=reservoir](%s););out geom;' % (BB, BB)),
    ('road',     '(way[highway~"^(motorway|trunk|primary)$"](%s););out geom;' % BB),
    ('rail',     '(way[railway=rail][usage!=industrial](%s););out geom;' % BB),
    # 경계는 **relation 을 통째로 받지 않는다.** 도(道) 하나의 geometry 가
    # 수만 꼭짓점이라 공개 서버가 끝내 끊는다. 관계를 먼저 고르고 그 멤버 way 중
    # 우리 범위에 걸치는 것만 받는다.
    ('bound4',   'rel[boundary=administrative][admin_level=4](%s)->.r;'
                 'way(r.r)(%s);out geom;' % (BB, BB)),
    ('peak',     '(node[natural=peak][name](%s););out;' % BB),
    ('place',    '(node[place~"^(city|town|suburb|village)$"][name](%s););out;' % BB),
]

EPS = 0.00022      # 980 px · 0.274° 에서 1 px 이 0.00028° — 그보다 잘게 둘 까닭이 없다
R = 4              # 소수 넷째 자리 ≈ 10 m


def grab(name, q, tries=10):
    """한 켜를 받는다. 받아 둔 것이 있으면 그것을 쓴다."""
    cached = os.path.join(RAW, name + '.json')
    if os.path.exists(cached):
        return json.load(open(cached, encoding='utf-8'))
    for i in range(tries):
        m = MIRRORS[i % len(MIRRORS)]
        try:
            body = urllib.parse.urlencode({'data': '[out:json][timeout:90];' + q}).encode()
            req = urllib.request.Request(
                m, data=body, headers={'User-Agent': 'daehyang-gogae-research/1.0'})
            with urllib.request.urlopen(req, timeout=240) as r:
                d = json.loads(r.read().decode('utf-8'))
            if not os.path.isdir(RAW):
                os.makedirs(RAW)
            json.dump(d, open(cached, 'w', encoding='utf-8'), ensure_ascii=False)
            return d
        except Exception as e:
            sys.stderr.write('  %-22s %s\n' % (m.split('/')[2], str(e)[:60]))
            time.sleep(min(2 ** i, 30))
    raise SystemExit('%s 를 못 받았습니다. 잠시 뒤 다시 돌려 보십시오 — '
                     '받아 둔 켜는 %s 에 남아 다시 받지 않습니다.' % (name, RAW))


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


raw = {}
for name, q in LAYERS:
    raw[name] = grab(name, q)
    print('  %-9s %5d 건' % (name, len(raw[name].get('elements', []))))

doc = {
    '_': '© OpenStreetMap 기여자 · ODbL. research/fetch-osm.py 가 Overpass 에서 받아 '
         '추린 것입니다. 손으로 고치지 마십시오 — 고칠 일이 있으면 스크립트를 다시 '
         '돌리십시오. 그림의 출처 표시(범례)는 ODbL 이 요구하는 것이니 지우지 마십시오.',
    '강':     polys(raw['river']),
    '내':     polys(raw['stream_n']) + polys(raw['stream_s']),
    '물':     polys(raw['water'], EPS * 1.5),
    '고속':   [], '국도': [],
    '철도':   polys(raw['rail']),
    # 시·군·구 경계(admin_level=6)는 일부러 받지 않는다. 시·도 경계와 생김새가
    # 비슷해 둘을 함께 깔면 어느 쪽이 무슨 경계인지 읽히지 않는다. 이 그림에서
    # 뜻을 지는 것은 **대전광역시 경계** 하나다.
    '시도':   polys(raw['bound4']),
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

json.dump(doc, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('\n추린 것')
for k, v in doc.items():
    if k != '_':
        print('  %-7s %5d' % (k, len(v)))
print('\n→ %s · %d KB' % (OUT, os.path.getsize(OUT) // 1024))
if '--raw' not in sys.argv:
    for f in os.listdir(RAW) if os.path.isdir(RAW) else []:
        os.remove(os.path.join(RAW, f))
    if os.path.isdir(RAW):
        os.rmdir(RAW)
