
from django.urls import path,re_path
from . import views
from .views import (LoginView,UserView,ViewCreateUser,
                    ViewCreateCategory,ViewCreateTag,
                    UpdatePost
                    )
#class-based views,func base view
urlpatterns = [
    path('',views.index,name="index"),
    #urls method
    path('403',views.not_have_access,name='403'),
    path('404',views.not_found_page,name='404'),
    #auth
    path('login',LoginView.as_view(),name='login'),
    path('logout',views.LogoutView,name='logout'),
    path('register',views.register,name='register'),
    path('profile',views.ProfileView,name='profile'),
    path('user-view/',UserView.as_view(),name='user_view'),
    #bloga
    path('detail-post/<int:post_id>',views.detail_post,name='detail_post'),

    path('post-by-category/<int:category_id>',views.post_by_category,name='post-category'),
    path('post-by-author',views.post_by_author,name='post-author'),
    path('about',views.ViewAbout,name='about'),
    #admin view
    path('myadmin',views.ViewAdmin,name='myadmin'),
    #admin_user
    path('myadmin/user',views.ViewAdmin_User,name='user'),
    path('myadmin/CreateUser',ViewCreateUser.as_view(),name='CreateUser'),
    path('myadmin/delete/user/<int:user_id>',views.delete_user,name='delete_user'),
    path('myadmin/user/edit/<int:user_id>',views.edit_user,name='edit_user'),
    path('myadmin/user/update/<int:user_id>',views.update,name='update_user'),
    #admin_post
    path('myadmin/post',views.viewAdmin_Post,name='admin_post'),
    path('myadmin/delete/post/<int:post_id>',views.delete_post,name='delete_post'),
    path('myadmin/create/post',views.create_post,name='create_post'),
    path('myadmin/edit/post/<int:post_id>',UpdatePost.as_view(),name='edit_post'),
    #admin_category
    path('myadmin/category',views.ViewCategory,name='admin_category'),
    path('myadmin/create/category',ViewCreateCategory.as_view(),name='CreateCategory'),
    path('myadmin/delete/category/<int:category_id>',views.DeleteCategory,name='delete_category'),
    path('myadmin/category/edit/<int:category_id>',views.EditCategory,name='edit_category'),
    path('myadmin/category/update/<int:category_id>',views.UpdateCategory,name='update_category'),
    #admin_tags
    path('myadmin/tag',views.ViewTag,name='admin_tag'),
    path('myadmin/create/tag',ViewCreateTag.as_view(),name='CreateTag'),
    path('myadmin/edit/tag/<int:tag_id>',views.EditTag,name='edit_tag'),
    path('myadmin/tag/update/<int:tag_id>',views.UpdateTag,name='update_tag'),
    path('myadmin/delete/tag/<int:tag_id>',views.DeleteTag,name='delete_tag'),
    #admin_draft
    path('myadmin/draft',views.ViewDraft,name='admin_draft'),
    path('myadmin/draft/detail/<int:post_id>',views.get_post_draft,name='draft_detail'),
    path('myadmin/publish/<int:draft_id>/', views.publish_post, name='publish_post'),

    #conmment - post
    path('coment/post/<int:post_id>',views.comment_post,name='comment_post'),
    #favorites - post
    path('add_favorite/post/<int:post_id>',views.add_favorite,name='add_favorite'),
    path('favorite/delete/<int:favorites_id>',views.del_favorite,name='del_favorite'),

    #UserprofileInfo
    path('mode-incognito',views.mode_incognito,name='mode_incognito'),
    path('mode-public',views.mode_public,name='mode_public'),


    #reading history
    path('del-history/<int:history_id>',views.delete_reading_history,name='del_history'),
    #search
    path('search-result',views.resultSearch,name='result_search'),
    path('view_change_pass',views.view_change_pass,name="pass"),
    path('del-review/<int:review_id>',views.del_review,name="del_review"),
] 
