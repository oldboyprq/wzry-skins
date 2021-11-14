# /usr/bin/python3
# coding:utf-8
# @Author:prq
# @Time:2021/10/10 20:56

import os
import requests
from lxml import etree
import threading

# 获取英雄信息
r = requests.get("https://pvp.qq.com/web201605/js/herolist.json")
# print(r.text)

# 在当前目录创建保存皮肤的文件夹skins
try:
    os.mkdir('./skins')
    print("文件夹创建成功，皮肤保存在skins下")
except FileExistsError as e:
    print("skins文件夹已存在")

# 存放英雄名称和对应代码
names, codes = list(), list()
for i in r.json():
    # print(i)
    names.append(i["cname"])
    codes.append(i["ename"])


# 获取皮肤
def get_skins(num: int):
    # 每个线程要获取的英雄数量
    k = 20
    # 处理末尾不足20的部分
    if num + 20 > len(r.json()):
        k = len(r.json()) - num
    # 对每个英雄进行处理
    for i in range(k):
        name = names[num + i]
        code = codes[num + i]
        # 创建英雄文件夹
        try:
            os.mkdir('./skins/{}'.format(name))
            print("{}文件夹创建成功".format(name))
        except FileExistsError as e:
            print("{}文件夹已存在".format(name))
        '''
        获取皮肤名称
        json里有一个字段叫skin_name，但个别英雄有缺少
        所以直接用网页上的
        '''
        url = "https://pvp.qq.com/web201605/herodetail/{}.shtml".format(code)
        skin = requests.get(url)
        skin.encoding = 'gbk'
        html = etree.HTML(skin.text)
        skin_names = list(html.xpath('//ul[@class="pic-pf-list pic-pf-list3"]/@data-imgname')[0].split('|'))
        # 下载皮肤
        for j in range(len(skin_names)):
            url = "http://game.gtimg.cn/images/yxzj/img201606/skin/hero-info/{}/{}-bigskin-{}.jpg".format(code, code,
                                                                                                          j + 1)
            index_j = skin_names[j].index('&')
            image_name = skin_names[j][:index_j] + '.jpg'
            image = requests.get(url).content
            try:
                with open('./skins/{}/{}'.format(name, image_name), 'wb') as fp:
                    fp.write(image)
                    fp.close()
                    print("{}下载完成".format(image_name))
            except Exception as e:
                print("%s" % e)
            break # auto 一个线程爬一个皮肤就退出，减少执行时间，正常使用注释掉这句即可。
        break # auto 一个线程爬一个皮肤就退出，减少执行时间，正常使用注释掉这句即可。


start = 0
threads = list()
while start < len(r.json()):
    threads.append(threading.Thread(target=get_skins, args=(start,)))
    start = start + 20  # 每一个线程用的起始位置
for t in threads:
    t.start()
for t in threads:
    t.join()
