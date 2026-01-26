"""
Приложение магазина (товары и заказы)

Этот пакет объединяет модели, сериализаторы и другие компоненты
для работы с товарами и заказами в интернет-магазине.
"""

default_app_config = 'app.goods.apps.GoodsConfig'

# Импортируем модели
# from .models import (
#     Product,
#     ProductImage,
#     ProductSpecification,
#     Tag,
#     Comment,
#     Category,
#     Order,
#     OrderItem,
#     OrderStatus
# )

# # Импортируем сериализаторы
# from .serializers import (
#     ProductSerializer,
#     ImageSerializer,
#     CategorySerializer,
#     CommentSerializer,
#     TagSerializer,
#     ProductSpecificationSerializer,
#     OrderSerializer,
#     OrderCreateSerializer,
#     OrderListSerializer,
#     OrderItemSerializer,
#     OrderStatusSerializer
# )

# # Определяем публичный API пакета
# __all__ = [
#     # Модели
#     'Product',
#     'ProductImage',
#     'ProductSpecification',
#     'Tag',
#     'Comment',
#     'Category',
#     'Order',
#     'OrderItem',
#     'OrderStatus',
    
#     # Сериализаторы
#     'ProductSerializer',
#     'ImageSerializer',
#     'CategorySerializer',
#     'CommentSerializer',
#     'TagSerializer',
#     'ProductSpecificationSerializer',
#     'OrderSerializer',
#     'OrderCreateSerializer',
#     'OrderListSerializer',
#     'OrderItemSerializer',
#     'OrderStatusSerializer',
# ]

# # Документация
# __doc__ = """
# Доступные компоненты:

# Модели:
# - Product: Модель товара
# - Category: Модель категории
# - Order: Модель заказа
# - OrderItem: Элемент заказа
# - OrderStatus: Статус заказа
# - ProductImage: Изображение товара
# - ProductSpecification: Характеристики товара
# - Tag: Тег товара
# - Comment: Отзыв о товаре

# Сериализаторы:
# - ProductSerializer: Сериализация товаров
# - CategorySerializer: Сериализация категорий
# - OrderSerializer: Сериализация заказов
# - OrderCreateSerializer: Сериализация создания заказа
# - OrderListSerializer: Сериализация списка заказов
# - OrderItemSerializer: Сериализация элементов заказа
# - OrderStatusSerializer: Сериализация статусов заказа
# - ImageSerializer: Сериализация изображений
# - CommentSerializer: Сериализация отзывов
# - TagSerializer: Сериализация тегов
# - ProductSpecificationSerializer: Сериализация характеристик
# """
