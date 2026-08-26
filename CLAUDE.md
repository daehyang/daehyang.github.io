# daehyang.github.io

대전향토문화연구회 공식 홈페이지. Jekyll + GitHub Pages(legacy build).
`main`에 푸시하면 몇 분 내 https://daehyang.github.io 에 반영된다.

남은 일은 `internal` 저장소의 **Issues**에 있다. 연구회 GitHub 운영 문서도 그 저장소의
`docs/` 에 있다 — `operations.md`(임원용 절차, 홈페이지 관리 방법 포함) ·
`maintenance.md`(기술) · `decisions.md`(결정 기록). 비공개 저장소이므로 접근 권한이 필요하다.

## 브랜치와 푸시

- **`main` 에 직접 푸시**한다. 브랜치와 PR 을 만들지 않는다
  (`internal/docs/decisions.md` 0012). 세 저장소 중 `journal` 만 브랜치·PR 을 쓴다.
- `main` 이 곧 배포다. 그래서 **사이트에 나가는 파일을 고쳤으면 푸시 전에 로컬 빌드로
  확인한다** (아래 "로컬 빌드"). Liquid 오류는 빌드에서만 잡힌다.
  `CLAUDE.md`·`README.md`·`Gemfile` 은 `_config.yml` 의 `exclude` 에 있어 빌드에
  영향이 없으므로 이 확인이 필요없다.

## 구조

```
_config.yml       사이트 설정 + 연구회 식별 정보(org.*) — 푸터·메타에서 참조
_layouts/         default.html(전체 골격) / page.html / post.html
assets/           style.css, seal.svg(파비콘·브랜드 인장)
index.md          첫 화면 (레이아웃 default 직접 지정)
about.md journal.md projects.md notice.md    고정 페이지 (permalink 각자 지정)
_posts/           소식 글: YYYY-MM-DD-제목.md
```

## 규칙

- **본문은 한국어**로 쓴다. 단체명·회지명 등은 필요할 때 한자를 병기한다(`大田鄕土文化硏究會`).
- 고정 페이지는 front matter에 `title`과 `permalink`를 둔다. 레이아웃은 `_config.yml`의
  `defaults`가 자동으로 붙이므로 따로 쓰지 않는다 (`index.md`만 예외).
- 연구회 식별 정보(창립일·위키백과·위키데이터·ISNI·회지 ISSN)는 `_config.yml`의 `org.*`에 한 번만 두고
  `_layouts/default.html`에서 참조한다. 페이지 본문에 숫자를 새로 하드코딩하지 않는다.
  단 `about.md`의 "공식 식별 정보" 표는 독자에게 보여주는 표라 예외로 값을 직접 적는다 —
  값을 바꿀 때는 `_config.yml`과 함께 바꾼다.
- 외부 리소스는 Google Fonts만 쓴다. CDN 스크립트를 새로 들이지 않는다.
- 외부 기관으로 나가는 주소는 **틀을 `_config.yml`의 `org.*`에 두고** 페이지에서
  이어 붙인다. 기관이 화면을 개편해 경로가 바뀌어도 한 줄만 고치면 된다.
  지금 그런 값은 `org.nlk_url`(국립중앙도서관 저자전거 화면)이다.
- **연구회 자기 문서(한국어 위키백과 「대전향토문화연구회」)는 직접 편집하지 않는다.** 이해충돌로
  본다. 사실이 틀리면 그 문서의 토론 문서에 근거를 대고 고쳐 달라고 요청한다. 사이트에서는
  링크만 건다(`org.wikipedia`).
  그 주소가 죽으면 ISNI 기록(`isni.org/isni/0000000530772340`)의 Notes 항목이
  같은 주소를 담고 있으니 거기서 새 주소를 찾는다 — 도서관이 ISNI 에 제출하는
  값이라 개편되면 그쪽도 갱신될 가능성이 높다.

## 생성물 — 직접 고치지 말 것

다음은 `internal` 저장소의 `tools/export_public.py`가 만든다. 손으로 고치면 다음 실행에서
덮어쓴다. 내용을 바꾸려면 `internal/placenames/registry.csv`를 고치고 스크립트를 다시 돌린다.

```
_placenames/DHC-*.md        향토문화 ID 한 건이 한 장 → /id/<ID>/
assets/data/placenames.csv  공개 목록의 기계 판독용 사본
catalogue/*.md              해마다 동결하는 발간본 「대전향토문화목록」
```

`_placenames`는 Jekyll 컬렉션이다(`_config.yml`의 `collections`). 주소는 각 문서의
`permalink`으로 정한다 — 컬렉션 permalink의 `:name`은 슬러그화 때 소문자로 바뀌어
`DHC-`가 `dhc-`가 되기 때문이다. **`/id/<ID>/` 주소 형식은 바꾸지 않는다.**
위키데이터 외부 식별자 속성 제안의 formatter URL로 쓸 영구 주소이고,
이미 공개·인용된 ID의 링크가 끊긴다.

사람이 고치는 쪽은 `placenames.md`(목록 안내 페이지)와 두 레이아웃
(`_layouts/placename.html`, `_layouts/catalogue.html`)이다.

## 주의

- `_config.yml`의 `url`은 `https://daehyang.github.io`, `baseurl`은 빈 문자열이다.
  저장소 이름이 조직명과 같아 organization site로 동작하므로 이 값을 바꾸면 링크가 깨진다.
- `org.email`은 **아직 빈 값**이다. 대표 메일이 확정되면 기입한다. 그때
  `about.md`의 "대표 연락처는 준비 중입니다" 문장도 함께 고친다.
- 회지 안내(`journal.md`)의 DOI 표는 Zenodo에서 호마다 수동으로 받은 DOI를 적는 곳이다.
  자동 발급이 아니다 — `journal` 저장소의 `CLAUDE.md` 참조.
- `Gemfile`은 로컬 미리보기용이다. GitHub Pages는 자체 `github-pages` 버전으로 빌드하므로
  플러그인을 추가할 때는 GitHub Pages 허용 목록에 있는지 먼저 확인한다.

## 로컬 빌드

`bundle install && bundle exec jekyll serve`가 정식 경로다. `github-pages` gem 전체를
받지 않고 빠르게 확인만 하려면 jekyll을 직접 써도 된다(2026-08-25에 Jekyll 4.4.1로 확인):

```
gem install jekyll jekyll-feed jekyll-sitemap tzinfo tzinfo-data
jekyll build --destination <임시경로> --disable-disk-cache
```

- Windows에서 `tzinfo`·`tzinfo-data`가 없으면 `_config.yml`의 `timezone: Asia/Seoul`
  때문에 빌드가 실패한다.
- 경로가 아주 긴 폴더에서 빌드하면 `.jekyll-cache` 쓰기가 실패한다 —
  그때는 `--disable-disk-cache`를 붙인다.
- 빌드 산출물(`_site/`, `.jekyll-cache/`)은 `.gitignore`에 있다. 커밋하지 않는다.
