from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('supportmessage/new',views.PostCreateView.as_view(), name='post-create')
]