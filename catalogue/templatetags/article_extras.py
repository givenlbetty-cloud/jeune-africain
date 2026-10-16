from django import template

from catalogue.article_content import render_article_content

register = template.Library()


@register.filter(name="article_html")
def article_html(content):
    return render_article_content(content)
