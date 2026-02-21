from django.db.models import ProtectedError
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from user.models import Role
from user.permissions import IsAdminUser
from user.seiralizers import RoleDetailSerializer, RoleSerializer


class RoleListCreateView(generics.ListCreateAPIView):
    """
    List all roles or create a new role. Only Administrator can create new roles.
    """

    queryset = Role.objects.all()
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return RoleDetailSerializer
        return RoleSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        title = serializer.validated_data.get("title")
        if Role.objects.filter(title__iexact=title).exists():
            raise ValidationError({"title": "A role with this title already exists."})

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {"message": "Role created successfully.", "role": serializer.data},
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class RoleRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a role instance. Only Administrator can modify or delete roles.
    """

    queryset = Role.objects.all()
    permission_classes = [IsAdminUser]
    lookup_field = "pk"

    def get_serializer_class(self):
        if self.request.method == "GET":
            return RoleDetailSerializer
        return RoleSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        new_title = serializer.validated_data.get("title")
        if (
            new_title
            and Role.objects.filter(title__iexact=new_title)
            .exclude(pk=instance.pk)
            .exists()
        ):
            raise ValidationError({"title": "A role with this title already exists."})

        self.perform_update(serializer)

        return Response(
            {"message": "Role updated successfully.", "role": serializer.data}
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.user_set.exists():
            return Response(
                {"error": "This role is assigned to users and cannot be deleted."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            self.perform_destroy(instance)
            return Response(
                {"message": "Role deleted successfully."}, status=status.HTTP_200_OK
            )
        except ProtectedError:
            return Response(
                {"error": "This role cannot be deleted due to existing dependencies."},
                status=status.HTTP_400_BAD_REQUEST,
            )
