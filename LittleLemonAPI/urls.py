from django.urls import path
from .views import *

urlpatterns = [
    path('categories', CategoryView.as_view()),
    path('menu-items', MenuItemView.as_view()),
    path('menu-items/<int:id>', SingleMenuItem.as_view()),
    path('groups/manager/users', ManagerView.as_view()),
    path('groups/manager/users/<int:id>', SingleManagerView.as_view()),
    path('groups/delivery-crew/users', DeliveryCrewView.as_view()),
    path('groups/delivery-crew/users/<int:id>', SingleDeliveryCrewView.as_view()),
    path('cart/menu-items', CartView.as_view()),
    path('orders/<int:id>', SingleOrderView.as_view()),
    path('orders', OrderView.as_view()),
]