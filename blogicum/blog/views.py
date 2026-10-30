from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from .models import Post, Category


def published_posts(queryset):
    return queryset.select_related(
        'category', 'author', 'location',
    ).filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    )


def index(request):
    template = 'blog/index.html'
    post_list = published_posts(Post.objects.all())[:5]

    context = {
        'post_list': post_list
    }

    return render(request, template, context)


def category(request, category_slug):
    template = 'blog/category.html'

    category_obj = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )

    post_list = published_posts(category_obj.posts.all())

    context = {
        'category': category_obj,
        'post_list': post_list
    }

    return render(request, template, context)


def detail(request, pk):
    template = 'blog/detail.html'
    detail = get_object_or_404(
        published_posts(Post.objects.all()),
        pk=pk
    )

    context = {
        'post': detail
    }

    return render(request, template, context)
