import re
import os
import config
from pprint import pprint
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter
#from test import EmailData
import email
import matplotlib.pyplot as plt
import numpy as np
import tqdm
TrainProcess = 1
def add_number(rects):
	for i in rects:
		height=round(i.get_height(),2)
		plt.text(i.get_x()+i.get_width()/2,height,height,ha="center",va="bottom")

def EmailData(FilePath):
    fp = open(FilePath, "r", encoding='iso8859', errors='ignore')
    msg = email.message_from_file(fp)
    data = ''
    # 循环信件中的每一个mime的数据块
    for par in msg.walk():
        if not par.is_multipart():  # 这里要判断是否是multipart，是的话，里面的数据是无用的，至于为什么可以了解mime相关知识。
            name = par.get_param("name")  # 如果是附件，这里就会取出附件的文件名
            if name:
                pass
            #   #有附件
            #   # 下面的三行代码只是为了解码象=?gbk?Q?=CF=E0=C6=AC.rar?=这样的文件名
            #   h = email.Header.Header(name)
            #   dh = email.Header.decode_header(h)
            #   fname = dh[0][0]
            #   print ('附件名:', fname)
            #   data = par.get_payload(decode=True) #　解码出附件数据，然后存储到文件中

            #   try:
            #     f = open(fname, 'wb') #注意一定要用wb来打开文件，因为附件一般都是二进制文件
            #   except:
            #     print ('附件名有非法字符，自动换一个')
            #     f = open('aaaa', 'wb')
            #   f.write(data)
            #   f.close()
            else:
                # 不是附件，是文本内容
                data += (' '.join(re.sub('<.*?>|</.*?>|&nbsp|0x\d+|&deg|[a-z|\d]{15,}|\+|-', '',
                                         par.get_payload(decode=False), flags=re.S | re.I).split()))  # 解码出文本内容，直接输出来就可以了。
    fp.close()
    return data


def BayesClassifier():
    if os.path.exists('res.json'):
        os.remove('res.json')
    # HamSet = os.listdir(config.HamPath)
    # SpamSet = os.listdir(config.SpamPath)
    # PHamInAll = len(HamSet)/(len(HamSet)+len(SpamSet))
    # PSpamInall = 1-PHamInAll
    HamSet = []
    SpamSet = []
    with open('indecTrain') as f:
        Line = f.readline()
        while Line:
            TrainData = Line.split()
            if(TrainData[0][0].lower() == 's'):
                SpamSet.append(TrainData[1])
            else:
                HamSet.append(TrainData[1])
            Line = f.readline()
        print("读取完成")
    SpamVocabularyCounter = Counter()
    HamVocabularyCounter = Counter()
    HamVocabularyCounter = FileCounter(HamSet, config.HamPath)
    SpamVocabularyCounter = FileCounter(SpamSet, config.SpamPath)

    # with open('StopWords.txt') as f:
    #     ban_word = f.read().split()
    OnlyInHam = set(HamVocabularyCounter[0].keys(
    ))-set(SpamVocabularyCounter[0].keys())
    OnlyInSpam = set(SpamVocabularyCounter[0].keys(
    ))-set(HamVocabularyCounter[0].keys())
    CorrectHamNum = len(OnlyInSpam)+HamVocabularyCounter[1]
    CorrectSpamNum = len(OnlyInHam)+SpamVocabularyCounter[1]
    for i in OnlyInHam:
        SpamVocabularyCounter[0][i] = 1
    for i in OnlyInSpam:
        HamVocabularyCounter[0][i] = 1
    for i in HamVocabularyCounter[0]:
        HamVocabularyCounter[0][i] /= CorrectHamNum
    for i in SpamVocabularyCounter[0]:
        SpamVocabularyCounter[0][i] /= CorrectSpamNum
    # for i in ban_word:
    #     SpamVocabularyCounter.pop(i,'')
    #     HamVocabularyCounter.pop(i,'')
    print("训练完成")
    with open('res.json', 'w+') as f:
        f.write(json.dumps(
            [SpamVocabularyCounter[0], HamVocabularyCounter[0]]))


