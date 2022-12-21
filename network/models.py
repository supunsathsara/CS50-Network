from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=280)
    created_at = models.DateTimeField(auto_now_add=True)


class Relationship(models.Model):
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower"
    )
    followed = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followed"
    )


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
