from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from user.models import User, Role
from user.seiralizers import UserListWithRoleSerializer, ChangeUserRoleSerializer
from user.permissions import IsAdminUser

from user.models import User
from user.seiralizers import LoginSerializer, RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        )


class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class EmployeesCountView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        count = (
            User.objects.exclude(
                role__title__in=[
                    "Complainant",
                    "Witness",
                    "Suspect",
                    "Base User",
                ]
            )
            .distinct()
            .count()
        )

        return Response({"totalEmployees": count})




class UserListView(generics.ListAPIView):
    queryset = User.objects.all().select_related('role').order_by('-date_joined')
    serializer_class = UserListWithRoleSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class UserRoleUpdateView(generics.GenericAPIView):
    serializer_class = ChangeUserRoleSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data["user"]
        role = serializer.validated_data["role"]
        
        old_role_title = user.role.title if user.role else "No Role"
        
        user.role = role
        user.save()
        
        return Response({
            "message": f"User role updated successfully from '{old_role_title}' to '{role.title}'.",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "old_role": old_role_title,
                "new_role": role.title,
                "new_role_id": role.id
            }
        }, status=status.HTTP_200_OK)


class UserRoleDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all().select_related('role')
    serializer_class = UserListWithRoleSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    lookup_field = 'pk'