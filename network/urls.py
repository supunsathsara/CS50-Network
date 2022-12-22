from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("new_post/", views.new_post, name="new_post"),
    path("delete_post/<int:post_id>/", views.delete_post, name="delete_post"),
    path("profile/<str:username>/", views.profile, name="profile"),
    path("following/", views.following, name="following"),
    path("edit_post/<int:post_id>/", views.edit_post, name="edit_post"),
    path("like_post/<int:post_id>/", views.like_post, name="like_post"),
    path("follow/<int:user_id>/", views.follow_user, name="follow"),
    path("unfollow/<int:user_id>/", views.unfollow_user, name="unfollow"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
]
