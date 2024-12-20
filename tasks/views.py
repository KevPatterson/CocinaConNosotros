from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import *
from django.contrib import messages
from .forms import TaskForm, RecipeForm, RatingForm, CommentForm, IngredientForm
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.admin.views.decorators import staff_member_required
from auditlog.models import LogEntry
from django_password_history.models import UserPasswordHistory
from .forms import CustomUserCreationForm
from .forms import *
from django.forms import inlineformset_factory
from .models import FavoriteRecipe
import json
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.http import JsonResponse
from .models import Recipe, FavoriteRecipe, Ingredient, Comment, Rating
from django.db.models import Avg, Q, Count
import random  # Importar random para seleccionar una receta aleatoria
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models.signals import post_save
from django.dispatch import receiver

#from django_otp.decorators import otp_required
#from django_otp.plugins.otp_totp.models import TOTPDevice

# Create your views here.

from django.contrib.auth import login, authenticate
from django.db import IntegrityError

@csrf_protect
def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Registro exitoso! Ahora puedes iniciar sesión.')
            return redirect('signin')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

        # Si las contraseñas no coinciden
    return render(request, 'signup.html', {
            "form": UserCreationForm,
            "error": "Las contraseñas no coinciden."
})

@csrf_protect
@login_required
def tasks(request):
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, 'tasks.html', {"tasks": tasks})

@csrf_protect
@login_required
def tasks_completed(request):
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'tasks.html', {"tasks": tasks})

@csrf_exempt
def home(request):
    return render(request, 'home.html')

@csrf_protect
@login_required
def signout(request):
    logout(request)
    return redirect('home')

@csrf_protect
def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {"form": AuthenticationForm})
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])

        if user is None:
            # Agrega un mensaje flash para SweetAlert2
            messages.error(request, "Nombre de usuario o contraseña incorrectos.")
            return render(request, 'signin.html', {"form": AuthenticationForm})

        # Agrega un mensaje flash para el inicio de sesión exitoso
        messages.success(request, f"Bienvenide '{user.username}' .")
        login(request, user)

        # Redirección basada en el rol
        if user.is_superuser:
            return redirect('admin_dashboard')  # Redirige a la vista de administrador
        else:
            return redirect('dashboard')  # Redirige al dashboard estándar

@csrf_protect
@login_required
def task_detail(request, task_id):
    if request.method == 'GET':
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        form = TaskForm(instance=task)
        return render(request, 'task_detail.html', {'task': task, 'form': form})
    else:
        try:
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html', {'task': task, 'form': form, 'error': 'Error updating task.'})

@csrf_protect
@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.datecompleted = timezone.now()
        task.save()
        return redirect('tasks')

@csrf_protect
@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')

@csrf_protect
@login_required
def user_dashboard(request):
    query = request.GET.get('q', '')  # Captura el término de búsqueda
    recipes = Recipe.objects.filter(author=request.user)  # Filtra recetas del usuario actual

    # Filtro por búsqueda
    if query:
        recipes = recipes.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    # Paginación
    paginator = Paginator(recipes, 10)
    page_number = request.GET.get('page')
    recipes_page = paginator.get_page(page_number)

    # Estadísticas rápidas
    recipes_count = recipes.count()  # Total de recetas creadas
    favorites_count = FavoriteRecipe.objects.filter(user=request.user).count()  # Total de recetas favoritas

    # Cálculo del promedio de valoraciones (usando la relación ratings)
    average_rating = recipes.annotate(avg_rating=Avg('ratings__rating')).aggregate(avg_rating=Avg('ratings__rating'))['avg_rating'] or 0

    # Inspiración del día: Seleccionar hasta 5 recetas aleatorias
    all_recipes = list(Recipe.objects.all())
    daily_inspiration = random.sample(all_recipes, min(5, len(all_recipes)))

    return render(request, 'user_dashboard.html', {
        'user': request.user,
        'recipes': recipes_page,
        'query': query,
        'recipes_count': recipes_count,
        'favorites_count': favorites_count,
        'average_rating': round(average_rating, 2),
        'daily_inspiration': daily_inspiration,  # Agregado para mostrar inspiración del día
    })

