# templatetags/pagination_tags.py
from django import template
register = template.Library()

@register.simple_tag
def get_pagination_pages(current_page, total_pages, delta=2):
    pages = [1]
    try:
        current_page = int(current_page)
        total_pages = int(total_pages)
    except ValueError:

        return pages

    if current_page - delta > 2:
        pages.append('...')

    start_page = max(current_page - delta, 2)
    end_page = min(current_page + delta, total_pages - 1) + 1
    pages.extend(range(start_page, end_page))

    if current_page + delta < total_pages - 1:
        pages.append('...')

    pages.append(total_pages)
    return pages
