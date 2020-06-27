---
layout: post
title: "{{submission.title}}"
author: "{{submission.author}}"
---

[Link to Reddit post](https://reddit.com{{submission.permalink}}})

---

{% for comment in comments %}

> ## <a name="{{loop.index}}"></a> Written By <a href="https://reddit.com{{comment.permalink}}" target="_blank">/u/{{comment.author}}</a> <a href="#{{loop.index}}" class="sub-header">({{loop.index}} / {{comments|length}})

{{comment.body}}  

<a href="https://reddit.com{{comment.permalink}}" target="_blank">{{comment.replies|length}} Replies</a>

---

{% endfor %}