@csrf_protect
@login_required
def add_to_favorites(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    favorite, created = FavoriteRecipe.objects.get_or_create(user=request.user, recipe=recipe)
    if created:
        return JsonResponse({'success': True, 'message': 'Receta añadida a favoritos.'})
    else:
        return JsonResponse({'success': False, 'message': 'La receta ya está en favoritos.'})

@csrf_protect
@login_required
def remove_from_favorites(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    favorite = FavoriteRecipe.objects.filter(user=request.user, recipe=recipe)
    if favorite.exists():
        favorite.delete()
        return JsonResponse({'success': True, 'message': 'Receta eliminada de favoritos.'})
    else:
        return JsonResponse({'success': False, 'message': 'La receta no estaba en favoritos.'})

@csrf_protect
@login_required
def favorite_recipes(request):
    favorites = FavoriteRecipe.objects.filter(user=request.user).select_related('recipe')
    return render(request, 'favorite_recipes.html', {'favorites': favorites})

@login_required
@csrf_protect
def recipe_delete(request, pk):
    if request.method == "POST":
        recipe = get_object_or_404(Recipe, pk=pk, author=request.user)
        recipe.delete()
        return JsonResponse({"success": True, "message": "Receta eliminada correctamente."})
    return JsonResponse({"success": False, "message": "No tienes permisos para eliminar esta receta."}, status=400)

@csrf_protect
@login_required
def force_password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)  # Mantiene la sesión activa
            return redirect('user_dashboard.html')  # Redirige a la página principal del usuario
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'force_password_change.html', {'form': form})

@csrf_protect
@login_required
def custom_password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Mantiene la sesión activa después de cambiar la contraseña
            return redirect('password_change_done')  # Redirige a una página de éxito
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'password_change_form.html', {'form': form})

@csrf_protect
@login_required
def password_change_done(request):
    return render(request, 'password_change_done.html')

@csrf_protect
@login_required
def create_recipe(request):
    if request.method == "POST":
        recipe_form = RecipeForm(request.POST, request.FILES)

        if recipe_form.is_valid():
            # Guardar la receta
            recipe = recipe_form.save(commit=False)
            recipe.author = request.user  # Asigna el autor
            recipe.save()

            # Procesar ingredientes dinámicos
            ingredient_names = request.POST.getlist('new_ingredient_name')
            ingredient_quantities = request.POST.getlist('new_ingredient_quantity')

            for name, quantity in zip(ingredient_names, ingredient_quantities):
                if name.strip() and quantity.strip():  # Validar que no estén vacíos
                    Ingredient.objects.create(
                        recipe=recipe,
                        name=name.strip(),
                        quantity=quantity.strip()
                    )

            # Añadir mensaje de éxito
            messages.success(request, f"La receta '{recipe.title}' fue creada exitosamente.")
            return redirect('dashboard')
        else:
            # Añadir mensaje de error
            messages.error(request, "Hubo un problema al crear la receta. Por favor, verifica los datos.")
    else:
        recipe_form = RecipeForm()

    return render(request, 'create_recipe.html', {
        'recipe_form': recipe_form,
    })

@csrf_protect
@login_required  # Esto asegura que solo los usuarios autenticados puedan acceder
def recipe_book(request):
    recipes = Recipe.objects.all()  # Muestra todas las recetas (puedes filtrar por usuario si es necesario)
    return render(request, 'recipe_book.html', {'recipes': recipes})

@csrf_protect
@login_required
def my_recipes(request):
    recipes = Recipe.objects.filter(author=request.user)
    return render(request, 'my_recipes.html', {'recipes': recipes})

from django.db.models import Avg, Count

