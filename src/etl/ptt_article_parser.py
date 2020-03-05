"""ptt crawler etl"""

import codecs
import requests
from bs4 import BeautifulSoup
import time
import re
import json

from src.system.config_setting import ConfigSetting


class PttArticleParser:
    """Ptt article parser"""

    def __init__(self, link, article_id, board, timeout=3):
        config_setting = ConfigSetting()
        self.log = config_setting.set_logger("[PttCrawler]")
        self.config = config_setting.yaml_parser()
        self.link = link
        self.article_id = article_id
        self.board = board
        self.timeout = timeout
        self.soup = None
        self.main_content = None
        self.metas = None
        self.author_id = ''
        self.author_name = ''
        self.title = ''
        self.date = ''
        self.resp = None

    def article_parser(self, verify=False):
        self.request_article_content(verify)
        self.request_cleaning()
        self.parse_article_information()
        self.parse_article_content()
        article_data = self.article_json_transfer()
        return article_data

    def request_article_content(self, verify):
        self.resp = requests.get(url=self.link, cookies={
                            'over18': '1'}, verify=verify, timeout=self.timeout)
        if self.resp.status_code != 200:
            log.error('invalid url:{}'.format(self.resp.url))
            return json.dumps({"error": "invalid url"}, sort_keys=True, ensure_ascii=False)
        
    def request_cleaning(self):
        self.soup = BeautifulSoup(self.resp.text, 'html.parser')
        self.main_content = self.soup.find(id="main-content")
        self.metas = self.main_content.select('div.article-metaline')
    
    def parse_article_information(self):
        if self.metas:
            self.author_id = self.metas[0].select('span.article-meta-value')[
                0].string if self.metas[0].select('span.article-meta-value')[0] else self.author_id
            # self.log.info(self.author_id)
            self.author_name = re.findall(re.compile('[(](.*?)[)]', re.S), self.author_id)
            self.author_id = self.author_id.split('(',1)[0]
            self.title = self.metas[1].select('span.article-meta-value')[0].string if self.metas[1].select(
                'span.article-meta-value')[0] else title
            self.date = self.metas[2].select('span.article-meta-value')[0].string if self.metas[2].select(
                'span.article-meta-value')[0] else date

            # remove meta nodes
            for meta in self.metas:
                meta.extract()
            for meta in self.main_content.select('div.article-metaline-right'):
                meta.extract()
    
    def parse_article_content(self):
        # 移除 '※ 發信站:' (starts with u'\u203b'), '◆ From:' (starts with u'\u25c6'), 空行及多餘空白
        # 保留英數字, 中文及中文標點, 網址, 部分特殊符號
        filtered = [v for v in self.main_content.stripped_strings if v[0]
                    not in [u'※', u'◆'] and v[:2] not in [u'--']]
        expr = re.compile(
            u'[^\u4e00-\u9fa5\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b\s\w:/-_.?~%()]')
        for i in range(len(filtered)):
            filtered[i] = re.sub(expr, '', filtered[i])

        filtered = [_f for _f in filtered if _f]  # remove empty strings
        # remove last line containing the url of the article
        filtered = [x for x in filtered if self.article_id not in x]
        self.content = ' '.join(filtered)
        self.content = re.sub(r'(\s)+', ' ', self.content)
    
    def article_json_transfer(self):
        article_data = {
            'authorId': self.author_id,
            'authorName': self.author_name,
            'title': self.title,
            'publishedTime': self.date,
            'content': self.content,
            'canonicalUrl': self.link
        }
        return json.dumps(article_data, sort_keys=True, ensure_ascii=False)

