#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
from datetime import datetime
from typing import List, Union

import pandas as pd
from jsonpath import jsonpath
from retry import retry

from .config import EASTMONEY_KLINE_FIELDS, EASTMONEY_REQUEST_HEADERS, EASTMONEY_QUOTE_FIELDS
from ..shared import session, rpc
from ..util import QUOTE_ID_MODE, get_quote_id, to_numeric


@to_numeric
@retry(tries=3, delay=1)
def get_quote_history_single(code: str,
                             beg: str = '19000101',
                             end: str = '20500101',
                             klt: int = 101,
                             fqt: int = 1,
                             **kwargs) -> pd.DataFrame:
    fields = list(EASTMONEY_KLINE_FIELDS.keys())
    columns = list(EASTMONEY_KLINE_FIELDS.values())
    fields2 = ",".join(fields)
    if kwargs.get(QUOTE_ID_MODE):
        quote_id = code
    else:
        quote_id = get_quote_id(code)
    params = (
        ('fields1', 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13'),
        ('fields2', fields2),
        ('beg', beg),
        ('end', end),
        ('rtntype', '6'),
        ('secid', quote_id),
        ('klt', f'{klt}'),
        ('fqt', f'{fqt}'),
    )

    json_response = session.get(rpc.API_STOCK_KLINE_GET, headers=EASTMONEY_REQUEST_HEADERS, params=params).json()
    klines: List[str] = jsonpath(json_response, '$..klines[:]')
    if not klines:
        columns.insert(0, 'code')
        columns.insert(0, 'name')
        return pd.DataFrame(columns=columns)

    rows = [kline.split(',') for kline in klines]
    name = json_response['data']['name']
    code = quote_id.split('.')[-1]
    df = pd.DataFrame(rows, columns=columns)
    df.insert(0, 'code', code)
    df.insert(0, 'name', name)

    return df


@to_numeric
def get_latest_quote(stock_codes: Union[str, List[str]],
                     **kwargs) -> pd.DataFrame:
    if isinstance(stock_codes, str):
        stock_codes = [stock_codes]

    quote_id_list = [get_quote_id(stock_code) for stock_code in stock_codes]
    secids: List[str] = quote_id_list

    columns = {**EASTMONEY_QUOTE_FIELDS, **kwargs.get('extra_fields', {})}
    fields = ",".join(columns.keys())
    params = (
        ('OSVersion', '14.3'),
        ('appVersion', '6.3.8'),
        ('fields', fields),
        ('fltt', '2'),
        ('plat', 'Iphone'),
        ('product', 'EFund'),
        ('secids', ",".join(secids)),
        ('serverVersion', '6.3.6'),
        ('version', '6.3.8'),
    )

    json_response = session.get(rpc.API_ULIST_GET, headers=EASTMONEY_REQUEST_HEADERS, params=params).json()
    rows = jsonpath(json_response, '$..diff[:]')
    if not rows:
        df = pd.DataFrame(columns=columns.values())
    else:
        df = pd.DataFrame(rows)[list(columns.keys())].rename(columns=columns)

    df['update_time'] = df['update_time'].apply(lambda x: str(datetime.fromtimestamp(x)))
    df['last_deal_day'] = pd.to_datetime(df['last_deal_day'], format='%Y%m%d').astype(str)
    return df
