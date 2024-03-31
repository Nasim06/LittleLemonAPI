from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter





router = DefaultRouter(trailing_slash=False)
router.register(r'menu-items', views.MenuItemsView)
router.register(r'category', views.CategoryView)
router.register(r'groups/manager', views.ManagerView, basename="manager-view")
router.register(r'groups/delivery-crew', views.DeliveryCrewView, basename="delivery-crew-view")

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]