@csrf_protect
@login_required
def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    is_favorited = FavoriteRecipe.objects.filter(user=request.user, recipe=recipe).exists()

    if request.method == "POST":
        content = request.POST.get("content").strip()
        parent_id = request.POST.get("parent_id")  # Para identificar si es una respuesta
        if content:
            parent_comment = Comment.objects.filter(id=parent_id).first() if parent_id else None
            Comment.objects.create(recipe=recipe, user=request.user, content=content, parent=parent_comment)
            return redirect('recipe_detail', recipe_id=recipe.id)

    comments = recipe.comments.filter(parent__isnull=True).prefetch_related('replies')  # Comentarios principales con sus respuestas
    ratings_data = recipe.ratings.aggregate(average_rating=Avg('rating'), total_ratings=Count('rating'))

    return render(request, 'recipe_detail.html', {
        'recipe': recipe,
        'is_favorited': is_favorited,
        'comments': comments,
        'average_rating': round(ratings_data['average_rating'] or 0, 2),
        'total_ratings': ratings_data['total_ratings'] or 0,
    })

from django.http import JsonResponse

@csrf_protect
@login_required
def rate_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    # Verificar si el usuario ya ha valorado esta receta
    existing_rating = Rating.objects.filter(recipe=recipe, user=request.user).first()

    if request.method == "POST":
        try:
            rating_value = int(request.POST.get('rating', 0))
            if rating_value < 1 or rating_value > 5:
                return JsonResponse({'success': False, 'message': 'Valoración inválida.'}, status=400)

            if existing_rating:
                existing_rating.rating = rating_value
                existing_rating.save()
                message = f'Se actualizó tu valoración a {rating_value} estrellas.'
            else:
                Rating.objects.create(recipe=recipe, user=request.user, rating=rating_value)
                message = f'Has valorado esta receta con {rating_value} estrellas.'

            return JsonResponse({'success': True, 'message': message, 'recipe_id': recipe.id})
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Por favor, selecciona una valoración válida.'}, status=400)

    return render(request, 'rate_recipe.html', {'recipe': recipe, 'existing_rating': existing_rating})

# Vista para comentar una receta
from django.http import JsonResponse

@csrf_protect
@login_required
def comment_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            recipe.comments.create(user=request.user, content=content)
            return JsonResponse({
                'success': True,
                'message': 'Comentario enviado con éxito.',
                'recipe_id': recipe.id,
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'El comentario no puede estar vacío.',
            }, status=400)

    return render(request, 'comment_recipe.html', {'recipe': recipe})

@csrf_protect
@login_required
def add_comment(request):
    if request.method == "POST":
        data = json.loads(request.body)
        content = data.get("content", "").strip()
        recipe_id = data.get("recipe_id")

        if content and recipe_id:
            recipe = get_object_or_404(Recipe, id=recipe_id)
            Comment.objects.create(
                recipe=recipe,
                user=request.user,
                content=content
            )
            return JsonResponse({"success": True})
    return JsonResponse({"success": False, "message": "Error al agregar el comentario."})

@csrf_protect
@login_required
def reply_to_comment(request):
    if request.method == "POST":
        data = json.loads(request.body)
        content = data.get("content", "").strip()
        parent_id = data.get("parent_id")

        if content and parent_id:
            parent_comment = get_object_or_404(Comment, id=parent_id)
            Comment.objects.create(
                recipe=parent_comment.recipe,
                user=request.user,
                content=content,
                parent=parent_comment
            )
            return JsonResponse({"success": True})
    return JsonResponse({"success": False, "message": "Error al agregar la respuesta."})