def FileCounter(FireDirList, FilePath):
    FileVocabularyCounter = Counter()
    FileVocabularyNum = 0
    # with open('StopWords.txt') as f:
    #     ban_word = f.read().split()
    for i in FireDirList:
        with open(i, 'r') as f:
            data = EmailData(i)
            data = re.sub('[^0-9a-z\-/+ \']', ' ', data, flags=re.I)
            FileVocabularyList = data.lower().strip().split()
            FileVocabularyCounter += Counter(FileVocabularyList)
        global TrainProcess
        print("已完成{}封邮件读取，邮件为{}".format(TrainProcess, i))
        TrainProcess += 1
    for i in ban_word:
        FileVocabularyCounter.pop(i, '')
    for i in FileVocabularyCounter:
        FileVocabularyNum += FileVocabularyCounter[i]
    return (FileVocabularyCounter, FileVocabularyNum)


def BayesClassifier1():
    if os.path.exists('res1.json'):
        os.remove('res1.json')
    HamSet = []
    SpamSet = []
    with open('indecTrain') as f:
        Line = f.readline()
        while Line:
            TrainData = Line.split()
            if(TrainData[0][0].lower() == 's'):
                SpamSet.append(TrainData[1])
            else:
                HamSet.append(TrainData[1])
            Line = f.readline()
        print("读取完成")

    # SpamVocabularyCounter = Counter()
    # HamVocabularyCounter = Counter()

    HamVocabularyCounter = FileCounter1(HamSet, config.HamPath)
    SpamVocabularyCounter = FileCounter1(SpamSet, config.SpamPath)
    ResCounter = Counter()
    # with open('StopWords.txt') as f:
    #     ban_word = f.read().split()
    OnlyInHam = set(HamVocabularyCounter[0].keys()) - \
        set(SpamVocabularyCounter[0].keys())
    OnlyInSpam = set(SpamVocabularyCounter[0].keys()) - \
        set(HamVocabularyCounter[0].keys())
    CorrectEmailNum = len(OnlyInHam)+HamVocabularyCounter[1]+len(OnlyInSpam)
    CorrectHamNum = len(OnlyInSpam)+HamVocabularyCounter[1]
    CorrectSpamNum = len(OnlyInHam)+SpamVocabularyCounter[1]
    PHamInAll = HamVocabularyCounter[1] / \
        (HamVocabularyCounter[1]+SpamVocabularyCounter[1])
    PSpamInall = 1-PHamInAll
    for i in OnlyInHam:
        SpamVocabularyCounter[0][i] = 1
    for i in OnlyInSpam:
        HamVocabularyCounter[0][i] = 1
    for i in SpamVocabularyCounter[0]:
        PWordSpam = SpamVocabularyCounter[0][i]/SpamVocabularyCounter[1]
        PWordHam = HamVocabularyCounter[0][i]/HamVocabularyCounter[1]
        ResCounter[i] = (PWordSpam) / \
            ((PWordHam*PHamInAll+PWordSpam*PSpamInall))
    d_order = sorted(SpamVocabularyCounter[0].items(), key=lambda x: x[1], reverse=True)[:-1]
    # pprint(d_order)
    SpamResDic = {}
    HamResDic={}
    for i in d_order:
        SpamResDic[i[0]] = ResCounter[i[0]]
    SpamResDic['spam_prob']=PSpamInall

    # for i in ban_word:
    #     SpamVocabularyCounter.pop(i,'')
    #     HamVocabularyCounter.pop(i,'')
    with open('res1.json', 'w+') as f:
        f.write(json.dumps(SpamResDic))


def FileCounter1(FireDirList, FilePath):
    FileVocabularyCounter = Counter()
    FileVocabularyNum = 0
    ResCounter = Counter()
    # with open('StopWords.txt') as f:
    #     ban_word = f.read().split()
    for i in tqdm.tqdm(FireDirList):
        with open(i, 'r') as f:
            data = EmailData(i)
            data = re.sub('[^0-9a-z\-/+ \']', ' ', data.lower(), flags=re.I)
            FileVocabularyList = list(set(data.lower().strip().split()))
            FileVocabularyCounter += Counter(FileVocabularyList)
        global TrainProcess
        #print("已完成{}封邮件读取，邮件为{}".format(TrainProcess, i))
        TrainProcess += 1
    FileVocabularyNum += len(FileVocabularyList)
    for i in ban_word:
        FileVocabularyCounter.pop(i, '')
    for i in FileVocabularyCounter:
        if FileVocabularyCounter[i] != 1 and len(i)>=3:
            FileVocabularyNum += FileVocabularyCounter[i]
            ResCounter[i] = FileVocabularyCounter[i]
    return (ResCounter, FileVocabularyNum)


