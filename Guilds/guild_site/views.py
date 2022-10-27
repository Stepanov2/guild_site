from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import F
from django.http import HttpResponseNotFound
from django.shortcuts import render, get_list_or_404, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View

from .forms import ReplyForm, DeleteForm, ConfirmRegistrationForm
from .models import Post, SiteUser, Category, AuthCode, Reply


# Create your views here.

# BEGIN context processors


def add_categories_to_context(request):
    """Context processor that adds list of categories to context(for menu rendering)"""
    return {'categories': Category.objects.all()}

# todo: view_title
def confirm_registration_view(request):

    if request.method == 'GET':
        form = ConfirmRegistrationForm
        return render(request, 'check_code.html', {'form': form})
    if request.method == 'POST':
        form = ConfirmRegistrationForm(request.POST, user_id=request.user.id)
        if form.is_valid():
            siteuser = request.user.siteuser
            siteuser.is_activated = True
            siteuser.save()

            return redirect(to='/')
        return render(request, 'check_code.html', {'form': form})


def new_code_view(request):
    if request.user.siteuser.is_activated:
        return redirect('/')
    AuthCode.objects.create(user=request.user.siteuser)
    return redirect('verify_user')


def post_list_view(request, slug=None):  # slug for category, if none is specified - we are on the main page.
    if slug is not None:

        category = Category.objects.filter(slug=slug).first()
        if category is None:
            return HttpResponseNotFound(f'Не нашли категорию {slug}')
        postset = Post.objects.filter(category=category)

    else:
        postset = Post.objects.all()

    page = request.GET.get('page', 1)
    paginator = Paginator(postset, 2)

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'posts.html', {'posts': posts})


def post_detail_view(request, slug, pk):  # todo 404 error checking
    reply_result = ''
    post = Post.objects.prefetch_related('reply_set').get(id=pk)
    reply_form = ReplyForm()
    if request.method == 'POST':
        reply_form = ReplyForm(request.POST)
        if reply_form.is_valid():
            Reply.objects.create(user=request.user.siteuser, post=post, body=reply_form.cleaned_data['body'])
            reply_form = ReplyForm()
            post = Post.objects.prefetch_related('reply_set').get(id=pk)  # need to re-fetch new reply
            reply_result = 'Успешно добавили ваш отклик. Отклик ожидает утверждения автором объявления.'
        else:
            reply_result = 'Не удалось запостить ваш отклик, потому что' + str(reply_form.errors)
    return render(request, 'posts.html', {'post': post,
                                          'reply_form': reply_form,
                                          'reply_result': reply_result})


def my_replies_view(request):
    user = request.user.siteuser
    replies = Reply.objects.prefetch_related('post', 'post__category').filter(post__user=user).order_by(F('approved').desc(nulls_first=True), '-created')
    return render(request, 'my_replies.html', {'replies': replies})


def post_delete_view(request, pk): # todo
    post = get_object_or_404(Post, id=pk)
    post_delete_form = DeleteForm()
    return render(request, 'delete_post.html', {'post': post,
                                                'post_delete_form': post_delete_form})


def comment_delete_view(request):
    return render(request, 'delete_comment.html', {})


def dummy_view(request):

    return render(request, 'dummy.html', {})
