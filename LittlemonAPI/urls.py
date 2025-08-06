from django.urls import path
from . import views

urlpatterns = [
    path('menu-items/', views.MenuItemListCreateView.as_view(), name='menu-item-list'),
    path('menu-items/<int:pk>', views.MenuItemRetrieveUpdateDeleteView.as_view(), name='menu-item-detail'),
    path('cart/menu-items/', views.CartCustomerView.as_view()),

    path('groups/manager/users/', views.ManagerUserGroupView.as_view()),
    path('groups/manager/users/<int:userId>', views.ManagerUserGroupView.as_view()),
    path('groups/delivery-crew/users/', views.DeliveryUserGroupView.as_view()),
    path('groups/delivery-crew/users/<int:userId>', views.DeliveryUserGroupView.as_view()),
]