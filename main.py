#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
import datetime

from util import draw_img, draw_k_img, num, notify, update_file
from where_my_money import common
from where_my_money.fund import get_fund_codes
from where_my_money.util.rsi import multi_process_match_rsi
from where_my_money.util.workday import previous_work_day


def find_match_etf(_start_time, _below_rsi=31, _record_cost_time=True):
    all_funds = get_fund_codes('etf')
    match_etf_list, cost_time = multi_process_match_rsi(all_funds, _below_rsi)
    if not match_etf_list:
        match_etf_list.append({'code': 0, 'name': '暂无匹配结果', 'cur_rsi': 0})

    log_file = IMG_PATH + 'etf_rsi_cost_time.txt'
    png_file = IMG_PATH + 'etf_rsi_cost_time.png'
    if _record_cost_time:
        with open(log_file, 'a+') as f:
            f.writelines(','.join([_start_time, str(cost_time), '\n']))

    record_lines = draw_img.get_record_data(log_file)
    draw_img.draw_img(record_lines, png_file)

    print('draw etf rsi task img done.')
    return match_etf_list


def find_hs_turnover():
    df = common.get_latest_quote(['上证指数', '深证成指'])
    all_turnover = df['turnover'].sum()
    return [df.iloc[-1]['update_time'], num.science_num(all_turnover, 2)]


def draw_hs_k_data():
    end_time = datetime.datetime.now().strftime('%Y%m%d')
    beg_time = previous_work_day(end_time, 200).strftime('%Y%m%d')

    h_df = common.get_quote_history_single(code='上证指数', beg=beg_time, end=end_time)
    if not h_df.empty:
        h_last_one = h_df.iloc[-1]
        draw_k_img.draw_k_img(_df=h_df, _save_path=IMG_PATH + h_last_one['code'] + '.png', _render_len=125)
        print('draw h k line img done.')

    s_df = common.get_quote_history_single(code='399001', beg=beg_time, end=end_time)
    if not s_df.empty:
        s_last_one = s_df.iloc[-1]
        draw_k_img.draw_k_img(_df=s_df, _save_path=IMG_PATH + s_last_one['code'] + '.png', _render_len=125)
        print('draw s k line img done.')


def merge_and_notify(_start_time, _hs_turnover, _matched_etf):
    turnover_msg = ''
    etf_msg = ''

    if _hs_turnover is not None:
        turnover_msg = ''.join([_hs_turnover[0], ' 沪深成交额: ', _hs_turnover[1]])
        update_file.update_hs_turnover("README.md", turnover_msg)

    if _matched_etf is not None:
        etf_msg = ''.join([' '.join([str(etf_dict['code']), str(etf_dict['name']), str(etf_dict['cur_rsi']), '\n'])
                           for etf_dict in _matched_etf])

    notify.send(' '.join([_start_time[:-6], 'etf统计']), ''.join([turnover_msg, '\n\n', etf_msg]))


IMG_PATH = 'static/'

if __name__ == '__main__':
    hs_turnover = None
    matched_etf = None

    start_time_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    try:
        draw_hs_k_data()
    except Exception as e:
        print('draw_hs_k_data has error!', e)

    try:
        hs_turnover = find_hs_turnover()
    except Exception as e:
        print('find_hs_turnover has error!', e)

    try:
        matched_etf = find_match_etf(start_time_str)
    except Exception as e:
        print('find_match_etf has error!', e)

    merge_and_notify(start_time_str, hs_turnover, matched_etf)
