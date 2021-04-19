from lxml import etree
import os
import json
import pprint
import jieba
import jieba.posseg as pseg
from sklearn.feature_extraction.text import TfidfVectorizer
import requests
import tqdm
import math
import csv
import numpy as np
import wordcloud
import matplotlib.pyplot as plt
import re
import cv2
from gensim.test.utils import common_texts, get_tmpfile
from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence

stopwords = ['吕州', '林城', '银行卡', '明白', '白云', '嗡嗡嘤嘤',
             '阴云密布', '雷声', '陈大', '谢谢您', '安置费', '任重道远',
             '孤鹰岭', '阿庆嫂', '岳飞', '师生', '养老院', '段子', '老总']
replace_words = {'师母': '吴慧芬', '陈老': '陈岩石', '老赵': '赵德汉', '达康': '李达康', '高总': '高小琴',
                 '猴子': '侯亮平', '老郑': '郑西坡', '小艾': '钟小艾', '老师': '高育良', '同伟': '祁同伟',
                 '赵公子': '赵瑞龙', '郑乾': '郑胜利', '孙书记': '孙连城', '赵总': '赵瑞龙', '昌明': '季昌明',
                 '沙书记': '沙瑞金', '郑董': '郑胜利', '宝宝': '张宝宝', '小高': '高小凤', '老高': '高育良',
                 '伯仲': '杜伯仲', '老杜': '杜伯仲', '老肖': '肖钢玉', '刘总': '刘新建', "美女老总": "高小琴"}
names = {}  # 姓名字典
relationships = {}  # 关系字典
lineNames = []  # 每段内人物的关系
node = []  # 存放处理后的人物


def get_data():
    if not os.path.exists('data.json'):
        if not os.path.exists('a.html'):
            data = requests.get(
                'https://baike.baidu.com/item/%E4%BA%BA%E6%B0%91%E7%9A%84%E5%90%8D%E4%B9%89/17545218#%E5%88%86%E9%9B%86%E5%89%A7%E6%83%85').text
            open('a.html', 'w+').write(data)
            open('a.html').close()
        html = etree.parse('a.html', etree.HTMLParser())
        story = []
        for i in html.xpath("//ul[@id='dramaSerialList']//dd"):
            story.append(''.join(i.xpath('.//p/text()')))
        name = html.xpath("//ul[@id='dramaSerialList']//dt/span/text()")
        ResDic = {}
        for i in range(len(story)):
            ResDic[name[i]] = story[i]
        open('data.json', 'w+').write(json.dumps(ResDic))
        open('data.json').close()
        return ResDic
    else:
        ResDic = json.loads(open('data.json').read())
        open('data.json').close()
        return ResDic


def getLine():
    data = get_data()
    ResList = []
    for key in data:
        tmp = data[key].split('。')
        ResList += tmp
    return ResList


def read_txt():  # 读取剧作并分词
    # 加载人物字典(注意这个文件要用utf-8编码，可以使用sublime进行转换为utf-8编码)
    jieba.load_userdict("name.txt")
    # f=codecs.open(path,'r') #读取剧作,并将其转换为utf-8编码
    LineList = getLine()
    print('词句加载完成')
    for line in tqdm.tqdm(LineList):
        poss = pseg.cut(line)  # 分词并返回该词词形
        lineNames.append([])  # 为新读入的一段添加人物名称列表
        for w in poss:
            if w.word in stopwords:  # 去掉某些停用词
                continue
            if w.flag != "nr" or len(w.word) < 2:
                if w.word not in replace_words:
                    continue
            if w.word in replace_words:  # 将某些在文中人物的昵称替换成正式的名字
                w.word = replace_words[w.word]
            lineNames[-1].append(w.word)  # 为当前段增加一个人物
            if names.get(w.word) is None:  # 如果这个名字从来没出现过，初始化这个名字
                names[w.word] = 0
                relationships[w.word] = {}
            names[w.word] += 1  # 该人物出现次数加1
    for line in lineNames:  # 通过对于每一段段内关系的累加，得到在整篇小说中的关系
        for name1 in line:
            for name2 in line:
                if name1 == name2:
                    continue
                # 如果没有出现过两者之间的关系，则新建项
                if relationships[name1].get(name2) is None:
                    relationships[name1][name2] = 1
                else:
                    relationships[name1][name2] += 1  # 如果两个人已经出现过，则亲密度加1


def write_csv():
    # 在windows这种使用\r\n的系统里，不用newline=‘’的话
    # 会自动在行尾多添加个\r，导致多出一个空行，即行尾为\r\r\n
    csv_edge_file = open("edge.csv", "w+", newline="")
    writer = csv.writer(csv_edge_file)
    # 先写入列名,"type"为生成无向图做准备
    writer.writerow(["source", "target", "weight", "type"])
    for name, edges in relationships.items():
        for v, w in edges.items():
            if w > 20:
                node.append(name)
                writer.writerow((name, v, str(w), "undirected"))  # 按行写入数据
    csv_edge_file.close()
    # 生成node文件
    s = set(node)
    csv_node_file = open("node.csv", "w", newline="")
    wnode = csv.writer(csv_node_file)
    wnode.writerow(["ID", "Label", "Weight"])
    for name, times in names.items():
        if name in s:
            wnode.writerow((name, name, str(times)))
    csv_node_file.close()


def cal_tfidf(data):
    data = re.sub('[^\u4e00-\u9fa5]', '', data)
    ban_word = open('ban_word.txt', encoding='utf8').read().split('\n')
    jieba.load_userdict("name.txt")
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
    d_order = sorted(res_dic.items(), key=lambda x: x[1], reverse=True)[:50]
    ResData = ''
    for i in d_order:
        # if i[0]=='大风':
        #     ResData+=('大风厂'+' ')*math.floor(i[1]*100)
        # else:
        ResData += (i[0]+' ')*math.floor(i[1]*100)
    return ResData


def MakeCloud():
    LineList = get_data()
    data = ''.join(LineList)
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


def w2v():
    jieba.load_userdict("name.txt")
    ban_word = open('ban_word.txt', encoding='utf8').read().split('\n')
    LineList = get_data()
    data = ''.join(LineList)
    
    data = re.sub('[^\u4e00-\u9fa5]', '', data)
    DataList = [word for word in jieba.lcut(data) if word not in ban_word]
    tmplst=[]
    reslst=[]
    LineList=getLine()
    for i in LineList:
        tmp=re.sub('[^\u4e00-\u9fa5]', '', i)
        tmplst=[word for word in jieba.lcut(data) if word not in ban_word]
        reslst.append(tmplst)
    NewData = ' '.join(DataList)

    #sentences = LineSentence(NewData)

# 训练模型
    model = Word2Vec(reslst, hs=1,min_count=1,window=10)

    # 保存模型
    model_file = 'model.w2v'
    model.save(model_file)
def MakeCloud1():
    model = Word2Vec.load('model.w2v')
    tmp=(model.wv.most_similar(u'大风厂',topn=50))
    ResData=''
    for i in tmp:
        # if i[0]=='大风':
        #     ResData+=('大风厂'+' ')*math.floor(i[1]*100)
        # else:
        ResData += (i[0]+' ')*math.floor(i[1]*100)
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
        margin=0).generate(ResData)
    plt.imshow(wc)
    #image_colors = ImageColorGenerator(mask_img)
    # plt.imshow(wc.recolor(color_func=image_colors))
    plt.axis('off')  # 隐藏图像坐标轴
    plt.show()  # 展示图片
if __name__ == '__main__':
    # edge_file="edge.txt"
    # read_txt()
    # write_csv()
    #w2v()
    MakeCloud1()

