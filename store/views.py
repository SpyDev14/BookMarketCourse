from django.db.models.functions.math import Round
from django.views.decorators.http    import require_http_methods, require_GET
from django.contrib.auth.models      import User
from django.db.models                import Avg, Count, Q, F
from django.shortcuts                import render, redirect
from django.db.models                import QuerySet 
from django.utils                    import timezone
from django.http                     import HttpRequest,HttpResponse, HttpResponseBadRequest
from django.http                     import HttpResponseForbidden, HttpResponseNotAllowed
from django.http                     import QueryDict
from django_filters.rest_framework   import DjangoFilterBackend
from rest_framework.permissions      import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.viewsets         import ModelViewSet, GenericViewSet
from rest_framework.filters          import SearchFilter, OrderingFilter
from rest_framework                  import mixins


from .permissions import IsOwnerOrStuffOrReadOnly
from .serializers import *
from .models      import *

@require_GET
def get_home_page(request: HttpRequest):
	books = Book.objects.all()
	return render(request, 'store/home.html', {'books' : books})


class BooksViewSet(ModelViewSet):
	queryset: QuerySet = (
		# ещё можно засунуть readers в этот запрос (сразу, чтобы делался только 1 запрос в БД),
		# но способ там будет завязан на особой возможности postgres, так что пускай будет 2
		Book.objects.annotate(
			likes_count    = Count('userbookrelation', filter = Q(userbookrelation__liked = True)),
			ratings_count  = Count('userbookrelation', filter = Q(userbookrelation__rate__isnull = False)),
			average_rating = Round(
				Avg(
					'userbookrelation__rate',
					filter = Q(userbookrelation__rate__isnull = False )
				),
				precision = 2
			),
		)
		.prefetch_related('readers')
		.select_related('owner')
		.defer(
			# owner (model User) exclude fields
			*[
				f'owner__{field.name}' for field in User._meta.fields
				if field.name not in {
					'username',
					'email',
				}
			],
    	)
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

	
class UserBookRelationViewSet(mixins.UpdateModelMixin, GenericViewSet):
	queryset = UserBookRelation.objects.all()
	permission_classes = [IsAuthenticated]
	serializer_class = UserBookRelationSerializer
	lookup_field = 'book'

	def get_object(self):
		book_id = self.kwargs['book']
		book = Book.objects.get(pk = book_id)

		obj, _ = UserBookRelation.objects.get_or_create(
			user = self.request.user,
			book = book
		)
		return obj