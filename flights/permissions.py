# flights/permissions.py (فایل جدید)
from rest_framework.permissions import BasePermission

class IsFlightManager(BasePermission):
    """
    فقط اعضای گروه 'Flight Managers' می‌تونند پروازها رو اضافه/ویرایش کنند
    """
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='Flight Managers').exists()

class IsPassenger(BasePermission):
    """
    تمام کاربران احراز‌شده می‌تونند پرواز به لیستشون اضافه کنند
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated