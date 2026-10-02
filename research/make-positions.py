# -*- coding: utf-8 -*-
"""고개-위치.csv(정본)에서 사본 셋을 만든다.

    python3 make-positions.py        ← research/ 에서

  ① 고개-위치.geojson  — 현대 지도용. GitHub 이 열면 지도로 그린다
  ② 고개-위치.svg      — 이름이 함께 찍힌 지도. GitHub 이 그대로 그린다
  ③ 대전-고개-대조표.md 3.1 의 「대장」 표

표준 라이브러리만 쓴다.
"""
import csv, io, json, math, re

CSV, GJ, SVG, DOC = '고개-위치.csv', '고개-위치.geojson', '고개-위치.svg', '대전-고개-대조표.md'
BG = '배경-osm.json'
rows = list(csv.DictReader(io.open(CSV, encoding='utf-8')))
pts = [r for r in rows if r['위도']]

# 바탕 지도(OpenStreetMap). 없으면 점만 그린다 — 그림이 못 나오는 일은 없게 둔다.
try:
    bg = json.load(io.open(BG, encoding='utf-8'))
except IOError:
    bg = {}


def ko_count(n):
    """점 수를 우리말 수사로 — 열일곱 번째 좌표가 서면 제목이 따라와야 한다."""
    ones = '한 두 세 네 다섯 여섯 일곱 여덟 아홉'.split()
    tens = '열 스물 서른 마흔 쉰 예순 일흔 여든 아흔'.split()
    if not 1 <= n <= 99:
        return '%d' % n
    t, o = divmod(n, 10)
    return (tens[t - 1] if t else '') + (ones[o - 1] if o else '')


def label_of(r):
    """지도에 찍을 짧은 이름 — 우리말 이름이 있으면 그것, 없으면 한자."""
    t = r['표제']
    if t.startswith('(미상)'):
        return r['한자'].split(' / ')[0]
    return t.split(' · ')[0]


# ── ① GeoJSON ────────────────────────────────────────────────────────────────
# name 을 맨 앞에 둔다. GitHub 은 점을 누르면 속성 표를 띄우고, 다른 뷰어
# (geojson.io·QGIS·Mapbox)는 name 으로 이름표를 단다.
feats = []
for r in pts:
    named = not r['표제'].startswith('(미상)')
    feats.append({
        "type": "Feature",
        "geometry": {"type": "Point",
                     "coordinates": [float(r['경도']), float(r['위도'])]},
        "properties": {
            "name": '%s %s' % (label_of(r), r['한자']) if named else r['한자'],
            "표제": r['표제'], "한자": r['한자'],
            "급": r['급'], "도엽자리": r['도엽자리'], "비고": r['비고'],
            "marker-color": ("#7d93ab" if r['급'] == 'C'
                             else ("#2a78d6" if named else "#7b7a73")),
            "marker-size": "small" if r['급'] == 'C' else "medium",
        }})
io.open(GJ, 'w', encoding='utf-8').write(json.dumps(
    {"type": "FeatureCollection",
     "properties": {"이름": "대전 지역 고개 — 좌표가 선 것",
                    "만든것": "이 파일은 research/고개-위치.csv 에서 make-positions.py 가 "
                              "만듭니다. 손으로 고치지 마십시오 — 다음 실행에서 덮어씁니다. "
                              "내용을 바꾸려면 고개-위치.csv 를 고치십시오.",
                    "설명": "대전향토문화연구회 고개 조사. 급 B 는 미군 AMS 1:50,000"
                            "(저본 1919) 그리드를 환산한 것으로 ±1 km, 급 C 는 "
                            "그 고개가 있는 동(洞)의 중심이라 고개 자체의 자리가 "
                            "아닙니다(1~3 km 틀릴 수 있습니다). "
                            "자세한 것은 research/대전-고개-대조표.md 의 3.1 과 14.5-3.",
                    "출처": "research/고개-위치.csv"},
     "features": feats}, ensure_ascii=False, indent=1) + '\n')


