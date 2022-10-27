import django.http
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import F
from django.http import HttpResponseNotFound
from django.shortcuts import render, get_list_or_404, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.http import Http404
from django.core.exceptions import PermissionDenied
from .models import Category, AuthCode, Post, Reply, SiteUser
from .filters import ReplyFilter
from .forms import ReplyForm, DeleteForm, ConfirmRegistrationForm, PostForm, ManageSubscriptionsForm


# Create your views here.

# BEGIN context processors



def add_categories_to_context(request):
    """Context processor that adds list of categories to context(for menu rendering)"""
    return {'categories': Category.objects.all()}

# todo: view_title for everything
@login_required
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

@login_required
def new_code_view(request):
    if request.user.siteuser.is_activated:
        return redirect('/')
    AuthCode.objects.create(user=request.user.siteuser)
    return redirect('verify_user')


def post_list_view(request, slug=None):  # slug for category, if none is specified - we are on the main page.
    postset = None;
    valid_user = None
    if slug is not None:

        category = Category.objects.filter(slug=slug).first()
        if category is None:
            return HttpResponseNotFound(f'Не нашли категорию {slug}')
        postset = Post.objects.filter(category=category)

    else:
        postset = Post.objects.all()
    if request.GET.get('author'):
        try:
            valid_user = SiteUser.objects.filter(pk=int(request.GET.get('author'))).exists()
        except ValueError:
            pass
        if valid_user:
            postset = postset.filter(user_id=int(request.GET.get('author')))

    page = request.GET.get('page', 1)
    paginator = Paginator(postset, 2)

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'posts.html', {'posts': posts})


def post_detail_view(request, slug, pk):
    reply_result = ''
    try:
        post = Post.objects.prefetch_related('reply_set').order_by(F('approved').desc(nulls_first=True),'created').get(id=pk)
    except Post.DoesNotExist:
        raise Http404
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

@login_required
def post_create_edit_view(request, pk=None):
    post = None
    if not request.user.pk or not request.user.siteuser.is_activated:
        raise PermissionDenied
    if pk is None:
        form = PostForm()
    else:
        try:
            post = Post.objects.get(id=pk)
        except Post.DoesNotExist:
            raise Http404
        if post.user.user != request.user:
            raise PermissionDenied
        form = PostForm(instance=post)
    if request.method == 'GET':
        return render(request, 'edit_post.html', {'form': form})
    elif request.method == 'POST':
        form = PostForm(request.POST)
        # print(form.__dict__)
        if form.is_valid():
            print(form.cleaned_data)
            print(request.POST)
            if post:
                post.title = form.cleaned_data['title']
                post.body = form.cleaned_data['body']
                post.category = form.cleaned_data['category']
                post.save()
            else:
                Post.objects.create(user=request.user.siteuser,
                                    title=form.cleaned_data['title'],
                                    category=form.cleaned_data['category'],
                                    body=form.cleaned_data['body'])
            return redirect('/')  # todo
        else:
            return render(request, 'edit_post.html', {'form': form})

@login_required
def my_replies_view(request):

    user = request.user.siteuser
    replies = Reply.objects.prefetch_related('post', 'post__category').filter(post__user=user).order_by(F('approved').desc(nulls_first=True), '-created')
    filtered_replies = ReplyFilter(request.GET, user=user, queryset=replies)
    return render(request, 'my_replies.html', {'replies': filtered_replies.qs,
                                               'reply_browser': True,
                                               'filterset': filtered_replies})

@login_required
def post_delete_view(request, pk):  # todo
    post = get_object_or_404(Post, id=pk)
    if post.user.pk != request.user.id:
        raise PermissionDenied
    post_delete_form = DeleteForm()
    if request.method == 'GET':
        return render(request, 'delete_post.html', {'post': post, 'form': post_delete_form})
    if request.method == 'POST' and request.POST.get('confirmation'):
        post.delete()
        return redirect('/')
    else:
        return render(request, 'delete_post.html', {'post': post, 'form': post_delete_form})

@login_required
def manage_subscription_view(request):
    if not request.user.pk:
        raise PermissionDenied
    message = ''
    if request.method == 'POST':
        form = ManageSubscriptionsForm(request.POST)
        if form.is_valid():
            siteuser = request.user.siteuser
            siteuser.subscription.set(form.cleaned_data['subscription'])
            siteuser.save()
            message = 'Подписки обновлены!'
    form = ManageSubscriptionsForm(instance=request.user.siteuser)
    return render(request, 'list_subscriptions.html', {'form': form, 'message': message})

@login_required
def update_reply_status(request: django.http.HttpRequest):
    print(request.GET)
    reply = get_object_or_404(Reply, pk=request.GET.get('reply'))
    if reply.post.user.user != request.user:
        raise PermissionDenied
    try:
        reply.approved = bool(request.GET.get('vote'))
    except ValueError:
        raise PermissionDenied
    reply.save()
    return redirect(request.GET.get('return_to') if request.GET.get('return_to') else '/')

@login_required
def comment_delete_view(request):  # maybe in next version=)
    return render(request, 'dummy.html', {})


def dummy_view(request):

    return render(request, 'dummy.html', {})
