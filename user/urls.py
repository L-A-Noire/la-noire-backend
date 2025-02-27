from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from user.views import (
    LoginView,
    RegisterView,
    RoleListCreateView,
    RoleRetrieveUpdateDestroyView,
    UserDetailView,
)
from user.views.user_views import (
    EmployeesCountView,
    UserListView,
    UserRoleDetailView,
    UserRoleUpdateView,
)

urlpatterns = [
    # Auth URLs
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("login/refresh/", TokenRefreshView.as_view(), name="login-refresh"),
    path("profile/", UserDetailView.as_view(), name="user-detail"),
    # Role Management URLs (Admin only)
    path("roles/", RoleListCreateView.as_view(), name="role-list-create"),
    path(
        "roles/<int:pk>/", RoleRetrieveUpdateDestroyView.as_view(), name="role-detail"
    ),
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/<int:pk>/role/", UserRoleDetailView.as_view(), name="user-role-detail"),
    path("users/change-role/", UserRoleUpdateView.as_view(), name="user-change-role"),
    path("employees-count/", EmployeesCountView.as_view(), name="employees-count"),
]
