# -*- encoding: utf8 -*-
import email
import re


def EmailData(FilePath):
    fp = open(FilePath, "r",encoding='iso8859',errors='ignore')
    msg = email.message_from_file(fp)
    data=''
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
                data+=(' '.join(re.sub('<.*?>|</.*?>|&nbsp|0x\d+|&deg', '',
                                      par.get_payload(decode=False), flags=re.S).split()))  # 解码出文本内容，直接输出来就可以了。
    fp.close()
    return data

            # print ('+'*60) # 用来区别各个部分的输出
# data=''
# i=0
# with open('indecTest', mode='a') as filename:
#     with open('index') as f:
#         Line=f.readline()
#         while Line:
#             if(i>40000):
#                 filename.write(Line)
#             Line=f.readline()
#             i+=1
#with open()
print(EmailData('./bigdataset/trec07p/data/inmail.38790'))