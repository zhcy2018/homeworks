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
# print(EmailData('./bigdataset/trec07p/data/inmail.38790'))
import base64
a=base64.b64decode('''
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
AAAASUVORK5CYII=
''')
open('test.jpg','wb+').write(a)