from django.contrib import admin

from .models import MenuItem, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'featured', 'category')
    list_filter = ('category', 'featured')
    search_fields = ('title', 'category__title')
    raw_id_fields = ('category',)
