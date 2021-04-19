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
from sklearn.feature_extraction.text import TfidfVectorizer
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

classifiers = [
    KNeighborsClassifier(),
    SVC(kernel="linear", C=0.025),
    SVC(gamma=2, C=1),
    GaussianProcessClassifier(1.0 * RBF(1.0)),
    DecisionTreeClassifier(max_depth=5),
    RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1),
    MLPClassifier(alpha=1, max_iter=1000),
    AdaBoostClassifier(),
    GaussianNB(),
    QuadraticDiscriminantAnalysis()]


def cal_tfidf(data):
    res1 = ' '.join(jieba.lcut(data))
    corpus = [res1]
    vector = TfidfVectorizer(stop_words=ban_word)
    try:
        tfidf = vector.fit_transform(corpus)
    except:
        return 0
    return res1
    
def GetData(FileDir='./tc-corpus-answer/answer'):
    global ban_word
    TmpX=[]
    XResList = []
    YResList = []
    DirList = os.listdir(FileDir)
    count=0
    for i in tqdm.tqdm(DirList):
        TmpPath = FileDir+'/'+i
        print(TmpPath)
        for j in tqdm.tqdm(os.listdir(TmpPath)):
            with open((TmpPath+'/'+j), 'rb') as f:
                charset = chardet.detect(f.read())['encoding']
            with open((TmpPath+'/'+j), encoding=charset, errors='ignore') as f:
                tmp=cal_tfidf(f.read())
                if tmp:
                    TmpX.append(tmp)
                    YResList.append(int(re.findall('C(\d+)-', i)[0]))
    vector = TfidfVectorizer(stop_words=ban_word)
    tfidf = vector.fit_transform(TmpX)
    X_train, X_test, y_train, y_test = \
    train_test_split(tfidf, YResList, random_state=42)
    test=KNeighborsClassifier()
    print('*'*100)
    print('开始训练')
    print('*'*100)
    test.fit(X_train, y_train)
    print('预测')
    y_pred = test.predict(X_test)
    print(classification_report(y_test, y_pred))
    return 0

def TextCluster(FileDir='./tc-corpus-answer/answer'):
    global ban_word
    TmpX=[]
    XResList = []
    YResList = []
    DirList = os.listdir(FileDir)
    count=0
    for i in tqdm.tqdm(DirList):
        TmpPath = FileDir+'/'+i
        print(TmpPath)
        for j in tqdm.tqdm(os.listdir(TmpPath)):
            with open((TmpPath+'/'+j), 'rb') as f:
                charset = chardet.detect(f.read())['encoding']
            with open((TmpPath+'/'+j), encoding=charset, errors='ignore') as f:
                data=f.read()
                data=re.sub('[^\u4e00-\u9fa5]','',data)
                tmp=cal_tfidf(data)
                if tmp:
                    vector = TfidfVectorizer(stop_words=ban_word)
                    tfidf = vector.fit_transform([tmp])
                    res_dic = {}
                    wordlist = vector.get_feature_names()
                    weightlist = tfidf.toarray()
                    for ite1 in range(len(weightlist)):
                        for ite2 in range(len(wordlist)):
                            res_dic[wordlist[ite2]] = weightlist[ite1][ite2]
                    d_order = sorted(res_dic.items(), key=lambda x: x[1], reverse=True)[0:50]
                    TmpList=[]
                    for ite in d_order:
                        TmpList.append(ite[0])
                    XResList.append(' '.join(TmpList))
                    YResList.append(int(re.findall('C(\d+)-', i)[0]))
    vectorizer = TfidfVectorizer(max_features = 8000)
    X = vectorizer.fit_transform(XResList)
    X_train, X_test, y_train, y_test = \
    train_test_split(X, YResList, random_state=42)
    km = KMeans(n_clusters=20, init='k-means++', max_iter=300, n_init=1, verbose=False)
    km.fit(X_train)
    y_pred=km.predict(X_test)


    with open('./kmeans.pickle', 'wb') as f:
        pickle.dump(km, f)
    print("利用Kmeans聚类结果如下:")
    # print(calinski_harabasz_score(X,km))
    print(adjusted_mutual_info_score(y_test,y_pred))
    order_centroids = km.cluster_centers_.argsort()[:, ::-1]
    terms = vectorizer.get_feature_names()
    Cluster_Result_predict=[]
    for i in range(20):
        print("Cluster",i+1,":", end='')
        words=[]
        for ind in order_centroids[i, :30]:
            print(' %s' % terms[ind], end='')
            words.append(terms[ind])
        Cluster_Result_predict.append(' '.join(words))
        print()
    
    print(Cluster_Result_predict)

