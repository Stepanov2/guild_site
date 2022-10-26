from django.shortcuts import render, get_list_or_404, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View

from .forms import CommentForm, DeleteForm, ConfirmRegistrationForm
from .models import Post, SiteUser, Category, AuthCode


# Create your views here.

# BEGIN context processors


def add_categories_to_context(request):
    """Context processor that adds list of categories to context(for menu rendering)"""
    return {'categories': Category.objects.all()}


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
        posts = get_list_or_404(Post, category__slug=slug)
    else:
        posts = Post.objects.all()
    return render(request, 'posts.html', {'posts': posts})


def post_detail_view(request, pk):  # todo 404 error checking
    post = Post.objects.prefetch_related('comment_set').get(id=pk)
    comment_form = CommentForm()
    return render(request, 'posts.html', {'post': post,
                                          'comment_form': comment_form})


def post_delete_view(request, pk):
    post = get_object_or_404(Post, id=pk)
    post_delete_form = DeleteForm()
    return render(request, 'delete_post.html', {'post': post,
                                                'post_delete_form': post_delete_form})


def comment_delete_view(request):
    return render(request, 'delete_comment.html', {})


def dummy_view(request):

    return render(request, 'dummy.html', {})
