from django.urls import path
from django.contrib import admin

from . import views

urlpatterns = [
    path('', views.show_subjects),
    path('admin/', admin.site.urls),

    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('teachers/', views.show_teachers, name='teacher'),
    path('praise/', views.praise_or_criticize, name='praise'),
    path('criticize/', views.praise_or_criticize, name='criticize'),
    path('captcha/', views.get_captcha, name='captcha')
]