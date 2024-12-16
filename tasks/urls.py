from django.urls import path, include
from tasks import views
from .views import auditlog_view, protected_media
#from two_factor.views import LoginView, SetupView


urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('tasks/', views.tasks, name='tasks'),
    path('tasks_completed/', views.tasks_completed, name='tasks_completed'),
    path('logout/', views.signout, name='logout'),
    path('signin/', views.signin, name='signin'),
    #path('create_task/', views.create_task, name='create_task'),
    path('tasks/<int:task_id>', views.task_detail, name='task_detail'),
    path('taks/<int:task_id>/complete', views.complete_task, name='complete_task'),
    path('tasks/<int:task_id>/delete', views.delete_task, name='delete_task'),
    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('create_recipe/', views.create_recipe, name='create_recipe'),
    path('recipe/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('my_recipes/', views.my_recipes, name='my_recipes'),
    path('recipes/<int:recipe_id>/edit/', views.edit_recipe, name='recipe_edit'),
    path('rate_recipe/<int:recipe_id>/', views.rate_recipe, name='recipe_rate'),
    path('comment_recipe/<int:recipe_id>/', views.comment_recipe, name='recipe_comment'),
    path('comments/add/', views.add_comment, name='add_comment'),
    path('comments/reply/', views.reply_to_comment, name='reply_to_comment'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/manage-users/', views.manage_users, name='manage_users'),
    path('admin/manage-recipes/', views.manage_recipes, name='manage_recipes'),
    path('admin/manage-comments/', views.manage_comments, name='manage_comments'),
    path('profile/', views.user_profile, name='user_profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('change-password/', views.change_password, name='change_password'),
]

urlpatterns += [
    path('admin/auditlog/', auditlog_view, name='auditlog_view'),
    path('cambiar_contraseña/', views.force_password_change, name='force_password_change'),
    path('password_change/', views.custom_password_change, name='password_change'),
    path('password_change/done/', views.password_change_done, name='password_change_done'),
    path('favorites/', views.favorite_recipes, name='favorite_recipes'),
    path('favorites/add/<int:recipe_id>/', views.add_to_favorites, name='add_to_favorites'),
    path('favorites/remove/<int:recipe_id>/', views.remove_from_favorites, name='remove_from_favorites'),
    path('media/<path:path>/', protected_media, name='protected_media'),
    path('accounts/', include('allauth.urls')),
] 

