import json
data1='悬崖之上 唐人街探案3 唐人街探案2 盗梦空间 唐人街探案 看不见的客人 无双 误杀 调音师 无罪之最 哈利·波特与火焰杯 妖猫传 隐秘的角落 名侦探柯南：绯色的子弹 天才枪手'.split()
data='''剧情 / 动作 / 悬疑
喜剧 / 悬疑
喜剧 / 动作 / 悬疑
剧情 / 科幻 / 悬疑 / 冒险
喜剧 / 动作 / 悬疑
剧情 / 悬疑 / 惊悚 / 犯罪
剧情 / 动作 / 悬疑 / 犯罪
剧情 / 悬疑 / 犯罪
喜剧 / 悬疑 / 惊悚 / 犯罪
剧情 / 悬疑 / 惊悚 / 犯罪
悬疑 / 奇幻 / 冒险
剧情 / 悬疑 / 奇幻 / 古装
剧情 / 悬疑 / 犯罪
动作 / 动画 / 悬疑 / 冒险
剧情 / 悬疑 / 犯罪
'''.split('\n')
res1=[i.split(' / ') for i in data]
res=[]
for i in range(len(data1)):
    res.append({'title':data1[i],'movieType':res1[i]})

open('database.json','w+',encoding='utf8').write(json.dumps(res))
