from django.contrib import admin
from .models import ShoppingCart, Bookmark, Component, Dish, Category

class CategoryAdmin(admin.ModelAdmin):
    display_fields = ('title', 'url_slug', 'hex_code')
    list_display = display_fields

class ComponentAdmin(admin.ModelAdmin):
    display_fields = ('title', 'unit')
    list_display = display_fields
    filter_options = ('title',)
    list_filter = filter_options

class DishAdmin(admin.ModelAdmin):
    display_fields = ('title', 'creator', 'bookmarks_count')
    list_display = display_fields
    filter_options = ('creator', 'title', 'categories')
    list_filter = filter_options

    def bookmarks_count(self, instance):
        return instance.bookmarks.count()

admin.site.register(Category, CategoryAdmin)
admin.site.register(Component, ComponentAdmin)
admin.site.register(Dish, DishAdmin)
admin.site.register(ShoppingCart)
admin.site.register(Bookmark)