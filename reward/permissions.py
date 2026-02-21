from rest_framework import permissions


class IsBaseUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role
            and request.user.role.title == "Base User"
        )


class IsPoliceOfficer(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role
            and request.user.role.title == "Police/Patrol Officer"
        )


class IsDetective(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role
            and request.user.role.title == "Detective"
        )


class CanViewRewardInfo(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.role:
            return False

        allowed = [
            "Police/Patrol Officer",
            "Detective",
            "Sergent",
            "Captain",
            "Chief",
            "Administrator",
        ]
        return request.user.role.title in allowed
