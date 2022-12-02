
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.core.paginator import Paginator
from .forms import PostForm
from django.urls import reverse_lazy
from .models import Post, Group, User
from .constants import PUB_VALUE


def page_list(request, post_list):
    # Показывать по 10 записей на странице.
    paginator = Paginator(post_list, PUB_VALUE)

    # Из URL извлекаем номер запрошенной страницы - это значение параметра page
    page_number = request.GET.get('page')

    # Получаем набор записей для страницы с запрошенным номером
    return paginator.get_page(page_number)


def index(request):
    # в переменную posts будет сохранена выборка из 10 объектов модели Post,
    # отсортированных по полю pub_date по убыванию
    post_list = Post.objects.select_related()
    page_obj = page_list(request, post_list)
    # Отдаем в словаре контекста
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_list(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.group_list.all()

    page_obj = page_list(request, post_list)

    context = {
        'text': slug,
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):

    # Здесь код запроса к модели и создание словаря контекста
    author = get_object_or_404(User, username=username)
    posts_author = Post.objects.filter(author=author)
    paginator = Paginator(posts_author, PUB_VALUE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'author': author,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    # Здесь код запроса к модели и создание словаря контекста
    post = get_object_or_404(Post, id=post_id)
    context = {
        'post': post,
        'count_posts': post.author.posts.count(),
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.author = request.user
            new_form.save()
            return redirect('posts:profile', request.user)
        form = PostForm()
    context = {'form': form,
               }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    edited_post = get_object_or_404(Post, id=post_id)
    print('Пост в views найден!!!!!!!')
    if request.user == edited_post.author:
        print('user тот же!!!!!!!!!!!')
        if request.method == 'POST':
            form = PostForm(request.POST or None, instance=edited_post)
            context = {
                'form': form,
                'is_edit': True,
            }
            if form.is_valid():
                print('проверка валидности пройдена !!!!!!!!')
                form.save()
                return redirect(
                    reverse_lazy(
                        'posts:post_detail',
                        kwargs={'post_id': post_id}
                    )
                )
            return render(request, 'posts/create_post.html', context)
        form = PostForm(request.POST or None, instance=edited_post)
        context = {
            'form': form,
            'is_edit': True,
        }
        return render(request, 'posts/create_post.html', context)
    return redirect(
        reverse_lazy(
            'posts:post_detail',
            kwargs={'post_id': post_id}
        )
    )
