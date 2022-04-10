from asgiref.sync import async_to_sync
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from network.models import User, Post, Follower, Like
from django import forms
from django.db.models import OuterRef, Count
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from project4.consumers import SocialNetWorkConsumer
from channels.layers import get_channel_layer

MAX_NUMBER_OF_POSTS_PAGE = 10


def index(req):

    if req.user.is_authenticated:
        userRegisted = req.session['_auth_user_id']
        userLikes = Like.objects.filter(
            post=OuterRef('id'), user_id=userRegisted)
        userPosts = Post.objects.filter().order_by(
            '-post_date').annotate(current_like=Count(userLikes.values('id')))
    else:
        userPosts = Post.objects.order_by('-post_date').all()
    userPosts = formatDateTime(userPosts)
    pagePost = calculateNewFeed(req, userPosts)
    return render(req, "network/index.html", {
        'posts': pagePost,
    })


def formatDateTime(pagePost):
    newPagePost = []
    for item in pagePost:
        item.post_date = item.post_date.strftime("%b %d %Y, %I:%M %p")
        newPagePost.append(item)
    return newPagePost


@csrf_exempt
@login_required
def getLoginUser(req):
    userRegisted = req.session['_auth_user_id']
    userPost = User.objects.get(id=userRegisted)
    result = userPost.serializerData()
    return JsonResponse(result, status=200)


@csrf_exempt
@login_required
def userPostSent(req):
    if req.method != "POST":
        return JsonResponse(status=400)
    data = json.loads(req.body)
    userPost = User.objects.get(id=req.session['_auth_user_id'])
    content = data
    postCreated = Post(user=userPost, text=content)
    postCreated.save()
    result = postCreated.serializerData()
    result['username'] = userPost.username
    result['user_id'] = userPost.id
    return JsonResponse(result, status=200)


@csrf_exempt
@login_required
def userProfile(req, username):
    userFollowers = 0
    userProfile = User.objects.get(username=username)
    userRequest = req.session['_auth_user_id']
    userFollowers = Follower.objects.filter(
        follower=userRequest, following=userProfile).count()
    userLikes = Like.objects.filter(
        post=OuterRef('id'), user_id=userRequest)
    userPost = Post.objects.filter(user=userProfile).order_by(
        'post_date').annotate(current_like=Count(userLikes.values('id')))

    numberFollowings = Follower.objects.filter(
        follower=userProfile).count()
    numberFollowers = Follower.objects.filter(
        following=userProfile).count()
    userPost = formatDateTime(userPost)
    page_obj = calculateNewFeed(req, userPost)
    return render(req, "network/userProfilePage.html", {
        'user_profile': userProfile,
        'posts': page_obj,
        'is_following': userFollowers,
        'total_following': numberFollowings,
        'total_followers': numberFollowers,
    })


def calculateNewFeed(req, userPosts):
    pagePaginator = Paginator(userPosts, MAX_NUMBER_OF_POSTS_PAGE)
    pageNum = req.GET.get('page')
    return pagePaginator.get_page(pageNum)


@csrf_exempt
@login_required
def userFollowFunction(req):

    userRegisted = req.session['_auth_user_id']
    followersUser = Follower.objects.filter(follower=userRegisted)
    likesUser = Like.objects.filter(post=OuterRef('id'), user_id=userRegisted)
    userPosts = Post.objects.filter(user_id__in=followersUser.values('following_id')).order_by(
        '-post_date').annotate(current_like=Count(likesUser.values('id')))
    userPosts = formatDateTime(userPosts)
    pagePost = calculateNewFeed(req, userPosts)
    return render(req, "network/followingUser.html", {
        'posts': pagePost,
    })


@csrf_exempt
@login_required
def userPostEdit(req, id):
    if req.is_ajax and req.method == "POST":
        content = json.loads(req.body)
        Post.objects.filter(
            id=id, user_id=req.session['_auth_user_id']).update(text=content)
        return JsonResponse({"result": 'ok', 'text': content})

    return JsonResponse({"error": "Bad request"}, status=400)


@csrf_exempt
@login_required
def userFollow(req, id):
    try:
        isFollow = 'follow'
        userGetFromDB = User.objects.get(id=req.session['_auth_user_id'])
        userGetFromDBById = User.objects.get(id=id)
        userFollower = Follower.objects.get_or_create(
            follower=userGetFromDB, following=userGetFromDBById)
        if not userFollower[1]:
            Follower.objects.filter(
                follower=userGetFromDB, following=userGetFromDBById).delete()
            isFollow = 'unfollow'
        numberFollowers = Follower.objects.filter(
            following=userGetFromDBById).count()
    except KeyError:
        return HttpResponseBadRequest("No content")
    return JsonResponse({"result": isFollow, "total_followers": numberFollowers})


@csrf_exempt
@login_required
def handleLikeForUser(req, id):
    try:
        userRequested = req.session['_auth_user_id']
        changeCSS = 'fas fa-heart'
        userTrigger = User.objects.get(id=userRequested)
        postGetLike = Post.objects.get(id=id)
        likeObject = Like.objects.get_or_create(
            user=userTrigger, post=postGetLike)
        if not likeObject[1]:
            changeCSS = 'far fa-heart'
            Like.objects.filter(user=userTrigger, post=postGetLike).delete()
        total_likes = Like.objects.filter(post=postGetLike).count()
    except KeyError:
        return HttpResponseBadRequest("No content")
    return JsonResponse({
        "idPost": id, "css_class": changeCSS, "total_likes": total_likes
    })


@csrf_exempt
def loginPage(req):
    if req.method == "POST":
        userNameInput = req.POST["username"]
        passwordInput = req.POST["password"]
        validUser = authenticate(
            req, username=userNameInput, password=passwordInput)
        if validUser is not None:
            login(req, validUser)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(req, "network/loginPage.html", {
                "message": "Invalid username or password."
            })
    return render(req, "network/loginPage.html")


def logoutPage(req):
    logout(req)
    return HttpResponseRedirect(reverse("index"))


@csrf_exempt
def registerForApp(req):
    if req.method == "POST":
        usernameInput = req.POST["username"]
        userEmail = req.POST["email"]

        passwordInput = req.POST["password"]
        confirmationInput = req.POST["confirmation"]
        if not isMatchingPassword(passwordInput, confirmationInput):
            return render(req, "network/registerPage.html", {
                "message": "These passwords must match."
            })
        try:
            userRegisted = User.objects.create_user(
                usernameInput, userEmail, passwordInput)
            userRegisted.save()
        except IntegrityError:
            return render(req, "network/registerPage.html", {
                "message": "This name is already taken."
            })
        login(req, userRegisted)
        return HttpResponseRedirect(reverse("index"))
    return render(req, "network/registerPage.html")


def isMatchingPassword(password, confirm):
    return password == confirm
