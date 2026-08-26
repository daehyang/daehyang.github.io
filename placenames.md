---
title: 대전의 지명과 문화유산 목록
permalink: /placenames/
description: 대전향토문화연구회가 문헌과 현지 조사로 확인하고 심의를 거쳐 확정한 대전의 지명·문화유산 목록.
---

대전향토문화연구회가 조사하고 심의를 거쳐 확정한 목록입니다.
고개와 나루, 옛 장터와 마을처럼 이 고장에 이름이 붙은 곳들을 문헌과 현지 조사로
확인해 하나씩 올립니다. 아직 심의 중인 항목은 올리지 않습니다.

항목마다 고유 번호와 그 번호로 열리는 고정 주소를 붙입니다.
이 번호를 **향토문화 ID**라 하며, `DHC-부여연도-일련번호` 꼴입니다.

> `DHC-2026-0001` → `https://daehyang.github.io/id/DHC-2026-0001`

번호는 한 번 붙이면 **다시 쓰지 않습니다.** 나중에 목록에서 내린 항목도 주소를
그대로 남기고 내렸다는 사실을 그 자리에 표시합니다. 이 목록을 인용한 글의 링크가
뒤에 끊기지 않게 하기 위한 것입니다.

## 목록

{% assign listed = site.placenames | where: "status", "확정" | sort: "hid" %}
{% assign retired = site.placenames | where: "status", "폐기" | sort: "hid" %}
{% if listed.size == 0 %}

아직 확정된 항목이 없습니다. 첫 심의가 끝나면 이곳에 실립니다.

{% else %}

<table>
  <thead>
    <tr><th>번호</th><th>이름</th><th>유형</th><th>소재지</th><th>발의</th></tr>
  </thead>
  <tbody>
  {% for item in listed %}
    <tr>
      <td><a href="{{ item.url | relative_url }}"><code>{{ item.hid }}</code></a></td>
      <td>{{ item.label }}{% if item.hanja %} ({{ item.hanja }}){% endif %}</td>
      <td>{{ item.kind }}</td>
      <td>{{ item.locality }}</td>
      <td>{{ item.credit }}</td>
    </tr>
  {% endfor %}
  </tbody>
</table>

{% endif %}

<p><a href="{{ '/assets/data/placenames.csv' | relative_url }}">목록 전체를 CSV 파일로 내려받기</a>
(내린 항목도 상태와 함께 들어 있습니다)</p>

{% if retired.size > 0 %}

### 목록에서 해제된 항목

<table>
  <thead>
    <tr><th>번호</th><th>이름</th><th>내린 사유</th></tr>
  </thead>
  <tbody>
  {% for item in retired %}
    <tr>
      <td><a href="{{ item.url | relative_url }}"><code>{{ item.hid }}</code></a></td>
      <td>{{ item.label }}{% if item.hanja %} ({{ item.hanja }}){% endif %}</td>
      <td>{{ item.retired_reason }}</td>
    </tr>
  {% endfor %}
  </tbody>
</table>
향토문화 ID는 내린 뒤에도 다시 쓰지 않습니다. 번호가 비어 있는 자리를 밝히기 위해
아래에 함께 싣습니다. 각 항목의 주소는 그대로 열립니다.

{% endif %}

## 인쇄물로 펴내는 목록

이 웹 목록은 늘 최신 상태입니다. 인쇄물은 두 가지로 나누어 펴냅니다.

- **해마다** — 그 해 새로 확정된 분량을 회지 [「대전향토연구」](/journal/)의
  **부록**으로 발표합니다. 인용하실 때는 그 회지 호를 밝히시면 됩니다.
- **몇 해마다** — 그동안 쌓인 목록 전체를 **단행본** 「대전향토문화목록」으로
  묶어 펴내고, Zenodo에 보존해 DOI를 받습니다.

글에 인용하실 때는 이 인쇄물을 쓰시는 편이 가장 안정적입니다. 발간 시점 그대로
동결된 판이라 내용이 나중에 바뀌지 않기 때문입니다.

{% assign editions = site.pages | where: "layout", "catalogue" | sort: "year" | reverse %}
{% if editions.size == 0 %}

첫 단행본을 준비하고 있습니다. 그동안은 회지 부록과 이 웹 목록을 보아 주십시오.

{% else %}

### 단행본


<ul class="entry-list">
{% for edition in editions %}
  <li>
    <time>{{ edition.year }}</time>
    <a href="{{ edition.url | relative_url }}">{{ edition.title }}</a>
  </li>
{% endfor %}
</ul>

{% endif %}

## 알려주실 곳이 있다면

문헌이나 어르신들의 말씀으로 확인되는 대전의 지명·문화유산은 회원이 아니어도
알려주실 수 있습니다. 근거가 되는 문헌이나 들으신 내용을 함께
[GitHub 저장소](https://github.com/daehyang)의 이슈로 남겨 주시거나,
회원을 통해 정기 회의 안건으로 올려 주십시오.
알려주신 곳은 담당 분과의 조사와 정기 회의 의결을 거쳐 이 목록에 오릅니다.
