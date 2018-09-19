# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import requests
import datetime
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re
import codecs
import time

# END IN this post
END_POST = '[正妹] 新年 第889彈'


def check_date_from_page(cur_article):
    """

    """
    def check_date(soup):
        """
        input beautifuy object, check date
        must find last
        """
        # get date
        date_string = soup.find('div', 'date').string.strip()
        date = datetime.datetime.strptime(date_string, "%m/%d")
        if date.month != 12 or date.day != 31:
            return False
        else:
            return True

    cur_article = cur_article.find('div', 'r-ent')
    while cur_article is not None:
        if not check_date(cur_article):
            # next
            cur_article = cur_article.find_next('div', 'r-ent')
        else:
            # find last match
            while cur_article is not None:
                prev_article = cur_article
                cur_article = cur_article.find_next('div', 'r-ent')
                # got 1/1
                if not check_date(cur_article):
                    return prev_article
            return prev_article
    return False


def get_website(url):
    """
    get the website from url
    """
    site = urlparse(url)
    site_netloc = site.scheme + '://' + site.netloc
    return site_netloc


def get_response(url):
    response = requests.get(url)
    while not response.ok:
        response = requests.get(url)
    return response


def get_prev_page_url(root_soup):
    return website + root_soup.find('div', id='action-bar-container').find('div', 'btn-group-paging').find_all('a')[1]['href']

####### second part of function #########


def get_date(soup):
    date_string = soup.find('div', 'date').string.strip()
    return date_string


def get_title(cur_soup):
    if cur_soup.find('div', 'title').find('a'):
        title = ''
        for string in cur_soup.find('div', 'title').a.strings:
            # if @ occur, need specical parse
            if string == '[email protected]':
                title = title + '@' + string['data-cfemail']
            else:
                title = title + string
        return title
    else:
        return False


def write_info(all_file, pop_file, soup):
    """soup is on <div r-ent>"""
    def check_title_string(title):
        """title is a string, true mean this is what we need"""
        match = re.search(r'\[公告\]', title)
        if not match:
            return True
        else:
            return False

    # check if title.a exist
    if not soup.find('div', 'title').find('a'):
        return False
    # check title contain [公告] or not
    title = get_title(soup)
    if check_title_string(title):
        # grab date, topic, url
        date_temp = soup.find('div', 'date').string.strip()
        # remove /
        date = re.sub(r'[/]', '', date_temp)
        # title
        url = website + soup.find('div', 'title').find('a')['href']
        # merge to one line
        write_line = ','.join([date, title, url])
        # if 爆, write to pop_file
        thumb_number = soup.find('div', 'nrec')
        if thumb_number.find('span'):
            thumb_number = thumb_number.span.string.strip()
        else:
            tuhmb_number = ''
        if thumb_number == '爆':
            pop_file.write(write_line + '\n')
        all_file.write(write_line + '\n')
        # write to all_file


if __name__ == '__main__':

    t0 = time.time()
    # find the 12/31 article
    url = "https://www.ptt.cc/bbs/Beauty/index.html"
    # get ptt's website
    website = get_website(url)
    # first flag
    first_flag = True
    ############### loading ####################
    response = get_response(url)
    root_soup = BeautifulSoup(response.text, 'lxml')
    ############### end loading ################
    find_soup = check_date_from_page(root_soup)

    while not find_soup:
        # find next page
        print('page: ' + url + ' not find!')
        print('get next page...')
        # prev page's url
        url = get_prev_page_url(root_soup)

        # if this is prist page, than direct minus 300 ...
        if first_flag == True:
            print("first page, direct jump ...")
            # got the number part
            match = re.search(r'(\d+)(?:.html$)', url)
            number = match[1]
            number = int(number) - 300
            # replace back
            url = re.sub(r"(\d+)(.html$)", str(number) + r'\2', url)
            print('jump to: ', url)
            first_flag = False

        # loading
        response = get_response(url)
        root_soup = BeautifulSoup(response.text, 'lxml')
        find_soup = check_date_from_page(root_soup)

    print('find!')

    # record time
    t1 = time.time()
    time_file = codecs.open("exec_time.txt", "a", "utf-8")
    time_file.write(
        'total time for get the proper 2017 last post: ' + str(t1 - t0) + '\n')
    time_file.close()
    ## second part of code##
    t2 = time.time()
    # start soup
    # root_soup is current soup on root
    start_soup = find_soup
    # open file
    all_file = codecs.open("all_articles.txt", "w", "utf-8")
    pop_file = codecs.open("all_popular.txt", "w", "utf-8")

    # first page is special case
    write_info(all_file, pop_file, start_soup)
    for cur_soup in start_soup.find_all_previous('div', 'r-ent'):
        if get_title(cur_soup):
            print('write file for "' + get_title(cur_soup) + '"')
        write_info(all_file, pop_file, cur_soup)

    # second page start
    is_continued = True
    while is_continued:
        # to next page
        url = get_prev_page_url(root_soup)
        response = get_response(url)
        root_soup = BeautifulSoup(response.text, 'lxml')

        # loop root_soup
        for cur_soup in reversed(root_soup.find_all('div', 'r-ent')):
            title = get_title(cur_soup)
            if title:
                date = get_date(cur_soup)
                print('write file for "' + date + " " + title + '"')
            write_info(all_file, pop_file, cur_soup)
            # ending point

            if title == END_POST:
                is_continued = False
                break
        is_continued == False
    all_file.close()
    pop_file.close()

    # record time
    t3 = time.time()
    time_file = codecs.open("exec_time.txt", "a", "utf-8")
    time_file.write('total time for crawl all 2017 post: ' +
                    str(t3 - t2) + '\n')
    time_file.write('total exec time: ' + str(t3 - t0) + '\n')

    time_file.close()