# ── ② SVG 지도 ───────────────────────────────────────────────────────────────
LAT0, LAT1, LON0, LON1 = 36.085, 36.505, 127.225, 127.585   # 그림 범위
PAD_L, PAD_R, PAD_T, PAD_B = 74, 56, 128, 134
INK, INK2, INK3 = '#0b0b0b', '#52514e', '#9a9992'
BLUE, GREY, SURF = '#2a78d6', '#7b7a73', '#fcfcfb'
SLATE = '#7d93ab'        # 급 C — 동(洞)까지만 아는 것
KM_LAT = 111.0
KM_LON = 111.320 * math.cos(math.radians((LAT0 + LAT1) / 2))

# **가로세로 축척을 같게 맞춥니다.** 전에는 폭과 높이를 따로 정해 두어
# 세로가 가로보다 31% 눌려 있었습니다 — 5 km 자는 가로로 잰 것이라
# 세로 거리를 그 자로 재면 그만큼 틀렸습니다. 이제 높이를 폭에서 끌어내
# 어느 쪽으로 재도 자가 맞습니다.
pw = 660
ph = int(round(pw * (LAT1 - LAT0) * KM_LAT / ((LON1 - LON0) * KM_LON)))
W, H = pw + PAD_L + PAD_R, ph + PAD_T + PAD_B
X = lambda lon: PAD_L + (lon - LON0) / (LON1 - LON0) * pw
Y = lambda lat: PAD_T + (LAT1 - lat) / (LAT1 - LAT0) * ph


def tw(s, size):
    """글자 폭 어림 — 한글·한자는 전각, 나머지는 반각."""
    return sum((size if ord(c) > 0x1100 else size * 0.55) for c in s)


def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def text(x, y, size, fill, t, anchor='start', weight=None, halo=SURF):
    """글자 하나를 두 번 찍는다 — 바탕색 테두리를 깔고 그 위에 글자.

    `paint-order` 한 줄이면 될 일이지만 그 속성을 모르는 그림 보기도 있고,
    모르면 테두리가 글자를 덮어 읽을 수 없게 된다. 두 번 찍기는 어디서나 같다.
    """
    w = ' font-weight="%s"' % weight if weight else ''
    c = ('<text x="%.1f" y="%.1f" font-size="%.1f" text-anchor="%s"%%s%s>%s</text>'
         % (x, y, size, anchor, w, esc(t)))
    out = []
    if halo:
        out.append(c % (' fill="none" stroke="%s" stroke-width="3.2" '
                        'stroke-linejoin="round"' % halo))
    out.append(c % (' fill="%s"' % fill))
    return out


placed = []            # 이미 자리를 잡은 상자들


def hit(b):
    for q in placed:
        if b[0] < q[2] and q[0] < b[2] and b[1] < q[3] and q[1] < b[3]:
            return True
    return (b[0] < PAD_L + 2 or b[2] > W - PAD_R - 2
            or b[1] < PAD_T + 2 or b[3] > PAD_T + ph - 2)


# 도곽 이름과 축척 자가 들어앉을 자리를 미리 잡아 둔다 — 그 위에 겹치지 않게.
for nm, s0, s1 in [('AMS Taejon 6622 I', 36.166667, 36.333333),
                   ('Kumsan 6622 II', 36.0, 36.166667)]:
    yy = Y(min(s1, LAT1))
    placed.append((X(127.50289) - 10 - tw(nm, 11), yy + 2, X(127.50289) - 2, yy + 19))
_km5 = 5 / KM_LON / (LON1 - LON0) * pw
placed.append((PAD_L + pw - 28 - _km5, PAD_T + ph - 36, PAD_L + pw - 6, PAD_T + ph))

SLOTS = [(10, 4, 'start'), (-10, 4, 'end'), (10, -9, 'start'), (-10, -9, 'end'),
         (10, 17, 'start'), (-10, 17, 'end'), (0, -12, 'middle'), (0, 23, 'middle'),
         (18, 17, 'start'), (-18, 17, 'end'), (18, -9, 'start'), (-18, -9, 'end')]
