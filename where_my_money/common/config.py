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
    'f61': 'turnover_rate'
}

# STOCK、ETF head
EASTMONEY_QUOTE_FIELDS = {
    'f12': 'code',
    'f14': 'name',
    'f3': 'chg_ptc',
    'f2': 'price',
    'f15': 'high',
    'f16': 'low',
    'f17': 'open',
    'f18': 'close',
    'f4': 'chg',
    'f8': 'turnover_rate',
    'f10': 'volume_ratio',
    'f9': 'dynamic_earnings_ratio',
    'f5': 'volume',
    'f6': 'turnover',
    'f20': 'total_market_value',
    'f21': 'circulating_market_value',
    'f13': 'market_code',
    'f124': 'update_time',
    'f297': 'last_deal_day',
}

EN_ZH = {
    'code': '代码',
    'name': '名称',
    'date': '日期',
    'price': '最新价',
    'open': '开盘',
    'close': '收盘',
    'high': '最高',
    'low': '最低',
    'volume': '成交量',
    'turnover': '成交额',
    'amplitude': '振幅',
    'chg_ptc': '涨跌幅',
    'chg': '涨跌额',
    'turnover_rate': '换手率',
    'volume_ratio': '量比',
    'dynamic_earnings_ratio': '动态市盈率',
    'yesterday_close': '昨日收盘',
    'total_market_value': '总市值',
    'circulating_market_value': '流通市值',
    'market_code': '市场编号',
    'update_time': '更新时间',
    'last_deal_day': '最新交易日',
}

EASTMONEY_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; Touch; rv:11.0) like Gecko',
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
}