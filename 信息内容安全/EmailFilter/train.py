import re
import os
import config
from pprint import pprint
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter
#from test import EmailData
import email

TrainProcess = 1


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
                data += (' '.join(re.sub('<.*?>|</.*?>|&nbsp|0x\d+|&deg', '',
                                         par.get_payload(decode=False), flags=re.S).split()))  # 解码出文本内容，直接输出来就可以了。
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
    CorrectHamNum = len(OnlyInHam)+HamVocabularyCounter[1]
    CorrectSpamNum = len(OnlyInSpam)+SpamVocabularyCounter[1]
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


def BayesClassifier1():
    if os.path.exists('res.json'):
        os.remove('res.json')
    HamSet = os.listdir(config.HamPath)
    SpamSet = os.listdir(config.SpamPath)
    PHamInAll = len(HamSet)/(len(HamSet)+len(SpamSet))
    PSpamInall = 1-PHamInAll
    SpamVocabularyCounter = Counter()
    HamVocabularyCounter = Counter()
    HamVocabularyCounter = FileCounter1(HamSet, config.HamPath)
    SpamVocabularyCounter = FileCounter1(SpamSet, config.SpamPath)

    # with open('StopWords.txt') as f:
    #     ban_word = f.read().split()
    OnlyInHam = set(HamVocabularyCounter.keys()) - \
        set(SpamVocabularyCounter.keys())
    OnlyInSpam = set(SpamVocabularyCounter.keys()) - \
        set(HamVocabularyCounter.keys())
    # CorrectHamNum=len(OnlyInHam)+HamVocabularyCounter[1]
    # CorrectSpamNum=len(OnlyInSpam)+SpamVocabularyCounter[1]
    for i in OnlyInHam:
        SpamVocabularyCounter[i] = 1/len(SpamSet)
    for i in OnlyInSpam:
        HamVocabularyCounter[i] = 1/len(HamSet)
    # for i in ban_word:
    #     SpamVocabularyCounter.pop(i,'')
    #     HamVocabularyCounter.pop(i,'')
    with open('res.json', 'w+') as f:
        f.write(json.dumps([SpamVocabularyCounter, HamVocabularyCounter]))


def FileCounter(FireDirList, FilePath):
    FileVocabularyCounter = Counter()
    FileVocabularyNum = 0
    with open('StopWords.txt') as f:
        ban_word = f.read().split()
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


def FileCounter1(FireDirList, FilePath):
    FileVocabularyCounter = Counter()
    FileVocabularyNum = 0
    with open('StopWords.txt') as f:
        ban_word = f.read().split()
    for i in FireDirList:
        with open(FilePath+'/'+i, 'r') as f:
            data = re.sub('[^0-9a-z\-/+ \']', ' ', f.read(), flags=re.I)
            FileVocabularyList = list(set(data.strip().split()))
            FileVocabularyCounter += Counter(FileVocabularyList)
    for i in ban_word:
        FileVocabularyCounter.pop(i, '')
    return FileVocabularyCounter


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


def GetRes(FilePath):
    tmp = EmailData(FilePath)

    # f=open(FilePath,'r',errors='ignore')
    # tmp=f.read()
    # f.close()
    tmp = re.sub('[^0-9a-z\-/+ \']', ' ', tmp, flags=re.I).lower().split()
    count = 1
    for i in tmp:
        if ham.__contains__(i):
            var1 = spam[i]/ham[i]
            count *= var1
    if count > 1000:
        return "Spam"
    else:
        return "ham"


def TestRes_1(FilePath):
    # tmp=EmailData(FilePath)

    f = open(FilePath, 'r', errors='ignore')
    tmp = f.read()
    f.close()
    tmp = re.sub('[^0-9a-z\-/+ \']', ' ', tmp, flags=re.I).lower().split()
    count = 1
    for i in tmp:
        if ham.__contains__(i):
            var1 = spam[i]/ham[i]
            count *= var1
    if count > 1000:
        return "Spam"
    else:
        return "ham"


def TestRes():
    count = 0
    TmpValue = 0
    with open('indecTest') as f:
        Line = f.readline()
        while Line:
            TestData = Line.split()
            GuessRes = GetRes(TestData[1])
            TmpValue += 1
            if GuessRes.lower() == TestData[0].lower():
                count += 1
               # print("预测结果为{}正确".format(TestData[0]))
                if(count % 1000 == 0):
                    print("预测准确率为{}".format(str(count/TmpValue)))
            else:
                pass
               # print("预测结果为{},但真实结果为{}".format(GuessRes,TestData[0]))
            Line = f.readline()
        print("预测准确率为{}".format(str(count/35419)))

    print(count)


if __name__ == '__main__':
    #    wordlist=FileVocabularDfitf(os.listdir(config.SpamPath),config.SpamPath)
    with open('StopWords.txt') as f:
        ban_word = f.read().split()
    BayesClassifier()
    with open('res.json') as f:
        data = json.loads(f.read())
        spam = data[0]
        ham = data[1]
    TestRes()
