#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import multiprocessing as mp

import numpy as np
from .workday import previous_work_day
from ..common import get_quote_history_single


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


def rsi_list(_code):
    _rsi = [0, 0]

    end_time = datetime.datetime.now().strftime('%Y%m%d')
    beg_time = previous_work_day(end_time, 600).strftime('%Y%m%d')
    try:
        day_k_df = get_quote_history_single(code=_code, beg=beg_time, end=end_time)
        day_close_k = day_k_df.iloc[:, 4]
        if len(day_close_k) < 2:
            return _rsi
        elif len(day_close_k) > 255:
            _rsi = Rsi.smooth_rsi(day_close_k, 28)
        else:
            _rsi = Rsi.smooth_rsi(day_close_k, 28, True)
    except Exception as e:
        print("exception", _code, e)
        pass
        return _rsi
    return _rsi


def below_rsi(_dict, max_rsi):
    _rsi = rsi_list(_dict['code'])
    print(_dict['code'], _dict['name'], _rsi[-2:])

    if 0 < _rsi[-1] <= max_rsi:
        _dict['cur_rsi'] = _rsi[-1]
        return _dict
    return None


def multi_process_match_rsi(_list_df, _rsi):
    start_t = datetime.datetime.now()
    _num_cores = int(mp.cpu_count())
    print("use {} cpu calculate codes rsi below {}".format(_num_cores, _rsi))

    pool = mp.Pool(_num_cores)
    results = [pool.apply_async(below_rsi, args=({'code': row.values[0], 'name': row.values[1]}, _rsi))
               for index, row in _list_df.iterrows()]
    results = [p.get() for p in results]

    end_t = datetime.datetime.now()
    elapsed_sec = (end_t - start_t).total_seconds()
    print("multi-process calculation cost: {}s".format("{:.2f}".format(elapsed_sec)))
    return list(filter(None, results)), elapsed_sec
