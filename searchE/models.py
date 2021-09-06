from django.db import models

# Create your models here.

class Author(models.Model):
    link = models.URLField(primary_key = True, max_length = 200) #个人主页链接，pk
    name = models.CharField(max_length = 50)
    follower = models.CharField(max_length = 100, blank = True)
    image = models.CharField(max_length = 400, null = True)
    profile = models.TextField(blank = True)

    def __str__(self):
        return self.name

    def parseJson(dct):
        if isinstance(dct,dict):
            author = Author(link = dct['link'], name = dct['name'], follower= dct['follower'].encode('utf-8'), image = dct['image'], profile = dct['profile'])
            return author
        else:
            return dct


    
class Video(models.Model):
    url = models.URLField(primary_key = True, max_length = 200)
    title = models.CharField(max_length = 200)
    image = models.CharField(max_length = 200)
    viewCount = models.CharField(max_length = 200)
    datePublished = models.CharField(max_length = 50)
    likes = models.CharField(default = '',max_length = 50)
    dislikes = models.CharField(default = '',max_length = 50)
    comment_num = models.IntegerField(default = 0)
    comment_one = models.TextField(default = '')
    comment_two = models.TextField(default = '')
    comment_three = models.TextField(default = '')
    comment_four = models.TextField(default = '')
    comment_five = models.TextField(default = '') 
    authorLink = models.URLField()
    description = models.TextField()
    # foreign key
    author = models.ForeignKey(Author,on_delete=models.CASCADE, related_name='works')

    def __str__(self):
        return self.title

    def parseJson(dct):
        if isinstance(dct,dict):
            try:

                video = Video(url = dct['url'], title = dct['title'],\
                    image = dct['image'], viewCount = dct['viewCount'],\
                    datePublished = dct['datePublished'], likes = dct['likes'], dislikes = dct['dislikes'],\
                    comment_num =len(dct['comment']), authorLink = dct['authorLink'], description = dct['description'], \
                    author = Author.objects.get(link = dct['authorLink']))
                for i in range(1, video.comment_num+1):
                    if i==1:
                        video.comment_one = dct['comment'][0]
                    elif i ==2:
                        video.comment_two = dct['comment'][1]
                    elif i ==3:
                        video.comment_three = dct['comment'][2]
                    elif i ==4:
                        video.comment_four = dct['comment'][3]
                    elif i ==5:
                        video.comment_five = dct['comment'][4]
                return video
            except Author.DoesNotExist: #如果匹配作者失败了，会返回dict类型变量
                return dct
        else:
            return dct
                




