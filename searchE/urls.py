from django.urls import path,include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name = 'index'), #主页面
    path('authorIndex/',views.authorIndex, name = 'authorIndex'),
    path('search/', views.search, name = 'search'), #搜索页面
    path('author/<str:key_word>', views.author, name = 'author'), # 作者分页
    path('video/<str:key_word>', views.video, name = 'video'), #作品分页
    path('video/Detail/<str:video_id>', views.videoDetail, name = 'videoDetail'), # 视频详情页
    path('author/Detail/<str:author_id>', views.authorDetail, name = 'authorDetail'), #作者详情页
]