from math import ceil

from flask import request
from mongoengine import QuerySet

from config import MAX_PAGINATED_LIMIT
from utils.errors import PaginationPageInvalid, PaginationLimitInvalid


def default_mapping_fn(item, *args, **kwargs):
    return item.to_dict()


def get_page_count(no_items, limit) -> int:
    if no_items:
        return ceil(no_items / limit)
    else:
        return 0


def get_paginated_items_from_qs(qs: QuerySet, mapping_fn=default_mapping_fn, *args, **kwargs):
    page = request.args.get('page', default=0)
    limit = request.args.get('limit', default=MAX_PAGINATED_LIMIT)

    try:
        page = int(page)
    except ValueError:
        raise PaginationPageInvalid()

    try:
        limit = int(limit)
    except ValueError:
        raise PaginationLimitInvalid()

    limit = min(limit, MAX_PAGINATED_LIMIT)
    skip = page * limit

    qs = qs.skip(skip).limit(limit)

    no_total_items = qs.count()
    no_items = qs.count(with_limit_and_skip=True)
    no_items_before = max(skip, 0)
    no_items_after = max(no_total_items - skip - no_items, 0)

    return {
        'limit': limit,
        'skip': skip,
        'no_items': no_items,
        'no_total_items': no_total_items,
        'no_items_before': no_items_before,
        'no_items_after': no_items_after,
        'page': page,
        'no_pages': get_page_count(no_total_items, limit),
        'no_pages_before': get_page_count(no_items_before, limit),
        'no_pages_after': get_page_count(no_items_after, limit),
        'items': [mapping_fn(item, *args, **kwargs) for item in qs],
    }
