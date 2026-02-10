"""
URL configuration for contacts API.
Endpoints for contact CRUD and availability management.
"""

from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'contacts'

router = DefaultRouter()
# Use a custom regex pattern to accept string-based IDs
router.register(r'contacts', views.ContactViewSet, basename='contact')

urlpatterns = [
    path('', include(router.urls)),
]

# Override router-generated routes for string-based PKs
# The DefaultRouter generates routes like: contacts/<pk>/
# We need to make sure the regex accepts strings like 'cont_123' or 'doctor_1'
urlpatterns += [
    re_path(
        r'^contacts/(?P<pk>[a-zA-Z0-9_-]+)/$',
        views.ContactViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
        name='contact-detail'
    ),
    re_path(
        r'^contacts/(?P<pk>[a-zA-Z0-9_-]+)/availability/$',
        views.ContactViewSet.as_view({'post': 'availability'}),
        name='contact-availability'
    ),
    re_path(
        r'^contacts/(?P<pk>[a-zA-Z0-9_-]+)/appointments/$',
        views.ContactViewSet.as_view({'get': 'appointments'}),
        name='contact-appointments'
    ),
]
