# chat/urls.py
from django.urls import path
from django.conf.urls import url
from . import views


urlpatterns = [
    path('configuration', views.video_conf, name='video_conf'),

    path('video_callback/', views.video_callback),

    # test link
    path('video_test', views.create_video, name='create_video'),
    url(r'^video_test/(?P<room_name>[^/]+)/$', views.video_room, name='video_room'),
    path('video_test/kick', views.kick_video, name='kick_video')
]