FS = 12.5
labels, leaders = [], []
for r in sorted(pts, key=lambda r: (-float(r['위도']), float(r['경도']))):
    x, y = X(float(r['경도'])), Y(float(r['위도']))
    s = label_of(r)
    w = tw(s, FS)
    for i, (dx, dy, anc) in enumerate(SLOTS):
        lx, ly = x + dx, y + dy
        x0 = lx if anc == 'start' else (lx - w if anc == 'end' else lx - w / 2)
        box = (x0 - 2, ly - FS, x0 + w + 2, ly + 4)
        if not hit(box):
            placed.append(box)
            labels.append((lx, ly, anc, s, not r['표제'].startswith('(미상)'), r['급']))
            if i >= 8:
                leaders.append((x, y, lx + (4 if anc == 'start' else (-4 if anc == 'end' else 0)), ly - 4))
            break
    else:
        placed.append((x + 8, y - FS, x + 8 + w, y + 4))
        labels.append((x + 10, y + 4, 'start', s, not r['표제'].startswith('(미상)'), r['급']))

o = ['<!-- 이 그림은 research/고개-위치.csv 에서 make-positions.py 가 만듭니다.'
     ' 손으로 고치지 마십시오 — 다음 실행에서 덮어씁니다.'
     ' 내용을 바꾸려면 고개-위치.csv 를 고치십시오. -->',
     '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
     'font-family="Pretendard, -apple-system, &quot;Apple SD Gothic Neo&quot;, '
     '&quot;Noto Sans KR&quot;, &quot;Malgun Gothic&quot;, sans-serif">' % (W, H, W, H),
     '<rect width="%d" height="%d" fill="%s"/>' % (W, H, SURF)]

# 제목
n = {g: sum(1 for r in pts if r['급'] == g) for g in 'ABC'}
nX = len(rows) - len(pts)
o += ['<text x="%d" y="38" font-size="20" font-weight="700" fill="%s">'
      '대전 지역 고개 — 자리를 아는 %s</text>' % (PAD_L, INK, ko_count(len(pts))),
      '<text x="%d" y="59" font-size="12.5" fill="%s">'
      '마름모 %s — 고갯마루 그 점 · 동그라미 %s — 옛 지도에서 환산 '
      '(<tspan font-weight="600">±1 km</tspan>) · 네모 %s — 자리는 그 동(洞) 어디쯤</text>'
      % (PAD_L, INK2, ko_count(n['A']), ko_count(n['B']), ko_count(n['C'])),
      '<text x="%d" y="77" font-size="12" fill="%s">'
      '동그라미는 하나도 빠짐없이 네모(AMS 도엽) 안에 있습니다 — '
      '네모 밖에는 환산할 저본이 없기 때문입니다</text>' % (PAD_L, INK3),
      '<text x="%d" y="95" font-size="12" fill="%s">'
      '이 밖에 자리를 전혀 모르는 고개가 %s 건 더 있어 여기 없습니다</text>'
      % (PAD_L, INK3, ko_count(nX))]

# ── 바탕 지도 (OpenStreetMap) ────────────────────────────────────────────────
# 점만 있으면 어디가 어디인지 알 수 없다. 물줄기·길·경계·산이 깔려야 비로소
# 「이 고개가 저 골짜기 머리」라고 읽힌다. 다만 바탕은 어디까지나 바탕이다 —
# 색을 다 빼고 가늘게 깔아, 파란 점이 늘 그림의 주인으로 남게 한다.
WATER_F, RIVER, STREAM = '#dde8f1', '#a9c5dd', '#cfdeeb'
EXPWY, ROAD, RAIL = '#ddd0ba', '#e8e0d2', '#d6d5cd'
BND4 = '#c9c3d6'
BGINK, BGMARK = '#8e8b81', '#b8b4a7'


L, Rt, T, B = PAD_L, PAD_L + pw, PAD_T, PAD_T + ph      # 그림틀


def clip(line):
    """그림틀 밖을 파이썬에서 잘라 낸다 — 토막 여럿이 될 수 있다.

    SVG 의 `clipPath` 로 해도 되지만 **쓰지 않는다.** GitHub 은 `.svg` 를
    그릴 때 내용을 한 번 걸러 내보내므로, 걸러 내는 쪽이 `clipPath` 를
    떨어뜨리면 바탕선이 여백으로 흘러나온다. 여기서 잘라 두면 무엇이
    그리든 같고, 틀 밖 좌표가 통째로 빠져 파일도 작아진다.
    """
    out, cur = [], []
    px = [(X(lo), Y(la)) for lo, la in line]
    for i in range(len(px) - 1):
        seg = lb(px[i], px[i + 1])
        if seg is None:
            if len(cur) > 1:
                out.append(cur)
            cur = []
            continue
        a2, b2 = seg
        if not cur or cur[-1] != a2:
            if len(cur) > 1:
                out.append(cur)
            cur = [a2]
        cur.append(b2)
    if len(cur) > 1:
        out.append(cur)
    return out


