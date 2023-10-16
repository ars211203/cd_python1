from django.contrib import admin
from .models import Category, Tag, Post, Comment,UserProfileInfo
from django.urls import reverse
from django.utils.html import format_html

admin.site.site_header = "Admin page"
admin.site.site_title = "Blog admin"
admin.site.index_title = "Quản lý trang admin"

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
admin.site.register(Category, CategoryAdmin)

class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
admin.site.register(Tag, TagAdmin)

class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'author', 'content', 'created_at']
    list_display_links = ['post']
    list_filter = ['post']
    search_fields = ['post__title', 'content']

admin.site.register(Comment, CommentAdmin)

class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'content','read_count', 'get_categories','image', 'author']
    def get_categories(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])
    get_categories.short_description = 'Categories'
    fields = (('title','image'),('categories','tags'),'content','author')
    list_display_links = ['title']
    list_filter = ['author']
    search_fields = ['title', 'content']
    ordering = ['-created_at']
admin.site.register(Post, PostAdmin)



class UserProfileInfoAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_email')  # Các trường muốn hiển thị

    # Định nghĩa một phương thức để lấy email của user
    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = 'Email'  # Mô tả cho trường email

admin.site.register(UserProfileInfo, UserProfileInfoAdmin)