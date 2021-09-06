from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect
from django.template import loader
from django.conf import settings
from django.db.models import Q
from wordcloud import WordCloud,STOPWORDS

from .models import Video,Author

from django.core.paginator import Paginator
from django.views.generic import ListView

import re
import json
import os
import time
import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# create my views here.

def createModels():
    author_dirs = os.listdir('searchE/author/')
    for author_dir in author_dirs:
        if author_dir[-4:]!='json':
            continue
        else:
            with open('searchE/author/' + author_dir, 'r') as f:
                dct = json.load(f)
                author = Author.parseJson(dct)
                author.save()
    video_dirs = os.listdir('searchE/video/')
    for video_dir in video_dirs:
        if video_dir[-4:]!='json':
            continue
        else:
            with open('searchE/video/' + video_dir, 'r') as f:
                dct = json.load(f)
                video = Video.parseJson(dct)
                if isinstance(video,Video):
                    video.save() #只有成功和author连接后才会save一部作品
    #再清除掉那些没有作品的作者
    for author_ in Author.objects.all():
        video_set = Video.objects.filter(author = author_)
        if video_set.count()==0:
            author_.delete()

def analyse_intern(): #分析作者更新频率和粉丝数
    intern_list = []
    follower_list = []
    last_date_obj = datetime.date(1,1,1)
    for author_ in Author.objects.all():
        time = [] #保存所有更新intern的一个list
        video_list = Video.objects.filter(author = author_)
        for video in video_list:
            temp = temp = datetime.datetime.strptime(video.datePublished, "%Y-%m-%d").toordinal()
            time.append(temp)
        time_np = np.array(time)
        time_np.sort()
        intern = []
        for i in range(1,len(time_np)):
            temp = time_np[i]-time_np[i-1]
            intern.append(temp)
        intern_np = np.array(intern)
        if intern_np.mean()>800: 
            continue
        else:
            intern_list.append(intern_np.mean())
        #下面处理author_.followers
        if author_.follower[-2]!='K':
            if author_.follower[2:-1]=='':
                follower = 0
            else: 
                follower = int(author_.follower[2:-1])
        else:
            follower = int(author_.follower.replace('.','').replace('K','')[2:-1])*100
        follower_list.append(follower) 
    plt.xlabel('Update intern/Day')
    plt.ylabel('Follower popularity/Man')
    plt.title('The correlation between update intern and followers')
    colors = np.random.rand(685)
    plt.scatter(intern_list,follower_list,marker="x",s=20, c=colors,alpha=0.5,) #marker是点的样式，s是点的大小,c是颜色（默认是蓝色）。
    plt.savefig('analyse_favor.jpg')
    plt.show()

def analyse_date(): #分析作者们都是星期几发视频
    label = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    count = np.zeros(7, dtype='int')
    for video in Video.objects.all():
        date_obj = datetime.datetime.strptime(video.datePublished, "%Y-%m-%d")
        count[int(datetime.datetime.strftime(date_obj, '%w'))] += 1
    plt.pie(count, labels = label, autopct="%.2f%%",explode=[0.1,0,0,0,0,0,0.1])
    plt.axis('equal')
    plt.title('Video Published Time')
    plt.legend()
    plt.savefig('analyse_date.jpg')
    plt.show()

def analyse_word():
    # get text
    text = ''
    for video in Video.objects.all():
        if video.comment_one!='':
            text += video.comment_one
        if video.comment_two!='':
            text += video.comment_two
        if video.comment_one!='':
            text += video.comment_three
        if video.comment_four!='':
            text += video.comment_four
        if video.comment_five!='':
            text += video.comment_five
    # clean text
    text = re.sub(r'==.*?==+', '',text)
    text = text.replace('\n', '')
    # generate cloud
    wordcloud = WordCloud(width = 3000, height = 2000, random_state=1, background_color='black', \
        colormap='Set2',collocations=False, stopwords=STOPWORDS).generate(text)
    plt.figure(figsize=(40,30))
    plt.imshow(wordcloud)
    plt.axis('off')
    plt.savefig('analyse_word.jpg') 
    plt.show()

def alternative():
   # get text
    text = ''
    for video in Video.objects.all():
        if video.comment_one!='':
            text += video.comment_one
        if video.comment_two!='':
            text += video.comment_two
        if video.comment_one!='':
            text += video.comment_three
        if video.comment_four!='':
            text += video.comment_four
        if video.comment_five!='':
            text += video.comment_five
    # clean text
    text = re.sub(r'==.*?==+', '',text)
    text = text.replace('\n', '')
    all_words = re.split('\W', text)
    word_list = pd.Series(all_words).value_counts().head(100)
    STOPWORDS.update(['I','The','This','s','t','m'])
    for ind in word_list.index:
        if ind not in STOPWORDS:
            print(ind,word_list[ind])

