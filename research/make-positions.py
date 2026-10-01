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
rows = list(csv.DictReader(io.open(CSV, encoding='utf-8')))
pts = [r for r in rows if r['위도']]


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
            "marker-color": "#2a78d6" if named else "#7b7a73",
            "marker-size": "medium",
        }})
io.open(GJ, 'w', encoding='utf-8').write(json.dumps(
    {"type": "FeatureCollection",
     "properties": {"이름": "대전 지역 고개 — 좌표가 선 것",
                    "만든것": "이 파일은 research/고개-위치.csv 에서 make-positions.py 가 "
                              "만듭니다. 손으로 고치지 마십시오 — 다음 실행에서 덮어씁니다. "
                              "내용을 바꾸려면 고개-위치.csv 를 고치십시오.",
                    "설명": "대전향토문화연구회 고개 조사. 좌표는 미군 AMS 1:50,000"
                            "(저본 1919) 그리드를 환산한 것으로 ±1 km 로 읽으십시오. "
                            "자세한 것은 research/대전-고개-대조표.md 의 3.1 과 14.5-3.",
                    "만든날": "2026-10-01"},
     "features": feats}, ensure_ascii=False, indent=1) + '\n')


# ── ② SVG 지도 ───────────────────────────────────────────────────────────────
LAT0, LAT1, LON0, LON1 = 36.090, 36.300, 127.243, 127.517   # 그림 범위
W, H = 980, 790
PAD_L, PAD_R, PAD_T, PAD_B = 74, 56, 96, 86
INK, INK2, INK3 = '#0b0b0b', '#52514e', '#9a9992'
BLUE, GREY, SURF = '#2a78d6', '#7b7a73', '#fcfcfb'
KM_LAT = 111.0
KM_LON = 111.320 * math.cos(math.radians((LAT0 + LAT1) / 2))

pw, ph = W - PAD_L - PAD_R, H - PAD_T - PAD_B
X = lambda lon: PAD_L + (lon - LON0) / (LON1 - LON0) * pw
Y = lambda lat: PAD_T + (LAT1 - lat) / (LAT1 - LAT0) * ph


def tw(s, size):
    """글자 폭 어림 — 한글·한자는 전각, 나머지는 반각."""
    return sum((size if ord(c) > 0x1100 else size * 0.55) for c in s)


placed = []            # 이미 자리를 잡은 상자들


def hit(b):
    for q in placed:
        if b[0] < q[2] and q[0] < b[2] and b[1] < q[3] and q[1] < b[3]:
            return True
    return (b[0] < 8 or b[2] > W - 8 or b[1] < PAD_T - 22 or b[3] > H - PAD_B + 24)


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
            labels.append((lx, ly, anc, s, not r['표제'].startswith('(미상)')))
            if i >= 8:
                leaders.append((x, y, lx + (4 if anc == 'start' else (-4 if anc == 'end' else 0)), ly - 4))
            break
    else:
        placed.append((x + 8, y - FS, x + 8 + w, y + 4))
        labels.append((x + 10, y + 4, 'start', s, not r['표제'].startswith('(미상)')))

o = ['<!-- 이 그림은 research/고개-위치.csv 에서 make-positions.py 가 만듭니다.'
     ' 손으로 고치지 마십시오 — 다음 실행에서 덮어씁니다.'
     ' 내용을 바꾸려면 고개-위치.csv 를 고치십시오. -->',
     '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
     'font-family="Pretendard, -apple-system, &quot;Apple SD Gothic Neo&quot;, '
     '&quot;Noto Sans KR&quot;, &quot;Malgun Gothic&quot;, sans-serif">' % (W, H, W, H),
     '<rect width="%d" height="%d" fill="%s"/>' % (W, H, SURF)]

# 제목
o += ['<text x="%d" y="38" font-size="20" font-weight="700" fill="%s">'
      '대전 지역 고개 — 좌표가 선 열여섯</text>' % (PAD_L, INK),
      '<text x="%d" y="59" font-size="12.5" fill="%s">미군 AMS 1:50,000(저본 1919) '
      '그리드를 환산한 값 · <tspan font-weight="600">±1 km 로 읽으십시오</tspan></text>' % (PAD_L, INK2),
      '<text x="%d" y="77" font-size="12" fill="%s">지도 위쪽 바깥(북위 36°20′ 너머)이 '
      '대전 시가입니다 — 고개는 모두 그 남쪽에 있습니다</text>' % (PAD_L, INK3)]

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

# AMS 도엽 두 장의 도곽 — 14.5-1 에서 읽은 값
for lon_e in (127.25289, 127.50289):
    o.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" stroke-width="1.5"/>'
             % (X(lon_e), PAD_T, X(lon_e), PAD_T + ph, '#cfcec6'))
o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.5"/>'
         % (X(127.25289), Y(36.166667), X(127.50289), Y(36.166667), '#cfcec6'))
o.append('<text x="%.1f" y="%.1f" font-size="11" fill="%s" text-anchor="end">'
         'AMS Taejon 6622 I ↑ · Kumsan 6622 II ↓  (36°10′)</text>'
         % (X(127.50289) - 6, Y(36.166667) - 7, INK3))

# 점
for r in pts:
    x, y = X(float(r['경도'])), Y(float(r['위도']))
    named = not r['표제'].startswith('(미상)')
    o.append('<circle cx="%.1f" cy="%.1f" r="5" fill="%s" stroke="%s" stroke-width="2"/>'
             % (x, y, BLUE if named else SURF, BLUE if named else GREY))
for a, b, c, d in leaders:
    o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1"/>'
             % (a, b, c, d, INK3))
for lx, ly, anc, s, named in labels:
    o.append('<text x="%.1f" y="%.1f" font-size="%.1f" text-anchor="%s" fill="%s"%s>%s</text>'
             % (lx, ly, FS, anc, INK if named else INK2,
                ' font-weight="600"' if named else '', s))

# 범례 · 축척
ly0 = H - PAD_B + 40
o += ['<circle cx="%d" cy="%d" r="5" fill="%s"/>' % (PAD_L + 6, ly0 - 4, BLUE),
      '<text x="%d" y="%d" font-size="12" fill="%s">우리말 이름이 선 것</text>' % (PAD_L + 18, ly0, INK2),
      '<circle cx="%d" cy="%d" r="5" fill="%s" stroke="%s" stroke-width="2"/>' % (PAD_L + 176, ly0 - 4, SURF, GREY),
      '<text x="%d" y="%d" font-size="12" fill="%s">아직 (미상) — 한자만</text>' % (PAD_L + 188, ly0, INK2)]
km5 = 5 / KM_LON / (LON1 - LON0) * pw                      # 5 km 의 화면 길이
sx = W - PAD_R - km5
o += ['<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" stroke-width="2"/>' % (sx, ly0 - 6, sx + km5, ly0 - 6, INK2),
      '<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" stroke-width="2"/>' % (sx, ly0 - 10, sx, ly0 - 2, INK2),
      '<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" stroke-width="2"/>' % (sx + km5, ly0 - 10, sx + km5, ly0 - 2, INK2),
      '<text x="%.1f" y="%d" font-size="11.5" fill="%s" text-anchor="middle">5 km</text>' % (sx + km5 / 2, ly0 + 12, INK2),
      '<text x="%d" y="%d" font-size="11" fill="%s">북 ↑ · 등장방형 도법</text>' % (PAD_L + 6, ly0 + 20, INK3),
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
