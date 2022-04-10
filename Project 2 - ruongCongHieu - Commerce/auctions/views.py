from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import User, Auction, Bid, Category, Comment, PersonalWatchlist, Person
from .forms import AuctionForm


def index(req):
    allAuctions = queryAll(Auction).order_by('id').reverse()
    usersStoraged = queryAll(Person)
    userCategory = queryAll(Category)
    userRequest = req.user
    if userRequest.id is None:
        context = {
            'auctions': allAuctions,
            'persons': usersStoraged,
        }
        return render(req, "auctions/index.html", context)
    userWatchlist = PersonalWatchlist.objects.get(user=req.user)
    numberOfAuctions = userWatchlist.auctions.count()
    context = {
        'auctions': allAuctions,
        'totalAuctions': numberOfAuctions,
        'my_watchlist': userWatchlist,
        'persons': usersStoraged,
        'userCategory': userCategory
    }
    return render(req, "auctions/index.html", context)

def queryAll(Models):
    return Models.objects.all()

def add_auction_item(req):
    usersStoraged = queryAll(Person)
    userRequest = req.user
    if userRequest.id is None:
        return redirect('login')
    userWatchlist = PersonalWatchlist.objects.get(user=req.user)
    numberOfAuctions = userWatchlist.auctions.count()
    
    if req.method == 'GET':
        context = {
            'form': AuctionForm(),
            'totalAuctions': numberOfAuctions,
            'persons': usersStoraged,
        }

        return render(req, "auctions/auctionsAddPage.html", context)
    else:
        formAuction = AuctionForm(req.POST, req.FILES)

        if formAuction.is_valid():
            title = formAuction.cleaned_data['title']
            description = formAuction.cleaned_data['description']
            starting_bid = formAuction.cleaned_data['starting_bid']
            category = formAuction.cleaned_data['category']
            person = formAuction.cleaned_data['person']
            image = formAuction.cleaned_data['image']

            # Create auction
            Auction.objects.create(
                user=req.user,
                title=title, 
                description=description, 
                starting_bid=starting_bid,
                category=category,
                person=person,
                image=image,
            )
            
            return redirect('index')


def login_user_view(req):
    if req.method == "POST":

        user_name = req.POST["username"]
        pass_word = req.POST["password"]
        userAuth = authenticate(req, username=user_name, password=pass_word)

        if userAuth is not None:
            login(req, userAuth)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(req, "auctions/loginPage.html", {
                "message": "Invalid username or password."
            })
    else:
        if req.user.is_authenticated:
            return redirect('index')
        return render(req, "auctions/loginPage.html")


def user_logout(req):
    logout(req)
    return HttpResponseRedirect(reverse("index"))


def user_register(req):
    if req.method == "POST":
        user_name = req.POST["username"]
        email_user = req.POST["email"]

        pass_word = req.POST["password"]
        confirmationPassword = req.POST["confirmation"]
        if pass_word != confirmationPassword:
            return render(req, "auctions/registerUserPage.html", {
                "message": "Both of passwords must be match."
            })

        try:
            userRegisted = User.objects.create_user(user_name, email_user, confirmationPassword)
            PersonalWatchlist.objects.create(user=userRegisted)
            userRegisted.save()
        except IntegrityError:
            return render(req, "auctions/registerUserPage.html", {
                "message": "Username already taken. Please use another"
            })
        login(req, userRegisted)
        return HttpResponseRedirect(reverse("index"))
    else:
        if req.user.is_authenticated:
            return redirect('index')
        return render(req, "auctions/registerUserPage.html")




def my_listings_view(req, user):
    userQuery = User.objects.get(username=user)
    auctionsFilterByUser = Auction.objects.filter(user=userQuery)
    userWatchlist = PersonalWatchlist.objects.get(user=req.user)
    numberOfAuction = userWatchlist.auctions.count()
    userRequestName = req.user.username

    if userRequestName != user:
        return redirect('my_listings_view', user=userRequestName)

    context = {
        'auctions': auctionsFilterByUser,
        'my_watchlist': userWatchlist,
        'totalAuctions': numberOfAuction,
    }

    return render(req, "auctions/myListingsPage.html", context)


def watchlist_item(req):
    if req.method == 'GET':

        userRequest = req.user
        if userRequest.id is None:
            return redirect('index')

        userStoraged = queryAll(Person)
        userWatchlist = PersonalWatchlist.objects.get(user=userRequest)
        numberOfAuction = userWatchlist.auctions.count()
        userCategory = queryAll(Category)
        context = {
            'my_watchlist': userWatchlist,
            'persons': userStoraged,
            'totalAuctions': numberOfAuction,
            'userCategory': userCategory
        }
        return render(req, "auctions/watchlistPage.html", context)



