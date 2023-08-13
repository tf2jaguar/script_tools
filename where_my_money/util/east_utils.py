#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
import json
import re
import time
from collections import namedtuple
from functools import wraps
from typing import Union, List, TypeVar

import pandas as pd

from ..config import SEARCH_RESULT_CACHE_PATH
from ..shared import (SEARCH_RESULT_DICT, session)

QUOTE_ID_MODE = 'quote_id_mode'
Quote = namedtuple('Quote', ['code', 'name', 'pinyin', 'id', 'jys', 'classify', 'market_type', 'security_typeName',
                             'security_type', 'mkt_num', 'type_us', 'quote_id', 'unified_code', 'inner_code'])
F = TypeVar('F')


def to_numeric(func: F) -> F:
    ignore = ['code']

    @wraps(func)
    def run(*args, **kwargs):
        values = func(*args, **kwargs)
        if isinstance(values, pd.DataFrame):
            for column in values.columns:
                if column not in ignore:
                    values[column] = values[column].apply(convert)
        elif isinstance(values, pd.Series):
            for index in values.index:
                if index not in ignore:
                    values[index] = convert(values[index])
        return values

    def convert(o: Union[str, int, float]) -> Union[str, float, int]:
        if not re.findall('\d', str(o)):
            return o
        try:
            if str(o).isalnum():
                o = int(o)
            else:
                o = float(o)
        except:
            pass
        return o

    return run


def get_quote_id(stock_code: str) -> str:
    if len(str(stock_code).strip()) == 0:
        raise Exception('code should not be empty!')
    quote = search_quote(stock_code)
    if isinstance(quote, Quote):
        return quote.quote_id
    if quote is None:
        print(f'code "{stock_code}" may be error!')
        return ''


def search_quote(keyword: str, count: int = 1, use_local: bool = True) -> Union[Quote, None, List[Quote]]:
    if use_local and count == 1:
        quote = search_quote_locally(keyword)
        if quote:
            return quote
    url = 'https://searchapi.eastmoney.com/api/suggest/get'
    params = (
        ('input', f'{keyword}'),
        ('type', '14'),
        ('token', 'D43BF722C8E33BDC906FB84D85E326E8'),
        ('count', f'{count}'))
    json_response = session.get(url, params=params).json()
    items = json_response['QuotationCodeTable']['Data']
    if items is not None:
        quotes = [Quote(*item.values()) for item in items]
        save_search_result(keyword, quotes[:1])
        if count == 1:
            return quotes[0]
        return quotes
    return None


def search_quote_locally(keyword: str) -> Union[Quote, None]:
    q = SEARCH_RESULT_DICT.get(keyword)
    if q is None or not q.get('last_time'):
        return None
    last_time: float = q['last_time']
    max_ts = 3600 * 24 * 3
    now = time.time()
    if (now - last_time) > max_ts:
        return None
    _q = q.copy()
    del _q['last_time']
    quote = Quote(**_q)
    return quote


def save_search_result(keyword: str, quotes: List[Quote]):
    with open(SEARCH_RESULT_CACHE_PATH, 'w', encoding='utf-8') as f:
        for quote in quotes:
            now = time.time()
            d = dict(quote._asdict())
            d['last_time'] = now
            SEARCH_RESULT_DICT[keyword] = d
            break
        json.dump(SEARCH_RESULT_DICT.copy(), f)
