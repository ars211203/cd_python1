from django import forms
from django.contrib.auth.models import User
from .models import UserProfileInfo,Post,Category,Tag,Comment
from django.contrib.auth.mixins import LoginRequiredMixin 

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfileInfo
        fields = ('profile_pic',)

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name','slug')
class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ('name','slug')

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image','categories','tags', 'status']
        widgets = {
            'categories': forms.CheckboxSelectMultiple(),
            'tags': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        self.author = kwargs.pop('author', None)
        super(PostForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(PostForm, self).save(commit=False)
        instance.author = self.author

        if commit:
            instance.save()

        return instance
from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['post', 'author', 'content']
class ImageUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfileInfo
        fields = ['profile_pic']