from django.urls import path
from .views import post_list_view, post_detail_view, comment_delete_view, post_delete_view, dummy_view, \
    confirm_registration_view, new_code_view, my_replies_view
from django.views.decorators import cache




urlpatterns = [
    path('', post_list_view, name='all_posts'),
    path('category/<slug:slug>', post_list_view, name='posts_by_category'),
    path('category/<slug:slug>/<int:pk>', post_detail_view, name='show_post'),
    path('my_replies', my_replies_view, name='my_replies'),
    path('articles', dummy_view, name='non_news_posts'),
    path('posts/<int:pk>', dummy_view, name='show_post'),
    path('posts/new', dummy_view, name='new_post'),
    path('posts/new_article', dummy_view, name='new_article'),
    path('posts/new_news', dummy_view, name='new_news'),
    path('posts/edit/<int:pk>', dummy_view, name='edit_post'),
    path('posts/delete/<int:pk>', dummy_view, name='delete_post'),
    path('verify_user', confirm_registration_view, name='verify_user'),
    path('new_code', new_code_view, name='new_code'),
    path('subscriptions', dummy_view, name='subscriptions'),
    path('edit_profile', dummy_view, name='edit_profile'),


]

