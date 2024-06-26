from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'iserv-groups', views.IservGroupViewSet)
router.register(r'existing-accounts', views.ExistingAccountViewSet)

urlpatterns = router.urls