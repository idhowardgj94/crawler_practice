# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import requests
import datetime
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re
import codecs
import time


def get_response(url):
    response = requests.get(url)
    while not response.ok:
        response = requests.get(url)
    return response


class MemberCount(object):
    class CountInfo(object):
        def __init__(self, count):
            self.count = count
            self.name_list = []

        def insert_name(self, name):
            self.name_list.append(name)
            self.name_list.sort()

        def delete_name(self, name):
            self.name_list.remove(name)

        def get_count(self):
            return self.count

        def get_name_list(self):
            return self.name_list

    def __init__(self):
        # referience to count_table that contain the name
        self.name_table = {}
        # key is count,  value is name list
        self.count_table = {}
        self.max_count = 0

    def add_count_by_name(self, name):
        if name not in self.name_table.keys():
            if 1 not in self.count_table:
                self.count_table[1] = self.CountInfo(1)
            self.count_table[1].insert_name(name)
            self.name_table[name] = self.count_table[1]
        else:
            # delete from orignal CountInfo object
            # and get count+1
            cur_count_object = self.name_table[name]
            count = cur_count_object.get_count()
            cur_count_object.delete_name(name)

            count = count + 1
            # check this count is biggest or not
            if self.max_count < count:
                self.max_count = count
            # insert to  count_table(count+1)
            if count not in self.count_table:
                self.count_table[count] = self.CountInfo(count)
            self.count_table[count].insert_name(name)
            self.name_table[name] = self.count_table[count]

    def get_top_ten_list(self):
        ret_list = []
        number = 0
        cur_count = self.max_count
        while number < 10:
            name_list = self.count_table[cur_count].get_name_list()
            for name in name_list:
                if number < 10:
                    ret_list.append((number + 1, name, cur_count))
                    number = number + 1
                else:
                    return ret_list
            cur_count = cur_count - 1
        return ret_list


if __name__ == '__main__':
    start_date = 101
    end_date = 1231
    like_count = MemberCount()
    boo_count = MemberCount()
    all_like = 0
    all_boo = 0
    t1 = time.time()
    all_file = codecs.open("all_articles.txt", "r", "utf-8")

    print('search date between ' + str(start_date) + ' to ' + str(end_date))
    for line in all_file:
        line_list = [x for x in line.split(',')]
        url = line_list[len(line_list) - 1]
        date = int(line_list[0])

        # check date
        if end_date - start_date >= end_date - date and end_date - date >= 0:
            print("look indside web")
            print(date)
            print(url.strip())
            response = get_response(url.strip())
            soup = BeautifulSoup(response.text, 'lxml')
            exec_time = time.time()
            for push_soup in soup.find_all('div', 'push'):
                if push_soup.find('span', 'push-tag'):
                    push_category = push_soup.find(
                        'span', 'push-tag').string.strip()
                    push_name = push_soup.find(
                        'span', 'push-userid').string.strip()
                    if push_category == '推':
                        all_like = all_like + 1
                        like_count.add_count_by_name(push_name)
                    if push_category == '噓':
                        all_boo = all_boo + 1
                        boo_count.add_count_by_name(push_name)
            exec_finish_time = time.time()
            if exec_finish_time - exec_time < 0.5:
                print('sleep for a while ....')
                time.sleep(0.1)
        check_time = time.time()
        print("exec time now: %f" % ((check_time - t1) / 60))
    push_file = codecs.open("push[%d-%d].txt" %
                            (start_date, end_date), "w", "utf-8")
    push_file.write('all like: %d\n' % all_like)
    push_file.write('all boo: %d\n' % all_boo)
    like_top_ten_list = like_count.get_top_ten_list()
    boo_top_ten_list = boo_count.get_top_ten_list()
    for item in like_top_ten_list:
        push_file.write('like #%d: %s %d\n' % (item[0], item[1], item[2]))
    for item in boo_top_ten_list:
        push_file.write('boo #%d: %s %d\n' % (item[0], item[1], item[2]))
    push_file.close()
    t2 = time.time()
    total_time = (t2 - t1) / 60
    print("total time: %f" % total_time)
