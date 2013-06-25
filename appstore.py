#! /bin/env python
#encoding:utf-8

import re
import urllib2
import xml.etree.ElementTree as ElementTree
import sys
from traceback import print_exc
import sqlite3

rank_top_limit = 100
sqlite_db_file = './appstore_rank.db'

def gen_category_data():
    s = '<select id="feedGenre"><option value="">所有类型</option><option value="6004">体育</option><option value="6013">健康健美</option><option value="6020">医疗</option><option value="6006">参考</option><option value="6000">商业</option><option value="6022">商品指南</option><option value="6018">图书</option><option value="6001">天气</option><option value="6016">娱乐</option><option value="6010">导航</option><option value="6002">工具</option><option value="6021">报刊杂志</option><option value="6008">摄影与录像</option><option value="6007">效率</option><option value="6017">教育</option><option value="6009">新闻</option><option value="6003">旅行</option><option value="6014">游戏</option><option value="6012">生活</option><option value="6005">社交</option><option value="6023">美食佳饮</option><option value="6015">财务</option><option value="6011">音乐</option></select>'
    for cid, cname in re.findall(r'value="([^"]*)">([^<]*)<', s):
        if not cid:
            yield None, cname.strip()
        else:
            yield int(cid.strip()), cname.strip()


def gen_rss_url(cid, limit):
    if cid:
        return 'https://itunes.apple.com/cn/rss/topfreeapplications/limit=%d/genre=%d/xml' % (limit, cid)
    else:
        return 'https://itunes.apple.com/cn/rss/topfreeapplications/limit=%d/xml' % (limit)

def create_rank_table():
    cx = sqlite3.connect(sqlite_db_file)
    cu = cx.cursor()
    cu.execute('create table if not exists app_rank_info('
                'id integer primary key, '
                'category varchar(30),'
                'rank integer, '
                'app_id varchar(100), '
                'name varchar(100), '
                'link varchar(256), '
                'app_update varchar(100),'
                'rank_update date)')
    cx.close()


def insert_app_rank(category, appid, rank, name, link, app_updated):
    cx = None
    try:
        cx = sqlite3.connect(sqlite_db_file)
        cu = cx.cursor()
        sql = 'insert into app_rank_info(category, rank, app_id, name, link, app_update, rank_update) values("%s", %d, "%s", "%s", "%s", "%s", date())' % (category.decode('utf-8'), rank, appid, name, link, app_updated)
        print sql.encode('utf-8')
        cu.execute(sql)
        cx.commit()
    finally:
        if cx: cx.close()

    
def parse_app_data(category, html):
    from cStringIO import StringIO
    root = ElementTree.parse(StringIO(html)).getroot()
    for i, entry in enumerate([child for child in root if child.tag.endswith('entry')]):
        app_id, app_name, link, app_updated = None, None, None, None
        for prop in entry:
            if prop.tag.endswith('id'):
                app_id = prop.text
            elif prop.tag.endswith('name'):
                app_name = prop.text
            elif prop.tag.endswith('link'):
                link = prop.attrib['href']
            elif prop.tag.endswith('updated'):
                app_updated = prop.text
        insert_app_rank(category, app_id, i, app_name, link, app_updated)


def fetch(url, name):
    try:
        sys.stdout.write('%s\n'% url)
        sys.stdout.flush()
        html = urllib2.urlopen(url).read()
        parse_app_data(name, html)
    except:
        print_exc(file=sys.stderr)
    finally:
        pass
    
def main():
    from multiprocessing import Process
    procs = []
    create_rank_table()
    for cid, name in gen_category_data():
        url = gen_rss_url(cid, rank_top_limit)
        p = Process(target=fetch, args=(url, name,))
        p.start()
        procs.append(p)
    [p.join() for p in procs]


if __name__ == '__main__':
    main()
