# -*- coding: utf-8 -*-
import requests
import os
import time
from bs4 import BeautifulSoup
import threading
import logging

logging.basicConfig(level=logging.INFO,  # 控制台打印的日志级别
                    filename='download.log',
                    filemode='w',  ##模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
                    # a是追加模式，默认如果不写的话，就是追加模式
                    format=
                    '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
                    # 日志格式
                    )

base_url = 'https://m.xiannvtu.com'
pic_header = headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0"}
end_list = []


def download_page(url):
    while True:
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0"}
            r = requests.get(url, headers=headers)
            r.encoding = 'gbk'
            return r.text
        except:
            time.sleep(5)
            continue


def create_dir(name):
    if not os.path.exists(name):
        os.makedirs(name)


def get_pic(href, classification, text):
    page_html = download_page(href)
    soup = BeautifulSoup(page_html, 'html.parser')
    content = soup.select('div.single-post-content a img')
    for item in content:
        pic_link = item.get('src')
        logging.info('下载图片:' + classification + '>>' + text + '>>' + pic_link.split('/')[-1])
        page_download = True
        while page_download:
            try:
                r = requests.get(pic_link, headers=headers)
                with open('pic/{}/{}/{}'.format(classification, text, pic_link.split('/')[-1]), 'wb') as f:
                    f.write(r.content)
                    time.sleep(1)
                    page_download = False
            except:
                time.sleep(5)
                continue

    page_info = soup.select('div.fenye a')
    if (len(page_info) == 1):
        if (page_info[0].get_text() == '上一页'):
            return
        else:
            last_page_url = page_info[0].get('href')
            get_pic(base_url + "/v/" + last_page_url, classification, text)
    else:
        last_page_url = page_info[1].get('href')
        get_pic(base_url + "/v/" + last_page_url, classification, text)


def pic_list(href, classification):
    logging.info("下载页:" + href)
    page_html = download_page(href)
    soup = BeautifulSoup(page_html, 'html.parser')
    content = soup.select('#content div.post-header a')
    for item in content:
        text = item.get_text()
        link = item.get('href')
        create_dir('pic/{}/{}'.format(classification, text))
        get_pic(base_url + link, classification, text)

    last_page_html = soup.select('#webpage a')
    if (len(last_page_html) == 1):
        if (last_page_html[0].get_text() == '上一页'):
            end_list.append(classification)
            return
        else:
            last_page_url = last_page_html[0].get('href')
            pic_list(base_url + last_page_url, classification)
    else:
        last_page_url = last_page_html[1].get('href')
        pic_list(base_url + last_page_url, classification)


def item_url_list(page):
    soup = BeautifulSoup(page, 'html.parser')
    item_list = soup.select('li.cat-item a')

    threads = []
    isFirst = True
    while len(threads) > 0 or isFirst:
        for thread in threads:
            if not thread.is_alive():
                threads.remove(thread)
        if isFirst:
            for item in item_list:
                href = item.get('href')
                text = item.get_text()
                create_dir('pic/{}'.format(text))
                thread = threading.Thread(target=pic_list, args=(href, text))
                thread.setDaemon(True)
                thread.start()
                logging.info(text + "下载进程开始...")
                threads.append(thread)
            isFirst = False

    logging.info("下载结束...")


def execute(url):
    page_html = download_page(url)
    item_url_list(page_html)


def main():
    create_dir('pic')
    execute("https://m.xiannvtu.com/")


if __name__ == '__main__':
    main()
