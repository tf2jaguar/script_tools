# STOCK、ETF、FUND K line's head
EASTMONEY_KLINE_FIELDS = {
    'f51': 'date',
    'f52': 'open',
    'f53': 'close',
    'f54': 'high',
    'f55': 'low',
    'f56': 'volume',
    'f57': 'turnover',
    'f58': 'amplitude',
    'f59': 'chg_ptc',
    'f60': 'chg',
    'f61': 'turn_rate'
}

EASTMONEY_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; Touch; rv:11.0) like Gecko',
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
}