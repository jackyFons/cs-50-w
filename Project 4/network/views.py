import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt

from .models import User, Post, Follows


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


# ---------------- MY CODE ----------------

def index(request):
    """
    Returns all posts.
    """
    posts = get_pagination_posts(request, Post.objects.all().order_by("-timestamp"))

    return render(request, "network/index.html", {
        "posts": posts
    })


@login_required
def new_post(request):
    """
    Creates a new post
    """
    # POST method needed
    if request.method == 'POST':
        content = request.POST["post-body"]
        new_post = Post(
            poster=request.user,
            content=content
        )
        new_post.save()
    return HttpResponseRedirect(reverse(index))


@csrf_exempt
@login_required()
def change_likes(request, id):
    """
    Uses an API to change the like button and number of likes a post has
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Requires POST method."}, status=404)

    try:
        post = Post.objects.get(pk=id)
        user = request.user

        # Removes user from likes
        if user in post.liked_by.all():
            post.liked_by.remove(user)
            is_liked = False
        # Adds user to likes
        else:
            post.liked_by.add(user)
            is_liked = True
        post.save()

        # Returns data that will be used to update the visuals in Javascript to prevent the page from refreshing
        return JsonResponse({"likes": post.likes_count(), "is_liked": is_liked}, status=200)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)


def view_profile(request, username):
    """
    Shows a user's profile page with all of their posts.
    Updates following list after a user decides to follow them.
    """

    # User whose profile is being viewed
    user = User.objects.get_by_natural_key(username)

    # User's posts
    posts = get_pagination_posts(request, Post.objects.filter(poster=user.id).order_by("-timestamp"))

    # The 'follow' variable will be used to determine what the follow button says
    # - Retrieves follow status based on database when the page is loaded
    if request.method == 'GET':
        if Follows.objects.filter(followers=request.user, following=user).count() == 0:
            follow = False
        else:
            follow = True

    # - Changes the follow variable and adds/removes the user from the following when the button is clicked
    elif request.method == 'POST':
        if request.POST["follow-btn"] == "follow":
            Follows.objects.create(followers=request.user, following=user)
            follow = True
        else:
            Follows.objects.get(followers=request.user, following=user).delete()
            follow = False

    return render(request, "network/profile.html", {
        "p_user": user,
        "posts": posts,
        "follower_count": Follows.objects.filter(followers=user).count(),
        "following_count": Follows.objects.filter(following=user).count(),
        "follow": follow
    })


@login_required
def following(request):
    """
    Shows the logged-in user a page with all the posts of the users they follow.
    """
    current_following = Follows.objects.filter(followers=request.user).values('following_id')
    post_obj = []

    for user in current_following:
        post_obj += Post.objects.filter(poster=user['following_id'])
    post_obj.sort(key=lambda x: x.timestamp, reverse=True)

    posts = get_pagination_posts(request, post_obj)

    return render(request, "network/following.html", {
        "posts": posts
    })


@csrf_exempt
@login_required
def save_edit(request, id):
    """
    Uses API to edit a user's post.
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Requires POST method."}, status=404)

    try:
        post = Post.objects.get(poster=request.user, pk=id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    data = json.loads(request.body)
    post.content = data['content']
    post.save()

    return JsonResponse({"content": data['content']}, status=200)


def get_pagination_posts(request, posts):
    """
    Helper function that returns a Page of posts
    """
    # Creates paginator that will only show 10 posts per page
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page', 1)
    return paginator.get_page(page_number)
