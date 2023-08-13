#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
import mplfinance as mpf
import numpy as np
import pandas as pd

from util import num

my_color = mpf.make_marketcolors(up='r', down='g', edge='inherit', wick='inherit', volume='inherit')
my_style = mpf.make_mpf_style(marketcolors=my_color, figcolor='(0.82, 0.83, 0.85)', gridcolor='(0.82, 0.83, 0.85)')


class FontStyle:
    @staticmethod
    def style(_name='WenQuanYi Micro Hei', _size='12', _color='black', _weight='bold', _va='bottom', _ha=None):
        # PingFang HK
        style = {'fontname': _name, 'size': _size, 'color': _color, 'weight': _weight, 'va': _va}
        if _ha:
            style['ha'] = _ha
        return style

    @staticmethod
    def normal_left():
        return FontStyle.style(_weight='normal', _ha='left')

    @staticmethod
    def normal_right():
        return FontStyle.style(_weight='normal', _ha='right')


def text_val(one_data, key, _science=False, _round=False, div=1, r=2):
    if key not in one_data:
        return '-'

    if _science:
        return num.science_num(one_data[key], r)
    elif _round:
        return np.round(one_data[key] / div, r)
    else:
        return one_data[key]


class InterCandle:
    def __init__(self, data, style, save_path='static/stock.png'):
        self.data = data
        self.style = style
        self.save_path = save_path

        self.fig = mpf.figure(style=style, figsize=(12, 8), facecolor=(0.82, 0.83, 0.85))
        fig = self.fig
        self.ax1 = fig.add_axes([0.08, 0.25, 0.88, 0.60])
        self.ax1.set_ylabel('price')
        self.ax2 = fig.add_axes([0.08, 0.15, 0.88, 0.10], sharex=self.ax1)
        self.ax2.set_ylabel('volume')

        self.t1 = fig.text(0.50, 0.94, ' - ', FontStyle.style(_size='16', _ha='center'))
        self.t2 = fig.text(0.12, 0.90, '开/收: ', FontStyle.normal_right())
        self.t3 = fig.text(0.14, 0.89, f'', FontStyle.style(_size='24', _color='red'))
        self.t4 = fig.text(0.14, 0.86, f'', FontStyle.style(_color='red'))
        self.t5 = fig.text(0.22, 0.86, f'', FontStyle.style(_color='red'))
        self.t6 = fig.text(0.12, 0.86, f'', FontStyle.normal_right())
        self.t7 = fig.text(0.43, 0.90, '高: ', FontStyle.normal_right())
        self.t8 = fig.text(0.43, 0.90, f'', FontStyle.style(_color='red'))
        self.t9 = fig.text(0.43, 0.86, '低: ', FontStyle.normal_right())
        self.t10 = fig.text(0.43, 0.86, f'', FontStyle.style(_color='green'))
        self.t11 = fig.text(0.60, 0.90, '成交量(手): ', FontStyle.normal_right())
        self.t12 = fig.text(0.60, 0.90, f'', FontStyle.normal_left())
        self.t13 = fig.text(0.60, 0.86, '成交额(元): ', FontStyle.normal_right())
        self.t14 = fig.text(0.60, 0.86, f'', FontStyle.normal_left())
        self.t15 = fig.text(0.74, 0.90, '涨停: ', FontStyle.normal_right())
        self.t16 = fig.text(0.74, 0.90, f'', FontStyle.style(_color='red'))
        self.t17 = fig.text(0.74, 0.86, '跌停: ', FontStyle.normal_right())
        self.t18 = fig.text(0.74, 0.86, f'', FontStyle.style(_color='green'))
        self.t19 = fig.text(0.86, 0.90, '均价: ', FontStyle.normal_right())
        self.t20 = fig.text(0.86, 0.90, f'', FontStyle.normal_left())
        self.t21 = fig.text(0.86, 0.86, '昨收: ', FontStyle.normal_right())
        self.t22 = fig.text(0.86, 0.86, f'', FontStyle.normal_left())

    def refresh_texts(self, last_two_data):
        last_data = last_two_data.iloc[-1]
        penultimate_data = last_two_data.iloc[-2]

        self.t1.set_text(f'{text_val(last_data, "code")} - {text_val(last_data, "name")}')
        self.t3.set_text(f'{text_val(last_data, "open", _round=True)} / {text_val(last_data, "close", _round=True)}')
        self.t4.set_text(f'{text_val(last_data, "chg", _round=True)}')
        self.t5.set_text(f'[{text_val(last_data, "chg_ptc", _round=True)}%]')
        self.t6.set_text(f'{last_data.name.date()}')
        self.t8.set_text(f'{text_val(last_data, "high", _round=True)}')
        self.t10.set_text(f'{text_val(last_data, "low", _round=True)}')
        self.t12.set_text(f'{text_val(last_data, "volume", _science=True, _round=True)}')
        self.t14.set_text(f'{text_val(last_data, "turnover", _science=True, _round=True)}')
        self.t16.set_text(f'{text_val(last_data, "upper_lim", _round=True)}')
        self.t18.set_text(f'{text_val(last_data, "lower_lim", _round=True)}')
        self.t20.set_text(f'{text_val(last_data, "average", _round=True)}')
        self.t22.set_text(f'{text_val(penultimate_data, "close", _round=True)}')

        if penultimate_data["close"] > last_data["open"]:
            self.t8.set_color('green')

        if last_data["chg"] > 0:
            close_number_color = 'red'
        elif last_data["chg"] < 0:
            close_number_color = 'green'
        else:
            close_number_color = 'black'
        self.t3.set_color(close_number_color)
        self.t4.set_color(close_number_color)
        self.t5.set_color(close_number_color)

    def refresh_plot(self, _start, _range):
        all_data = self.data
        plot_data = all_data.iloc[_start: _start + _range]

        mpf.plot(plot_data,
                 ax=self.ax1,
                 volume=self.ax2,
                 mav=(5, 10, 20),
                 type='candle',
                 style=self.style,
                 datetime_format='%Y-%m',
                 xrotation=0)

        # self.fig.show()
        self.fig.savefig(self.save_path)
        self.fig.clear()


def draw_k_img(_df, _save_path, _render_len=120):
    _df['date'] = pd.to_datetime(_df['date'])
    _df = _df.set_index('date')

    # At least two ele.
    candle = InterCandle(_df, my_style, save_path=_save_path)

    length = _render_len if len(_df) > _render_len else len(_df)
    start = 0 if len(_df) < length else len(_df) - length

    candle.refresh_texts(_df.iloc[start + length - 2:])
    candle.refresh_plot(start, length)