# def Kmeans_Cluster(FileContent):
#     ALL_text = []
#     for i in FileContent:
#         for j in i:
#             ALL_text.append(j)
#     ALL_text = [' '.join(i) for i in ALL_text]
#     vetor = TfidfVectorizer(max_features=5000)
#     tfidf = vetor.fit_transform(ALL_text)
#     weight = tfidf.toarray()
#     km = KMeans(n_clusters=20, init='k-means++', max_iter=300, n_init=1, verbose=False)
#     s = km.fit(weight)
#     print("利用Kmeans聚类结果如下:")
#     order_centroids = km.cluster_centers_.argsort()[:, ::-1]
#     terms = vetor.get_feature_names()
#     Cluster_Result_predict=[]
#     for i in range(20):
#         print("Cluster",i+1,":", end='')
#         words=[]
#         for ind in order_centroids[i, :30]:
#             print(' %s' % terms[ind], end='')
#             words.append(terms[ind])
#         Cluster_Result_predict.append(' '.join(words))
#         print()
#     return Cluster_Result_predict
def cal_tfidf1(data):
    res1 = ' '.join(jieba.lcut(data))
    corpus = [res1]
    vector = TfidfVectorizer(max_features = 8000,stop_words=ban_word)
    tfidf = vector.fit_transform(corpus)
    return tfidf
    # res_dic = {}
    # wordlist = vector.get_feature_names()
    # weightlist = tfidf.toarray()
    # for i in range(len(weightlist)):
    #     print("-------在"+name+"中第", i, "段评论的词语 tf-idf 权重------")
    #     for j in range(len(wordlist)):
    #         res_dic[wordlist[j]] = weightlist[i][j]
    # d_order = sorted(res_dic.items(), key=lambda x: x[1], reverse=True)[:50]
    # for i in d_order:
    
if __name__=='__main__':
    TextCluster()
    # with open("kmeans.pickle", 'rb') as f:
    #     model = pickle.load(f)
    # model.predict(cal_tfidf1(open('tc-corpus-answer\\answer\\C16-Electronics\\C16-Electronics46.txt','r',encoding='gbk').read()))
    

              precision    recall  f1-score   support			

           3       0.81      0.81      0.81       170
           4       0.00      0.00      0.00        11
           5       0.17      0.09      0.12        11
           6       0.38      0.43      0.40         7
           7       0.66      0.66      0.66       122
          11       0.97      0.92      0.95       173
          15       0.00      0.00      0.00         6
          16       0.00      0.00      0.00         7
          17       0.00      0.00      0.00         9
          19       0.96      0.96      0.96       338
          23       0.00      0.00      0.00        12
          29       0.80      0.40      0.53        20
          31       0.95      0.93      0.94       302
          32       0.93      0.92      0.92       278
          34       0.89      0.85      0.87       388
          35       0.33      0.29      0.31         7
          36       0.80      0.29      0.42        14
          37       0.50      0.06      0.11        17
          38       0.60      0.87      0.71       266
          39       0.93      0.91      0.92       300

    accuracy                           0.85      2458
   macro avg       0.53      0.47      0.48      2458
weighted avg       0.85      0.85      0.84      2458



              precision    recall  f1-score   support

           3       0.90      0.92      0.91       170
           4       0.00      0.00      0.00        11
           5       0.00      0.00      0.00        11
           6       0.50      0.14      0.22         7
           7       0.81      0.69      0.74       122
          11       0.94      0.89      0.91       173
          15       1.00      0.33      0.50         6
          16       1.00      0.29      0.44         7
          17       1.00      0.11      0.20         9
          19       0.93      0.99      0.96       338
          23       1.00      0.08      0.15        12
          29       0.91      0.50      0.65        20
          31       0.93      0.97      0.95       302
          32       0.95      0.94      0.94       278
          34       0.90      0.96      0.93       388
          35       0.75      0.43      0.55         7
          36       1.00      0.50      0.67        14
          37       0.86      0.35      0.50        17
          38       0.86      0.95      0.90       266
          39       0.90      0.96      0.93       300

    accuracy                           0.91      2458
   macro avg       0.81      0.55      0.60      2458
weighted avg       0.90      0.91      0.90      2458





              precision    recall  f1-score   support

           3       0.80      0.85      0.82       170
           4       1.00      0.18      0.31        11
           5       0.00      0.00      0.00        11
           6       0.50      0.14      0.22         7
           7       0.71      0.58      0.64       122
          11       0.88      0.82      0.85       173
          15       1.00      0.50      0.67         6
          16       1.00      0.29      0.44         7
          17       0.83      0.56      0.67         9
          19       0.91      0.95      0.93       338
          23       0.89      0.67      0.76        12
          29       1.00      0.50      0.67        20
          31       0.91      0.92      0.91       302
          32       0.87      0.89      0.88       278
          34       0.82      0.90      0.86       388
          35       0.75      0.86      0.80         7
          36       0.86      0.43      0.57        14
          37       0.67      0.35      0.46        17
          38       0.82      0.87      0.85       266
          39       0.91      0.94      0.93       300

    accuracy                           0.86      2458
   macro avg       0.81      0.61      0.66      2458
weighted avg       0.86      0.86      0.85      2458