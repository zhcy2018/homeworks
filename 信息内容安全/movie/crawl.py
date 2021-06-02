from paddle.fluid.data import data
import requests
import chardet
import os
import json
from lxml import etree
from lxml.etree import HTMLParser
from pprint import pprint
import snownlp
import jieba
import re
import cv2
from gensim.test.utils import common_texts, get_tmpfile
from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence
import numpy as np
import math
import wordcloud
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer


def classift_dic():
    data = '剧情 喜剧 动作 爱情 科幻 动画 悬疑 惊悚 恐怖 犯罪 同性 音乐 歌舞 传记 历史 战争 西部 奇幻 冒险 灾难 武侠 情色 古装'.split()
    count = 0
    dic = {}
    for i in data:
        dic[i] = count
        count += 1
    return dic


def get_movieType(movieName):
    database = json.loads(open('database.json').read())
    open('database.json').close()
    for i in database:
        if i['title'] == movieName:
            return i['movieType']
    raise ValueError


def recomand(movieName):
    res = []
    movieType = get_movieType(movieName)
    database = json.loads(open('database.json').read())
    open('database.json').close()
    dic = classift_dic()
    vector_raw = [0 for i in dic]
    for i in movieType:
        vector_raw[dic[i]] += 1
    for j in database:
        vector = [0 for i in dic]
        for key in j['movieType']:
            vector[dic[key]] += 1
        if get_sim(vector_raw, vector) > 0.7:
            res.append(j)
    return res


def get_sim(s1, s2):
    if len(s1) != len(s2):
        raise ValueError
    r1 = 0
    r2 = 0
    r3 = 0
    for i in s1:
        r1 += pow(i, 2)
    r1 = pow(r1, 0.5)
    for i in s2:
        r2 += pow(i, 2)
    r2 = pow(r2, 0.5)
    for i in range(len(s1)):
        r3 += s1[i]*s2[i]
    return r3/(r1*r2)


def getdata():
    header = {'Accept': '*/*',
              'Accept-Language': 'zh-CN,en-US;q=0.7,en;q=0.3',
              'Referer': 'https://movie.douban.com/',
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0'

              }
    count = 0
    if not os.path.exists('a.json'):
        tmp = requests.get(
            'https://movie.douban.com/j/search_subjects?type=movie&tag=%E7%83%AD%E9%97%A8&page_limit=50&page_start=0', headers=header).content
        # charset = chardet.detect(tmp)['encoding']
        # print (charset)
        with open('a.json', 'wb') as f:
            f.write(tmp)
    with open('a.json', 'r', encoding='utf8') as f:
        data = json.loads(f.read())['subjects']
    pos_data = ''
    neg_data = ''
    movie_list = []
    while count < 50:
        a = open('{}.html'.format(str(count)), encoding='utf8').read()
        open('{}.html'.format(str(count))).close()
        pos = ['还行', '推荐', '力荐']
        neg = ['较差', '很差']
        html = etree.HTML(a, etree.HTMLParser())
        res = html.xpath(
            '//span[@class="comment-info"]/span[@class!="comment-time "]/@title')
        res1 = html.xpath('//span[@class="short"]/text()')

        movie_list.append(
            {'title': data[count]['title'], 'rate': data[count]['rate'], 'comment': [res, res1]})
        for i in range(len(res)):
            if res[i] in pos:
                pos_data += res1[i].strip()+'\n'
            else:
                neg_data += res1[i].strip()+'\n'
        count += 1
    open('b.json', 'w', encoding='utf8').write(json.dumps(movie_list))
    open('pos.txt', 'w', encoding='utf8').write(pos_data)
    open('neg.txt', 'w', encoding='utf8').write(neg_data)
    open('b.json').close()
    open('pos.txt').close()
    open('neg.txt').close()


def snowpos(data):
    # s = snownlp.sentiment.train('neg.txt', 'pos.txt')
    # snownlp.sentiment.save('sentiment.marshal')
    res = snownlp.SnowNLP(data).sentiments
    print(res)
    return res


