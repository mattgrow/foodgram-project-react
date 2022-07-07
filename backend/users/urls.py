from api.views import UserSubscriptionListView, UserViewSet, subscribe
from django.urls import include, path
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import routers


router = routers.DefaultRouter()
router.register('users', UserViewSet, basename='users')
urlpatterns = [
    path('users/<int:user_id>/subscribe/', subscribe, name='subscribe'),
    path(
        'users/subscriptions/',
        UserSubscriptionListView.as_view(),
        name='my_subscribe_list'
    ),
    path(
        'users/me/',
        UserViewSet.as_view({'get': 'me'}),
        name='me',
    ),
    path(
        'users/set_password/',
        DjoserUserViewSet.as_view({'post': 'set_password'}),
        name='set_password',
    ),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
