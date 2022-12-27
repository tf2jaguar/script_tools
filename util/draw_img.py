#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker


def file_get_last_lines(file_path, num) -> []:
    """
    读取大文件的最后几行
    :param file_path: 文件路径
    :param num: 读取行数
    :return:
    """
    num = int(num)
    blk_size_max = 4096
    n_lines = []
    with open(file_path, 'rb') as fp:
        fp.seek(0, os.SEEK_END)
        cur_pos = fp.tell()
        while cur_pos > 0 and len(n_lines) < num:
            blk_size = min(blk_size_max, cur_pos)
            fp.seek(cur_pos - blk_size, os.SEEK_SET)
            blk_data = fp.read(blk_size)
            assert len(blk_data) == blk_size
            lines = blk_data.split(b'\n')

            # adjust cur_pos
            if len(lines) > 1 and len(lines[0]) > 0:
                n_lines[0:0] = lines[1:]
                cur_pos -= (blk_size - len(lines[0]))
            else:
                n_lines[0:0] = lines
                cur_pos -= blk_size

            fp.seek(cur_pos, os.SEEK_SET)

    if len(n_lines) > 0 and len(n_lines[-1]) == 0:
        del n_lines[-1]

    return n_lines[-num:]


def get_record_data(_path, _lines=60) -> []:
    lines = file_get_last_lines(_path, _lines)
    record_list = []
    for line in lines:
        record_list.append(line.decode('utf-8').split(','))
    return record_list


def draw_img(_list, _save_path) -> None:
    x = []
    y = []

    for d in _list:
        x.append(str(d[0])[5:10])
        y.append(float(d[1]))

    plt.gca().yaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f s'))
    plt.bar(x, y, width=0.5)
    plt.savefig(_save_path)
