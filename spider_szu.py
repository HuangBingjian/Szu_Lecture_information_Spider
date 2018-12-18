# -*- coding: utf-8 -*-
import requests
import re
from bs4 import BeautifulSoup
import time

# 头部信息
headers = {
    'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
}

is_new = True       # 选择是否最新讲座信息
names = []
urls = []
times = []
Info_dict = {}      # 字典，获取讲座信息
Info = []

f = open('./讲座信息.txt', 'w', encoding='utf-8')  # 写入txt


def get_login_web(url):
    r_session  = requests.Session()
    response = r_session.post(url, headers=headers)
    page = response.text.encode("latin1").decode("gbk")
    soup = BeautifulSoup(page, 'html.parser')
    # print(soup.prettify())

    # print('------------------------讲座信息列表------------------\n')
    for x_a in soup.find_all('a',text="信息工程学院"):                # 发文单位为信息工程学院
        x_class = x_a.find_parent().find_previous_siblings()            # 类别
        if x_class[0].find('a').get_text() != '学术':                  # 如果类别不是讲座
            continue

        x_lecture = x_a.find_parent().find_next_siblings()              # 讲座
        name = x_lecture[0].find('a').get_text()[1:]                    # 提取讲座名称
        url = 'https://www1.szu.edu.cn/board/' + x_lecture[0].find('a')['href']
        if(re.match(r'学术讲座',name) or re.match(r'学术沙龙',name) or re.match(r'学术报告',name)):# 关键词
            names.append(name)
            urls.append(url) # 提取链接
            # print(name)
            # print(url)
    # print('--------------------------END------------------------\n\n')


def analyse_urls():
    if urls != None and times != None:                                # 保证抓取的链接列表不为空
        for url,num in zip(urls,range(len(urls))):
            get_url(url,num)                                            # 抓取相应链接的信息

        # 获取当前时间
        list_time = time.strftime("%Y-%m-%d-%H-%M", time.localtime(time.time())).split('-')
        now_time = list(map(int, list_time))

        # 按讲座时间排序
        times.sort(reverse=True)
        for t in times:
            if (is_new is True and t[:5] >= now_time) or is_new is False:
                index = t[5]
                Info.append(Info_dict[index])
                f.write(Info_dict[index])

        for i in Info:
            print(i)

    else:
        # 如果匹配失败
        print('暂无最新讲座信息')
        return

def get_url(url,num):
    res = requests.get(url)
    res.encoding = 'gb18030'
    bs = BeautifulSoup(res.text, 'lxml')
    # req = request.Request(url)
    # html = urlopen(req)
    # bs = BeautifulSoup(html.read(), "html.parser")
    text_all = ''

    # 方案1：
    # <p></p>
    for p in bs.find_all('p'):
        text = p.get_text()
        text_all = text_all + text

    # 方案1失败则方案2
    # 启发式，在<td></td>格式中，文本内容均未换行，即所有文本在一行中。
    if text_all == '':
        text = bs.get_text()
        text_all = re.findall(u'报告题目(.*)',text, re.M|re.I)[0]
        text_all = '报告题目' + text_all

    # 提取讲座时间，以便后续排序
    text_time = re.findall(u'时间(.*)地点',text_all, re.M|re.I)
    if text_time == []:
        text_time = re.findall(u'时间(.*)', text_all, re.M | re.I)
    if text_time == []:  # 如果依旧为空，说明提取失败，设置默认值
        time = [3000, 0, 0, 0, 0, num]
        times.append(time)
    else:
        time = re.findall(u'\d+',text_time[0])
        # 时间的12进制转24进制
        if '下午' in text_time[0] and int(time[3])<12:
            time[3] = str(int(time[3]) + 12)
        # 消掉日期前的0，如07改为7
        time = list(map(int, time))
        # 时间长度是否为5
        if len(time) == 5:
            time.append(num)
        elif len(time) >5:
            time = time[:5]
            time.append(num)
        else:
            for i in range(5-len(time)):
                time.append(0)
            time.append(num)
            # print(time)
        times.append(time)

    # 换行，整理文本
    text_all = text_all.replace('\n','').replace('主讲嘉宾','\n\n主讲嘉宾').replace('邀请人','\n\n邀请人').replace('时间','\n\n时间')\
            .replace('地点','\n\n地点').replace('会议室','会议室\t').replace('报告摘要','\n\n报告摘要').replace('嘉宾简介','\n\n嘉宾简介')
    text_all += '\n\n--------------------------------------------------------------------------------------------\n\n'
    Info_dict[num] = text_all


if __name__ == "__main__":
    web = "https://www1.szu.edu.cn/board/?infotype=%D1%A7%CA%F5"
    get_login_web(web)
    analyse_urls()
    f.close()
    input('\n按任意键结束!')