from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.decorators import login_required 
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Auction, Rate, Comment


CATEGORIA = ["Cars", "Toys", "Love", "Night", "Sky", "Air", "Dom", "My"]


# головна сторінка ----------------------------------------------------------------------------------------------------------------------
def index(request):
    auctions = Auction.objects.all()
    couples_auction_price = []
    for auction in auctions:
        couple = []
        couple.append(auction)
        rates = Rate.objects.filter(auction = auction)
        if rates: 
            last_rate = rates.last()
            last_price = int(last_rate.rate)           
        else:
            last_price = int(auction.startprice)
        couple.append(last_price)
        couples_auction_price.append(couple)
    return render(request, "auctions/index.html", { 
        "couples_auction_price": list(couples_auction_price)
    })


# Увійти ---------------------------------------------------------------------------------------------------------------------------------
def login_view(request):
    if request.method == "POST":

        # Спроба авторизації користувача
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Перевірте, чи успішна автентифікація
        if user is not None:
            login(request, user)
            auctions = user.auctions.all()
            return HttpResponseRedirect(reverse("watchlist", args=(user.username, )))
        
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


# Вийти --------------------------------------------------------------------------------------------------------------------------------
@login_required
def logout_view(request):    
    logout(request)
    return HttpResponseRedirect(reverse("index"))


# Регестрація --------------------------------------------------------------------------------------------------------------------------
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Переконайтеся, що пароль збігається з підтвердженням
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Спроба створити нового користувача
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


# створення нового аукціону ------------------------------------------------------------------------------------------------------------
@login_required 
def new(request):
    if not request.user.is_authenticated:
        return render(request, "auctions/login.html")
 
    if request.method == "POST":
        if not request.POST["name"]:
            return render(request, "auctions/new.html", {
                "categories": CATEGORIA,
                "message": "You have not inputed the auction name!!!"
            })

        elif not request.POST["startprice"]:
            return render(request, "auctions/new.html", {
                "categories": CATEGORIA,
                "message": "You have not inputed the auction startprice!!!"
            })

        elif not request.POST["categories"]:
            return render(request, "auctions/new.html", {
                "categories": CATEGORIA,
                "message": "You have not inputed the auction categories!!!"
            })

        user_id = request.user.id
        user_creator = User.objects.get(pk = user_id)
        auction = Auction(user_creator = user_creator, name = request.POST["name"], 
                          information = request.POST["information"], startprice = request.POST["startprice"], 
                          photo = request.POST["photo"], category = request.POST["categories"], not_closed = True)
        auction.save()
        return HttpResponseRedirect(reverse("auction", args=(auction.id,)))

    return render(request, "auctions/new.html", {
        "categories": CATEGORIA
    })


# переглянути обраний аукціон ----------------------------------------------------------------------------------------------------------
def auction(request, auction_id):
    if not request.user.is_authenticated:
        return render(request, "auctions/login.html")   

    auction = Auction.objects.get(pk = auction_id)             
    rates = Rate.objects.filter(auction = auction)             
    comments = Comment.objects.filter(auction = auction)        
    user = request.user                                        
    auctions = user.auctions.all()                             
    user_creator = str(auction.user_creator)
    current_user = str(user)
    last_rate = rates.last()                                   

   
    if request.method == "POST":       
        if auction in auctions:                                                   
            user.auctions.remove(auction)            
            user.save()            
        else:
            user.auctions.add(auction) 
            user.save() 
        return HttpResponseRedirect(reverse("watchlist", args = (user.username,)))

   
    if auction.not_closed == True:   
        if last_rate:
            actual_price = last_rate.rate
        else:
            actual_price = auction.startprice

        return render(request, "auctions/auction.html", {
            "auctions": auctions,
            "auction": auction, 
            "rates": rates,
            "comments": comments,
            "actual_price": actual_price,
            "user_creator": user_creator,
            "current_user": current_user
        })

    
    else:
        if last_rate:
            user_winner = last_rate.rating_user            
        else: 
            user_winner = auction.user_creator

       
        if user == user_winner:
            return render(request, "auctions/auction.html", {
                "auctions": auctions,
                "auction": auction,
                "rates": rates,
                "comments": comments,
                "message": "Congratulations!!!! You are the winner!!!!!!!"
            })

        
        if user == auction.user_creator and not last_rate:
            return render(request, "auctions/auction.html", {
                "auctions": auctions,
                "auction": auction,
                "rates": rates,
                "comments": comments,
                "message": "No interested buyers were found for your product!"
            })

       
        return render(request, "auctions/auction.html", {
            "auctions": auctions,   
            "auction": auction,
            "rates": rates,
            "comments": comments,
        })


