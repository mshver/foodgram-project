from django.contrib.auth import get_user_model
from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter
from api.models import Dish

UserModel = get_user_model()

class ComponentFilter(SearchFilter):
    search_param = 'title'

class DishFilter(FilterSet):
    categories = filters.AllValuesMultipleFilter(field_name='categories__url_slug')
    creator = filters.ModelChoiceFilter(queryset=UserModel.objects.all())
    bookmarked = filters.BooleanFilter(method='get_bookmarked')
    in_cart = filters.BooleanFilter(method='get_in_cart')

    def get_bookmarked(self, queryset, field_name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(bookmarks__user=self.request.user)
        return queryset

    def get_in_cart(self, queryset, field_name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(cart_items__user=self.request.user)
        return queryset

    class Meta:
        model = Dish
        fields = ('categories', 'creator')