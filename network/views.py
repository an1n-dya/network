from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import json

from .models import User, Post, Follow


def index(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, "network/index.html", {
        "page_obj": page_obj,
        "page_title": "All Posts"
    })


@login_required
def create_post(request):
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            Post.objects.create(user=request.user, content=content)
        return HttpResponseRedirect(reverse("index"))
    return HttpResponseRedirect(reverse("index"))


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(user=profile_user)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Check if current user is following this profile
    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        is_following = Follow.objects.filter(
            follower=request.user, 
            following=profile_user
        ).exists()
    
    follower_count = Follow.objects.filter(following=profile_user).count()
    following_count = Follow.objects.filter(follower=profile_user).count()
    
    return render(request, "network/profile.html", {
        "profile_user": profile_user,
        "page_obj": page_obj,
        "is_following": is_following,
        "follower_count": follower_count,
        "following_count": following_count,
        "is_own_profile": request.user == profile_user
    })


@login_required
def following(request):
    # Get users that current user follows
    following_users = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
    posts = Post.objects.filter(user__in=following_users)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, "network/index.html", {
        "page_obj": page_obj,
        "page_title": "Following"
    })


@csrf_exempt
@login_required
def toggle_follow(request, username):
    if request.method == "POST":
        profile_user = get_object_or_404(User, username=username)
        
        if profile_user == request.user:
            return JsonResponse({"error": "Cannot follow yourself"}, status=400)
        
        follow_obj, created = Follow.objects.get_or_create(
            follower=request.user,
            following=profile_user
        )
        
        if not created:
            follow_obj.delete()
            is_following = False
        else:
            is_following = True
        
        follower_count = Follow.objects.filter(following=profile_user).count()
        
        return JsonResponse({
            "is_following": is_following,
            "follower_count": follower_count
        })
    
    return JsonResponse({"error": "POST request required"}, status=400)


@csrf_exempt
@login_required
def edit_post(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        
        if post.user != request.user:
            return JsonResponse({"error": "Unauthorized"}, status=403)
        
        data = json.loads(request.body)
        content = data.get("content", "").strip()
        
        if content:
            post.content = content
            post.save()
            return JsonResponse({"success": True, "content": post.content})
        else:
            return JsonResponse({"error": "Content cannot be empty"}, status=400)
    
    return JsonResponse({"error": "POST request required"}, status=400)


@csrf_exempt
@login_required
def toggle_like(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            is_liked = False
        else:
            post.likes.add(request.user)
            is_liked = True
        
        return JsonResponse({
            "is_liked": is_liked,
            "like_count": post.like_count()
        })
    
    return JsonResponse({"error": "POST request required"}, status=400)


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
