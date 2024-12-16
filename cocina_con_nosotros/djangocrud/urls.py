"""djangocrud URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from tasks import views

urlpatterns = [
    path('',include('tasks.urls')),
    #path('', include('two_factor.urls', 'two_factor')),
    path('admin/', admin.site.urls),
    path('book/', views.recipe_book, name='recipe_book'),
    path('recipe/<int:pk>/', views.recipe_detail, name='recipe_detail'),
    path('my_recipes/', views.my_recipes, name='my_recipes'),
    path('rate_recipe/<int:recipe_id>/', views.rate_recipe, name='recipe_rate'),
    path('comment_recipe/<int:recipe_id>/', views.comment_recipe, name='recipe_comment'),
]

#if settings.DEBUG:
#    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)