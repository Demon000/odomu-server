from math import ceil

from flask import request
from mongoengine import QuerySet

from config import MAX_PAGINATED_LIMIT
from utils.errors import PaginationPageInvalid, PaginationLimitInvalid


def default_mapping_fn(item, *args, **kwargs):
    return item.to_dict()


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
    if no_total_items:
        no_pages = ceil(no_total_items / limit)
    else:
        no_pages = 0

    return {
        'limit': limit,
        'skip': skip,
        'page': page,
        'no_items': no_items,
        'no_total_items': no_total_items,
        'no_pages': no_pages,
        'items': [mapping_fn(item, *args, **kwargs) for item in qs],
    }