def get_data_summary(urllist):
    header = {'Accept': '*/*',
              'Accept-Language': 'zh-CN,en-US;q=0.7,en;q=0.3',
              'Referer': 'https://movie.douban.com/',
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0'

              }
    if not os.path.exists('c.json'):
        res = []
        for i in urllist:
            tmp = requests.get(i, headers=header).text
            html = etree.HTML(tmp, etree.HTMLParser())
            name = html.xpath('//title/text()')[0].replace('(豆瓣)', '').strip()
            movieType = html.xpath('//span[@property="v:genre"]/text()')
            res.append({'title': name, 'movieType': movieType})
        with open('c.json', 'w+') as f:
            f.write(json.dumps(res))
# data=open('summary.html',encoding='utf8').read()
# html = etree.HTML(data, etree.HTMLParser())
# print()


def MakeCloud(data):
    data = cal_tfidf(data)
    mask_img = np.array(cv2.imread("c1.jpg"))
    font = r'msyh.ttf'
    wc = wordcloud.WordCloud(
        background_color="white",  # 设置背景颜色，与图片的背景色相关
        mask=mask_img,  # 设置背景图片
        collocations=False,
        font_path=font,  # 显示中文，可以更换字体
        max_font_size=4000,  # 设置字体最大值
        random_state=1,  # 设置有多少种随机生成状态，即有多少种配色方案
        width=1600,
        margin=0).generate(data)
    plt.imshow(wc)
    #image_colors = ImageColorGenerator(mask_img)
    # plt.imshow(wc.recolor(color_func=image_colors))
    plt.axis('off')  # 隐藏图像坐标轴
    plt.show()  # 展示图片


def cal_tfidf(data):
    data = re.sub('[^\u4e00-\u9fa5]', '', data)
    ban_word = open('ban_word.txt', encoding='utf8').read().split('\n')
    res1 = ' '.join(jieba.lcut(data))
    corpus = [res1]
    vector = TfidfVectorizer(stop_words=ban_word)
    tfidf = vector.fit_transform(corpus)
    res_dic = {}
    wordlist = vector.get_feature_names()
    weightlist = tfidf.toarray()
    for i in range(len(weightlist)):
        for j in range(len(wordlist)):
            res_dic[wordlist[j]] = weightlist[i][j]
    d_order = sorted(res_dic.items(), key=lambda x: x[1], reverse=True)[:30]
    ResData = ''
    for i in d_order:
        ResData += (i[0]+' ')*math.floor(i[1]*100)
    return ResData


# pprint(recomand('调音师'))
# MakeCloud(data)
lst = ['打丧尸永远这种配置，一个狠人，一个二逼，一个辣妹，一个傻白甜，一个任性作死鬼，一个暗搓搓的不明人物，一个特别作用的人……',
       '我猜，导演把智商分了一点给僵尸吧',
       '剧情属实有够俗套的，模板的不能再模板的剧情套路，期待了一整场的大电锯，最后居然只是用来锯墙？？？勉勉强强给个三星 ，希望不要再无脑尬吹！',
       '扎导是不是不会拍2个小时的电影...',
       ' 不愧是奈飞，花重金告诉华纳他们失去了一个鬼才',
       '大肌肉老爹+作死小公主+暗恋中年妇女，狂锯黑佬+叨逼小哥，偷渡犯+祭品保安，没心没肺网红情侣+神经质女飞机，自己骂自己的小日本+老色批安保官，无妄之灾的尸王和瞎嘚瑟怀孕媳妇，嗯！就这些了',
       '一般般，期待导演剪辑版哈哈',
       '不愧是奈飞，花重金告诉华纳他们失去了一个鬼才',
       '扎导一定自以为很屌',
       '本以为是扎导在脱离大片厂限制后放飞自我的丧尸爽片（事实上也有很多对丧尸题材设定拓展的细节），没想到竟然是一部饱含深情、写满了对亡女怀念和作为父亲的自责的私密之作，也难怪这次扎导会亲自掌镜，想想还真是挺浪漫的']





score = 0
for i in lst:
    score += snowpos(i)
print(score)

