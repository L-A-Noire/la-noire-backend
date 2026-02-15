from django.urls import path
from user.views import RegisterView, LoginView, UserDetailView, RoleListCreateView, RoleRetrieveUpdateDestroyView

urlpatterns = [
    # Auth URLs
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', UserDetailView.as_view(), name='user-detail'),

    # Role Management URLs (Admin only)
    path('roles/', RoleListCreateView.as_view(), name='role-list-create'),
    path('roles/<int:pk>/', RoleRetrieveUpdateDestroyView.as_view(),
         name='role-detail'),
]
