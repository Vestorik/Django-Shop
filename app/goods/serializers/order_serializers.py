"""
    1. OrderStatusSerializer
    Базовый сериализатор для статуса заказа
    Возвращает ID и название статуса
    2. OrderItemSerializer
    Сериализует элемент заказа
    Содержит вложенный сериализатор ProductSerializer для получения информации о товаре
    Имеет вычисляемые поля unit_price и total_price
    Поля product_id и price_at_time разделены на write_only/read_only для лучшего контроля
    3. OrderSerializer (основной)
    Главный сериализатор для заказа
    Использует вложенные сериализаторы для всех связанных объектов
    Имеет отдельные поля для ID (*_id) и объектов (*) для удобства API
    Поддерживает создание и обновление элементов заказа через items_data
    Содержит вычисляемые поля:
    total_price - пересчитанная общая стоимость
    created_at_formatted и updated_at_formatted - отформатированные даты
    4. OrderCreateSerializer
    Унаследован от основного сериализатора
    Делает все обязательные поля действительно обязательными
    Используется для создания новых заказов
    5. OrderListSerializer
    Упрощенный сериализатор для списка заказов
    Содержит только основную информацию
    Используется для уменьшения объема данных при получении списка заказов
    Особенности реализации:
    Гибкое управление связями: Использование пар field/field_id позволяет легко работать с API

    Валидация: Полная валидация данных, включая проверку:

    Доступного количества товара на складе
    Поддержки типа доставки торговой точкой
    Корректности данных пользователя
    Гибкое создание заказов: Возможность передавать элементы заказа в виде списка словарей

    Вычисляемые поля: Автоматическое пересчет суммы заказа при создании/обновлении

    Форматирование дат: Удобные форматированные представления дат
"""


