from django.urls import include, path
from rest_framework import routers
from .views import (IngredientViewSet, RecipeViewSet, TagViewSet)


router_v1 = routers.DefaultRouter()
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
urlpatterns = [
    path(
        'recipes/download_shopping_cart/',
        RecipeViewSet.as_view({'get': 'download_shopping_cart'}),
        name='download_shopping_cart',
    ),
    path('', include(router_v1.urls)),
    path('', include('users.urls',)),
]
