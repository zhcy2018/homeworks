# -*- coding: utf-8 -*-
import re
import json
import redis
import jieba
from pprint import pprint
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer


def get_save_data():
    # pool = redis.ConnectionPool(host='192.168.31.150', port=6379, decode_responses=True)
    # r = redis.Redis(connection_pool=pool)
    pool = redis.ConnectionPool(
        host='127.0.0.1', port=6379, decode_responses=True)
    r = redis.Redis(connection_pool=pool)
    # r.lpush("list1", 11, 22, 33)
    data = (r.lrange('book_review1', 0, -1))
    dic = {}
    for i in data:
        tmp = json.loads(i)
        if(dic.__contains__(tmp['book_name'])):
            (dic[tmp['book_name']]).append(
                re.sub('<.*?>|</.*?>|&nbsp', '', tmp['review']))
        else:
            dic[tmp['book_name']] = [
                re.sub('<.*?>|</.*?>|&nbsp', '', tmp['review'])]
    store = json.dumps(dic)
    open('store_file.json', 'w+').write(store)


def cal_tfidf(key_list, name):
    res1 = ' '.join(jieba.lcut(key_list[0]))
    res2 = ' '.join(jieba.lcut(key_list[1]))
    corpus = [res1, res2]
    vector = TfidfVectorizer(stop_words=ban_word)
    tfidf = vector.fit_transform(corpus)
    res_dic = {}
    wordlist = vector.get_feature_names()
    weightlist = tfidf.toarray()
    for i in range(len(weightlist)):
        print("-------在"+name+"中第", i, "段评论的词语 tf-idf 权重------")
        for j in range(len(wordlist)):
            res_dic[wordlist[j]] = weightlist[i][j]
        d_order = sorted(res_dic.items(), key=lambda x: x[1], reverse=True)
        pprint(d_order[0:10])
        res_dic = {}


if __name__=='__main__':
    a = open('store_file.json').read()
    ban_word = open('ban_word.txt', encoding='utf8').read().split('\n')
    data = (json.loads(a))
    for i in data:
        cal_tfidf(data[i], i)
