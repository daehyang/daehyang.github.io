# daehyang.github.io

대전향토문화연구회 공식 홈페이지. Jekyll + GitHub Pages(legacy build).
`main`에 푸시하면 몇 분 내 https://daehyang.github.io 에 반영된다.

전체 진행 상황과 남은 일은 **`internal` 저장소의 `docs/SETUP-GUIDE.md`**가 기준이다
(비공개 저장소이므로 접근 권한 필요).

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
- 연구회 식별 정보(창립일·위키데이터·ISNI)는 `_config.yml`의 `org.*`에 한 번만 두고
  `_layouts/default.html`에서 참조한다. 페이지 본문에 숫자를 새로 하드코딩하지 않는다.
  단 `about.md`의 "공식 식별 정보" 표는 독자에게 보여주는 표라 예외로 값을 직접 적는다 —
  값을 바꿀 때는 `_config.yml`과 함께 바꾼다.
- 외부 리소스는 Google Fonts만 쓴다. CDN 스크립트를 새로 들이지 않는다.

## 주의

- `_config.yml`의 `url`은 `https://daehyang.github.io`, `baseurl`은 빈 문자열이다.
  저장소 이름이 조직명과 같아 organization site로 동작하므로 이 값을 바꾸면 링크가 깨진다.
- `org.email`은 **아직 빈 값**이다. 대표 메일이 확정되면 기입한다. 그때
  `about.md`의 "대표 연락처는 준비 중입니다" 문장도 함께 고친다.
- 회지 안내(`journal.md`)의 DOI 표는 Zenodo에서 호마다 수동으로 받은 DOI를 적는 곳이다.
  자동 발급이 아니다 — `journal` 저장소의 `CLAUDE.md` 참조.
- `Gemfile`은 로컬 미리보기용이다. GitHub Pages는 자체 `github-pages` 버전으로 빌드하므로
  플러그인을 추가할 때는 GitHub Pages 허용 목록에 있는지 먼저 확인한다.
