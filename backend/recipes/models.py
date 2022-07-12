from django.core.validators import MinValueValidator
from django.db import models
from users.models import User


class Tag(models.Model):

    name = models.CharField(
        'Название',
        max_length=30,
        unique=True
    )
    color = models.CharField(
        'Цветовой код',
        max_length=7,
        default='#000000',
        unique=True
    )
    slug = models.SlugField(
        'slug',
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'

    def __str__(self):
        return self.name


class Ingredient(models.Model):

    name = models.CharField(
        'Название',
        max_length=100,
    )
    measurement_unit = models.CharField(
        'Ед. измерения',
        max_length=30,
    )

    class Meta:
        verbose_name = 'Ингридиент'

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Recipe(models.Model):

    name = models.CharField('Название', max_length=200)
    text = models.TextField('Описание', max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(
        'Изображение',
        null=True
    )
    cooking_time = models.IntegerField(
        'Время готовки, мин.',
        validators=[
            MinValueValidator(1)
        ]
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredientQty',
        verbose_name='Ингридиенты'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.author.username})'

    def get_favorited_count(self):
        return self.favorites.count()


class RecipeIngredientQty(models.Model):

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингридиент'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество в рецепте',
    )

    class Meta:
        verbose_name = 'Ингридиент рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient'
            )
        ]


class Favorite(models.Model):

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )

    class Meta:
        verbose_name = 'Избранный рецепт'

    def __str__(self):
        return (
            f'Рецепт {self.recipe.pk} '
            f'(пользователь {self.user.pk})'
        )


class Shopping(models.Model):

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cards',
        verbose_name='Рецепт'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cards',
        verbose_name='Пользователь'
    )

    class Meta:
        verbose_name = 'Рецепт в корзине'


class Follow(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followings',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Автор, на которого подписались'
    )

    def __str__(self):
        return (
            f'Подписчик: {self.user.get_full_name()} - '
            f'Автор: {self.author.get_full_name()}'
        )

    class Meta:
        verbose_name = 'Подписка'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author',),
                name='unique_follows'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='restric_self_follow'
            )
        ]
