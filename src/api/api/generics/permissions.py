from rest_framework.permissions import IsAuthenticated

from seller.user import enums
from seller.vendor import enums as vendor_enums
from seller.eater import enums as eater_enums


class IsASuperUser(IsAuthenticated):
    """
        Check if the user is an Admin
    """

    def has_permission(self, request, view):
        return super().has_permission(
            request,
            view
        ) and (
                       request.user.is_active and request.user.is_superuser
               )


class IsAnEater(IsAuthenticated):
    """
        Check if the user is an Eater
    """

    def has_permission(self, request, view):
        return super().has_permission(
            request,
            view
        ) and (
                       request.user.is_superuser or request.user.user_type == enums.EATER
               ) and (
                       request.user.eater.status == eater_enums.ACTIVE
               )


class IsAVendor(IsAuthenticated):
    """
        Check if the user is an Vendor
    """

    def has_permission(self, request, view):
        return super().has_permission(
            request,
            view
        ) and (
                       request.user.is_superuser or request.user.user_type == enums.VENDOR
               ) and (
                       request.user.vendor.status == vendor_enums.APPROVED or vendor_enums.COMPLETED
               )


class ProfileIncompleteVendor(IsAuthenticated):
    """
        Check if the user is an Vendor whose profile is incomplete
    """

    def has_permission(self, request, view):
        return super().has_permission(
            request,
            view
        ) and (
                       request.user.is_superuser or request.user.user_type == enums.VENDOR
               ) and not (
                request.user.vendor.status == vendor_enums.APPROVED
        )
