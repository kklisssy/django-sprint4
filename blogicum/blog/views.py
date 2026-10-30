from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .forms import UserForm, PostForm, CommentForm
from .models import Post, Category, Comment
from django.core.paginator import Paginator
from django.db.models import Count

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

    post_list = post_list.annotate(
        comment_count=Count('comments'),
    )

    paginator = Paginator(post_list, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'profile': profile_user,
        'page_obj': page_obj,
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


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect(
                'blog:profile',
                username=request.user.username,
            )
    else:
        form = PostForm()

    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, post_id):
    template = 'blog/create.html'
    post = get_object_or_404(Post, pk=post_id)

    if request.user != post.author:
        return redirect('blog:post_detail', pk=post.pk)

    if request.method == 'POST':
        form = PostForm(
            request.POST,
            request.FILES,
            instance=post,
        )

        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)

    return render(request, template, {'form': form})


@login_required
def delete_post(request, post_id):
    template = 'blog/create.html'
    post = get_object_or_404(Post, pk=post_id)

    if request.user != post.author:
        return redirect('blog:post_detail', pk=post.pk)

    if request.method == 'POST':
        post.delete()
        return redirect(
            'blog:profile',
            username=request.user.username,
        )

    form = PostForm(instance=post)
    return render(request, template, {'form': form})


@login_required
def add_comment(request, post_id):
    template = 'blog/detail.html'
    post = get_object_or_404(Post, pk=post_id)

    if request.user != post.author:
        post = get_object_or_404(
            published_posts(Post.objects.all()),
            pk=post_id,
        )

    if request.method == 'POST':
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('blog:post_detail', pk=post.pk)
    else:
        return redirect('blog:post_detail', pk=post.pk)

    context = {
        'post': post,
        'form': form,
        'comments': post.comments.select_related('author'),
    }
    return render(request, template, context)


@login_required
def edit_comment(request, post_id, comment_id):
    template = 'blog/comment.html'
    comment = get_object_or_404(
        Comment,
        pk=comment_id,
        post_id=post_id,
    )

    if request.user != comment.author:
        return redirect('blog:post_detail', pk=post_id)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)

        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', pk=post_id)
    else:
        form = CommentForm(instance=comment)

    context = {
        'form': form,
        'comment': comment,
    }
    return render(request, template, context)


@login_required
def delete_comment(request, post_id, comment_id):
    template = 'blog/comment.html'
    comment = get_object_or_404(
        Comment,
        pk=comment_id,
        post_id=post_id,
    )

    if request.user != comment.author:
        return redirect('blog:post_detail', pk=post_id)

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', pk=post_id)

    return render(request, template, {'comment': comment},)


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
    post_list = published_posts(Post.objects.all())
    post_list = post_list.annotate(
        comment_count=Count('comments'),
    )
    
    paginator = Paginator(post_list, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj
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
    post_list = post_list.annotate(
        comment_count=Count('comments'),
    )

    paginator = Paginator(post_list, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'category': category_obj,
        'page_obj': page_obj
    }

    return render(request, template, context)


def detail(request, pk):
    template = 'blog/detail.html'
    post  = get_object_or_404(
        Post.objects.select_related('category', 'author', 'location'),
        pk=pk
    )

    if request.user != post.author:
        post = get_object_or_404(
            published_posts(Post.objects.all()),
            pk=pk,
        )

    context = {
        'post': post,
        'form': CommentForm(),
        'comments': post.comments.select_related('author'),
    }

    return render(request, template, context)