def FileVocabularDfitf(FireDirList, FilePath):
    FileVocabularyCounter = Counter()
    FileVocabularyNum = 0
    data = ''
    for i in FireDirList:
        with open(FilePath+'/'+i, 'r') as f:
            data += f.read()
    # with open('StopWords.txt') as f:
    #     ban_word = f.read().split()
    copus = [data]

    vector = TfidfVectorizer(stop_words=ban_word)
    tfidf = vector.fit_transform(copus)
    res_dic = {}
    wordlist = vector.get_feature_names()
    weightlist = tfidf.toarray()
    for i in range(len(weightlist)):
        print("-------在中第", i, "段评论的词语 tf-idf 权重------")
        for j in range(len(wordlist)):
            res_dic[wordlist[j]] = weightlist[i][j]
        d_order = sorted(res_dic.items(), key=lambda x: x[1], reverse=True)
        pprint(d_order[0:15])
        res_dic = {}
    res_word = []
    for i in range(15):
        res_word.append(d_order[i][0])
    return res_word


def GetRes(FilePath,ham,spam):
    tmp = EmailData(FilePath)
    tmp = re.sub('[^0-9a-z\-/+ \']', ' ', tmp, flags=re.I).lower().split()
    # for i in ban_word:
    #     tmp.pop(i, '')
    count = 1
    for i in tmp:
        if spam.__contains__(i):
            var1 = spam[i]/ham[i]
            count *= var1
    if count > 1.356:
        return "Spam"
    else:
        return "ham"


# def GetRes1(FilePath):
#     tmp = EmailData(FilePath)

#     # f=open(FilePath,'r',errors='ignore')
#     # tmp=f.read()
#     # f.close()
#     tmp = re.sub('[^0-9a-z\-/+ \']', ' ', tmp, flags=re.I).lower().split()
#     count = 1
#     for i in tmp:
#         if ham.__contains__(i):
#             var1 = spam[i]/ham[i]
#             count *= var1
#     if count > 1000:
#         return "Spam"
#     else:
#         return "ham"
def GetRes1(FilePath,res):
    #print(FilePath)
    tmp = EmailData(FilePath)
    count=1
    flag=0
    tmp = ((re.sub('[^0-9a-z\-/+ \']', ' ', tmp, flags=re.I).lower().split()))
    # for i in ban_word:
    #     tmp.pop(i, '')
    # d_order = sorted(tmp.items(), key=lambda x: x[1], reverse=True)[:30]
    
    for i in tmp:
        # if len(i[0])>30:
        #     return ("Spam",9999)

        if spam.__contains__(i):
            count *= spam[i]
            # if spam[i]==1:
            #     count1=0.01
            # else:
            #     count1=1-spam[i]
            # res*=(spam[i]/count1)
            flag += 1   
    # res=count/count1
    # if len(tmp)>600:
    #     return ("ham",9999)
    count*=data['spam_prob']
    if count>1.3:
        return ("Spam",count)
    else:
        return ("ham",count)