from rest_framework import serializers
from goods.models.order_models import Order, OrderItem, OrderStatus
from goods.serializers import ProductSerializer
from goods.models import Product
from accounts.models import Profile
from accounts.serializers import ProfileSerializer
from market.models import DeliveryType, TradePoint
from market.serializers import DeliveryTypeSerializer, TradePointSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Сериализатор для элемента заказа
    """

    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Product.objects.filter(is_active=True), source="product" 
    )
    total_price = serializers.SerializerMethodField()
    unit_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        #  Определяем поля
        fields = [
            "id",
            "product",
            "product_id",
            "quantity",
            "price_at_time",
            "unit_price",
            "total_price",
        ]
        read_only_fields = ["price_at_time"]

    def get_unit_price(self, obj):
        """Возвращает цену за единицу товара на момент заказа"""
        return obj.get_unit_price()

    def get_total_price(self, obj):
        """Возвращает общую стоимость товара в заказе"""
        return obj.get_total_price()

    def validate_quantity(self, value):
        """
        Проверяет, что количество товара положительное число
        """
        if value <= 0:
            raise serializers.ValidationError("Количество должно быть больше нуля")
        return value

    def validate(self, attrs):
        """
        Дополнительная валидация элемента заказа
        """
        product = attrs.get("product")
        quantity = attrs.get("quantity", 1)

        if product and product.quantity < quantity:
            raise serializers.ValidationError(
                {"quantity": f"Недостаточно товара на складе. Доступно: {product.quantity}"}
            )

        return attrs


class OrderStatusSerializer(serializers.ModelSerializer):
    """
    Сериализатор для статуса заказа
    """

    class Meta:
        model = OrderStatus
        fields = ["id", "name"]


class OrderSerializer(serializers.ModelSerializer):
    """
    Основной сериализатор для заказа
    """

    status = OrderStatusSerializer(read_only=True)
    status_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=OrderStatus.objects.all(), source="status", required=False
    )
    created_by = ProfileSerializer(read_only=True)
    created_by_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Profile.objects.all(), source="created_by", required=False
    )
    delivery_type = DeliveryTypeSerializer(read_only=True)
    delivery_type_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=DeliveryType.objects.all(), source="delivery_type"
    )
    trade_point = TradePointSerializer(read_only=True)
    trade_point_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=TradePoint.objects.all(), source="trade_point"
    )
    items = OrderItemSerializer(source="order_items", many=True, read_only=True)
    items_data = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
        help_text="Список элементов заказа в формате [{product_id: 1, quantity: 2}, ...]",
    )
    total_price = serializers.SerializerMethodField()
    created_at_formatted = serializers.SerializerMethodField()
    updated_at_formatted = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "created_at",
            "created_at_formatted",
            "updated_at",
            "updated_at_formatted",
            "created_by",
            "created_by_id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "delivery_type",
            "delivery_type_id",
            "trade_point",
            "trade_point_id",
            "comment",
            "status",
            "status_id",
            "delivery_cost",
            "total_amount",
            "total_price",
            "items",
            "items_data",
        ]
        read_only_fields = ["created_at", "updated_at", "delivery_cost", "total_amount"]

    def get_total_price(self, obj):
        """
        Возвращает общую стоимость заказа
        """
        return obj.calculate_total_price()

    def get_created_at_formatted(self, obj):
        """
        Возвращает отформатированную дату создания
        """
        return obj.created_at.strftime("%d.%m.%Y %H:%M")

    def get_updated_at_formatted(self, obj):
        """
        Возвращает отформатированную дату обновления
        """
        return obj.updated_at.strftime("%d.%m.%Y %H:%M")

    def validate(self, attrs):
        """
        Валидация данных заказа
        """
        # Проверяем, что профиль существует
        created_by = attrs.get("created_by")
        if not created_by:
            raise serializers.ValidationError({"created_by": "Пользователь не найден"})

        # Проверяем, что торговая точка поддерживает выбранный тип доставки
        delivery_type = attrs.get("delivery_type")
        trade_point = attrs.get("trade_point")

        if delivery_type and trade_point:
            if not trade_point.possible_delivery_type.filter(id=delivery_type.id).exists():
                raise serializers.ValidationError(
                    {
                        "delivery_type": f"Торговая точка {trade_point.name} не поддерживает тип доставки {delivery_type.name}"
                    }
                )

        return attrs

    def create(self, validated_data):
        """
        Создание заказа и его элементов
        """
        # Извлекаем данные элементов заказа
        items_data = validated_data.pop("items_data", [])

        # Создаем заказ
        order = Order.objects.create(**validated_data)

        # Добавляем элементы заказа
        if items_data:
            for item_data in items_data:
                product_id = item_data.get("product_id")
                quantity = item_data.get("quantity", 1)

                try:
                    product = Product.objects.get(id=product_id, is_active=True)

                    # Проверяем количество на складе
                    if product.quantity < quantity:
                        raise serializers.ValidationError(
                            f"Недостаточно товара {product.name} на складе"
                        )

                    # Создаем элемент заказа
                    OrderItem.objects.create(order=order, product=product, quantity=quantity)

                except Product.DoesNotExist:
                    raise serializers.ValidationError(f"Товар с id={product_id} не найден")

        # Обновляем общую сумму
        order.update_total_amount()

        return order

    def update(self, instance, validated_data):
        """
        Обновление заказа
        """
        # Извлекаем данные элементов заказа
        items_data = validated_data.pop("items_data", None)

        # Обновляем основные поля заказа
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # Обновляем элементы заказа, если они переданы
        if items_data is not None:
            # Удаляем старые элементы
            instance.order_items.all().delete()

            # Добавляем новые элементы
            for item_data in items_data:
                product_id = item_data.get("product_id")
                quantity = item_data.get("quantity", 1)

                try:
                    product = Product.objects.get(id=product_id, is_active=True)

                    # Проверяем количество на складе
                    if product.quantity < quantity:
                        raise serializers.ValidationError(
                            f"Недостаточно товара {product.name} на складе"
                        )

                    # Создаем элемент заказа
                    OrderItem.objects.create(order=instance, product=product, quantity=quantity)

                except Product.DoesNotExist:
                    raise serializers.ValidationError(f"Товар с id={product_id} не найден")

        # Обновляем общую сумму
        instance.update_total_amount()

        return instance


class OrderCreateSerializer(OrderSerializer):
    """
    Сериализатор для создания заказа
    Отличается от основного тем, что делает больше полей обязательными
    """

    first_name = serializers.CharField(required=True, max_length=50)
    last_name = serializers.CharField(required=True, max_length=50)
    email = serializers.EmailField(required=True)
    phone = serializers.CharField(required=True, max_length=20)
    delivery_type_id = serializers.PrimaryKeyRelatedField(
        queryset=DeliveryType.objects.all(), source="delivery_type", required=True
    )
    trade_point_id = serializers.PrimaryKeyRelatedField(
        queryset=TradePoint.objects.all(), source="trade_point", required=True
    )
    items_data = serializers.ListField(
        child=serializers.DictField(),
        required=True,
        min_length=1,
        help_text="Список элементов заказа в формате [{product_id: 1, quantity: 2}, ...]",
    )

    class Meta(OrderSerializer.Meta):
        # Делаем все поля обязательными для создания заказа
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
            "email": {"required": True},
            "phone": {"required": True},
            "delivery_type_id": {"required": True},
            "trade_point_id": {"required": True},
            "items_data": {"required": True},
        }


class OrderListSerializer(OrderSerializer):
    """
    Сериализатор для списка заказов
    Содержит только основную информацию
    """

    class Meta:
        model = Order
        fields = [
            "id",
            "created_at",
            "created_at_formatted",
            "updated_at",
            "updated_at_formatted",
            "first_name",
            "last_name",
            "status",
            "total_amount",
            "delivery_cost",
        ]
        read_only_fields = fields
