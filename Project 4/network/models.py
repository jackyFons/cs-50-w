from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Follows(models.Model):
    objects = models.manager
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    followers = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")


class Post(models.Model):
    objects = models.manager
    poster = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.CharField(max_length=300, null=True, blank=True)
    liked_by = models.ManyToManyField(User, blank=True, related_name="post_likes")

    def __str__(self):
        return f" {self.poster} posted: {self.content} at {self.timestamp}"

    def likes_count(self):
        return self.liked_by.all().count()

    def serialize(self):
        return {
            "id": self.id,
            "poster": self.poster.username,
            "content": self.content,
            "timestamp": self.timestamp.strftime("%m/%d/%Y, %H:%M"),
            "likes": self.likes_count(),
        }
