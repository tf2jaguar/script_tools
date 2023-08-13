#!/usr/bin/python
# -*- coding: utf-8 -*-
def science_num(num_val, r):
    def str_of_size(_num, _level):
        if _level >= 2:
            return _num, _level
        elif _num >= 10000:
            _num /= 10000
            _level += 1
            return str_of_size(_num, _level)
        else:
            return _num, _level

    units = ['', ' 万', ' 亿']
    num, level = str_of_size(num_val, 0)
    if level > len(units):
        level -= 1
    return '{}{}'.format(round(num, r), units[level])
