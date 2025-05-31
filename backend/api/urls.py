from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views import ComponentsView, DishView, CategoriesView

app_name = 'api'

router = DefaultRouter()
router.register('categories', CategoriesView, basename='categories')
router.register('components', ComponentsView, basename='components')
router.register('dishes', DishView, basename='dishes')

urlpatterns = [
    path('', include(router.urls)),
]