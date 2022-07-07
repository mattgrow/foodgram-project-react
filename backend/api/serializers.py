from django.http import Http404
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer

from recipes.models import (Favorite, Follow, Ingredient, Recipe,
                            RecipeIngredientQty, Shopping, Tag)
from rest_framework import serializers
from users.models import User

from .fields import DecodeImageField

ERRORS = {
    'no_such_ingredient': 'Ингредиента с id {} нет в базе!',
}


class RecipeSimpleSerializer(serializers.ModelSerializer):

    image = DecodeImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class UserSerializer(UserCreateSerializer):

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User

        fields = (
            'username',
            'id',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(author=obj).exists()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class RecipeIngredientQtySerializer(serializers.HyperlinkedModelSerializer):

    id = serializers.IntegerField(required=False, source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredientQty
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeMainSerializer(RecipeSimpleSerializer):

    ingredients = RecipeIngredientQtySerializer(
        source='recipeingredientqty_set', many=True, read_only=True
    )
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is not None and not request.user.is_anonymous:
            current_user = request.user
            return Favorite.objects.filter(
                recipe=obj, user=current_user
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is not None and not request.user.is_anonymous:
            current_user = request.user
            return Shopping.objects.filter(
                recipe=obj, user=current_user
            ).exists()
        return False


class RecipeCreateSerializer(RecipeMainSerializer):

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = RecipeIngredientQtySerializer(
        source='recipeingredientqty_set', many=True
    )

    def validate(self, data):
        ingredients_list = []
        ingredients_data = data.get('recipeingredientqty_set')
        for ingredient_data in ingredients_data:
            ingredient = ingredient_data.get('ingredient')
            try:
                _ = get_object_or_404(
                    Ingredient, pk=ingredient.get('id')
                )
            except Http404:
                raise serializers.ValidationError(
                    ERRORS.get('Ингредиент отсутствует в базе')
                    .format(ingredient.get('id'))
                )
            if ingredient in ingredients_list:
                raise serializers.ValidationError(
                    'В рецепте дублируются ингредиенты')
            ingredients_list.append(ingredient)
        return data

    def create_ingredients(self, ingredients_data, recipe):
        RecipeIngredientQty.objects.bulk_create(
            [RecipeIngredientQty(
                recipe=recipe,
                ingredient=get_object_or_404(
                    Ingredient, pk=ingredient_data.pop('ingredient').get('id')
                ),
                amount=ingredient_data.pop('amount')
            ) for ingredient_data in ingredients_data]
        )

    def add_tags(self, recipe, tag_list):
        for tag in tag_list:
            recipe.tags.add(tag)
        return recipe

    def create(self, validated_data):
        tag_list = validated_data.pop('tags')
        ingredients_data = validated_data.pop('recipeingredientqty_set')
        recipe = Recipe.objects.create(**validated_data)
        self.add_tags(recipe, tag_list)
        self.create_ingredients(ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        tag_list = validated_data.pop('tags')
        ingredients_data = validated_data.pop('recipeingredientqty_set')
        recipe = instance
        recipe.tags.clear()
        self.add_tags(recipe, tag_list)
        RecipeIngredientQty.objects.filter(recipe=recipe).delete()
        self.create_ingredients(ingredients_data, recipe)
        super().update(recipe, validated_data)
        return recipe


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
        read_only_fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class FollowSerializer(UserSerializer):

    recipes = RecipeSimpleSerializer(
        many=True, read_only=True
    )
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'username',
            'id',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()
