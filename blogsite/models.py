#import modules
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.shortcuts import get_object_or_404
from django.core.validators import MaxLengthValidator,MinLengthValidator

    
#model blogs
class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name
class Tag(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    def __str__(self):
        return self.name    
class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to='images',null=False,default=None,blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField('Category')
    tags = models.ManyToManyField('Tag')
    read_count = models.IntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')

    def move_to_draft(self):
        self.status = 'draft'
        self.save()
    def __str__(self):
        return self.title
    def get_latest_published_post():
        latest_post = Post.objects.filter(status='published').order_by('-created_at').first()
        return latest_post
    
class Draft(models.Model):
    post = models.OneToOneField('Post', on_delete=models.CASCADE)
    can_push = models.BooleanField(default=False)
    def push_post(self):
        if self.can_push:
            self.post.status = 'published'
            self.post.save()

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content


class Favorites(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Review(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0,
            validators= [
                MaxLengthValidator(5),
                MinLengthValidator(0),
            ]
    )
    created_at = models.DateTimeField(auto_now_add=True)

class ReadingHistory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.userd


class UserProfileInfo(models.Model):
    MODE_CHOICES = (
        ('incognito', 'Incognito '),
        ('public', 'Public'),
    )
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pic',blank=True)
    mode = models.CharField(max_length=10, choices=MODE_CHOICES, default='public')
    def __str__(self):
        return self.user.username


