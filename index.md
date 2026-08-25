---
layout: default
title:
---

<p class="preface">
<span class="first">대전의 기억은 기록될 때 남습니다.</span><br>
대전향토문화연구회는 이 고장의 고개와 나루, 옛 고을과 사람의 일을
조사하고 기록하여, 누구나 찾아 쓸 수 있는 지식으로 남기는 연구 모임입니다.
</p>

연구의 결과는 회지 「대전향토연구」로 펴내고, 위키백과·위키데이터·위키문헌에
연결하여 오래 남도록 합니다. 규장각 소장 『1872년 지방지도』 465장을
위키데이터에 구조화하는 일을 마쳤으며, 대전의 옛 고갯길 조사를 진행하고 있습니다.

---

## 최근 소식

<ul class="entry-list">
{% for post in site.posts limit: 5 %}
  <li>
    <time datetime="{{ post.date | date_to_xmlschema }}">{{ post.date | date: "%Y.%m.%d" }}</time>
    <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
  </li>
{% endfor %}
</ul>

[소식 전체 보기](/notice/)
