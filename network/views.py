from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User 
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from .models import Post, User, Follow
import json



def index(request):
    posts = Post.objects.all().order_by('-timestamp')
    paginator = Paginator(posts, 10)  # Show 10 posts per page

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        "page_obj": page_obj
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
    
@login_required
def new_post(request):
    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            post = Post(user=request.user, content=content)
            post.save()
    return redirect("index")


@csrf_exempt  # to improve
def toggle_like(request, post_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    user = request.user
    if not user.is_authenticated:
        return JsonResponse({"error": "Authentication required."}, status=403)

    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    if user in post.likes.all():
        post.likes.remove(user)
        liked = False
    else:
        post.likes.add(user)
        liked = True

    return JsonResponse({
        "liked": liked,
        "likes_count": post.likes.count()
    })

@login_required
def toggle_follow(request, username):
    if request.method == "POST":
        target_user = get_object_or_404(User, username=username)

        # Don't allow following yourself
        if request.user == target_user:
            return HttpResponseRedirect(reverse("profile", args=[username]))

        # Check if already following
        follow_obj = Follow.objects.filter(user=target_user, follower=request.user)
        if follow_obj.exists():
            follow_obj.delete()  # unfollow
        else:
            Follow.objects.create(user=target_user, follower=request.user)  # follow

    return HttpResponseRedirect(reverse("profile", args=[username]))

@login_required
def following(request):
    followed_users = Follow.objects.filter(follower=request.user).values_list("user", flat=True)
    posts = Post.objects.filter(user__in=followed_users).order_by("-timestamp")

    paginator = Paginator(posts, 10)  # Paginate just like index
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "network/following.html", {
        "page_obj": page_obj
    })


@login_required
@require_http_methods(["PUT"])
def edit_post(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    if post.user != request.user:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    data = json.loads(request.body)
    new_content = data.get("content", "")

    if not new_content.strip():
        return JsonResponse({"error": "Content cannot be empty."}, status=400)

    post.content = new_content
    post.save()

    return JsonResponse({"message": "Post updated."})

def profile(request, username):
    user_profile = User.objects.get(username=username)
    posts = Post.objects.filter(user=user_profile).order_by("-timestamp")
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    followers = Follow.objects.filter(user=user_profile).count()
    following = Follow.objects.filter(follower=user_profile).count()

    is_following = False
    if request.user.is_authenticated and request.user != user_profile:
        is_following = Follow.objects.filter(user=user_profile, follower=request.user).exists()

    return render(request, "network/profile.html", {
        "user_profile": user_profile,
        "page_obj": page_obj,
        "followers": followers,
        "following": following,
        "is_following": is_following
    })
