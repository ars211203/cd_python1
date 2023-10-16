# import modules
from django.shortcuts import render,redirect,HttpResponse
from blogsite.forms import UserProfileForm,UserForm,PostForm,CategoryForm,TagForm
from django.contrib.auth import authenticate,login,logout,decorators
from django.contrib.auth.mixins import LoginRequiredMixin 
from django.views import View
from .models import Post,Category,User,Tag,Draft,Comment,UserProfileInfo,Favorites,ReadingHistory,Review
from django.shortcuts import get_object_or_404
from django.http import JsonResponse,Http404
from operator import attrgetter
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.paginator import Paginator

#method 
def get_superuser_data(user):
    if user.is_superuser:
        return True
    else:
        return False
def not_found_page(request):
    return render(request,'404/index.html')
def not_have_access(request):
    return render(request,'403/index.html')
# Create your views here.
def index(request):
    #all post 
    all_post = Post.objects.filter(status='published')
    #get new post
    new_post = None
    get_new_post = Post.objects.filter(status='published').order_by('-created_at').first()
    if get_new_post:
        new_post = get_new_post
    #get 4 post
    limited_posts = all_post[:4]
    #Popular
    category = Category.objects.all()
    popular_post = None  # Khởi tạo popular_post với giá trị mặc định là None
    popular = all_post.order_by('-read_count')
    if popular.exists():
        popular_post = popular[:4]
    #context
    #all_category
    context = {
        'new_post': new_post,
        'limited_posts': limited_posts,
        'all_post': all_post,
        'popular_post': popular_post,
        'category':category,
    }
    return render(request, 'wsite/index.html', context)
# Blogs
def detail_post(request,post_id):
    post_exists  = Post.objects.filter(id=post_id).exists()
    if post_exists:
        post = Post.objects.get(id=post_id)
        related_posts = Post.objects.filter(categories__in=post.categories.all()).exclude(id=post_id)[:3]
        #read_count
        post.read_count += 1
        post.save()
        #comment_list
        comment = Comment.objects.filter(post=post)
        review = Review.objects.filter(post=post)
        is_login = False
        is_favorite = False
        favorite = None
        history = None
        is_rating = False
        if request.user.is_authenticated:
            is_login = True
            existing_favorites = Favorites.objects.filter(post=post, author=request.user).exists()
            existing_history = ReadingHistory.objects.filter(post=post,user=request.user).exists()
            #check mode user
            user = UserProfileInfo.objects.get(user=request.user)
            if existing_favorites:
                favorite = Favorites.objects.get(post=post,author=request.user)
                is_favorite = True
            if not existing_history and user.mode == 'public':
                history = ReadingHistory(post=post, user=request.user)
                history.save()
            #rating
            rating = request.POST.get('rating')
            if rating:
                Review.objects.create(post = post,author = request.user,rating = rating)
                is_rating = True
        else:
            is_login = False
        context = {
            'post': post,
            'is_favorite':is_favorite,
            'favorite':favorite,
            'comment':comment,
            'myurl':request.get_full_path(),
            'related_posts':related_posts,
            'review':review,
            'is_rating':is_rating,
        }
        return render(request,'wsite/blog/posts/index.html',context)
    else:
        return redirect('404')
    

