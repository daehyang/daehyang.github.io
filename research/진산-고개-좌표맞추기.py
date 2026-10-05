# -*- coding: utf-8 -*-
"""해동지도 진산군 도엽의 고개를 좌표에 앉힙니다 (2026-10-05).

규장각 지명 색인의 화소 좌표를, 오늘 좌표를 아는 지점 여섯으로 어파인 변환해
고개 자리를 구합니다. 색인은 이 저장소의 `규장각-색인.csv` 에서 읽고(받는 법은
`고지도-받는-법.md`), 기준 좌표는 `배경-osm.json`(OpenStreetMap)에서 가져왔습니다.

    python3 진산-고개-좌표맞추기.py

**잔차를 반드시 보십시오 — 1.7 km 입니다.** 회덕 방안식 도엽(1.3 km)보다 나쁩니다.
해동지도 진산군은 6·7책 저화질 회화식 도엽이고, 읍치를 왼쪽 아래로 몰아 그렸습니다.
그래서 **이 결과로 「어느 고개인가」를 가리지 못합니다.** 쓸 수 있는 것은
**차례와 방향**뿐입니다 — 예컨대 `方古峙` 가 `晩目峙` 보다 서쪽이라는 것.

**기준점 여덟 가운데 둘을 뺐습니다.** `천비산`(잔차 6.7 km)과 `서대산`(4.2 km)은
도엽이 둘 다 만인산 동쪽에 몰아 그려 놓아 변환을 망칩니다. 여덟 다 쓰면
잔차가 3.3 km 로 뛰므로, 뺀 뒤의 1.7 km 를 씁니다. **뺐다는 사실을 숨기지 마십시오.**

생성물 — 결과는 `규장각-고지도-새계열.md` 5.13 과 `해동지도-진산군-판독.md` 에.
"""
import csv, math

SHEET = ('해동지도', '진산군')

# 오늘 좌표 — 배경-osm.json 의 봉우리/마을 점, 배티재는 고갯마루
REF = {'대둔산': (36.1246, 127.3205), '오대산': (36.1353, 127.3452),
       '이치험애': (36.1216, 127.3472), '객사': (36.1475, 127.3758),
       '만이산': (36.1966, 127.4407), '인대봉': (36.1053, 127.3978),
       '서대산': (36.2207, 127.5384), '천비산': (36.2345, 127.3879)}
DROP = ('서대산', '천비산')          # 도엽이 어그러뜨린 둘 — 머리말을 보십시오
GOGAE = ['방고치', '만목치', '신치', '거치', '삽치', '송원치', '국치험애']


def 색인(계열, 도엽):
    P = {}
    with open('규장각-색인.csv', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if r['계열'] == 계열 and 도엽 in r['도엽']:
                P.setdefault(r['지명'], ((int(r['x1']) + int(r['x2'])) / 2.0,
                                        (int(r['y1']) + int(r['y2'])) / 2.0))
    return P


def 최소제곱(A, b):
    """정규방정식을 가우스 소거로 — numpy 없이 돌게 두었습니다."""
    n = 3
    M = [[sum(A[k][i] * A[k][j] for k in range(len(A))) for j in range(n)]
         + [sum(A[k][i] * b[k] for k in range(len(A)))] for i in range(n)]
    for i in range(n):
        p = max(range(i, n), key=lambda r: abs(M[r][i]))
        M[i], M[p] = M[p], M[i]
        for r in range(n):
            if r != i:
                f = M[r][i] / M[i][i]
                for c in range(i, n + 1):
                    M[r][c] -= f * M[i][c]
    return [M[i][n] / M[i][i] for i in range(n)]


def km(a, b):
    return math.hypot((a[0] - b[0]) * 111.0,
                      (a[1] - b[1]) * 111.0 * math.cos(math.radians(36.17)))


def main():
    P = 색인(*SHEET)
    names = [n for n in REF if n not in DROP and n in P]
    A = [[P[n][0], P[n][1], 1.0] for n in names]
    cl = 최소제곱(A, [REF[n][1] for n in names])
    ca = 최소제곱(A, [REF[n][0] for n in names])
    앉히기 = lambda p: (ca[0] * p[0] + ca[1] * p[1] + ca[2],
                     cl[0] * p[0] + cl[1] * p[1] + cl[2])

    print('── %s %s · 기준점 %d' % (SHEET[0], SHEET[1], len(names)))
    s = 0.0
    for n in names:
        d = km(앉히기(P[n]), REF[n]); s += d * d
        print('   %-6s 잔차 %4.2f km' % (n, d))
    print('   RMS %.2f km   (뺀 기준점: %s)' % (math.sqrt(s / len(names)), ' '.join(DROP)))
    print()
    for n in GOGAE:
        if n in P:
            la, lo = 앉히기(P[n]); print('   %-6s %.4f, %.4f' % (n, la, lo))
    print()
    # 1919년 1:50,000 Kumsan 도엽이 짚어 준 자리와 견주기 (대조표 14.7)
    for n, (la, lo), 라벨 in [('방고치', (36.162, 127.348), '方峴里 · AMS 1034.2/1473.5'),
                            ('만목치', (36.1883, 127.3161), '벌곡면 만목리(晩木里)')]:
        if n in P:
            print('   %s → %s : %.1f km' % (n, 라벨, km(앉히기(P[n]), (la, lo))))


if __name__ == '__main__':
    main()
