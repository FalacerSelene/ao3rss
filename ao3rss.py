#! /usr/bin/env python3

import requests
import re

from flask import Flask
from bs4 import BeautifulSoup
from time import strptime, strftime


ao3root = 'https://archiveofourown.org'


def ao3url(work_id):
    return '{}/works/{}/navigate'.format(ao3root, work_id)


class Work(object):
    def __init__(self, work_id):
        self.work_id = work_id
        self.url = ao3url(work_id)
        self.soup = self._get_soup(self.url)
        self.title = self.soup.find('h2', class_='heading').find('a').string
        self.chapters = [
                self._convert_chapter(c)
                for c
                in (self.soup
                    .find('ol', class_='chapter index group')
                    .find_all('li'))]

    def _convert_chapter(self, chapter):
        linkelem = chapter.find('a')
        link = '{}{}'.format(ao3root, linkelem.attrs['href'])
        title = linkelem.string
        spanelem = chapter.find('span', class_='datetime')
        date = re.sub('^\((.*)\)$', '\\1', spanelem.string)
        time = strptime(date, '%Y-%m-%d')
        date = strftime('%a, %d %b %Y %T', time)
        return {'title': title, 'date': date, 'link': link}

    def _get_soup(self, url):
        rsp = requests.get(url)
        if rsp.status_code != 200:
            raise ValueError('Failed to get work: {}!'.format(rsp.status_code))

        return BeautifulSoup(rsp.text, 'html.parser')

    def most_recent_date(self):
        if not self.chapters:
            return None
        r = self.chapters[-1]
        return r['date']

    def as_rss(self):
        chapter_rss = [self._chapter_rss(c) for c in self.chapters]
        chapter_rss.reverse()
        all_chaps = '\n'.join(chapter_rss)
        d = self.most_recent_date()
        return '''\
<?xml version='1.0'>
<rss version='2.0'>
    <channel>
    <title>{}</title>
    <link>{}</link>
    <pubDate>{}</pubDate>
    <lastBuildDate>{}</lastBuildDate>
    <ttl>720</ttl>
{}
    </channel>
</rss>
'''.format(self.title, self.url, d, d, all_chaps).strip()


    def _chapter_rss(self, chapter):
        return '''\
    <item>
        <title>{}</title>
        <link>{}</link>
        <pubDate>{}</pubDate>
    </item>'''.format(chapter['title'], chapter['link'], chapter['date'])


app = Flask('ao3')

@app.route('/work/<workid>')
def get_work(workid):
    w = Work(workid)
    return w.as_rss(), 200, {
        'Content-Type': 'application/rss+xml',
        'X-Clacks-Overhead': 'GNU Terry Pratchett'
    }


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3336)