from django.views.generic.base import TemplateView
from django.urls import include, path
from rest_framework import routers
from . import views

app_name = 'equi_app'

router = routers.DefaultRouter()

urlpatterns = [
    path('', views.index.as_view(), name='index'),
    path('prep_data/', TemplateView.as_view(template_name='equi_app/prep_data.html')),
    path('<int:query_idx>/', views.index.as_view(), name='index'),
    path('show_more_segments/', views.show_more_segments.as_view()),
    path('iterative_synthesis/', views.iterative_synthesis.as_view()),
    path('iterative_synthesis_init/', views.iterative_synthesis_init.as_view()),
    path('iterative_synthesis_live/', views.iterative_synthesis_live.as_view()),
    path('set_run/', views.set_run.as_view()),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]