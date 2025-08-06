from django.urls import path
from . import views

urlpatterns = [
    # path('groups/manager/users/', views.manager_list, name='manager-list')
    path('groups/manager/users/', views.ManagerUserGroupView.as_view()),
    path('groups/manager/users/<int:userId>', views.ManagerUserGroupView.as_view()),

    path('groups/delivery-crew/users/', views.DeliveryUserGroupView.as_view(), name='delivery-list'),
    path('groups/delivery-crew/users/<int:userId>', views.DeliveryUserGroupView.as_view()),
]