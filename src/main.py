import requests
import datetime
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re
import codecs
import time
import sys


def get_response(url):
    count = 0
    # 只連五次
    response = requests.get(url)
    while not response.ok and count < 5:
        response = requests.get(url)
    return response

# 第一題，沒參數


def _crawl():
    END_POST = '[正妹] 新年 第889彈'

    def check_date_from_page(cur_article):
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

    def get_prev_page_url(root_soup):
        return website + root_soup.find('div', id='action-bar-container').find('div', 'btn-group-paging').find_all('a')[1]['href']

    def get_date(soup):
        date_string = soup.find('div', 'date').string.strip()
        return date_string

    def get_title(cur_soup):
        if cur_soup.find('div', 'title').find('a'):
            title = ''
            for string in cur_soup.find('div', 'title').a.strings:
                # if @ occur, need specical parse
                title = title + string
            return title
        else:
            return False

    def write_info(all_file, pop_file, soup):
        """soup is on <div r-ent>"""
        def check_title_string(title):
            """title is a string, true mean this is what we need"""
            match = re.search(r'^\[公告\]', title)
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
    print(
        'total time for get the proper 2017 last post: ' + str(t1 - t0) + '\n')

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

    print('total time for crawl all 2017 post: ' +
          str(t3 - t2) + '\n')
    print('total exec time: ' + str(t3 - t0) + '\n')


# 第二題 starte_date, end_date


def _push(start_date, end_date):
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
            print(url)
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
            if exec_finish_time - exec_time < 0.1:
                print('sleep for a while ....')
                time.sleep(0.1)
        check_time = time.time()
        print("exec time now: %f" % ((check_time - t1) / 60))
    all_file.close()
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


def _keyword(start_date, end_date, keyword):
    def get_url_by_keyword(url, keyword):
        # test_article = 'https://www.ptt.cc/bbs/Beauty/M.1504013271.A.1ED.html'
        # keyword = r'她真的好強阿推一個'
        keyword_pattern = re.compile(keyword)
        url_pattern = re.compile(r'\.jpg|\.png|\.jpeg|\.gif$')
        # *********** above is parameter ***********************
        validate_flag = False
        # this flag determine if this article's pic save or not
        save_flag = False
        pic_list = []
        print('get response from:', url)
        response = get_response(url)
        soup = BeautifulSoup(response.text, 'lxml')
        end_soup = soup.find_all('span', 'f2')
        # 檢查格式符不符合規定
        # validate_flag = False
        for end in end_soup:
            if end.find(string=re.compile("發信站")):
                article_end_soup = end
                validate_flag = True
                break

        if validate_flag:
            # 從結束點開始往上找
            for article_content in article_end_soup.previous_siblings:
                # 分 case
                # 如果 article_content 是 string
                # 搜尋關鍵字
                # 如果 article_content 是 tag
                # class = richcontent: do nothing
                # a check a.string 的尾巴是不是.jpg, png ... 是 存在list中，否，do nothing
                # div class = article-metaline article-metaline-right: children.string 關鍵字搜尋
                content_type = type(article_content)
                # string case
                if content_type is NavigableString:
                    if keyword_pattern.search(article_content):
                        print('set "save_flag" to true')
                        save_flag = True
                if content_type is Tag:
                    if article_content.name == 'a':
                        # match url pattern
                        if url_pattern.search(article_content.string):
                            print('append url:', article_content.string)
                            pic_list.append(article_content.string)
                    if article_content.has_attr('class'):
                        class_list = article_content.get('class')
                        if 'article-metaline' in class_list or 'article-metaline-right' in class_list:
                            for meta_content in article_content.children:
                                match = None
                                if type(meta_content) is Tag:
                                    match = keyword_pattern.search(
                                        meta_content.string)
                                elif type(meta_content) is NavigableString:
                                    match = keyword_pattern.search(
                                        meta_content)
                                if match:
                                    print('set "save_flag" to true')
                                    save_flag = True
            if save_flag:
                print('continue search url in reply part')
                # 從結束點往下找
                for reply_content in article_end_soup.next_elements:
                    # is tag and name = a, than match
                    if type(reply_content) is Tag:
                        if reply_content.name == 'a' and reply_content.string is not None:
                            # print(reply_content.string)
                            if url_pattern.search(reply_content.string):
                                print('append url:', reply_content.string)
                                pic_list.append(reply_content.string)
        if save_flag:
            return pic_list
        else:
            return None

    # start_date = 1201
    # end_date = 1231
    # keyword = '正妹'
    pic_list = []
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
            print(url)
            result = get_url_by_keyword(url.strip(), keyword)
            if result is not None:
                pic_list.extend(result)
    all_file.close()

    keyword_file = codecs.open(
        "keyword[%d-%d].txt" % (start_date, end_date), "w", "utf-8")
    for url in pic_list:
        keyword_file.write('%s\r\n' % (url))
    keyword_file.close()


if __name__ == '__main__':
    print('command: %s' % sys.argv[1])
    command = sys.argv[1]
    print('argument: ',  str(sys.argv[2:]))
    argument_list = sys.argv[2:]
    # 第一題
    if command == 'crawl':
        print('command valid! execute...')
        _crawl()
    if command == 'push':
        print('command valid! execute...')
        _push(int(argument_list[0]), int(argument_list[1]))
    if command == 'keyword':
        print('command valid! execute...')
        _keyword(int(argument_list[0]), int(
            argument_list[1]), argument_list[2])
    else:
        print('command invalid')
    print('end of program! terminate...')
