from django.urls import path, include
from .           import views
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('books', views.BooksViewSet)
router.register('bookrelations', views.UserBookRelationViewSet, basename='bookrelations')

urlpatterns = [
    path('', views.get_home_page, name = 'home_page'),
    path('api/', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)