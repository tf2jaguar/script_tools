#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import multiprocessing as mp
import os
import sys

import efinance as ef
import numpy as np

sys.path.append(os.path.dirname(__file__) + os.path.sep + '..')

from util import notify, draw_img


class Rsi:
    """
     LC := REF(CLOSE,1);   // 前一天收盘价
     RSI$1:SMA(MAX(CLOSE-LC,0),N1,1)/SMA(ABS(CLOSE-LC),N1,1)*100; // N1周期的rsi
    """

    @staticmethod
    def get_sma(c, n, m):
        """
        sma函数；c/列表，n/周期，m/权重，返回sma列表
        :param c: 列表
        :param n: 周期
        :param m: 权重
        :return: sma列表
        """
        c_re = []
        m_n = m / n
        m_n2 = 1 - m_n
        sma_temp = c[0]
        c_re.append(sma_temp)
        for i in range(1, len(c)):
            sma_temp = c[i] * m_n + sma_temp * m_n2
            c_re.append(sma_temp)
        return c_re

    @staticmethod
    def smooth_rsi(t, n, is0=False):
        """
        平滑rsi函数；输入一个列表和周期，返回rsi列表
        :param t: 列表
        :param n: 周期
        :param is0: is0为True的时候，将首个值赋0，序列少的时候使用
        :return: rsi列表
        """
        close = list(t)[1:]
        lc = list(t)[:-1]
        close_lc = np.array(close) - np.array(lc)
        if not is0:
            close_lc1 = np.maximum(close_lc, 0)  # MAX(CLOSE-LC,0)
            close_lc2 = abs(close_lc)  # ABS(CLOSE-LC)
        else:
            close_lc1 = [0] + list(np.maximum(close_lc, 0))  # MAX(CLOSE-LC,0)
            close_lc2 = [0] + list(abs(close_lc))  # ABS(CLOSE-LC)
        close_lc_s = Rsi.get_sma(close_lc1, n, 1)  # SMA(MAX(CLOSE-LC,0),N1,1)
        close_lc2_s = Rsi.get_sma(close_lc2, n, 1)  # SMA(ABS(CLOSE-LC),N1,1)
        # 考虑了分母是0，分子和分母都是0的情况
        divisor = np.array(close_lc_s) * 100
        dividend = np.array(close_lc2_s)
        t_rsi = [round(e_temp, 2) if e_temp != np.inf and not np.isnan(e_temp) else 0
                 for e_temp in np.divide(divisor, dividend, out=np.zeros_like(divisor), where=dividend != 0)]
        return t_rsi


def stock_rsi(_code):
    _rsi = [0, 0]

    end_time = datetime.datetime.now().strftime('%Y%m%d')
    beg_time = previous_work_day(end_time, 600).strftime('%Y%m%d')
    day_k_df = ef.stock.get_quote_history(stock_codes=_code, beg=beg_time, end=end_time)
    # 收盘
    day_close_k = day_k_df.iloc[:, 4]
    try:
        if len(day_close_k) < 2:
            return _rsi
        elif len(day_close_k) > 255:
            _rsi = Rsi.smooth_rsi(day_close_k, 28)
        else:
            _rsi = Rsi.smooth_rsi(day_close_k, 28, True)
    except Exception as e:
        print("exception", _code)
        pass
        return _rsi
    return _rsi


def below_rsi(etf_dict, max_rsi):
    _rsi = stock_rsi(etf_dict['code'])
    print(etf_dict['code'], etf_dict['name'], _rsi[-2:])

    if 0 < _rsi[-1] <= max_rsi:
        etf_dict['cur_rsi'] = _rsi[-1]
        return etf_dict
    return None


def multi_process_match_rsi(_funds_df, _rsi):
    start_t = datetime.datetime.now()
    _num_cores = int(mp.cpu_count())
    print("use {} cpu calculate etf's rsi below {}".format(_num_cores, _rsi))

    pool = mp.Pool(_num_cores)
    results = [pool.apply_async(below_rsi, args=({'code': row.values[0], 'name': row.values[1]}, _rsi))
               for index, row in _funds_df.iterrows()]
    results = [p.get() for p in results]

    end_t = datetime.datetime.now()
    elapsed_sec = (end_t - start_t).total_seconds()
    print("multi-process calculation cost: {}s".format("{:.2f}".format(elapsed_sec)))
    return list(filter(None, results)), elapsed_sec


def find_match_etf(_below_rsi=31, _record_cost_time=True, _send_notify=True):
    start_time_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

    all_funds = ef.fund.get_fund_codes('etf')
    match_etf_list, cost_time = multi_process_match_rsi(all_funds, _below_rsi)
    if not match_etf_list:
        match_etf_list.append({'code': 0, 'name': '暂无匹配结果', 'cur_rsi': 0})

    if _record_cost_time:
        with open(ETF_RSI_COST_TIME_LOG, 'a+') as f:
            f.writelines(','.join([start_time_str, str(cost_time), '\n']))

    if _send_notify:
        msg = ''.join([' '.join([str(etf_dict['code']), str(etf_dict['name']), str(etf_dict['cur_rsi']), '\n'])
                       for etf_dict in match_etf_list])
        notify.send(start_time_str[:-6] + ' etf统计', msg)
    return match_etf_list


def previous_work_day(_cur_day, _previous):
    cur_day = datetime.datetime.strptime(_cur_day, '%Y%m%d')
    while _previous > 0:
        cur_day += datetime.timedelta(days=-1)
        # 一二 三四五 六七
        # 0 1 2 3 4 5 6
        if cur_day.weekday() < 5:
            _previous -= 1
    return cur_day


def draw_etf_rsi_task_img():
    record_lines = draw_img.get_record_data(ETF_RSI_COST_TIME_LOG)
    draw_img.draw_img(record_lines, ETF_RSI_COST_TIME_IMG)
    print('draw etf rsi task img done.')


if __name__ == '__main__':
    ETF_RSI_COST_TIME_LOG = 'etf_rsi_cost_time.txt'
    ETF_RSI_COST_TIME_IMG = 'etf_rsi_cost_time.png'
    find_match_etf()
    draw_etf_rsi_task_img()
