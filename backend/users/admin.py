from django.contrib import admin
from recipes.models import Favorite, Follow, Ingredient, Recipe, Shopping, Tag

from .models import User

admin.autodiscover()
admin.site.enable_nav_sidebar = False


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'pk',
        'email',
        'first_name',
        'last_name',
        'is_active',
        'is_staff',
        'last_login',
    )
    list_editable = ('is_active',)
    list_filter = ('is_active',)
    search_fields = (
        'username',
        'email',
    )


class IngredientInlineAdmin(admin.TabularInline):
    model = Recipe.ingredients.through


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'cooking_time',
        'author'
    )
    fieldsets = [
        (None, {'fields': (
            'name',
            'cooking_time',
            'author',
            'tags',
            'image',
            'get_favorited_count',
        )})
    ]
    inlines = (IngredientInlineAdmin,)
    list_filter = (
        'tags',
        'author',
    )
    search_filter = (
        'name',
        'author',
    )
    readonly_fields = ('get_favorited_count',)

    def get_favorited_count(self, obj):
        return obj.get_favorited_count()
    get_favorited_count.short_description = 'Количество добавлений в избранное'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'color',
        'slug',
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    list_filter = ('measurement_unit',)
    search_filter = (
        'name',
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'user',
    )


@admin.register(Shopping)
class ShoppingAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'user',
    )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author',
    )
