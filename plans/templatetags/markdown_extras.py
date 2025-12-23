from django import template
from django.utils.safestring import mark_safe
import markdown as md
import bleach

register = template.Library()

ALLOWED_TAGS = [
    "p", "br", "hr",
    "h1", "h2", "h3", "h4", "h5", "h6",
    "strong", "em", "code", "pre",
    "ul", "ol", "li",
    "blockquote",
    "a",
    "table", "thead", "tbody", "tr", "th", "td",
]

ALLOWED_ATTRIBUTES = {
    "a": ["href", "title", "rel", "target"],
    "th": ["colspan", "rowspan"],
    "td": ["colspan", "rowspan"],
}

@register.filter
def render_markdown(value: str) -> str:
    # 1) markdown -> HTML
    html = md.markdown(value or "", extensions=["fenced_code", "tables"])

    # 2) sanitize HTML to prevent XSS
    cleaned = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True,
    )

    # 3) tell Django it's safe AFTER cleaning
    return mark_safe(cleaned)
