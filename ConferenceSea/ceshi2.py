# coding=utf-8
from selenium import webdriver
from lxml import etree
driver = webdriver.Chrome()

driver.get("https://tieba.baidu.com/f?kw=%E5%A5%A5%E7%89%B9%E6%9B%BC")
a = driver.find_elements_by_xpath('//*[@id="pagelet_frs-list/pagelet/thread_list"]/ul/li')
print a
print 2
print driver.page_source
# driver.quit()
ac = driver.find_elements_by_id('su')