@csrf_protect
@login_required
def edit_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id, author=request.user)
    # Crear un formulario en línea para los ingredientes relacionados
    IngredientFormSet = inlineformset_factory(Recipe, Ingredient, form=IngredientForm, extra=0, can_delete=True)

    if request.method == 'POST':
        recipe_form = RecipeForm(request.POST, request.FILES, instance=recipe)
        ingredient_formset = IngredientFormSet(request.POST, instance=recipe)

        if recipe_form.is_valid() and ingredient_formset.is_valid():
            # Guardar la receta y los ingredientes existentes
            recipe_form.save()
            ingredient_formset.save()

            # Manejar ingredientes nuevos
            new_ingredient_names = request.POST.getlist('new_ingredient_name')
            new_ingredient_quantities = request.POST.getlist('new_ingredient_quantity')

            for name, quantity in zip(new_ingredient_names, new_ingredient_quantities):
                if name and quantity:
                    # Evitar duplicados si ya existen ingredientes con los mismos valores
                    if not Ingredient.objects.filter(recipe=recipe, name=name, quantity=quantity).exists():
                        Ingredient.objects.create(recipe=recipe, name=name, quantity=quantity)

            return redirect('my_recipes')  # Redirige a la lista de recetas
    else:
        recipe_form = RecipeForm(instance=recipe)
        ingredient_formset = IngredientFormSet(instance=recipe)

    return render(request, 'edit_recipe.html', {
        'recipe_form': recipe_form,
        'ingredient_formset': ingredient_formset,
        'recipe': recipe,
    })

#Vistas para el admnin

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test

# Verificar si el usuario es administrador
def is_admin(user):
    return user.is_superuser

CATEGORIES = ['Desayunos', 'Comidas', 'Bebidas', 'Postres']

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Total de recetas
    total_recipes = Recipe.objects.count()

    # Total de categorías
    total_categories = len(CATEGORIES)  # Total de categorías predefinidas

    # Total de usuarios activos
    total_active_users = User.objects.filter(is_active=True).count()

    # Datos para el gráfico: recetas creadas por mes
    from django.db.models.functions import TruncMonth
    from django.db.models import Count

    recipes_per_month = (
        Recipe.objects.annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Count('id'))
        .order_by('month')
    )

    # Preparar datos para Chart.js
    labels = [entry['month'].strftime('%B') for entry in recipes_per_month]
    data = [entry['total'] for entry in recipes_per_month]

    context = {
        'total_recipes': total_recipes,
        'total_categories': total_categories,
        'total_active_users': total_active_users,
        'chart_labels': labels,
        'chart_data': data,
    }

    return render(request, 'admin_views/dashboard.html', context)

@csrf_protect
@login_required
@user_passes_test(lambda u: u.is_superuser)
def manage_users(request):
    query = request.GET.get('q', '')  # Capturar el término de búsqueda
    if query:
        # Filtrar usuarios por nombre de usuario, email o fecha de creación
        users_list = User.objects.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(date_joined__icontains=query)
        ).order_by('-date_joined')
    else:
        users_list = User.objects.all().order_by('-date_joined')  # Ordenar por fecha de creación

    # Paginación
    paginator = Paginator(users_list, 10)  # Mostrar 10 usuarios por página
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)

    return render(request, 'admin_views/manage_users.html', {
        'users': users,
        'query': query,  # Pasar la consulta actual para mantenerla en el cuadro de búsqueda
    })

@csrf_protect
@login_required
@user_passes_test(lambda u: u.is_superuser)
def manage_recipes(request):
    query = request.GET.get('q', '')  # Capturar el término de búsqueda
    if query:
        # Convertir el término de búsqueda a booleano si aplica
        is_approved_query = None
        if query.lower() in ['activa', 'aprobada', 'true', 'sí']:
            is_approved_query = True
        elif query.lower() in ['inactiva', 'rechazada', 'false', 'no']:
            is_approved_query = False

        # Filtrar recetas por título, autor o estado
        recipes_list = Recipe.objects.filter(
            Q(title__icontains=query) |
            Q(author__username__icontains=query) |
            (Q(is_approved=is_approved_query) if is_approved_query is not None else Q())
        ).order_by('-created_at')
    else:
        recipes_list = Recipe.objects.all().order_by('-created_at')  # Ordenar por fecha de creación

    # Paginación
    paginator = Paginator(recipes_list, 10)  # Mostrar 10 recetas por página
    page_number = request.GET.get('page')
    recipes = paginator.get_page(page_number)

    return render(request, 'admin_views/manage_recipes.html', {
        'recipes': recipes,
        'query': query,  # Pasar la consulta actual para mantenerla en el cuadro de búsqueda
    })

