from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from recipes.models import (Favorite, Follow, Ingredient, Recipe,
                            RecipeIngredientQty, Shopping, Tag)
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from users.models import User

from .filters import IngredientFilter, RecipeFilter
from .permissions import CurrentUserOrAdminOrReadOnly
from .serializers import (FollowSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeMainSerializer,
                          TagSerializer, UserCreateSerializer, UserSerializer)

INGREDIENT_POSITION_CART = '{} {} --- {} {}\n'
SHOP_CART_HEADING = 'Список ингридиентов для похода в магазин\n\n'
SHOPPING_FILENAME = 'shopping_cart.txt'
BAD_REQUEST_ERRORS = {
    'already_favorited': 'Рецепт уже есть в избранном',
    'not_favorited': 'Рецепта нет в избранном',
    'already_in_cart': 'Рецепт уже есть в корзине',
    'not_in_cart': 'Рецепта нет в корзине',
}


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = [permissions.AllowAny]


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (CurrentUserOrAdminOrReadOnly,)
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateSerializer
        return RecipeMainSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @staticmethod
    def post_method_for_actions(request, recipe, serializer, model):
        user = request.user
        new_obj = model(user=user, recipe=recipe)
        new_obj.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_method_for_actions(request, recipe, model):
        user = request.user
        model_obj = get_object_or_404(model, user=user, recipe=recipe)
        model_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST'],
            permission_classes=[permissions.IsAuthenticated],
            name='Add to favorites'
            )
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        serializer = self.get_serializer(recipe)
        return self.post_method_for_actions(
            request=request,
            recipe=recipe,
            serializer=serializer,
            model=Favorite
        )

    @favorite.mapping.delete
    def unfavorite(self, request, pk=None):
        return self.delete_method_for_actions(
            request=request,
            recipe=self.get_object(),
            model=Favorite
        )

    @action(detail=True, methods=['POST'],
            permission_classes=[permissions.IsAuthenticated],
            name='Add to shopping cart'
            )
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        serializer = self.get_serializer(recipe)
        return self.post_method_for_actions(
            request=request,
            recipe=recipe,
            serializer=serializer,
            model=Shopping
        )

    @shopping_cart.mapping.delete
    def unshopping_cart(self, request, pk=None):
        return self.delete_method_for_actions(
            request=request,
            recipe=self.get_object(),
            model=Shopping
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        shopping_cart = {}
        ingredients = RecipeIngredientQty.objects.filter(
            recipe__shopping_cards__user=request.user
        ).values_list(
            'ingredient__name',
            'ingredient__measurement_unit',
        ).annotate(Sum('amount'))
        content = SHOP_CART_HEADING
        for item in ingredients:
            name = item[0]
            if name not in shopping_cart:
                shopping_cart[name] = {
                    'measurement_unit': item[1],
                    'amount': item[2]
                }
        for i, (name, data) in enumerate(shopping_cart.items(), 1):
            content += INGREDIENT_POSITION_CART.format(
                i,
                name,
                data["amount"],
                data["measurement_unit"]
            )
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            f'attachment; filename={SHOPPING_FILENAME}'
        )
        return response


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = IngredientFilter
    permission_classes = [permissions.AllowAny]


@api_view(['POST', 'DELETE'])
@permission_classes((permissions.IsAuthenticated, ))
def subscribe(request, user_id=None):
    if request.method == 'POST':
        user = request.user
        author = get_object_or_404(User, id=user_id)
        Follow.objects.get_or_create(user=user, author=author)
        serializer = FollowSerializer(data=request.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )
    elif request.method == 'DELETE':
        user = request.user
        author = get_object_or_404(User, id=user_id)
        follow = get_object_or_404(Follow, user=user, author=author)
        follow.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class UserSubscriptionListView(generics.ListAPIView):
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        authors = User.objects.filter(followers__user=user)
        return authors


class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]

    def get_serializer_class(self):
        if self.action in ['create']:
            return UserCreateSerializer
        return UserSerializer

    @action(detail=True, methods=['get'])
    def me(self, request, pk=None):
        user = self.request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)
