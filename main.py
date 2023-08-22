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


def find_hs_k_data():
    date_str = ''
    all_turnover = 0.0
    end_time = datetime.datetime.now().strftime('%Y%m%d')
    beg_time = previous_work_day(end_time, 200).strftime('%Y%m%d')

    h_df = common.get_quote_history_single(code='上证指数', beg=beg_time, end=end_time)
    if not h_df.empty:
        h_last_one = h_df.iloc[-1]
        date_str = h_last_one['date']
        all_turnover = h_last_one['turnover']
        draw_k_img.draw_k_img(_df=h_df, _save_path=IMG_PATH + h_last_one['code'] + '.png', _render_len=125)

    s_df = common.get_quote_history_single(code='399001', beg=beg_time, end=end_time)
    if not s_df.empty:
        s_last_one = s_df.iloc[-1]
        date_str = s_last_one['date']
        all_turnover = all_turnover + s_last_one['turnover']
        draw_k_img.draw_k_img(_df=s_df, _save_path=IMG_PATH + s_last_one['code'] + '.png', _render_len=125)

    print('draw hs k line img done.')
    return [date_str, num.science_num(all_turnover, 2)]


def merge_and_notify(_start_time, _hs_turnover, _matched_etf):
    turnover_msg = ''
    etf_msg = ''

    if not _hs_turnover:
        turnover_msg = ''.join([_hs_turnover[0], ' 沪深成交额: ', _hs_turnover[1]])
        update_file.update_hs_turnover("README.md", turnover_msg)

    if not _matched_etf:
        etf_msg = ''.join([' '.join([str(etf_dict['code']), str(etf_dict['name']), str(etf_dict['cur_rsi']), '\n'])
                           for etf_dict in _matched_etf])

    notify.send(' '.join([_start_time[:-6], 'etf统计']), ''.join([turnover_msg, '\n\n', etf_msg]))


IMG_PATH = 'static/'

if __name__ == '__main__':
    start_time_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    try:
        hs_turnover = find_hs_k_data()
    except Exception as e:
        print('find_hs_k_data has error!', e)

    try:
        matched_etf = find_match_etf(start_time_str)
    except Exception as e:
        print('find_match_etf has error!', e)

    merge_and_notify(start_time_str, hs_turnover, matched_etf)
