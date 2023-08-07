from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .forms import ListingForm, BidForm, CommentForm
from .models import Listing, User, Comment


def index(request):
    # Changed to return all necessary listings
    return render(request, "auctions/index.html", {
        "title": "Active Listings",
        "listings": Listing.objects.filter(active=True)
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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


# --------- my code ----------------
@login_required
def new_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST, seller=request.user)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.seller = request.user
            listing.current_bid = listing.starting_price
            if listing.url == "":
                listing.url = "https://cdn-icons-png.flaticon.com/512/46/46499.png"
            listing.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        form = ListingForm(seller=request.user)
        context = {'form': form}
        return render(request, "auctions/new_listing.html", context)


@login_required
def watchlist(request):
    user = request.user

    return render(request, "auctions/index.html", {
        "title": "Watchlist",
        "listings": user.watch_list.all()
    })


def categories(request, category=None):
    if category is not None:
        return render(request, "auctions/index.html", {
            "title": category + " Listings",
            "listings": Listing.objects.filter(category=category)
        })
    return render(request, "auctions/categories.html", {
        "categories": ["Art", "Books, Movies, & Music", "Clothing", "Electronics", "Health & Beauty",
                       "Home", "Pet Supplies", "Toys", "Other"]

    })


def view_listing(request, l_id):
    user = request.user
    listing = Listing.objects.get(id=l_id)
    bids = listing.bids.all()
    comments = listing.comments.all()
    if len(bids) > 0:
        has_bid = True
    else:
        has_bid = False

    try:
        winner = bids.latest("bid_amount").bidder

    except:
        winner = None

    if request.method == "POST":
        if "place_bid" in request.POST:
            bid_form = BidForm(request.POST, use_required_attribute=False, bid_listing=listing, bidder=user)
            if bid_form.is_valid():
                bid = bid_form.save(commit=False)
                bid.bid_listing = listing
                bid.bidder = user
                bid.save()

                listing.current_bid = bid.bid_amount
                listing.save()

                return HttpResponseRedirect(reverse("view_listing", kwargs={'l_id': l_id}))

        elif "post_comment" in request.POST:
            comment_form = CommentForm(request.POST, comment_listing=listing, commenter=user)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.comment_listing = listing
                comment.commenter = user
                comment.save()

                return HttpResponseRedirect(reverse("view_listing", kwargs={'l_id': l_id}))

    else:
        bid_form = BidForm(use_required_attribute=False, bid_listing=listing, bidder=user)

    return render(request, "auctions/view_listing.html", {
        "listing": listing,
        "user": user,
        "is_watched": user in listing.watch.all(),
        "comments": comments,
        "bid_form": bid_form,
        "comment_form": CommentForm(comment_listing=listing, commenter=user),
        "winner": winner,
        "has_bid": has_bid
    })


@login_required
def close_listing(request, l_id):
    listing = Listing.objects.get(id=l_id)
    listing.active = False
    listing.save()

    return HttpResponseRedirect(reverse("view_listing", kwargs={"l_id": l_id}))


def delete_listing(request, l_id):
    listing = Listing.objects.get(id=l_id)
    listing.delete()
    return HttpResponseRedirect(reverse("index", ))


@login_required
def change_watchlist(request, l_id):
    user = request.user
    listing = Listing.objects.get(id=l_id)

    if user in listing.watch.all():
        listing.watch.remove(user)
    else:
        listing.watch.add(user)

    return HttpResponseRedirect(reverse("view_listing", kwargs={"l_id": l_id}))


def view_all(request):
    return render(request, "auctions/index.html", {
        "title": "All Listings",
        "listings": Listing.objects.all()
    })