from django import forms
from .models import Listing, Bid, Comment


class ListingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.seller = kwargs.pop("seller")
        super(ListingForm, self).__init__(*args, **kwargs)
        self.fields["title"].widget.attrs.update({"class": "form-control"})
        self.fields["description"].widget.attrs.update({"class": "form-control"})
        self.fields["starting_price"].widget.attrs.update({"class": "form-control amount"})
        self.fields["url"].widget.attrs.update({"class": "form-control"})

    class Meta:
        model = Listing
        fields = ("title", "description", "starting_price", "url", "category")


class BidForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.bid_listing = kwargs.pop("bid_listing")
        self.bidder = kwargs.pop("bidder")
        super(BidForm, self).__init__(*args, **kwargs)
        self.fields["bid_amount"].widget.attrs.update({"class": "form-control amount"})

    def clean(self):
        bid = self.cleaned_data.get("bid_amount")

        if bid:
            if len(self.bid_listing.bids.all()) == 0:
                if bid < self.bid_listing.current_bid:
                    raise forms.ValidationError("Error: Your bid must be at least equal to the starting price.")
            else:
                if bid <= self.bid_listing.current_bid:
                    raise forms.ValidationError("Error: Your bid must be larger than the current bid.")
        return self.cleaned_data

    class Meta:
        model = Bid
        fields = ("bid_amount",)



class CommentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.commenter = kwargs.pop("commenter")
        self.comment_listing = kwargs.pop("comment_listing")
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields["comment"].widget.attrs.update({"class": "form-control"})
        self.fields["comment"].label = "Post a comment:"

    class Meta:
        model = Comment
        fields = ("comment",)