# пошук вибраних аукціонів --------------------------------------------------------------------------------------------------------------
@login_required
def watchlist(request, user_username):
    if not request.user.is_authenticated:
        return render(request, "auctions/login.html")

    user = User.objects.get(username = user_username)
    auctions = user.auctions.all()
    couples_auction_price = []
    for auction in auctions:
        couple = []
        couple.append(auction)
        rates = Rate.objects.filter(auction = auction)
        if rates: 
            last_rate = rates.last()
            last_price = int(last_rate.rate)           
        else:
            last_price = int(auction.startprice)
        couple.append(last_price)
        couples_auction_price.append(couple)    
    return render(request, "auctions/watchlist.html", {
        "user.username": user_username,  
        "auctions": auctions,
        "couples_auction_price": couples_auction_price
    }) 


# коментувати обраний аукціон -----------------------------------------------------------------------------------------------------------
@login_required
def comment(request, auction_id):
    if not request.user.is_authenticated:
        return render(request, "auctions/login.html")

    if request.method == "POST":        
        comment_text = request.POST["comment"]                                 
        commenting_user = request.user                                  
        commented_auction = Auction.objects.get(pk = auction_id)        
        new_comment = Comment(comment = comment_text, commenting_user = commenting_user, auction = commented_auction)
        new_comment.save()
        return HttpResponseRedirect(reverse("auction", args = (commented_auction.id,)))


# оцінити обраний аукціон ----------------------------------------------------------------------------------------------------------------
@login_required
def rate(request, auction_id):
    if not request.user.is_authenticated:
        return render(request, "auctions/login.html")

    if request.method == "POST":
        rate_value = int(request.POST["rate"])                         
        rating_user = request.user                                     
        rated_auction = Auction.objects.get(pk = auction_id)           
        auction_rates = Rate.objects.filter(auction = rated_auction)   

        
        for auction_rate in auction_rates:
            if rate_value <= int(auction_rate.rate):
                return render(request, "auctions/auction.html", {                                                        
                    "message": "The rate is too small",
                    "auctions": rating_user.auctions.all(),
                    "auction": rated_auction, 
                    "rates": auction_rates,
                    "comments": Comment.objects.filter(auction = rated_auction)
                })

        new_rate = Rate(rate = rate_value, rating_user = rating_user, auction = rated_auction)   
        new_rate.save()                                                                         
        return HttpResponseRedirect(reverse("auction", args = (rated_auction.id,)))


# отримати всі категорії ----------------------------------------------------------------------------------------------------------------
def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": CATEGORIA
    })


# отримання поточної категорії ---------------------------------------------------------------------------------------------------------
def category(request, category):
    category = request.GET["categories"]
    auctions = Auction.objects.filter(category = category)
    couples_auction_price = []
    for auction in auctions:
        couple = []
        couple.append(auction)
        rates = Rate.objects.filter(auction = auction)
        if rates: 
            last_rate = rates.last()
            last_price = int(last_rate.rate)           
        else:
            last_price = int(auction.startprice)
        couple.append(last_price)
        couples_auction_price.append(couple)

    return render(request, "auctions/category.html", {
        "category": category,
        "auctions": auctions,
        "couples_auction_price": couples_auction_price
    })


# закриття аукціону --------------------------------------------------------------------------------------------------------------------
@login_required
def close(request, auction_id):
    if not request.user.is_authenticated:
        return render(request, "auctions/login.html")

    auction = Auction.objects.get(pk = auction_id)
    user_creator = str(auction.user_creator)
    curent_user = str(request.user)
    if curent_user == user_creator:
        if request.method == "POST":
            auction.not_closed = False
            auction.save()
            return HttpResponseRedirect(reverse("auction", args = (auction.id,)))
