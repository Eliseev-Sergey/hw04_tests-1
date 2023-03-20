from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Group, Post, User
from .forms import PostForm
from .utils import get_page


def index(request):
    post_list = Post.objects.all()

    context = {
        'page_obj': get_page(request, post_list),
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug_name):
    group = get_object_or_404(Group, slug=slug_name)
    template = 'posts/group_list.html'
    post_list = group.posts.all()

    context = {
        'page_obj': get_page(request, post_list),
        'group': group,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.select_related('group',
                                        ).filter(author__username=username)

    context = {
        'page_obj': get_page(request, posts),
        'author': author
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    context = {
        'post': post
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    is_edit = False
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    context = {
        'form': form,
        'is_edit': is_edit
    }
    if not form.is_valid():
        return render(request, 'posts/create_post.html', context)
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', post.author.username)


@login_required
def post_edit(request, post_id):
    is_edit = True
    post = get_object_or_404(Post, pk=post_id)
    if post.author == request.user:
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=post
        )
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id=post_id)
        context = {'form': form, 'is_edit': is_edit, 'post_id': post_id}
        return render(request, 'posts/create_post.html', context)
    return redirect('posts:post_detail', post_id=post_id)
