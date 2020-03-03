"""ptt crawler etl"""

import codecs
import requests
from bs4 import BeautifulSoup
import time
import re
import json

from src.system.config_setting import ConfigSetting
from src.system.path_setting import PathSetting


class PttCrawlerEtl:
    """Pttcrawler pipeline"""
    PTT_URL = 'https://www.ptt.cc'

    def __init__(self, start, end, board, verify=False):
        config_setting = ConfigSetting()
        self.log = config_setting.set_logger("[PttCrawler]")
        self.config = config_setting.yaml_parser()
        self.path_setting = PathSetting()
        self.board = board
        self.start = start
        self.end = end
        self.article_id = None
        self.verify = verify

    def parse_articles(self, path='.', timeout=3):
        filename = self.board + '-' + \
            str(self.start) + '-' + str(self.end) + '.json'
        filename = self.path_setting.path_join('data', filename)
        self.store(filename, u'{"articles": [', 'w')
        for i in range(self.end-self.start+1):
            index = self.start + i
            print(self.PTT_URL + '/bbs/' + self.board +
                  '/index' + str(index) + '.html')
            resp = requests.get(
                url=self.PTT_URL + '/bbs/' + self.board +
                '/index' + str(index) + '.html',
                verify=self.verify, timeout=timeout
            )
            if resp.status_code != 200:
                self.log.error('invalid url:', resp.url)
                continue
            soup = BeautifulSoup(resp.text, 'html.parser')
            divs = soup.find_all("div", "r-ent")
            for div in divs:
                # try:
                    # ex. link would be <a href="/bbs/PublicServan/M.1127742013.A.240.html">Re: [問題] 職等</a>
                href = div.find('a')['href']
                link = self.PTT_URL + href
                article_id = re.sub('\.html', '', href.split('/')[-1])
                if div == divs[-1] and i == self.end-self.start:  # last div of last page
                    self.store(filename, self.parse(
                        link, article_id, self.board), 'a')
                else:
                    self.store(filename, self.parse(
                        link, article_id, self.board) + ',\n', 'a')
                # except:
                #     self.log.warn('Something error.')
            time.sleep(1)
        self.store(filename, u']}', 'a')
        return filename

    # @staticmethod
    def parse(self, link, article_id, board, timeout=3):
        print('Processing article:', article_id)
        resp = requests.get(url=link, cookies={
                            'over18': '1'}, verify=self.verify, timeout=timeout)
        if resp.status_code != 200:
            print('invalid url:', resp.url)
            return json.dumps({"error": "invalid url"}, sort_keys=True, ensure_ascii=False)
        soup = BeautifulSoup(resp.text, 'html.parser')
        main_content = soup.find(id="main-content")
        metas = main_content.select('div.article-metaline')
        author = ''
        title = ''
        date = ''
        if metas:
            author = metas[0].select('span.article-meta-value')[
                0].string if metas[0].select('span.article-meta-value')[0] else author
            title = metas[1].select('span.article-meta-value')[0].string if metas[1].select(
                'span.article-meta-value')[0] else title
            date = metas[2].select('span.article-meta-value')[0].string if metas[2].select(
                'span.article-meta-value')[0] else date

            # remove meta nodes
            for meta in metas:
                meta.extract()
            for meta in main_content.select('div.article-metaline-right'):
                meta.extract()

        # remove and keep push nodes
        pushes = main_content.find_all('div', class_='push')
        for push in pushes:
            push.extract()

        try:
            ip = main_content.find(text=re.compile(u'※ 發信站:'))
            ip = re.search('[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*', ip).group()
        except:
            ip = "None"

        # 移除 '※ 發信站:' (starts with u'\u203b'), '◆ From:' (starts with u'\u25c6'), 空行及多餘空白
        # 保留英數字, 中文及中文標點, 網址, 部分特殊符號
        filtered = [v for v in main_content.stripped_strings if v[0]
                    not in [u'※', u'◆'] and v[:2] not in [u'--']]
        expr = re.compile(
            u'[^\u4e00-\u9fa5\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b\s\w:/-_.?~%()]')
        for i in range(len(filtered)):
            filtered[i] = re.sub(expr, '', filtered[i])

        filtered = [_f for _f in filtered if _f]  # remove empty strings
        # remove last line containing the url of the article
        filtered = [x for x in filtered if article_id not in x]
        content = ' '.join(filtered)
        content = re.sub(r'(\s)+', ' ', content)
        # print 'content', content

        # push messages
        p, b, n = 0, 0, 0
        messages = []
        for push in pushes:
            if not push.find('span', 'push-tag'):
                continue
            push_tag = push.find('span', 'push-tag').string.strip(' \t\n\r')
            push_userid = push.find(
                'span', 'push-userid').string.strip(' \t\n\r')
            # if find is None: find().strings -> list -> ' '.join; else the current way
            push_content = push.find('span', 'push-content').strings
            push_content = ' '.join(push_content)[
                1:].strip(' \t\n\r')  # remove ':'
            push_ipdatetime = push.find(
                'span', 'push-ipdatetime').string.strip(' \t\n\r')
            messages.append({'push_tag': push_tag, 'push_userid': push_userid,
                             'push_content': push_content, 'push_ipdatetime': push_ipdatetime})
            if push_tag == u'推':
                p += 1
            elif push_tag == u'噓':
                b += 1
            else:
                n += 1

        # count: 推噓文相抵後的數量; all: 推文總數
        message_count = {'all': p+b+n, 'count': p -
                         b, 'push': p, 'boo': b, "neutral": n}

        # print 'msgs', messages
        # print 'mscounts', message_count

        # json data
        # data = {
        #     'url': link,
        #     'board': board,
        #     'article_id': article_id,
        #     'article_title': title,
        #     'author': author,
        #     'date': date,
        #     'content': content,
        #     'ip': ip,
        #     'message_count': message_count,
        #     'messages': messages
        # }
        data = {
            'authorId': author,
            'authorName': author,
            'title': title,
            'publishedTime': date,
            'content': '完整內文',
            'canonicalUrl': link
        }
        # print 'original:', d
        return json.dumps(data, sort_keys=True, ensure_ascii=False)

    @staticmethod
    def store(filename, data, mode):
        with codecs.open(filename, mode, encoding='utf-8') as f:
            f.write(data)