def category(req, category):
    categoryQueryByName = Category.objects.get(name=category)
    auctionFilter = Auction.objects.filter(category=categoryQueryByName).order_by('id').reverse()
    usersStoraged = queryAll(Person)
    userCategory = queryAll(Category)
    userRequest = req.user

    if userRequest.id is None:
        return render(req, "auctions/index.html")
    
    context = {
        'category_name': categoryQueryByName,
        'auctions': auctionFilter,
        'totalAuctions': PersonalWatchlist.objects.get(user=req.user).auctions.count(),
        'persons': usersStoraged,
        'userCategory': userCategory
    }
    return render(req, "auctions/categoryPage.html", context)

def add_watchlist(req, auction):
    if req.method == 'POST':
        auctionQueryById = Auction.objects.get(id=auction)
        userWatchlist = PersonalWatchlist.objects.get(user=req.user)
        if auctionQueryById in userWatchlist.auctions.all():
            userWatchlist.auctions.remove(auctionQueryById)
            userWatchlist.save()
        else:
            userWatchlist.auctions.add(auctionQueryById)
            userWatchlist.save()
        return HttpResponse('success')

def auction_view_page(req, auction):
    if req.method == 'GET':
        userStoraged = queryAll(Person)
        requestUserId = req.user.id
        if requestUserId is None:
            return redirect('login')

        userWatchlist = PersonalWatchlist.objects.get(user=req.user)
        numberOfAuction = userWatchlist.auctions.count()
        auctionQueryById = Auction.objects.get(id=auction)
        commentsAdded = auctionQueryById.comments.all().order_by('id').reverse()
        userCategory = queryAll(Category)
        context = {
            'auction': auctionQueryById,
            'my_watchlist': userWatchlist,
            'persons': userStoraged,
            'comments': commentsAdded,
            'totalAuctions':numberOfAuction,
            'userCategory': userCategory
        }
        return render(req, 'auctions/auctionUserPage.html', context)

def add_user_comment(req, auction):
    if req.method == 'POST':
        auctionQueryById = Auction.objects.get(id=auction)
        userComment = req.POST['comment']
        if not userComment:
            return HttpResponseRedirect(req.META.get('HTTP_REFERER', '/'))
        commentCreated = Comment.objects.create(comment=userComment, user=req.user)
        auctionQueryById.comments.add(commentCreated)
        auctionQueryById.save()
        return HttpResponseRedirect(req.META.get('HTTP_REFERER', '/'))


def update_auction_bid(req, auction):
    if req.method == 'POST':
        totalBidUpdate = req.POST["totalBid"]
        auctionQueryById = Auction.objects.get(id=auction)
        bidCreated = Bid.objects.create(user=req.user, auction=auctionQueryById, bid=totalBidUpdate)
        auctionQueryById.bids.add(bidCreated)
        auctionQueryById.last_bid = bidCreated
        auctionQueryById.save()
        return HttpResponse('success')



def user_delete_auction(req, auction):
    if req.method == 'GET':
        auctionQueryById = Auction.objects.get(id=auction)
        requestUser = req.user
        if auctionQueryById.user == requestUser:
            auctionQueryById.delete()
            return redirect('index')

def user_close_listing(req, auction):
    if req.method == 'GET':
        auctionQueryById = Auction.objects.get(id=auction)
        auctionQueryById.closed = True
        auctionQueryById.save()
        return HttpResponseRedirect(req.META.get('HTTP_REFERER', '/'))

def delete_user_comment(req, comment):
    if req.method == 'POST':
        commentQueryById = Comment.objects.get(id=comment)
        commentQueryById.delete()
        return HttpResponse('success')

def delete_item_from_watchlist_page(req, auction):
    if req.method == 'POST':
        auctionQueryById = Auction.objects.get(id=auction)
        userWatchlist = PersonalWatchlist.objects.get(user=req.user)
        userWatchlist.auctions.remove(auctionQueryById)
        userWatchlist.save()
        userStoraged = queryAll(Person)
        numberOfAuction = userWatchlist.auctions.count()
        context = {
            'my_watchlist': userWatchlist,
            'persons': userStoraged,
            'totalAuctions': numberOfAuction, 
        }
        return render(req, "auctions/watchlistPage.html", context)



