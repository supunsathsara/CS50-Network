from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import (
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseNotFound,
    HttpResponseRedirect,
    JsonResponse,
)
from django.urls import reverse
from django.shortcuts import get_object_or_404, render, redirect
from .models import User, Post, Relationship, Like
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required
import json


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
            return render(
                request,
                "network/login.html",
                {"message": "Invalid username and/or password."},
            )
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
            return render(
                request, "network/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request, "network/register.html", {"message": "Username already taken."}
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


# def index(request):
#     posts = Post.objects.all().order_by("-created_at")
#     # Add the is_being_edited flag to each post
#     for post in posts:
#         if post.is_being_edited:
#             post.is_being_edited = True
#         else:
#             post.is_being_edited = False
#     return render(request, "network/index.html", {"posts": posts})


def index(request):
    posts = Post.objects.order_by("-created_at").all()

    # paginate the posts
    paginator = Paginator(posts, 10)
    page = request.GET.get("page")
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    for post in posts:
        post.is_liked_by_user = False
        if request.user.is_authenticated:
            post.is_liked_by_user = Like.objects.filter(
                user=request.user, post=post
            ).exists()
        post.is_being_edited = False
        if post.is_being_edited:
            post.is_being_edited = True
        else:
            post.is_being_edited = False
    context = {
        "posts": posts,
        "is_paginated": paginator.num_pages > 1,
        "page_obj": posts,
    }
    return render(request, "network/index.html", context)


@login_required
def new_post(request):
    if request.method == "POST":
        # handle form submission
        request_body = request.body.decode("utf-8")
        request_data = json.loads(request_body)
        text = request_data["text"]
        post = Post.objects.create(user=request.user, text=text)
        return redirect("index")
    else:
        # display the form
        return render(request, "network/new_post.html")


@login_required
def following(request):
    following = Relationship.objects.filter(follower=request.user).values_list(
        "followed", flat=True
    )
    posts = Post.objects.filter(user__in=following).order_by("-created_at")

    # paginate the posts
    paginator = Paginator(posts, 10)
    page = request.GET.get("page")
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    context = {
        "posts": posts,
        "is_paginated": paginator.num_pages > 1,
        "page_obj": posts,
    }
    return render(request, "network/following.html", context)


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        # handle form submission
        if request.user != post.user:
            # return a 403 Forbidden response if the user is not the post owner
            return HttpResponseForbidden()
        request_body = request.body.decode("utf-8")
        request_data = json.loads(request_body)
        text = request_data["text"]
        post.text = text
        post.save()
        data = {"success": True, "text": post.text}
        return JsonResponse(data)
    else:
        # return a 403 Forbidden response if the request is not a POST request
        return HttpResponseForbidden()


@login_required
def like_post(request, post_id):
    post = Post.objects.get(id=post_id)
    if request.method == "POST":
        # handle form submission
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if not created:
            like.delete()
        is_liked = Like.objects.filter(user=request.user, post=post).exists()
        like_count = post.like_set.count()
        data = {"is_liked": is_liked, "like_count": like_count}
        return JsonResponse(data)
    else:
        # handle AJAX request
        data = {"like_count": post.like_set.count()}
        return JsonResponse(data)


# @login_required
# def like_post(request, post_id):
#     post = Post.objects.get(id=post_id)
#     if request.method == "POST":
#         # handle form submission
#         like, created = Like.objects.get_or_create(user=request.user, post=post)
#         if not created:
#             like.delete()
#         return redirect("index")


@login_required
def profile(request, username):
    user = User.objects.get(username=username)
    posts = Post.objects.filter(user=user).order_by("-created_at")
    is_following = False

    if request.user.is_authenticated:
        # Determine if the logged in user is following this user
        is_following = Relationship.objects.filter(
            follower=request.user, followed=user
        ).exists()

    # Pagination
    paginator = Paginator(posts, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    is_paginated = page_obj.has_other_pages()

    context = {
        "user": user,
        "posts": posts,
        "is_following": is_following,
        "page_obj": page_obj,
        "is_paginated": is_paginated,
    }

    return render(request, "network/profile.html", context)


@login_required
def follow_user(request, user_id):
    # Get the followed user
    followed_user = get_object_or_404(User, pk=user_id)

    # Create the relationship
    Relationship.objects.create(follower=request.user, followed=followed_user)

    # Return a success response
    return JsonResponse({"success": True})


@login_required
def unfollow_user(request, user_id):
    # Get the followed user
    followed_user = User.objects.get(id=user_id)
    # Try to get the Relationship object for the current user and the followed user
    try:
        relationship = Relationship.objects.get(
            follower=request.user, followed=followed_user
        )
    except Relationship.DoesNotExist:
        # If the Relationship object does not exist, return a 404 response
        return HttpResponseNotFound()
    except Relationship.MultipleObjectsReturned:
        # If multiple Relationship objects are returned, delete all of them
        Relationship.objects.filter(
            follower=request.user, followed=followed_user
        ).delete()
    else:
        # If only one Relationship object is returned, delete it
        relationship.delete()
    # Redirect the user back to the profile page
    return JsonResponse({"success": True})


# def profile(request, username):
#     user = User.objects.get(username=username)
#     posts = Post.objects.filter(user=user).order_by("-created_at")
#     is_following = Relationship.objects.filter(
#         follower=request.user, followed=user
#     ).exists()
#     return render(
#         request,
#         "network/profile.html",
#         {"user": user, "posts": posts, "is_following": is_following},
#     )


# @login_required
# def follow(request, user_id):
#     user_to_follow = get_object_or_404(User, id=user_id)
#     Relationship.objects.create(follower=request.user, followed=user_to_follow)
#     return redirect("profile", username=user_to_follow.username)


# @login_required
# def unfollow(request, user_id):
#     user_to_unfollow = get_object_or_404(User, id=user_id)
#     Relationship.objects.filter(
#         follower=request.user, followed=user_to_unfollow
#     ).delete()
#     return redirect("profile", username=user_to_unfollow.username)
