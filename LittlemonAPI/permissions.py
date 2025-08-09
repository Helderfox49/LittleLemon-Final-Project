from rest_framework.permissions import BasePermission

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                request.user.groups.filter(name='Manager').exists())


class IsDeliveryCrew(BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                request.user.groups.filter(name='Delivery Crew').exists())


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated or 
                request.user.groups.filter(name='Customer').exists())
    

class IsCustomerOrManagerOrDeliveryCrew(BasePermission):
    """
    Autorise l'accès si l'utilisateur est Customer, Manager ou Delivery Crew
    """
    def has_permission(self, request, view):
        return request.user.groups.filter(
            name__in=["Customer", "Manager", "Delivery Crew"]
        ).exists()
    

class IsManagerOrDeliveryCrew(BasePermission):
    """
    Autorise l'accès si l'utilisateur est Manager ou Delivery Crew
    """
    def has_permission(self, request, view):
        return request.user.groups.filter(
            name__in=["Manager", "Delivery Crew"]
        ).exists()
    

# class IsCustomer(BasePermission):
#     def has_permission(self, request, view):
#         return request.user.is_authenticated and (not (IsManager().has_permission(request, view) and \
#                not (IsDeliveryCrew().has_permission(request, view))))