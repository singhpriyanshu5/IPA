from rest_framework import permissions

class IsIntervieweeHimself(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class IsInterviewer(permissions.BasePermission):
    """
    Custom permission to check whether this particular user is interviewer
    """
    def has_permission(self, request, view):
        try:
            return request.user.interviewer
        except:
            return False

class IsInterviewee(permissions.BasePermission):
    """
    Custom permission to check whether this particular user is interviewer
    """
    def has_permission(self, request, view):
        try:
            return request.user.interviewee
        except:
            return False


class IsBoss(permissions.BasePermission):
    """
    Custom permission to check whether this particular user is interviewer
    """
    def has_permission(self, request, view):
        try:
            return request.user.boss
        except:
            return False


class IsAnonymous(permissions.BasePermission):
    """
    Allows access only to authenticated users.
    """
    def has_object_permission(self, request, view, obj):
        return obj == request.user
    def has_permission(self, request, view):
        return request.method != 'POST' or not(request.user and request.user.is_authenticated())

