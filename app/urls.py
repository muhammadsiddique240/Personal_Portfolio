from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import home, ProjectViewSet

router = DefaultRouter()
router.register(r'Project', ProjectViewSet, basename='Project')

urlpatterns = [
    path("api/", include(router.urls)),  # ✅ FIXED here
    # path("api/contact", contact_api_view),  # If needed later
    path('', home, name='home'),
]