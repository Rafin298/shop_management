# core/permissions.py
from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, req, view):
        return req.user.role == 'admin'

class IsSeller(BasePermission):
    def has_permission(self, req, view):
        return req.user.role == 'seller'

class IsCustomer(BasePermission):
    def has_permission(self, req, view):
        return req.user.role == 'customer'