@csrf_protect
@login_required
@user_passes_test(lambda u: u.is_superuser)
def manage_comments(request):
    query = request.GET.get('q', '')  # Capturar el término de búsqueda
    if query:
        # Filtrar comentarios por contenido, usuario o receta
        comments_list = Comment.objects.filter(
            Q(content__icontains=query) |
            Q(user__username__icontains=query) |
            Q(recipe__title__icontains=query)
        ).order_by('-created_at')
    else:
        comments_list = Comment.objects.all().order_by('-created_at')

    # Paginación
    paginator = Paginator(comments_list, 10)  # Mostrar 10 comentarios por página
    page_number = request.GET.get('page')
    comments = paginator.get_page(page_number)

    if request.method == "POST":
        action = request.POST.get("action")
        comment_id = request.POST.get("comment_id")
        try:
            comment = Comment.objects.get(id=comment_id)
            if action == "delete":
                comment.delete()
                messages.success(request, "El comentario fue eliminado correctamente.")
            elif action == "approve":
                comment.is_approved = True
                comment.save()
                messages.success(request, "El comentario fue aprobado.")
            elif action == "disapprove":
                comment.is_approved = False
                comment.save()
                messages.success(request, "El comentario fue desaprobado.")
        except Comment.DoesNotExist:
            messages.error(request, "El comentario no existe.")
        return redirect('manage_comments')

    return render(request, 'admin_views/manage_comments.html', {
        'comments': comments,
        'query': query,
    })

# Ver todos los registros
@csrf_protect
@login_required
@user_passes_test(lambda u: u.is_superuser)
@staff_member_required
def auditlog_view(request):
    query = request.GET.get('q', '')
    logs = LogEntry.objects.select_related('actor').order_by('-timestamp')

    # Filtro de búsqueda
    if query:
        logs = logs.filter(
            Q(actor__username__icontains=query) |
            Q(action__icontains=query) |
            Q(content_type__model__icontains=query)
        )

    # Paginación
    paginator = Paginator(logs, 10)  # Mostrar 10 registros por página
    page_number = request.GET.get('page')
    logs = paginator.get_page(page_number)

    context = {
        'logs': logs,
        'query': query,  # Para mantener el valor del cuadro de búsqueda
    }
    return render(request, 'admin_views/auditlog_list.html', context)

@csrf_protect
@login_required
def user_profile(request):
    return render(request, 'user_profile.html', {'user': request.user})

@csrf_protect
@login_required
def edit_profile(request):
    if request.method == 'POST':
        user = request.user
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        if 'photo' in request.FILES:
            user.profile.photo = request.FILES['photo']
            user.profile.save()
        user.save()
        messages.success(request, 'Perfil actualizado exitosamente.')
        return redirect('user_profile')
    return redirect('user_profile')

@csrf_protect
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Mantener la sesión activa
            messages.success(request, 'Tu contraseña ha sido actualizada exitosamente.')
            return redirect('user_profile')
        else:
            messages.error(request, 'Hubo un error al actualizar tu contraseña.')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'change_password.html', {'form': form})

@csrf_protect
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@csrf_protect
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
import os


from django.conf import settings
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
@csrf_protect
@login_required
def protected_media(request, path):
    # Construir la ruta completa del archivo
    file_path = os.path.join(settings.MEDIA_ROOT, path)

    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type="application/octet-stream")
            response['Content-Disposition'] = f'inline; filename={os.path.basename(file_path)}'
            return response
    else:
        raise Http404("Archivo no encontrado")