#auth
def register(request):
    registered = False 
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'profile_pic' in request.FILES:
                profile.profile_pic = request.FILES['profile_pic']
            profile.save()

            registered = True
            return redirect('login')
        else:
            print(user_form.errors,profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    return render(request,'auth/signup.html',{'user_form':user_form,
                                        'profile_form':profile_form,})
class LoginView(View):
    def get(self, request):
        return render(request, 'auth/login.html')
    def post(self,request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username,password=password)
        if user is None:
            context = {
                'error_message': 'Đăng nhập không thành công. Vui lòng kiểm tra lại tên người dùng và mật khẩu.'
            }
            return render(request, 'auth/login.html', context)
        login(request,user)
        return redirect('index')                                                                                            
def LogoutView(request):
    logout(request)
    return redirect('index')
class UserView(View):
    def get(self,request):
        if not request.user.is_authenticated:
            return HttpResponse('ban phai dang nhap')
        else:
            return HttpResponse('day la view users')
@decorators.login_required(login_url='login')   
def ProfileView(request):
    favorites = Favorites.objects.filter(author=request.user)
    readinghistory = ReadingHistory.objects.filter(user=request.user)
    reviews = Review.objects.filter(author=request.user)
    profile_user = UserProfileInfo.objects.filter(user=request.user)
    context = {
        'favorites': favorites,
        'readinghistory':readinghistory,
        'profile_user':profile_user,
        'reviews':reviews,
    }
    return render(request,'auth/profile.html',context)



def post_by_author(request):
    return render(request,'wsite/blog/post_by_author.html')

def ViewAbout(request):
    return render(request,'wsite/blog/about.html')

#admin
@decorators.login_required(login_url='login')
def ViewAdmin(request):
    if get_superuser_data(request.user):
        return render(request,'admin/index.html')
    else:
        return redirect('403')
#admin-user --------- @decorators.login_required(login_url='login')
@decorators.login_required(login_url='login')
def ViewAdmin_User(request):
    if get_superuser_data(request.user):
        users = User.objects.all()
        user_profiles = UserProfileInfo.objects.filter(user__in=users)
        context = {
            'user': users,
            'user_profiles': user_profiles,
        }
        return render(request, 'admin/user/index.html', context)
    else:
        return redirect('403')
class ViewCreateUser(View):
    def get(self,request):
        if get_superuser_data(request.user):
            return render(request,'admin/user/create.html')
        else:
            return redirect('403')
    def post(self,request):
        registered = False 
        if request.method == 'POST':
            user_form = UserForm(data=request.POST)
            profile_form = UserProfileForm(data=request.POST)

            if user_form.is_valid() and profile_form.is_valid():
                user = user_form.save()
                user.set_password(user.password)
                user.save()

                profile = profile_form.save(commit=False)
                profile.user = user

                if 'profile_pic' in request.FILES:
                    profile.profile_pic = request.FILES['profile_pic']
                profile.mode = 'public'
                profile.save()

                registered = True
                return redirect('user')
            else:
                print(user_form.errors,profile_form.errors)
        else:
            user_form = UserForm()
            profile_form = UserProfileForm()
        return redirect('user')

@decorators.login_required(login_url='login')
def delete_user(request, user_id):
    if get_superuser_data(request.user):
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return redirect('user')
        except ObjectDoesNotExist:
            return redirect('404')
    else:
        return redirect('403')
def post_by_category(request,category_id):
    posts = None
    try:
        category = Category.objects.get(id=category_id)
        posts = Post.objects.filter(categories=category)
    except ObjectDoesNotExist:
        return redirect('404')
    context = {
        'category_post':category,
        'posts':posts,
    }
    return render(request,'wsite/blog/post_by_category.html',context)
@decorators.login_required(login_url='login')
def edit_user(request,user_id):
    if get_superuser_data(request.user):
        user = User.objects.get(id=user_id)
        return render(request,'admin/user/edit.html',context={'user':user})
    else:
        return redirect('403')
@decorators.login_required(login_url='login')
def update(request, user_id):
    if get_superuser_data(request.user):
        user = User.objects.get(id=user_id)
        if user:
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.username = request.POST.get('username')
            user.email = request.POST.get('email')
            user.set_password(request.POST.get('password'))
            user.profile_pic = request.FILES.get('profile_pic')
            user.save()
            return redirect('user')
        else:
            return redirect('404')
    else:
        return redirect('403')
#admin_post --------- @decorators.login_required(login_url='login')
@decorators.login_required(login_url='login')
def viewAdmin_Post(request):
    if get_superuser_data(request.user):
        post = Post.objects.all()
        context = {'post':post}
        return render(request,'admin/post/index.html',context)
    else:
        return redirect('403')
@decorators.login_required(login_url='login')
def delete_post(request,post_id):
    if get_superuser_data(request.user):
        try:
            post = Post.objects.get(id=post_id)
            post.delete()
            return redirect('admin_post')
        except ObjectDoesNotExist:
            return redirect('404')
    else:
        redirect('403')
@decorators.login_required(login_url='login')
def create_post(request):
    if get_superuser_data(request.user):
        categories = Category.objects.all()
        tag = Tag.objects.all()
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                post.save()
                form.save_m2m()
                draft = Draft.objects.create(post=post, can_push=False)
                return redirect('admin_post')
        else:
            form = PostForm()
        context= {
            'categories':categories,
            'tags':tag,  
            'form': form
        }
        return render(request, 'admin/post/create.html',context)
    else:
        return redirect('403')
class UpdatePost(View):
    def get(self, request, post_id):
        if get_object_or_404(request.user):
            categories = Category.objects.all()
            tags = Tag.objects.all()
            post = Post.objects.get(id=post_id)
            context = {
                'categories': categories,
                'post': post,
                'tags': tags,
            }
            return render(request, 'admin/post/edit.html', context)
        else:
            return redirect('403')
    def post(self, request, post_id):
        post = Post.objects.get(id=post_id)
        if post:
            post.delete()
        return redirect('admin_post_list')  # Chuyển hướng đến trang danh sách bài viết
#admin_category --------- @decorators.login_required(login_url='login')
@decorators.login_required(login_url='login')
def ViewCategory(request):
    if get_superuser_data(request.user):
        category = Category.objects.all()
        context = {'category':category}
        return render(request,'admin/category/index.html',context)
    else:
        return redirect('403')
class ViewCreateCategory(View):
    def get(self,request):
        if get_superuser_data(request.user):
            return render(request,'admin/category/create.html')
        else:
            return redirect('403')
    def post(self,request):
        if request.method == 'POST':
            form = CategoryForm(data=request.POST)
            if form.is_valid:
                category = form.save()
                category.save()
                return redirect('admin_category')
@decorators.login_required(login_url='login')
def DeleteCategory(request,category_id):
    if get_superuser_data(request.user):
        try:
            category = Category.objects.get(id=category_id)
            category.delete()
            return redirect('admin_category')
        except ObjectDoesNotExist:
            return redirect('404')
    else:
        return redirect('403')
@decorators.login_required(login_url='login')
def EditCategory(request,category_id):
    if get_superuser_data(request.user):
        category = Category.objects.get(id=category_id)
        context={'category':category}
        return render(request,'admin/category/edit.html',context)
    else:
        return redirect('403')
@decorators.login_required(login_url='login')
def UpdateCategory(request,category_id):
    if get_object_or_404(request.user):
        category = Category.objects.get(id=category_id)
        category.name = request.POST.get('name')
        category.slug = request.POST.get('slug')
        category.save()
        return redirect('admin_category')
    else:
        return redirect('403')
#admin_tags --------- @decorators.login_required(login_url='login')
@decorators.login_required(login_url='login')
def ViewTag(request):
    if get_superuser_data(request.user):
        tag = Tag.objects.all()
        context = {'tag':tag}
        return render(request,'admin/tag/index.html',context)
    else:
        return redirect('403')
class ViewCreateTag(View):
    def get(self,request):
        if get_object_or_404(request.user):
            return render(request,'admin/tag/create.html')
        else:
            return redirect('403')
    def post(self,request):
        if get_superuser_data(request.user):
            if request.method == 'POST':
                form = TagForm(data=request.POST)
                if form.is_valid:
                    tag = form.save()
                    tag.save()
                    return redirect('admin_tag')
        else:
            return redirect('403')
@decorators.login_required(login_url='login')
def EditTag(request,tag_id):
    if get_object_or_404(request.user):
        tag = Tag.objects.get(id=tag_id)
        context={'tag':tag}
        return render(request,'admin/tag/edit.html',context)
    else:
        return redirect('403')
@decorators.login_required(login_url='login')
def UpdateTag(request,tag_id):
    if get_superuser_data(request.user):
        tag = Tag.objects.get(id=tag_id)
        tag.name = request.POST.get('name')
        tag.slug = request.POST.get('slug')
        tag.save()
        return redirect('admin_tag')
    else:
        return redirect('403')
@decorators.login_required(login_url='login')
def DeleteTag(request,tag_id):
    if get_superuser_data(request.user):
        try:
            tag = Tag.objects.get(id=tag_id)
            tag.delete()
            return redirect('admin_tag')
        except ObjectDoesNotExist:
            return redirect('404')
    else:
        return redirect('403')
#admin_draft --------- @decorators.login_required(login_url='login')
@decorators.login_required(login_url='login')
def ViewDraft(reqeust):
    if get_superuser_data(reqeust.user):
        draft_posts = Draft.objects.all()
        context = {
            'draft_posts':draft_posts,
        }
        return render(reqeust,'admin/draft/index.html',context)
    else:
        return redirect('403')


@decorators.login_required(login_url='login')
def get_post_draft(request, post_id):
    post = Post.objects.get(id=post_id)
    #comment
    if request.method == 'POST':
        comment_content = request.POST.get('content')
        comment = Comment.objects.create(post=post, author=request.user, content=comment_content)
        comment.save()
        return redirect('draft_detail')
    comments = Comment.objects.filter(post=post)
    context = {
        'post':post,
        'comments':comments,
    }
    return render(request,'admin/draft/detail.html',context)

@decorators.login_required(login_url='login')
def publish_post(request, draft_id):
    if get_superuser_data(request.user):
        try:
            draft = Draft.objects.get(id=draft_id)
            draft.can_push = True
            if draft.can_push:
                draft.post.status = 'published'
                draft.post.save()
                draft.delete()
                return redirect('admin_draft')
            else:
                return redirect('404')
        except Draft.DoesNotExist:
            return redirect('404')
    else:
        return redirect('403')
@decorators.login_required(login_url='login')
def comment_post(request, post_id):
    post = Post.objects.get(id=post_id)
    if post is None:
        return redirect('404')
    else:
        if request.method == 'POST':
            comment_content = request.POST.get('content')
            comment = Comment.objects.create(post=post, author=request.user, content=comment_content)
            comment.save()
            return redirect('detail_post',post.id)
#favorite
def del_favorite(request, favorites_id):
    favorite = Favorites.objects.filter(id=favorites_id).first()

    if favorite is None:
        return redirect('404')
    
    favorite.delete()
    return redirect('detail_post', favorite.post.id)
def add_favorite(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if Favorites.objects.filter(post=post, author=request.user).exists():
        return redirect('detail_post', post.id)
    
    favorite = Favorites.objects.create(post=post, author=request.user)
    favorite.save()
    return redirect('detail_post', post.id)

#mode user
@decorators.login_required(login_url='login')
def mode_incognito(request):
    mode_user = UserProfileInfo.objects.get(user=request.user)
    mode_user.mode = 'incognito'
    mode_user.save()
    return redirect('profile')
@decorators.login_required(login_url='login')
def mode_public(request):
    mode_user = UserProfileInfo.objects.get(user=request.user)
    mode_user.mode = 'public'
    mode_user.save()
    return redirect('profile')

#
def delete_reading_history(request, history_id):
    reading_history = ReadingHistory.objects.filter(id=history_id).first()
    
    if reading_history is None:
        return redirect('404')
    
    reading_history.delete()
    return redirect('profile')
#search
def resultSearch(request):
    searched =''
    page = None
    if request.method == "POST":
        searched = request.POST.get("searched", "")
        posts = Post.objects.filter(title__icontains=searched)
        # Phân trang
        page = Paginator(posts, 4)
        page_list = request.GET.get('page')
        page = page.get_page(page_list)

    context = {
        'searched': searched,
        'page': page,
    }
    return render(request, 'wsite/blog/posts/search.html', context)
#change pass
def view_change_pass(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user,request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request,user)
            return redirect('profile')
        else:
            return HttpResponse('khong doi dc')
    else:
        form = PasswordChangeForm(request.user)
    return render(request,'auth/change_pass.html',{'form':form})
#@decorators.login_required(login_url='login')
def del_review(request, review_id):
    review = Review.objects.filter(id=review_id).first()
    if review is None:
        return redirect('404')
    review.delete()
    return redirect('profile')