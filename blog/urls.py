from django.urls import path
from . import views

app_name = 'blog'

# rutas del blog
urlpatterns = [
    path('', views.listado_blog, name='listado_blog'),
    path('<int:blog_id>/', views.detalle_blog, name='detalle_blog'),
    path('like/<int:blog_id>/', views.like_blog, name='like_blog'),
]
