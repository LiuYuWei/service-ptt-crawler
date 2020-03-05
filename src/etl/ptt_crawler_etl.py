"""ptt crawler etl"""

import codecs
import requests
from bs4 import BeautifulSoup
import time
import re
import json

from src.system.config_setting import ConfigSetting
from src.system.path_setting import PathSetting
from src.etl.ptt_article_parser import PttArticleParser


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
        self.filename = self.board + '-' + \
            str(self.start) + '-' + str(self.end) + '.json'
        self.filename = self.path_setting.path_join('data', self.filename)

    def crawler_pipeline(self):
        self.file_initial_setting()
        self.parse_articles()

    def file_initial_setting(self):
        self.store(self.filename, u'{"articles": [', 'w')
    
    def parse_articles(self, path='.', timeout=3):
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
                try:
                    # ex. link would be <a href="/bbs/PublicServan/M.1127742013.A.240.html">Re: [問題] 職等</a>
                    href = div.find('a')['href']
                    link = self.PTT_URL + href
                    article_id = re.sub('\.html', '', href.split('/')[-1])
                    if div == divs[-1] and i == self.end-self.start:  # last div of last page
                        self.store(self.filename, self.parse(
                            link, article_id, self.board), 'a')
                    else:
                        self.store(self.filename, self.parse(
                            link, article_id, self.board) + ',\n', 'a')
                except:
                    self.log.warn('Something error.')
            time.sleep(1)
        self.store(self.filename, u']}', 'a')
        return self.filename

    def parse(self, link, article_id, board, timeout=3):
        self.log.info('Processing article:{}'.format(article_id))
        ptt_article_parser = PttArticleParser(link, article_id, board)
        return ptt_article_parser.article_parser()

    @staticmethod
    def store(filename, data, mode):
        with codecs.open(filename, mode, encoding='utf-8') as f:
            f.write(data)
