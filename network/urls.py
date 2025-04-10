
from django.urls import path
from . import views

from . import views

urlpatterns = [
    path("", views.index, name="index"), # Home page
    path("login", views.login_view, name="login"), # Login page
    path("logout", views.logout_view, name="logout"), # Logout page
    path("register", views.register, name="register"), # Registration page
    path("new", views.new_post, name="new_post"), # New post page
    path("like/<int:post_id>", views.toggle_like, name="toggle_like"), # Like/Unlike a post
    path("profile/<str:username>", views.profile, name="profile"), # User profile page
    path("follow/<str:username>", views.toggle_follow,name="toggle_follow"), # Follow/Unfollow a user
    path("following", views.following, name="following"), # Following page
    path("posts/<int:post_id>", views.edit_post, name="edit_post"), # Edit post page
    path("profile/<str:username>", views.profile, name="profile") # User profile page
]
