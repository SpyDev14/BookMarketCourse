from django.views.decorators.http  import require_http_methods, require_GET
from django.contrib.auth.models    import User
from django.shortcuts              import render, redirect
from django.db.models              import QuerySet 
from django.http                   import HttpRequest
from rest_framework.permissions    import IsAuthenticated
from rest_framework.viewsets       import ModelViewSet, GenericViewSet
from rest_framework.filters        import SearchFilter, OrderingFilter
from rest_framework                import mixins
from django_filters.rest_framework import DjangoFilterBackend

from store.permissions import IsOwnerOrStuffOrReadOnly
from store.serializers import BookSerializer, UserBookRelationSerializer
from store.models      import Book, UserBookRelation



@require_GET
def get_home_page(request: HttpRequest):
	books = Book.objects.all()
	return render(request, 'store/home.html', {'books' : books})


class BooksViewSet(ModelViewSet):
	queryset: QuerySet = (
		Book.objects.select_related('owner').defer(
			# owner (model User) exclude fields
			*[
				f'owner__{field.name}' for field in User._meta.fields
				if field.name not in {
					'username',
					'email',
				}
			],
    	)
		.prefetch_related('readers')
		.order_by('id')
	)

	serializer_class   = BookSerializer
	filter_backends    = [DjangoFilterBackend, SearchFilter, OrderingFilter]
	filterset_fields   = ['price', 'name', 'author']
	search_fields      = ['price', 'name', 'author', 'description']
	ordering_fields    = ['price', 'name', 'author', 'likes_count', 'ratings_count', 'average_rating']
	permission_classes = [IsOwnerOrStuffOrReadOnly]

	def perform_create(self, serializer: BookSerializer):
		serializer.validated_data['owner'] = self.request.user
		super().perform_create(serializer)

	def retrieve(self, request, *args, **kwargs):
		book = self.get_object()

		from . import logic

		logic.calculate_and_update_book_average_rating(book)
		logic.calculate_and_update_book_ratings_count(book)
		logic.calculate_and_update_book_likes_count(book)

		return super().retrieve(request, *args, **kwargs)

	
class UserBookRelationViewSet(mixins.UpdateModelMixin, GenericViewSet):
	queryset = UserBookRelation.objects.all()
	permission_classes = [IsAuthenticated]
	serializer_class = UserBookRelationSerializer
	lookup_field = 'book'

	def get_object(self):
		book_id = self.kwargs['book']

		obj, _ = UserBookRelation.objects.get_or_create(
			user = self.request.user,
			book = Book.objects.get(pk = book_id)
		)
		return obj