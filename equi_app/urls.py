from django.urls import include, path
from rest_framework import routers
from . import views

app_name = 'equi_app'

router = routers.DefaultRouter()

urlpatterns = [
    path('', views.index.as_view(), name='index'),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]