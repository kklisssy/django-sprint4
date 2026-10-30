from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .forms import UserForm
from .models import Post, Category

from django.contrib.auth import get_user_model

User = get_user_model()

def profile(request, username):
    template = 'blog/profile.html'
    profile_user = get_object_or_404(User, username=username)
    post_list = profile_user.posts.select_related(
        'category', 'author', 'location',
    )

    if request.user != profile_user:
        post_list = published_posts(post_list)

    context = {
        'profile': profile_user,
        'post_list': post_list,
    }
    return render(request, template, context)

@login_required
def edit_profile(request):
    template = 'blog/user.html'
    if request.method == 'POST':
        form = UserForm(request.POST, instance=request.user)

        if form.is_valid():
            user = form.save()
            return redirect('blog:profile', username=user.username)
    else:
        form = UserForm(instance=request.user)

    return render(request, template, {'form': form})


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
