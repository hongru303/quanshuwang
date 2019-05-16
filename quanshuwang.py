import requests
import re
import pymongo
from lxml import etree


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
}


#定义一个请求函数处理url的请求
def get_book_url(url):
    try:
        session = requests.Session()
        response = session.get(url, headers = headers)
        if response.status_code == 200:
            response.encoding = 'gbk'  # 把编码换成gbk，其他的都不支持
            re_content = re.sub('<br />', '', response.text)  # 把里面的换行全去掉，看着太难受
            return re_content
    except requests.ConnectionError:
        pass

#定义一个解析函数处理页面的解析
def get_parse_xpath(html):
    try:
        book_html = etree.HTML(html)
        parse_url = book_html.xpath('//div[contains(@class, "dirconone")]/li/a/@href')#解析出所有章节的url
        parse_text = book_html.xpath('//div[@id="content"]/text()')#解析出每一章的文本
        parse_title = book_html.xpath('//div[@class="bookInfo"]/h1/strong/text()')#解析出每一章的标题
        #parse_url.reverse()#倒叙
        return parse_url, parse_title, parse_text #返回三个列表的元祖结构
    except Exception as e:
        print(e)

#保存到mongo数据库
def download_mongo(save_mongo):
    try:
        client = pymongo.MongoClient()#连接mongodb
        db = client['quanshu']#新建一个库
        collection = db['透视之眼']#新建一个集合
        if collection.insert_one(save_mongo):#保存到mongo
            print('succesed save in mongo')
    except Exception as e:
        print(e)

def main(url):
    try:
        html = get_book_url(url)
        parse_url = get_parse_xpath(html)
        for urls in parse_url[0]:
            results = get_book_url(urls)
            parse_text = get_parse_xpath(results)
            save_book = {parse_text[1][0]: parse_text[2][0]}
            download_mongo(save_book)
            print('成功保存章节%s'%parse_text[1][0], urls)
    except ConnectionError:
        pass

if __name__ == '__main__':
    main('http://www.quanshuwang.com/book/0/437')


