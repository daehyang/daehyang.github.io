# -*- coding: utf-8 -*-
"""회덕 도엽의 고개를 좌표에 앉힙니다 (2026-10-04).

규장각 지명 색인의 화소 좌표를, 오늘 좌표를 아는 지점 넷~여섯으로
어파인 변환해 고개 자리를 구합니다. 기준 좌표는 이 저장소의
`배경-osm.json`(OpenStreetMap)에서 가져왔습니다.

    python3 회덕-고개-좌표맞추기.py

색인은 `/tmp/kyu_index.json` 이 있으면 쓰고, 없으면 규장각에서 받습니다.
받는 법은 `고지도-받는-법.md` 의 「지명 색인은 뷰어 요청에 딸려 옵니다」.

**잔차를 반드시 보십시오.** 방안식 도엽은 1.3 km, 1872년 회화식 도엽은
2.1 km 입니다. 고개 사이 간격이 1.8~4.5 km 이므로 **1872년 쪽은 어느 고개인지
가리는 데 쓸 수 없습니다.** 생성물 — 결과는 규장각-고지도-새계열.md 5.8 에.
"""
import json, math
import numpy as np
IDX=json.load(open('/tmp/kyu_index.json'))
REF={'계족산':(36.3847,127.4392),'식장산':(36.2997,127.4811),'세천':(36.3250,127.4908),
     '미호':(36.4595,127.4715),'전민':(36.4030,127.3988),'신탄':(36.4476,127.4360),
     '비래동':(36.3614,127.4544),'읍내동':(36.3779,127.4252),'추동':(36.3742,127.4729)}
def cen(e): return ((e[1]+e[3])/2.0,(e[2]+e[4])/2.0)
def allpts(ser,lab):
    for s in IDX[ser]:
        if s['도엽']==lab:
            out={}
            for n in s['색인']: out.setdefault(n[0],[]).append(cen(n))
            return out
def fit(pairs,name):
    A=np.array([[p[0],p[1],1.0] for p in pairs])
    cl=np.linalg.lstsq(A,np.array([p[3] for p in pairs]),rcond=None)[0]
    ca=np.linalg.lstsq(A,np.array([p[2] for p in pairs]),rcond=None)[0]
    res=[math.hypot((cl@[p[0],p[1],1]-p[3])*88700,(ca@[p[0],p[1],1]-p[2])*111000) for p in pairs]
    print('── %s · 기준점 %d · 잔차 평균 %.0f m 최대 %.0f m   [%s]'
          %(name,len(pairs),sum(res)/len(res),max(res),
            ' '.join('%s %.0f'%(p[4],r) for p,r in zip(pairs,res))))
    return cl,ca
def ap(cl,ca,p): return float(ca@[p[0],p[1],1]), float(cl@[p[0],p[1],1])

RES={}
# ── 방안식 둘 : 질치 두 건을 x 로 갈라 質峙(서) / 迭峙(동)
for ser,lab,ctrl in [('조선지도','회덕',['계족산!학족산봉','식장산','전민!정민역','미호']),
                     ('팔도군현지도','회덕',['계족산','식장산','전민!정민역','미호'])]:
    P=allpts(ser,lab); pairs=[]
    for c in ctrl:
        ref,key=(c.split('!')+[c])[:2] if '!' in c else (c,c)
        if key not in P: print('  ! %s 없음'%key); continue
        la,lo=REF[ref]; px,py=P[key][0]; pairs.append((px,py,la,lo,ref))
    cl,ca=fit(pairs,'%s %s'%(ser,lab))
    jj=sorted(P.get('질치',[]))      # x 오름차순 = 서→동
    names=[('質峙',jj[0])] + ([('迭峙',jj[1])] if len(jj)>1 else [])
    if len(jj)==1: names=[('迭峙',jj[0])] if ser=='조선지도' else names
    tgt=[('東峙',P['동치'][0])]+names+[('遠峙',P['원치'][0])]
    RES[ser]={}
    for nm,p in tgt:
        la,lo=ap(cl,ca,p); RES[ser][nm]=(la,lo); print('     %-4s %.4f, %.4f'%(nm,la,lo))
    print()
# ── 1872 회덕현지도
import re, urllib.request, urllib.parse, time
def viewer(cd,img,n=4):
    for i in range(n):
        try:
            b=urllib.parse.urlencode({'item_cd':'GZD','book_cd':cd,'vol_no':'','page_no':'',
                'imgFileNm':img,'tbl_conts_seq':'','mokNm':'','add_page_no':''}).encode()
            r=urllib.request.Request('https://kyudb.snu.ac.kr/pf01/rendererImg.do',b,
              {'User-Agent':'Mozilla/5.0','Referer':'https://kyudb.snu.ac.kr/book/text.do?mid=GZD',
               'Content-Type':'application/x-www-form-urlencoded'})
            return urllib.request.urlopen(r,timeout=120).read().decode('utf-8','replace')
        except Exception:
            if i==n-1: raise
            time.sleep(4*(i+1))
R=re.compile(r"\('(\d+)',\s*'(\d+)',\s*'(\d+)',\s*'(\d+)',\s*'([^']*)',\s*'([^']*\.jpg)'\)")
t=viewer('GM99999_00','KYKH002_0000_0046.jpg')
P8={}
for m in R.finditer(t):
    if m.group(6)!='KYKH002_0000_0046.jpg': continue
    P8.setdefault(m.group(5),[]).append(((int(m.group(1))+int(m.group(3)))/2.0,
                                         (int(m.group(2))+int(m.group(4)))/2.0))
pairs=[]
for key,ref in [('계족산','계족산'),('식장산','식장산'),('전민역','전민'),
                ('비래동','비래동'),('세천','세천'),('신탄시','신탄')]:
    if key in P8:
        la,lo=REF[ref]; px,py=P8[key][0]; pairs.append((px,py,la,lo,ref))
cl,ca=fit(pairs,'1872 회덕현지도')
la,lo=ap(cl,ca,P8['길치'][0]); RES['1872']={'吉峙':(la,lo)}
print('     %-4s %.4f, %.4f'%('吉峙',la,lo))
json.dump(RES,open('/tmp/geo_out.json','w'),ensure_ascii=False,indent=1)
