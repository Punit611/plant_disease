from django.contrib import admin
from django.urls import path,include
from authAndDetect import urls
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('signup', views.signup, name='signup'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('signin', views.signin, name='signin'),
    path('signout', views.signout, name='signout'),
    path('scan',views.scan,name='scan'),
    path('done',views.done,name='done'),
    path('preview',views.preview,name='preview'),
    
]
