---
title: 향토문화 ID 공개 등재부
permalink: /placenames/
description: 대전향토문화연구회가 심의를 거쳐 확정 등재한 대전 향토문화 항목의 공개 등재부.
---

대전향토문화연구회는 대전의 향토문화 항목(고개·나루·시장·마을 등)에 **향토문화 ID**를 부여하여
등재하고, 확정된 항목을 이곳에 공개합니다. 심의 중인 항목은 공개하지 않습니다.

향토문화 ID는 `DHC-부여연도-일련번호` 꼴이며, 항목마다 고정된 주소를 가집니다.
예: `DHC-2026-0001` → `https://daehyang.github.io/id/DHC-2026-0001`

한 번 부여한 ID는 **다시 쓰지 않습니다.** 등재를 폐기한 항목도 주소를 그대로 유지하고
폐기되었음을 표시합니다. 인용한 글의 링크가 뒤에 끊기지 않게 하기 위한 것입니다.

## 등재 항목

{% assign items = site.placenames | sort: "hid" %}
{% if items.size == 0 %}

확정 등재된 항목이 아직 없습니다. 첫 심의가 끝나면 이곳에 표시됩니다.

{% else %}

<table>
  <thead>
    <tr><th>향토문화 ID</th><th>지명</th><th>유형</th><th>소재지</th><th>상태</th></tr>
  </thead>
  <tbody>
  {% for item in items %}
    <tr>
      <td><a href="{{ item.url | relative_url }}"><code>{{ item.hid }}</code></a></td>
      <td>{{ item.label }}{% if item.hanja %} ({{ item.hanja }}){% endif %}</td>
      <td>{{ item.kind }}</td>
      <td>{{ item.locality }}</td>
      <td>{{ item.status }}</td>
    </tr>
  {% endfor %}
  </tbody>
</table>

<p><a href="{{ '/assets/data/placenames.csv' | relative_url }}">전체 목록 CSV로 내려받기</a></p>

{% endif %}

## 발간본 「대전향토문화목록」

등재부는 해마다 한 번 동결하여 「대전향토문화목록」으로 발간하고, Zenodo에 보존해 DOI를
부여합니다. 인용에는 발간본과 DOI를 쓰시는 것이 가장 안정적입니다.

{% assign editions = site.pages | where: "layout", "catalogue" | sort: "year" | reverse %}
{% if editions.size == 0 %}

첫 발간본을 준비하고 있습니다.

{% else %}

<ul class="entry-list">
{% for edition in editions %}
  <li>
    <time>{{ edition.year }}</time>
    <a href="{{ edition.url | relative_url }}">{{ edition.title }}</a>
  </li>
{% endfor %}
</ul>

{% endif %}

## 등재를 발의하려면

문헌이나 구술로 확인되는 대전의 향토문화 항목은 회원이 아니어도 발의할 수 있습니다.
근거 문헌을 갖추어 [GitHub 저장소](https://github.com/daehyang)의 이슈로 알려 주시거나,
회원을 통해 정기 회의 안건으로 올려 주십시오. 발의된 항목은 담당 분과의 심의와
정기 회의 의결을 거쳐 등재됩니다.
