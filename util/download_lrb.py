import datetime
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import pandas as pd

from where_my_money.stock import f10

CODE_MARKET_PATH = '../data/tdx_stocks.csv'
LR_DRI_PATH = '../data/lr'

REPORT_DATE_DICT = {'03-31': 1, '06-30': 2, '09-30': 3, '12-31': 4}


def split_df(df, n):
    """将DataFrame均分为n份并返回一个list"""
    split_indices = np.array_split(range(len(df)), n)
    return [df.iloc[indices] for indices in split_indices]


def mutil_run():
    df = pd.read_csv(CODE_MARKET_PATH, dtype={'股票代码': str})

    if not os.path.exists(LR_DRI_PATH):
        os.makedirs(LR_DRI_PATH)

    chunks = split_df(df, 12)
    executor = ThreadPoolExecutor(max_workers=12)
    all_task = [executor.submit(sync_run, c) for c in chunks]

    for task in as_completed(all_task):
        data = task.result()
        print("任务{} down load success".format(data))


def sync_run(obj):
    res = list()
    for index, row in obj.iterrows():
        stock_code = row['交易所简码'] + row['股票代码']
        one_res = after_last_record_to_write(stock_code=stock_code)
        current_thread = threading.current_thread()
        res.append(one_res)
        print(f"{current_thread.name} - {stock_code}-{one_res}")
    return res


def after_last_record_to_write(stock_code: str):
    filename = f'{LR_DRI_PATH}/{stock_code}.csv'
    last_one_report_date = '1996-01-01'
    if os.path.exists(filename):
        last_n = read_last_n_lines(filename, 1)
        last_one = str(last_n[0]).split(',')
        last_one_report_date = last_one[5].split(' ')[0]

    dates = get_last_days_of_need_query(last_one_day=last_one_report_date, n_year=20)
    try:
        data = f10.lrb(code=stock_code, dates=dates)
    except Exception:
        return "exception"

    # 将data字段转换为DataFrame并保存为CSV文件，如果文件存在则追加
    try:
        res_df = pd.DataFrame(data['data']).sort_values(by='REPORT_DATE')
        res_df.to_csv(filename, index=False, mode='a', header=not os.path.exists(filename))
        return "success"
    except KeyError:
        return "not_exist"


def get_last_days_of_need_query(last_one_day: str, n_year: int) -> str:
    last_one_date = datetime.datetime.strptime(last_one_day, "%Y-%m-%d")
    last_one_list = last_one_day.split('-')
    last_year = int(last_one_list[0])

    today = datetime.datetime.now()
    today_list = today.strftime("%Y-%m-%d").split('-')
    today_year = int(today_list[0])

    need_list = list()
    for y in range(n_year):
        if last_year <= today_year:
            for k in REPORT_DATE_DICT.keys():
                report_date = datetime.datetime.strptime(str(today_year) + '-' + k, "%Y-%m-%d")
                if today > report_date > last_one_date:
                    need_list.append(report_date.strftime("%Y-%m-%d"))
        today_year -= 1
    return ','.join(sorted(need_list))


def read_last_n_lines(filepath: str, n: int, block=-1024):
    with open(filepath, 'rb') as f:
        f.seek(0, 2)
        filesize = f.tell()
        while True:
            if filesize >= abs(block):
                f.seek(block, 2)
                s = f.readlines()
                if len(s) > n:
                    return s[-n:]
                    break
                else:
                    block *= 2
            else:
                block = -filesize
    return None


if __name__ == '__main__':
    # run one
    codes = "SZ001888"
    for code in codes.split(','):
        print(after_last_record_to_write(stock_code=code))

    # run all
    # mutil_run()