def lb(p0, p1):
    """리앙–바스키 — 토막 하나를 틀에 맞춰 자른다. 틀 밖이면 None."""
    x0, y0 = p0
    x1, y1 = p1
    dx, dy = x1 - x0, y1 - y0
    t0, t1 = 0.0, 1.0
    for pp, qq in ((-dx, x0 - L), (dx, Rt - x0), (-dy, y0 - T), (dy, B - y0)):
        if pp == 0:
            if qq < 0:
                return None
            continue
        r = qq / pp
        if pp < 0:
            if r > t1:
                return None
            t0 = max(t0, r)
        else:
            if r < t0:
                return None
            t1 = min(t1, r)
    return ((x0 + t0 * dx, y0 + t0 * dy), (x0 + t1 * dx, y0 + t1 * dy))


def clip_poly(line):
    """서덜랜드–호지먼 — 면(물)은 선처럼 자르면 안 된다. 잘린 자리를 틀의
    변으로 메워 닫아야 채움이 제대로 선다."""
    poly = [(X(lo), Y(la)) for lo, la in line]
    for side, keep in ((L, lambda q: q[0] >= L), (Rt, lambda q: q[0] <= Rt),
                       (T, lambda q: q[1] >= T), (B, lambda q: q[1] <= B)):
        if not poly:
            return []
        hor = side in (T, B)
        out = []
        for i in range(len(poly)):
            a2, b2 = poly[i - 1], poly[i]
            ka, kb = keep(a2), keep(b2)
            if ka != kb:
                d = (b2[1] - a2[1]) if hor else (b2[0] - a2[0])
                t = ((side - (a2[1] if hor else a2[0])) / d) if d else 0.0
                out.append((a2[0] + t * (b2[0] - a2[0]), a2[1] + t * (b2[1] - a2[1])))
            if kb:
                out.append(b2)
        poly = out
    return poly


def draw_water(key, fill):
    out = []
    for line in bg.get(key, []):
        q = clip_poly(line)
        if len(q) > 2:
            out.append('<path d="M%sZ" fill="%s" stroke="none"/>'
                       % ('L'.join('%.1f %.1f' % r for r in q), fill))
    return out


def draw(key, stroke, width, dash=None, fill='none', cap='round'):
    out = []
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    for line in bg.get(key, []):
        for seg in clip(line):
            out.append('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" '
                       'stroke-linecap="%s" stroke-linejoin="round"%s/>'
                       % ('M' + 'L'.join('%.1f %.1f' % q for q in seg),
                          fill, stroke, width, cap, d))
    return out


if bg:
    o += draw_water('물', WATER_F)
    o += draw_water('호수', WATER_F)        # 대청호
    o += draw_water('물섬', SURF)           # 섬은 물빛으로 칠하지 않는다
    o += draw('내', STREAM, 0.7)
    o += draw('강', RIVER, 2.2)
    o += draw('철도', RAIL, 1.2, dash='1 4')
    o += draw('국도', ROAD, 1.6)
    o += draw('고속', EXPWY, 2.6)
    o += draw('시도', BND4, 2, dash='8 5')