def index(request): #主页面
    request.encoding='utf-8'
    video_list = Video.objects.all()
    pag = Paginator(video_list,10)
    page_num = request.GET.get('page')
    if 'jump_page' in request.GET and request.GET['jump_page']:
        page_num = request.GET['jump_page']
    page_obj = pag.get_page(page_num)
    return render(request, 'searchE/index.html', {"page_obj":page_obj,"TOTAL_PAGE":pag.num_pages,"TOTAL_RESULT":pag.count,"PAGE_NUM":page_num,}) 
    return render(request,'base.html',{})

def authorIndex(request):
    request.encoding = 'utf-8'
    author_list = Author.objects.all()
    pag = Paginator(author_list,10)
    page_num = request.GET.get('page')
    if 'jump_page' in request.GET and request.GET['jump_page']:
        page_num = request.GET['jump_page']
    page_obj = pag.get_page(page_num)
    return render(request,'searchE/index_author.html',{"page_obj":page_obj,"TOTAL_PAGE":pag.num_pages,"TOTAL_RESULT":pag.count,"PAGE_NUM":page_num,})

def search(request):
    request.encoding='utf-8'
    if 'kw_author' in request.GET and request.GET['kw_author']:
        key_word = request.GET['kw_author']
        return redirect("/author/"+key_word)
    if 'kw_video' in request.GET and request.GET['kw_video']:
        key_word = request.GET['kw_video']
        return redirect("/video/"+key_word) 
    return render(request,'searchE/search.html',{})

def author(request,key_word): #搜索作者的搜索结果
    request.encoding='utf-8'
    startTime = time.time()
    author_list = Author.objects.filter(Q(name__contains=key_word)|Q(profile__contains=key_word))
    pag = Paginator(author_list,10)
    page_num = request.GET.get('page') 
    if 'jump_page' in request.GET and request.GET['jump_page']:
        page_num = request.GET['jump_page']
    page_obj = pag.get_page(page_num)
    intern = time.time() - startTime
    return render(request,'searchE/author.html',{"page_obj": page_obj,"TOTAL_PAGE":pag.num_pages,"TOTAL_RESULT":pag.count,"PAGE_NUM":page_num,"KEY_WORD":key_word,"intern":intern,})

def video(request,key_word):
    request.encoding='utf-8'
    startTime = time.time()
    video_list = Video.objects.filter(Q(title__contains=key_word)|Q(description__contains=key_word))
    pag = Paginator(video_list,10)
    page_num = request.GET.get('page')
    if 'jump_page' in request.GET and request.GET['jump_page']:
        page_num = request.GET['jump_page']
    page_obj = pag.get_page(page_num)
    intern = time.time() - startTime
    return render(request, 'searchE/video.html', {"page_obj":page_obj,"TOTAL_PAGE":pag.num_pages,"TOTAL_RESULT":pag.count,"PAGE_NUM":page_num,"KEY_WORD":key_word,"intern":intern,})

def authorDetail(request,author_id):
    request.encoding='utf-8'
    author_link = "https://www.youtube.com/channel/" + author_id
    m_author = Author.objects.get(link = author_link)
    video_list = Video.objects.filter(author = m_author)
    m_profile = m_author.profile.strip()
    paragraph_list = m_profile.split('\n')
    pag = Paginator(video_list,10)
    page_num = request.GET.get('page') 
    if 'jump_page' in request.GET and request.GET['jump_page']:
        page_num = request.GET['jump_page']
    page_obj = pag.get_page(page_num)
    return render(request,'searchE/authorDetail.html',{"author":m_author, "paragraph_list":paragraph_list,"page_obj":page_obj,"TOTAL_PAGE":pag.num_pages,"TOTAL_RESULT":pag.count,"PAGE_NUM":page_num, })

def videoDetail(request,video_id):
    request.encoding='utf-8'
    video_link = "https://www.youtube.com/watch?v="+video_id
    m_video = Video.objects.get(url = video_link)
    comment_list = []
    if m_video.comment_one:
        comment_list.append(m_video.comment_one)
    if m_video.comment_two:
        comment_list.append(m_video.comment_two)
    if m_video.comment_three:
        comment_list.append(m_video.comment_three)
    if m_video.comment_four:
        comment_list.append(m_video.comment_four)
    if m_video.comment_five:
        comment_list.append(m_video.comment_five)
    m_description = m_video.description.strip()
    paragraph_list = m_description.split('\n')
    return render(request, 'searchE/videoDetail.html',{"video":m_video,"comment_list":comment_list,"paragraph_list":paragraph_list,})