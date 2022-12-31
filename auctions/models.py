from django.contrib.auth.models import AbstractUser
from django.db import models


class Auction(models.Model):
    user_creator = models.CharField(max_length = 64)
    name = models.CharField(max_length = 100, blank = False)
    information = models.TextField(blank = False)
    startprice = models.IntegerField(blank = False)
    photo = models.URLField()
    category = models.CharField(max_length = 64, blank = False)
    not_closed = models.BooleanField(default = True)


class User(AbstractUser): 
    auctions = models.ManyToManyField(Auction, blank = True, related_name = "users")

    def __str__(self):
        return f"{self.username}"


class Rate(models.Model):    
    rate = models.IntegerField()   
    rating_user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "rates")
    auction = models.ForeignKey(Auction, on_delete = models.CASCADE, related_name = "rate_auction")

    def __str__(self):
        return f"{self.rating_user} {self.rate} {self.auction}"


class Comment(models.Model):    
    comment = models.TextField()  
    commenting_user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "comments")
    auction = models.ForeignKey(Auction, on_delete = models.CASCADE, related_name = "comment_auction")

    def __str__(self):
        return f"{self.commenting_user} {self.comment} {self.auction}"

