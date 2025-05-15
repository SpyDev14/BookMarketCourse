from rest_framework.permissions import IsAuthenticatedOrReadOnly, SAFE_METHODS
from django.http.request        import HttpRequest

class IsOwnerOrStuffOrReadOnly(IsAuthenticatedOrReadOnly):
	def has_object_permission(self, request: HttpRequest, view, obj):
		return bool(
			request.method in SAFE_METHODS or
			request.user and request.user.is_authenticated and
			bool(obj.owner == request.user or request.user.is_staff)
		)