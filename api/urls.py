from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet

router = DefaultRouter()

router.register('Categories', CategoryViewSet)

urlpatterns = router.urls