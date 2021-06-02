from itertools import count
import string
from sys import modules
from paddle.fluid import dataset
import pandas
import openccpy
from collections import Counter
import snownlp
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import make_moons, make_circles, make_classification
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import classification_report
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from Crypto.Util.number import bytes_to_long as b2l, long_to_bytes as l2b
from sklearn.metrics import adjusted_mutual_info_score
import pickle
import os
import re
import tqdm
import jieba
import json
import chardet


ban_word = open('ban_word.txt', encoding='utf8').read().split('\n')
# with open('./dataset/clean_weibo_text.csv','rb') as f:
#     charset = chardet.detect(f.read())['encoding']
# print(charset)
# a=pandas.read_csv('./dataset/clean_weibo_text.csv',encoding='utf-8')
# s=snownlp.SnowNLP
# print(s(a.text[188886]).sentiments)
# lst1=['','','','']
# count=0

# with open('./dataset/clean_weibo_text.csv',encoding='utf-8',errors='ignore') as f:
#     line=f.readline()
#     line=f.readline()
#     while line:
#         tmp=line.split(',')
#         lst1[int(tmp[0])]+=tmp[1]
#         line=f.readline()
#         count+=1
#         if count%1000==0:
#             print(count/265434)

# open('ht.txt','w+').write(lst1[0])
# open('at.txt','w+').write(lst1[1])
# open('dt.txt','w+').write(lst1[2])
# open('st.txt','w+').write(lst1[3])


s = snownlp.sentiment.train('ht.txt', 'dt.txt')
snownlp.sentiment.save('sentiment.marshal')


def SnowAn():
    s = snownlp.SnowNLP
    count = 0
    right = 0
    with open('./hotel.txt', encoding='utf-8', errors='ignore') as f:
        line = f.readline()
        line = f.readline()
        while line:
            count += 1
            tmp = line.split(',')
            if s(tmp[1]).sentiments > 0.4:
                num = 0
            else:
                num = 1
            if str(num) == tmp[0]:
                right += 1
            line = f.readline()
    print(right/count)


# SnowAn()


class Bclassfier():
    def __init__(self, train_text=None, train_lable=None, module=None, threshold=1) -> None:
        if len(train_text) != len(train_lable):
            raise ValueError
        self.train_text = train_text
        self.train_lable = train_lable
        self.module = module
        self.min = 1
        self.threshold = threshold
        print('initialized')

    def get_min(self):
        for i in self.module:
            tmp_min = i[min(i,  key=lambda key: i[key])]
            if self.min > tmp_min:
                self.min = tmp_min

    def string_pre(self, string):
        self.get_min()
        count = [1 for i in range(len(self.module))]
        res1 = [word for word in jieba.lcut(string) if word not in ban_word]
        for i in res1:
            for j in range(len(self.module)):
                count[j] *= self.module[j].get(i, self.min)
        res = count.index(max(count))
        return res

    def predict(self, dataset):
        if type(dataset) == str:
            return self.string_pre(dataset)
        elif type(dataset) == list:
            tmp_list = []
            for i in tqdm.tqdm(dataset):
                tmp_list.append(self.string_pre(i))
            return tmp_list
        else:
            raise TypeError

    def accuracy(self, dataset, lable):
        length = len(lable)
        if len(lable) != len(dataset):
            raise ValueError
        tmp_list = self.predict(dataset)
        count = 0
        for i in range(len(tmp_list)):
            if tmp_list[i] == lable[i]:
                count += 1
        return count/length

    def get_allnum(self, counterdata):
        count = 0
        for i in counterdata:
            count += counterdata[i]
        return count

    def train(self):
        self.module = []
        self.lable_dic = {}
        print('training...')
        for i in tqdm.tqdm(range(len(self.train_text))):
            if self.lable_dic.get(self.train_lable[i]) == None:
                self.lable_dic[self.train_lable[i]] = i
                self.module.append(Counter())
            for j in tqdm.tqdm(self.train_text[i]):
                self.module[i] += Counter([word for word in jieba.lcut(j)
                                           if word not in ban_word])
            all_num = self.get_allnum(self.module[i])
            for word in self.module[i]:
                self.module[i][word] = self.module[i][word]/all_num

    def save(self, filename='module.json'):
        f = open(filename, 'w+')
        f.write(json.dumps(self.module))
        f.close()

    def load(self, filename='module.json'):
        f = open(filename)
        self.module = json.loads(f.read())
        f.close()


# with open('pos.txt',encoding='utf8',errors='ignore') as f:
#     data1=f.read()
# with open('neg.txt',encoding='utf8',errors='ignore') as f:
#     data2=f.read()
# tmp_lst=[data1.split('\n'),data2.split('\n')]
# a=Bclassfier(tmp_lst,['pos','neg'])
# a.train()
# a.save()
# a.load()
# lst1=open('pos1.txt',encoding='utf8',errors='ignore').read().split('\n')
# lst4=[0 for i in lst1]
# lst2=open('neg1.txt',encoding='utf8',errors='ignore').read().split('\n')
# lst5=[1 for i in lst2]
# lst3=lst1+lst2
# lst6=lst4+lst5
# print(a.accuracy(lst3,lst6))


def handle_testset(filename):
    tmp_list = []
    tmp_list1 = []
    count = 0
    for i in filename:
        tmp = open(i, encoding='utf8', errors='ignore').read().split('\n')
        tmp_list += tmp
        tmp_list1 += [count for i in tmp]
        count += 1
    return tmp_list, tmp_list1


def handle_trainset(filename):
    tmp_list = []
    tmp_list1 = []
    count = 0
    for i in filename:
        tmp_list.append(
            open(i, encoding='utf8', errors='ignore').read().split('\n'))
        open(i, encoding='utf8', errors='ignore').close()
        tmp_list1.append(count)
        count += 1
    return tmp_list, tmp_list1


a, b = handle_trainset(['at.txt', 'dt.txt', 'ht.txt', 'st.txt'])
s = Bclassfier(a, b)
# s.train()
# s.save()
s.load()
c, d = handle_testset(['at_t.txt', 'dt_t.txt', 'ht_t.txt', 'st_t.txt'])
print(s.accuracy(c, d))


# print(s('萨摩耶 适合 陪伴 星座 宠物狗 看看 喜欢 白羊座 熊 金牛座 萨摩耶 双子座 松狮 巨蟹座 博美 狮子 苏格兰 牧羊犬 处女座 金毛 天秤座 哈士奇 天蝎座 阿拉斯加 雪橇犬 射手座 吉娃娃 摩羯座 藏獒 水瓶座 德国 牧羊犬 双鱼座 拉布拉多').sentiments)