def TestRes():
    count = 0
    TmpValue = 0
    count_flase=0
    count_flase1=0
    count_right=0
    count_right1=0
    TestNum=0
    f=open('res.json')
    data = json.loads(f.read())
    spam = data[0]
    ham = data[1]
    with open('indecTest') as f:
        Line = f.readline()
        while Line and TmpValue<10000:
            TestData = Line.split()
            GuessRes = GetRes(TestData[1],ham,spam)
            TmpValue += 1
            if GuessRes.lower() == TestData[0].lower():
                count += 1
                if(TestData[0].lower()=='spam'):
                    count_right+=1  #tp
                else:
                    count_right1+=1
               # print("预测结果为{}正确".format(TestData[0]))
            #     if(count % 1000 == 0):
            #         print("预测准确率为{}".format(str(count/TmpValue)))
            # else:
            #     pass
               # print("预测结果为{},但真实结果为{}".format(GuessRes,TestData[0]))
            else:
                if(TestData[0].lower()=='spam' ):
                    count_flase+=1      #fn
                else:
                    count_flase1+=1
            Line = f.readline()
        #print("预测准确率为{}".format(str(count/TmpValue)))
        accuracy=count/TmpValue
        recall=count_right/(count_right+count_flase)
        precision=count_right/(count_right+count_flase1)
        Fmeansure=2*precision*recall/(precision+recall)
        print("accuracy: {}".format(str(accuracy)))
        print("recall: {}".format(str(recall)))
        print("precision: {}".format(str(precision)))
        print("f-meansure: {}".format(str(Fmeansure)))
        ResList=[accuracy,recall,precision,Fmeansure]
        NameList=['accuracy','recall','precision','f-meansure']
        a=plt.bar([0,1,2,3],ResList,tick_label=NameList)
        add_number(a)
        # plt.show()


def TestRes1():
    x=[]
    y=[]
    count = 0
    TmpValue = 0
    count_flase=0
    count_flase1=0
    count_right=0
    count_right1=0
    with open('indecTest') as f:
        Line = f.readline()
        while Line and TmpValue<10000:
            TestData = Line.split()
            GuessRes = GetRes1(TestData[1],TestData[0])
            TmpValue += 1
            if GuessRes[0].lower() == TestData[0].lower():
                count += 1
                if(TestData[0].lower()=='spam'):
                    count_right+=1  #tp
                else:
                    count_right1+=1

               # print("预测结果为{}正确".format(TestData[0]))
            #     if(count % 1000 == 0):
            #         print("预测准确率为{}".format(str(count/TmpValue)))
            #         # return (count/TmpValue)
            #         pass
            # else:
            #     pass
                #print(TestData[1])
            else:
                if(TestData[0].lower()=='spam' ):
                    count_flase+=1      #fn
                else:
                    count_flase1+=1     #fp
                #print(GuessRes[1])
                #print("预测结果为{},但真实结果为{}".format(GuessRes,TestData[0]))
                # break
            if count_right>0:
                x.append(count_right/(count_right+count_flase))
                y.append(count_right/(count_right+count_flase1))
            Line = f.readline()
        plt.plot(x,y)
        plt.show()
        accuracy=count/TmpValue
        recall=count_right/(count_right+count_flase)
        precision=count_right/(count_right+count_flase1)
        Fmeansure=2*precision*recall/(precision+recall)
        print("accuracy: {}".format(str(accuracy)))
        print("recall: {}".format(str(recall)))
        print("precision: {}".format(str(precision)))
        print("f-meansure: {}".format(str(Fmeansure)))
        ResList=[accuracy,recall,precision,Fmeansure]
        NameList=['accuracy','recall','precision','f-meansure']
        a=plt.bar([0,1,2,3],ResList,tick_label=NameList)
        add_number(a)
        # plt.show()

    return count/TmpValue


if __name__ == '__main__':
    #    wordlist=FileVocabularDfitf(os.listdir(config.SpamPath),config.SpamPath)
    with open('StopWords.txt') as f:
        ban_word = f.read().split()
    #BayesClassifier1()
    #     data = json.loads(f.read())
    #     spam = data[0]
    #     ham = data[1]
    # TestRes()
    x = np.arange(0.98, 1, 0.001)
    # print(x)
    y = []
    with open('res1.json') as f:
        data = json.loads(f.read())
    # for j in tqdm.tqdm(x):
    #     spam={}
    #     for i in data:
    #         if data[i]>=j:
    #             spam[i]=data[i]
    #     y.append(TestRes1())
    # plt.plot(x,y)
    # plt.show()
    # pprint(y)
    # print(np.max(y))
    spam = {}
    d_order = sorted(data.items(), key=lambda x: x[1], reverse=True)[:3000]
    #pprint(d_order)
    for i in d_order:
        spam[i[0]]=i[1]
    spam['spam_prob']=data['spam_prob']
    # #spam=data
    # print(d_order[-1])
    import time
    time1=time.time()
    TestRes1()
    time2=time.time()
    print("*"*100)
    TestRes()
    time3=time.time()
    print(time2-time1)
    print(time3-time2)
