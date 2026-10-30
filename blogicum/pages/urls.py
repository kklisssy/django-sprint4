from django.urls import path

from . import views

app_name = 'pages'

urlpatterns = [
    path('about/', views.about, name='about'),
    path('rules/', views.rules, name='rules'),
]

handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'