# 산봉우리와 면 소재지 — 고개를 읽는 데 쓰는 두 가지 길잡이.
# 고개 이름표가 이미 자리를 잡은 뒤에 끼워 넣는다. 자리가 없으면 넣지 않는다 —
# 바탕이 주인공을 가리느니 바탕이 빠지는 편이 낫다.
bgtext = []
if bg:
    # 높은 것부터 집어 가되 서로 충분히 떨어진 것만 — 온 산이 다 적히면
    # 고개가 묻힌다. 바탕의 일은 길잡이지 목록이 아니다.
    seen, kept = {}, []
    for q in sorted(bg.get('봉우리', []), key=lambda q: -q['높이']):
        if q['높이'] < 330 or len(kept) >= 20 or q['이름'].endswith('점'):
            continue
        if not (LAT0 < q['위도'] < LAT1 and LON0 < q['경도'] < LON1):
            continue
        if q['이름'] in seen:
            continue
        x, y = X(q['경도']), Y(q['위도'])
        if any(math.hypot(x - a, y - b) < 80 for a, b in kept):
            continue
        seen[q['이름']] = 1
        kept.append((x, y))
        o.append('<path d="M%.1f %.1fl4.6 7.4h-9.2z" fill="%s"/>' % (x, y - 4.4, BGMARK))
        for dx, dy, anc in ((7, 4, 'start'), (-7, 4, 'end'), (0, -8, 'middle'), (0, 15, 'middle')):
            w = tw(q['이름'], 11)
            lx, ly = x + dx, y + dy
            x0 = lx if anc == 'start' else (lx - w if anc == 'end' else lx - w / 2)
            box = (x0 - 2, ly - 11, x0 + w + 2, ly + 3)
            if not hit(box):
                placed.append(box)
                bgtext += text(lx, ly, 11, BGINK, q['이름'], anc)
                break

    # 시(市)는 조금 크게 — 그림에 닻이 하나는 있어야 어디를 보고 있는지 안다.
    for q in bg.get('마을', []):
        if q['갈래'] not in ('city', 'town'):
            continue
        if not (LAT0 < q['위도'] < LAT1 and LON0 < q['경도'] < LON1):
            continue
        big = q['갈래'] == 'city'
        fs = 13.5 if big else 11
        x, y = X(q['경도']), Y(q['위도'])
        w = tw(q['이름'], fs)
        box = (x - w / 2 - 2, y - fs + 2, x + w / 2 + 2, y + 5)
        if hit(box):
            continue
        placed.append(box)
        bgtext += text(x, y + 3.5, fs, '#7c7970' if big else BGINK, q['이름'], 'middle',
                       '600' if big else None)
o += bgtext

# **바탕이 덜 받아졌으면 그림에 적는다.** 받다 만 지도를 다 받은 것처럼
# 내놓으면, 비어 있는 곳을 「거기엔 길도 내도 없다」로 읽게 된다. 그것이
# 제일 나쁘다.
# **바탕이 어디까지 깔렸는지 자료에서 재어 적는다.** 받다 만 지도를 다 받은
# 것처럼 내놓으면, 비어 있는 곳을 「거기엔 길도 내도 없다」로 읽게 된다 —
# 그것이 제일 나쁘다. 세어 두는 것이 아니라 **그때그때 재므로** 낡지 않는다.
# 켜마다 가장 북쪽을 재고 **그 가운데 가장 낮은 것**을 택한다. 큰 강 하나는
# 범위를 넘어가도 통째로 딸려 오므로 그것만 보면 넓게 받은 줄 안다.
tops = [max(la for ln in bg[k] for _, la in ln)
        for k in ('강', '내', '고속', '국도', '철도', '물') if bg.get(k)]
reach = min(tops) if tops else LAT1
if reach < LAT1 - 0.02:
    o += text(PAD_L, 113, 11.5, '#a8632a',
              '⚠ 바탕의 길·물줄기·산은 북위 %d°%02d′ 까지만 받았습니다 — 그 위가 '
              '비어 보이는 것은 「없다」가 아니라 「아직 안 받았다」입니다'
              % (int(reach), round((reach - int(reach)) * 60)))

# 그림틀 — 바탕선이 여기서 잘린다. 테가 있어야 잘린 자리가 뜻있게 보인다.
o.append('<rect x="%d" y="%d" width="%d" height="%d" fill="none" stroke="%s" '
         'stroke-width="1"/>' % (PAD_L, PAD_T, pw, ph, '#dcdbd3'))

# 눈금 — 0.05° 마다, 아주 옅게
lon = math.ceil(LON0 / 0.05) * 0.05
while lon < LON1:
    o.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" stroke-width="1" '
             'stroke-dasharray="2 5"/>' % (X(lon), PAD_T, X(lon), PAD_T + ph, '#e6e5df'))
    o.append('<text x="%.1f" y="%d" font-size="10.5" fill="%s" text-anchor="middle">%s</text>'
             % (X(lon), PAD_T + ph + 18, INK3, '127°%02d′' % round((lon - 127) * 60)))
    lon += 0.05
