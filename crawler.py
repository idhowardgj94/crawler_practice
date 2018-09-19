# -*- coding: utf-8 -*-
#!/usr/bin/env python3
import sys
'''
goal
爬 ptt beauty 板
* 2017 一整年文章
* 統計日期內推文跟噓文的數量
* 找出日期內最會推跟最會噓的人各前10名
* 統計日期內爆文的數量
* 抓取日期內爆文的所有圖片URL
* 關鍵字查詢
https://www.ptt.cc/bbs/Beauty/index.html
'''

if __name__ == '__main__':
    # first one will be the program's file name
    print('Number of arguments:', len(sys.argv), 'arguments.')
    print('Argument List:', str(sys.argv))
