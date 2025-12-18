# from django.contrib import admin
# from .models import Product, ProductImage, ProductSpecification, Tag, Comment
# # Register your models here.

# @admin.register(Product)
# class ProdutAdmin(admin.ModelAdmin):
#     list_display = (
#     'name',
#     'full_description',
#     'created_at',
#     'created_by',
#     'price',
#     'discount',
#     'limited',
#     'quantity',
#     'rating',
#     'preview'
#     )
    
#     list_filter = (
#         'limited',
#         'created_at',
#         'tags',
#         'quantity',
#     )
    
#  # Поля, по которым идёт поиск
#     search_fields = ['name', 'full_description', 'price']

#     # Поля, которые можно редактировать прямо в списке
#     list_editable = ['price', 'discount', 'quantity']

#     # Пагинация
#     list_per_page = 20