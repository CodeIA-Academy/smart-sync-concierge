"""URL configuration for traces app."""

from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'traces', views.TracesViewSet, basename='trace')

urlpatterns = router.urls