lat = math.ceil(LAT0 / 0.05) * 0.05
while lat < LAT1:
    o.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" stroke-width="1" '
             'stroke-dasharray="2 5"/>' % (PAD_L, Y(lat), PAD_L + pw, Y(lat), '#e6e5df'))
    o.append('<text x="%d" y="%.1f" font-size="10.5" fill="%s" text-anchor="end">%s</text>'
             % (PAD_L - 8, Y(lat) + 3.5, INK3, '36°%02d′' % round((lat - 36) * 60)))
    lat += 0.05

# AMS 도엽 두 장의 도곽 — 14.5-1 에서 읽은 값. 이제 그림이 넓어져 **도엽이
# 통째로** 들어오므로 선 몇 개가 아니라 네모로 그린다. 그러면 한 가지가 저절로
# 보인다 — **좌표가 선 고개는 모두 이 네모 안에 있고, 밖에 있는 고개는 아직
# 동(洞)까지밖에 모른다.** 급이 갈리는 까닭이 그림에 그대로 나온다.
SHEETS = [('AMS Taejon 6622 I', 36.166667, 36.333333),
          ('Kumsan 6622 II', 36.0, 36.166667)]
for nm, s0, s1 in SHEETS:
    y0, y1 = Y(min(s1, LAT1)), Y(max(s0, LAT0))
    o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" '
             'stroke="%s" stroke-width="1.5"/>'
             % (X(127.25289), y0, X(127.50289) - X(127.25289), y1 - y0, '#cfcec6'))
    o += text(X(127.50289) - 6, y0 + 15, 11, INK3, nm, 'end', halo=SURF)

# 점
# 점 — 생김새가 둘을 말한다. **동그라미는 옛 지도에서 자리를 얻은 것**(급 B),
# **네모는 오늘 이름은 아는데 자리는 동(洞)까지만인 것**(급 C). 그리고 동그라미
# 가운데 색이 찬 것만 우리말 이름이 섰다.
def mark(x, y, grade, named):
    out = []
    if grade == 'A':
        # 마름모 — **고갯마루 그 점**을 얻은 것. 동그라미(도엽 환산)와 한눈에 갈린다.
        d = 'M%.1f %.1fl6.4 6.4l-6.4 6.4l-6.4 -6.4z' % (x, y - 6.4)
        out.append('<path d="%s" fill="none" stroke="%s" stroke-width="3.5"/>' % (d, SURF))
        out.append('<path d="%s" fill="%s" stroke="%s" stroke-width="1.5"/>'
                   % (d, BLUE, '#17508f'))
    elif grade == 'C':
        out.append('<rect x="%.1f" y="%.1f" width="9" height="9" fill="none" '
                   'stroke="%s" stroke-width="3.5"/>' % (x - 4.5, y - 4.5, SURF))
        out.append('<rect x="%.1f" y="%.1f" width="9" height="9" fill="%s" '
                   'stroke="%s" stroke-width="2"/>' % (x - 4.5, y - 4.5, SURF, SLATE))
    else:
        out.append('<circle cx="%.1f" cy="%.1f" r="6.5" fill="none" stroke="%s" '
                   'stroke-width="3"/>' % (x, y, SURF))
        out.append('<circle cx="%.1f" cy="%.1f" r="5" fill="%s" stroke="%s" '
                   'stroke-width="2"/>'
                   % (x, y, BLUE if named else SURF, BLUE if named else GREY))
    return out


for r in pts:
    o += mark(X(float(r['경도'])), Y(float(r['위도'])), r['급'],
              not r['표제'].startswith('(미상)'))
for a1, b1, c1, d1 in leaders:
    o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="3"/>'
             % (a1, b1, c1, d1, SURF))
    o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1"/>'
             % (a1, b1, c1, d1, INK3))
for lx, ly, anc, nm, named, grade in labels:
    o += text(lx, ly, FS, (INK2 if grade == 'C' else INK) if named else INK2, nm, anc,
              '600' if named and grade != 'C' else None)

