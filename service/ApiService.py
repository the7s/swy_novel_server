from service.RequestService import RequestService
from bs4 import BeautifulSoup
import pymongo
import redis
from settings import *
import json
import math
import base64
from urllib import parse

client = pymongo.MongoClient('mongodb://root:123456@127.0.0.1:27017')
db = client['novel']

pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
redis_conn = redis.Redis(connection_pool=pool)

website_url = 'http://www.xbiquge.la'


class ApiService(object):

    def get_novel_categories(self, website_uri=website_url):
        """
        获取小说分类
        :param website_uri:
        :return:
        """

        if redis_conn.get(NOVEL_ALL_CATEGORY):
            category_str = redis_conn.get(NOVEL_ALL_CATEGORY)
            category_list = json.loads(category_str)
        else:
            category_list = self.get_data(page_url=website_uri)
            redis_conn.set('novel_all_category', json.dumps(category_list))
            for cat in category_list:
                redis_conn.hmset(CATEGORY_PREFIX_HASH + str(cat['category_id']), cat)

        return {
            'count': len(category_list),
            'data': category_list
        }

    def get_novel_list(self, category_id=1, page=1):
        """
        根据分类获取小说列表
        :param category_id: 分类id
         :param page: 页码
        :return:
        """
        # data, next_page_url = self.get_novel_data(page_url=category_uri)
        # db['novel'].insert_many(data)
        # category_uri = 'http://www.xbiquge.la/fenlei/2_191.html'

        # 暂时不处理全部题型的情况
        if category_id == 7:
            return []

        slice_index = page % 3
        if slice_index == 0:
            slice_index = 3

        url = WEBSITE_FENLEI + '/' + str(category_id) + '_' + str(math.ceil(page/3)) + '.html'

        data = self.get_novel_data(page_url=url, category_id=category_id, slice_index=slice_index)
        return data

    def get_novel_catalog(self, novel_uri):
        """
        根据小说id获取小说目录
        :param novel_uri:
        :return:
        """
        data = self.get_novel_catalog_data1(novel_uri)
        db['chapter'].insert_many(data)
        print('success！！！')

    def get_novel_content(self, chapter_uri):
        """
        根据小说章节id获取小说内容
        :param chapter_uri:
        :return:
        """

        pass

    def get_novel(self, novel_id):
        novel_url = parse.unquote_plus(novel_id)
        print(novel_url)

    def get_novel_detail(self, novel_url):
        """
        根据小说章节id获取小说内容
        :param novel_url:
        :return:
        """
        request_server = RequestService()
        html = request_server.get_one_page(novel_url)
        soup = BeautifulSoup(html, 'lxml')
        detail_dom = soup.select('.box_con')[0]
        novel_intro = detail_dom.select('#intro p')[1].get_text()
        novel_image = detail_dom.select('#sidebar #fmimg img')[0].attrs['src']
        return novel_image, novel_intro

    def get_data(self, page_url):
        request_server = RequestService()
        html = request_server.get_one_page(page_url)
        soup = BeautifulSoup(html, 'lxml')
        soup_li = soup.select('.nav ul li')[2:]
        del soup_li[6]
        category_list = []
        for li in soup_li:
            cat = {
                'category_id': len(category_list)+1,
                'category_uri': website_url + li.a.attrs['href'],
                'category_name': li.a.get_text(),
            }
            category_list.append(cat)
        return category_list

    def get_novel_data(self, page_url, category_id, slice_index):
        print(page_url, category_id, slice_index)
        request_server = RequestService()
        html = request_server.get_one_page(page_url)
        soup = BeautifulSoup(html, 'lxml')
        newcontent_soup = soup.select('#newscontent .l ul>li')

        novel_list = []
        if not newcontent_soup:
            return novel_list

        newcontent_soup = newcontent_soup[(slice_index-1)*10:slice_index*10]

        for li in newcontent_soup:
            # 访问详情页，获取详情页信息
            novel_url = li.findAll('span')[0].find('a').attrs['href']

            if not novel_url:
                break
            parse_url = base64.b64encode(novel_url.encode('utf-8')).encode()
            if redis_conn.exists(NOVEL_PREFIX_HASH + parse_url):
                novel_map = redis_conn.hgetall(NOVEL_PREFIX_HASH + parse_url)
            else:
                novel_image, novel_intro = self.get_novel_detail(novel_url)

                novel_map = {
                    'category_id': category_id,
                    'novel_url': parse_url,
                    'novel_name': li.findAll('span')[0].find('a').get_text(),
                    'novel_image': novel_image,
                    'novel_intro': novel_intro,
                    'novel_author': li.findAll('span')[-1].get_text(),
                }
                redis_conn.hmset(NOVEL_PREFIX_HASH + parse_url, novel_map)
            novel_list.append(novel_map)
        return novel_list

        # 判断是否为最后一行
        # page_soup = soup.select('#pagelink #pagestats')
        # cur_l_str = page_soup[0].get_text()
        # cur_last_page_list = cur_l_str.split('/')
        # if int(cur_last_page_list[0]) < int(cur_last_page_list[1]):
        #     has_next_dom = soup.select('#pagelink a.next')
        #     if not has_next_dom:
        #         return novel_list, soup.select('#pagelink a.last')[0].attrs['href']
        #     return novel_list, soup.select('#pagelink a.next')[0].attrs['href']
        # else:
        #     return novel_list, False

    def get_novel_catalog_data1(self, page_url):
        request_server = RequestService()
        html = request_server.get_one_page(page_url)
        soup = BeautifulSoup(html, 'lxml')
        soup_dd = soup.select('#list dl dd')
        chapter_list = []
        for dd in soup_dd:
            # chapter_list.append({})
            yield {
                'novel_url': page_url,
                'chapter_name': dd.a.text,
                'chapter_url': website_url + dd.a.attrs['href'],
            }
