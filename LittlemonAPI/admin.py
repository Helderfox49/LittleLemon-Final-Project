from django.contrib import admin
from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group, Permission
from django.dispatch import receiver

from .models import MenuItem, Category, Cart, Order


@receiver(post_migrate)
def create_groups(sender, **kwargs):
    Group.objects.get_or_create(name='Manager')
    Group.objects.get_or_create(name='Delivery Crew')
    

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

admin.site.register(Cart)
admin.site.register(Order)