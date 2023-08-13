#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime


def previous_work_day(_cur_day, _previous):
    cur_day = datetime.datetime.strptime(_cur_day, '%Y%m%d')
    while _previous > 0:
        cur_day += datetime.timedelta(days=-1)
        # 一二 三四五 六七
        # 0 1 2 3 4 5 6
        if cur_day.weekday() < 5:
            _previous -= 1
    return cur_day
