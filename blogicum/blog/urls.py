from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('profile/<str:username>/', views.profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('', views.index, name='index'),
    path('posts/<int:pk>/', views.detail, name='post_detail'),
    path(
        'category/<slug:category_slug>/',
        views.category,
        name='category_posts',
    ),
]
