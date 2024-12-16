from django.db import models
from django.contrib.auth.models import User
from auditlog.registry import auditlog

# Create your models here.

class Task(models.Model):
  title = models.CharField(max_length=200)
  description = models.TextField(max_length=1000)
  created = models.DateTimeField(auto_now_add=True)
  datecompleted = models.DateTimeField(null=True, blank=True)
  important = models.BooleanField(default=False)
  user = models.ForeignKey(User, on_delete=models.CASCADE)

  def __str__(self):
    return self.title + ' - ' + self.user.username


class Recipe(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    preparation = models.TextField()
    category = models.CharField(
        max_length=50,
        choices=[
            ('Desayunos', 'Desayunos'),
            ('Comidas', 'Comidas'),
            ('Postres', 'Postres'),
            ('Bebidas', 'Bebidas'),
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=False)
    difficulty = models.CharField(
        max_length=20,
        choices=[
            ('Fácil', 'Fácil'),
            ('Media', 'Media'),
            ('Difícil', 'Difícil'),
        ],
    )
    preparation_time = models.PositiveIntegerField(help_text="Tiempo en minutos")
    photo = models.ImageField(upload_to='media/recipes/photos', null=True, blank=True)

    def __str__(self):
        return self.title

from django.db import models
from django.contrib.auth.models import User

class FavoriteRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorite_recipes")
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')  # Evita duplicados
        verbose_name = "Favorite Recipe"
        verbose_name_plural = "Favorite Recipes"

    def __str__(self):
        return f"{self.user.username} - {self.recipe.title}"

class Ingredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    name = models.CharField(max_length=100)
    quantity = models.CharField(max_length=50)  # Ejemplo: "200 g", "2 tazas"

    def __str__(self):
        return f"{self.quantity} de {self.name}"

class Comment(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    def __str__(self):
        return f"Comentario de {self.user.username} en {self.recipe.title}"

class Moderation(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='moderations')
    moderator = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=50, choices=[
        ('approve', 'Aprobar'),
        ('block', 'Bloquear'),
    ])
    reason = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} por {self.moderator.username} en {self.recipe.title}"

class Rating(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=0)  # Ejemplo: de 1 a 5 estrellas

    class Meta:
        unique_together = ('recipe', 'user')  # Un usuario solo puede valorar una receta una vez

    def __str__(self):
        return f"{self.rating} estrellas para {self.recipe.title} por {self.user.username}"

# Registrar modelos para auditoría
auditlog.register(Task)
auditlog.register(Recipe)
auditlog.register(Ingredient)
auditlog.register(Comment)
auditlog.register(Moderation)
auditlog.register(Rating)

class PhotoUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='media/users/photos')

    def __str__(self):
        return f"{self.user.username}'s Photo"

class ConnectPhoto(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    photo_user = models.ForeignKey(PhotoUser, on_delete=models.CASCADE)

    def __str__(self):
        return f"Connect: {self.user.username} - Photo ID: {self.photo_user.id}"

class Role(models.Model):
    ROLE_CHOICES = [
        ('user', 'Usuario'),
        ('moderator', 'Moderador'),
        ('admin', 'Administrador'),
    ]
    
    name = models.CharField(max_length=20, choices=ROLE_CHOICES, unique=True)

    def __str__(self):
        return self.name

class ConnectRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.role.name}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)

    def str(self):
        return self.user.username
