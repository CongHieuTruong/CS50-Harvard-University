from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db import models
class Auction(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='for_user_main_auction_page')
    description = models.TextField()
    title = models.CharField(max_length=100)
    person = models.ForeignKey('Person', on_delete=models.CASCADE, related_name='person_of_auction', default=1)
    starting_bid = models.IntegerField()
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='category_of_auction', default=3)
    bids = models.ManyToManyField('Bid', related_name='bids_of_auction', blank=True)
    comments = models.ManyToManyField('Comment', related_name='comments_of_auction', blank=True)
    closed = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.now)
    last_bid = models.ForeignKey('Bid', on_delete=models.CASCADE, related_name='last_bid_of_auction', blank=True, null=True)
    image = models.ImageField(upload_to='images')
    
    def __str__(self):
        return self.title
    
    def datepublished(self):
        return self.date.strftime('%B %d %Y')

class Comment(models.Model):
    date = models.DateTimeField(default=timezone.now)
    comment = models.TextField()
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='user_comment')
    def __str__(self):
        return '%s %s' % (self.user, self.date)
class Bid(models.Model):
    auction = models.ForeignKey('Auction', on_delete=models.CASCADE, related_name='auction_bid')
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='user_place_bid')
    date = models.DateTimeField(default=timezone.now)
    bid = models.IntegerField()

    def __str__(self):
        return '%s' % (self.bid)

class PersonToCategory(models.Model):
    category = models.ManyToManyField('Category', blank=True, null=True)
    person = models.CharField(max_length=60)
    def __str__(self):
        return self.person
class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class User(AbstractUser):
    pass

class PersonalWatchlist(models.Model):
    auctions = models.ManyToManyField('Auction', related_name='auctions_of_personal_watchlist', blank=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='user_of_personal_watchlist')
    def __str__(self):
        return 'User WatchList: %s' % (self.user)
        
class Person(models.Model):
    category = models.ManyToManyField('Category', blank=True, null=True)
    person = models.CharField(max_length=60)
    def __str__(self):
        return self.person
