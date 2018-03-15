#encoding:utf-8
import json
import re
import threading

import scrapy
import time
from selenium.webdriver import ActionChains
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from qqtest.items import Feed

L = threading.Lock()

class Qzspider(scrapy.Spider) :
    name = 'qqspider'

    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        self.browser = webdriver.Chrome(executable_path="C:\Program Files\chromedriver.exe",options=chrome_options)
        self.browser.set_page_load_timeout(30)
        self.count = 0
        self.qzonetoken = 0
        super(Qzspider,self).__init__()


    def start_requests(self):
        self.browser.get('https://qzone.qq.com/')
        WebDriverWait(self.browser, 600).until(EC.presence_of_element_located((By.ID, "login_frame")))
        self.browser.switch_to.frame('login_frame')
        action = ActionChains(self.browser)
        action.click(self.browser.find_element_by_id("switcher_plogin"))
        action.send_keys_to_element(self.browser.find_element_by_id('u'), '*******') # 输入账户
        action.send_keys_to_element(self.browser.find_element_by_id('p'), '*******') # 输入密码
        action.click(self.browser.find_element_by_id('login_button'))
        action.perform()

        WebDriverWait(self.browser, timeout = 600).until(EC.presence_of_element_located((By.ID, "aMainPage")))
        self.browser.find_element_by_id('aMainPage').click()

        WebDriverWait(self.browser, timeout = 600).until(EC.presence_of_element_located((By.ID, "QM_Profile_Mood_A")))
        self.browser.find_element_by_id('QM_Profile_Mood_A').click()

        self.qzonetoken = self.browser.execute_script("return window.g_qzonetoken")
        self.g_tk = self.browser.execute_script("return QZONE.FP.getACSRFToken()")

        url = "https://h5.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6?uin=740624616&inCharset=utf-8&outCharset=utf-8&hostUin=740624616&notice=0&sort=0&pos=0&num=40&cgi_host=http%3A%2F%2Ftaotao.qq.com%2Fcgi-bin%2Femotion_cgi_msglist_v6&code_version=1&format=jsonp&need_private_comment=1&g_tk=" + bytes(
            self.g_tk) + "&qzonetoken=" + bytes(self.qzonetoken)

        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        select = scrapy.Selector(response)
        data = str(select.xpath("/html/body/pre/text()[1]").extract_first())
        data = data[10:-2]
        information = json.loads(data)

        msglist = information['msglist']

        for msg in msglist:
            commentlist = []
            if(msg.has_key('commentlist')):
                for comment in msg['commentlist'] :
                    aComment = {}
                    aComment['content'] = comment['content'] # 评论的内容
                    aComment['name'] = comment['name'] # 评论人

                    aComment["follow_up_comment"] = [] # 对评论的回应
                    # 如果对该条评论进行了回应
                    if(comment.has_key("list_3")):
                        for follow_up_comment in comment["list_3"]:
                            aComment["follow_up_comment"].append(follow_up_comment["content"])
                    commentlist.append(aComment)

            item = Feed(id = msg['tid'], content = msg['content'], comments_list = commentlist, createTime = msg['created_time'])
            
            yield item


        time.sleep(10)

        url = response.url
        pos = str(re.findall('pos=[0,1,2,3,4,5,6,7,8,9]*', url))

        posNum = int(pos[6:-2]) + 40
        if(posNum > 2879):
            return
        elif(2879 - posNum  < 40) :
            num = str(re.findall('num=[0,1,2,3,4,5,6,7,8,9]*', url))
            newUrl = url.replace(pos[2:-2],"pos="+str(posNum)).replace(num,"num="+str(2879-posNum))
        else:
            newUrl = url.replace(pos[2:-2], "pos=" + str(posNum))

        yield scrapy.Request(newUrl)




