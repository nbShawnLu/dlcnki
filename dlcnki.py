#!/usr/bin/env Python
# coding=utf-8
import sys
import os
from time import sleep
from selenium import webdriver


def browser_init(isWait):
    options = webdriver.ChromeOptions()
    prefs = {'profile.default_content_settings.popups': 0,
             'download.default_directory': 'D:\\code\\python\\cnki\\dl'}
    options.add_experimental_option('prefs', prefs)

    browser = webdriver.Chrome(
        executable_path='chromedriver.exe', chrome_options=options)
    browser.set_window_size(500, 500)
    if isWait:
        browser.implicitly_wait(50)
    return browser


def searchKey(keyword):
    browser.get("http://kns.cnki.net/kns/brief/default_result.aspx")
    browser.find_element_by_id('txt_1_value1').send_keys(keyword)
    browser.find_element_by_id('btnSearch').click()


def switchToFrame(browser):
    # print 'start switch'
    browser.switch_to.frame('iframeResult')
    # print 'end switch'


def getDownloadLinks(browser, paper_downloadLinks, n=20):
    i = 0
    for link in browser.find_elements_by_css_selector('a[href^=\/kns\/detail]'):
        # link.click()
        url = link.get_attribute('href')
        url_part = url.split('&')[3:6]
        url_str = '&'.join(url_part)
        down_url = 'http://kns.cnki.net/KCMS/detail/detail.aspx?' + url_str
        # print down_url
        paper_downloadLinks.append(down_url)
        i += 1
        if i >= n:
            break


def switchToPage(browser, n):
    for link in browser.find_elements_by_css_selector('a[href^=\?curpage]'):
        url = link.get_attribute('href')
        print(url)
        pageInd = 'curpage=%d&' % n
        print(pageInd)
        if pageInd in url:
            print("page: " + url)
            link.click()
            break


def switchNextPage(browser):
    browser.find_element_by_link_text(u'下一页').click()


def do_download(driver, urls, fail_downLoadUrl):
    for url in urls:
        print(url)
        driver.get(url)
        paper_title = driver.title
        print("paper title" + paper_title)
        if u'中国专利全文数据库' in paper_title:
            continue
        print("try download :" + paper_title)
        try:
            driver.find_element_by_xpath(
                "//a[contains(text(),'PDF下载')]").click()
            print("download success!!!")
        except Exception as e:
            try:
                driver.find_element_by_xpath(
                    "//a[contains(text(),'整本下载')]").click()
                print("download success!!!")
            except Exception as e:
                print("download fail!!!")
                fail_downLoadUrl.append(url)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("no keyword")
        sys.exit(1)
    keyword = sys.argv[1]  # 论文搜索的关键字
    paperNumber = 1  # 下载多少篇的论文
    if len(sys.argv) > 2:
        paperNumber = int(sys.argv[2])

    (pageNum, remNum) = divmod(paperNumber, 20)
    browser = browser_init(True)
    searchKey(keyword)
    switchToFrame(browser)
    paper_downloadLinks = []  # 论文下载链接

    curPage = 1
    while curPage <= pageNum:
        getDownloadLinks(browser, paper_downloadLinks)
        switchNextPage(browser)
        curPage += 1
    getDownloadLinks(browser, paper_downloadLinks, remNum)
    browser.quit()
    print("采集了%d条数据" % len(paper_downloadLinks))
    driver = browser_init(False)
    fail_downLoadUrl = []  # 记录下失败的网站
    do_download(driver, paper_downloadLinks, fail_downLoadUrl)
    print(fail_downLoadUrl)
    tryNum = 0
    # 尝试N次重新下载没有下载的
    while tryNum < 5:
        if len(fail_downLoadUrl) != 0:
            paper_downloadLinks = fail_downLoadUrl
            fail_downLoadUrl = []
            do_download(driver, paper_downloadLinks, fail_downLoadUrl)
            print(fail_downLoadUrl)
        else:
            break
        tryNum += 1
    sleep(10 * paperNumber)
    driver.quit()
