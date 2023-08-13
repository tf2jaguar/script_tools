#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
import re

import pandas as pd
import requests
from retry import retry

from .config import FUND_REQUEST_HEADERS
from ..config import rpc


@retry(tries=3, delay=1)
def get_fund_codes(ft: str = None) -> pd.DataFrame:
    params = [
        ('op', 'dy'),
        ('dt', 'kf'),
        ('rs', ''),
        ('gs', '0'),
        ('sc', 'qjzf'),
        ('st', 'desc'),
        ('es', '0'),
        ('qdii', ''),
        ('pi', '1'),
        ('pn', '50000'),
        ('dx', '0')]

    if ft is not None:
        params.append(('ft', ft))

    url = rpc.FUND_CODE_LIST
    response = requests.get(url, headers=FUND_REQUEST_HEADERS, params=params)

    columns = ['code', 'name']
    results = re.findall('"(\d{6}),(.*?),', response.text)
    df = pd.DataFrame(results, columns=columns)
    return df
