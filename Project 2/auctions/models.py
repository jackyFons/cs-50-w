import decimal

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.conf import settings

from django.db import models


class User(AbstractUser):
    pass


class Listing(models.Model):
    objects = models.Manager()

    listing_categories = (
        ("Art", "Art"), ("Books, Movie, & Music", "Books, Movies, & Music"),
        ("Clothing", "Clothing"), ("Electronics", "Electronics"),
        ("Health & Beauty", "Health & Beauty"), ("Home", "Home"),
        ("Pet Supplies", "Pet Supplies"), ("Toys", "Toys"), ("Other", "Other"))

    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    watch = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="watch_list", blank=True)
    title = models.CharField(help_text="Title", max_length=25, name="title")
    description = models.TextField(help_text="Description", max_length=1000, name="description")
    starting_price = models.DecimalField(help_text="Starting bid price", decimal_places=2, max_digits=12,
                                         validators=[MinValueValidator(decimal.Decimal('0.01'))], name="starting_price")
    current_bid = models.DecimalField(decimal_places=2, max_digits=12, null=True)
    url = models.URLField(help_text="Listing image URL", blank=True, name="url")
    category = models.CharField(help_text="Category", max_length=50, choices=listing_categories,
                                blank=True, name="category")

    def __str__(self):
        return f"{self.title}: {self.description} \nSeller: {self.seller}"


class Bid(models.Model):
    objects = models.Manager
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids", null=True)
    bid_listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids", null=True)
    bid_amount = models.DecimalField(decimal_places=2, max_digits=12, default=0)

    def __str__(self):
        return f"{self.bidder} bids ${self.bid_amount} on {self.bid_listing.title}"


class Comment(models.Model):
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments", null=True)
    comment_listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments", null=True)
    comment = models.TextField(max_length=1000, name="comment", default="")

    def __str__(self):
        return f"{self.comment}\n-{self.commenter}"
