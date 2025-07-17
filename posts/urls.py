from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list_view, name='post-list'),
    path('create-post/', views.create_post_view, name='create-post'),
    path('edit-post/<int:pk>/', views.edit_post_form, name='edit-post'),
    path('delete-post/<int:pk>/', views.delete_post_view, name='delete-post'),
    path('edit-comment/<int:pk>/', views.edit_comment_form, name='edit-comment'),
    path('delete-comment/<int:pk>/', views.delete_comment_view, name='delete-comment'),
    path('ajax-create-comment/<int:pk>/', views.create_comment_view, name='ajax-create-comment'),
    path('ajax-comment-list/<int:pk>/', views.ajax_comments_list_view, name='ajax-get-comments')
] 