# 범례 · 축척
ly0 = H - PAD_B + 40
KEY = [('A', True,  '고갯마루 그 점을 얻음 (±0.3 km)'),
       ('C', True,  '이름만 알고 자리는 동(洞)까지 (1~3 km)'),
       ('B', True,  '옛 지도에서 환산 (±1 km) · 이름도 섬'),
       ('B', False, '옛 지도에서 환산 · 이름은 아직 (미상)')]
for i, (g, nmd, lab) in enumerate(KEY):
    kx = PAD_L + 6 + (i % 2) * 330
    ky = ly0 + (i // 2) * 19
    o += mark(kx, ky - 4, g, nmd)
    o += text(kx + 13, ky, 12, INK2, lab)

# 바탕에 무엇이 깔려 있는지 — 선이 무슨 뜻인지 모르면 바탕은 얼룩일 뿐이다
if bg:
    kx = PAD_L + 6
    for stroke, wd, dash, lab in ((RIVER, 2.2, None, '물줄기'), (EXPWY, 2.6, None, '고속·국도'),
                                  (BND4, 2, '6 4', '시·도 경계'), (RAIL, 1.2, '1 4', '철도')):
        o.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="%s"%s/>'
                 % (kx, ly0 + 46, kx + 20, ly0 + 46, stroke, wd,
                    ' stroke-dasharray="%s"' % dash if dash else ''))
        o += text(kx + 25, ly0 + 50, 11, INK3, lab)
        kx += 33 + tw(lab, 11)
    o.append('<path d="M%d %dl4.6 7.4h-9.2z" fill="%s"/>' % (kx, ly0 + 42, BGMARK))
    o += text(kx + 7, ly0 + 50, 11, INK3, '산 — 회색 글자는 오늘 지명')
# 축척 자 — 그림틀 **안** 오른쪽 아래에 둔다(범례와 부딪치지 않게).
# 가로세로 축척이 같으므로 이 자는 어느 쪽으로 재도 맞는다.
km5 = 5 / KM_LON / (LON1 - LON0) * pw
sx, sy = PAD_L + pw - 16 - km5, PAD_T + ph - 22
o += ['<rect x="%.1f" y="%.1f" width="%.1f" height="34" fill="%s"/>'
      % (sx - 10, sy - 12, km5 + 20, SURF),
      '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2"/>' % (sx, sy, sx + km5, sy, INK2),
      '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2"/>' % (sx, sy - 4, sx, sy + 4, INK2),
      '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2"/>' % (sx + km5, sy - 4, sx + km5, sy + 4, INK2),
      '<text x="%.1f" y="%.1f" font-size="11.5" fill="%s" text-anchor="middle">5 km</text>' % (sx + km5 / 2, sy + 16, INK2),
      '<text x="%d" y="%d" font-size="11" fill="%s">북 ↑ · 등장방형 도법 · '
      '바탕·고갯마루 점은 © OpenStreetMap 기여자, ODbL</text>' % (PAD_L + 6, ly0 + 67, INK3),
      '</svg>']
io.open(SVG, 'w', encoding='utf-8').write('\n'.join(o) + '\n')


# ── ③ 대조표 3.1 의 「대장」 표 ──────────────────────────────────────────────
md = ['| 표제 | 한자 | 위도 | 경도 | 급 | 도엽 자리 | 비고 |',
      '|---|---|---|---|---|---|---|']
for r in rows:
    pl = ' · '.join('`%s`' % x for x in r['도엽자리'].split('; ') if x) or '—'
    md.append('| %s | `%s` | %s | %s | **%s** | %s | %s |' % (
        r['표제'], r['한자'], r['위도'] or '—', r['경도'] or '—', r['급'], pl, r['비고']))
doc = io.open(DOC, encoding='utf-8').read()
doc = re.sub(r'(?<=#### 대장\n\n)\|.*?\n(?=\n\*\*읽는 법)', '\n'.join(md) + '\n', doc, flags=re.S)
io.open(DOC, 'w', encoding='utf-8').write(doc)

print('%d 건 · 좌표 %d 점 → %s · %s · 대장 표' % (len(rows), len(pts), GJ, SVG))
