from rest_framework import serializers
from .models import DeliverySettings, DeliveryType, TradePoint


class DeliveryTypeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для типа доставки
    """
    class Meta:
        model = DeliveryType
        fields = [
            'id',
            'name',
            'is_express',
            'price',
        ]
        read_only_fields = ['id']

    def validate_price(self, value):
        """
        Проверяем, что цена положительная
        """
        if value < 0:
            raise serializers.ValidationError("Цена должна быть неотрицательной")
        return value



class DeliverySettingsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для настроек доставки
    """
    class Meta:
        model = DeliverySettings
        fields = [
            'id',
            'name',
            'min_order_amount_for_free_delivery',
            'delivery_cost',
            'express_delivery_cost',
        ]
        read_only_fields = ['id']

    def validate_name(self, value):
        """
        Проверяем, что имя уникально
        """
        if DeliverySettings.objects.filter(name=value).exists():
            if self.instance and self.instance.name == value:
                return value
            raise serializers.ValidationError("Настройки с таким именем уже существуют")
        return value

    def validate(self, attrs):
        """
        Дополнительная валидация
        """
        # Проверяем, что стоимостные параметры положительные
        for field in ['min_order_amount_for_free_delivery', 'delivery_cost', 'express_delivery_cost']:
            if attrs.get(field, 0) < 0:
                raise serializers.ValidationError({field: "Значение должно быть неотрицательным"})
        
        return attrs    


class TradePointSerializer(serializers.ModelSerializer):
    delivery_policy = DeliverySettingsSerializer(read_only=True)
    delivery_policy_id = serializers.PrimaryKeyRelatedField(
        queryset=DeliverySettings.objects.all(), source="delivery_policy", write_only=True
    )

    possible_delivery_type = DeliveryTypeSerializer(many=True, read_only=True)
    possible_delivery_type_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=DeliveryType.objects.all(),
        source="possible_delivery_type",
        write_only=True,
        required=False,
        help_text="Список ID типов доставки",
    )

    class Meta:
        model = TradePoint
        fields = [
            "name",
            "address",
            "city",
            'possible_delivery_type',
            'possible_delivery_type_ids',
            'delivery_policy',
            'delivery_policy_id',
        ]
        read_only_fields = ['id']
        
        def validate(self, data):
            """
            Валидация данных торговой точки
            """
            # Проверяем, что город и адрес не пустые
            city = data.get('city')
            address = data.get('address')
            
            if not city or not city.strip():
                raise serializers.ValidationError({'city': 'Город не может быть пустым'})
            
            if not address or not address.strip():
                raise serializers.ValidationError({'address': 'Адрес не может быть пустым'})

            # Проверяем, что типы доставки соответствуют политике
            delivery_policy = data.get('delivery_policy')
            possible_delivery_types = data.get('possible_delivery_type', [])
            

            return data
        
    def create(self, validated_data):
        """
        Создание торговой точки
        """
        # Извлекаем ID типов доставки
        delivery_type_ids = validated_data.pop('possible_delivery_type', [])
        
        # Создаем торговую точку
        trade_point = TradePoint.objects.create(**validated_data)
        
        # Добавляем типы доставки
        if delivery_type_ids:
            trade_point.possible_delivery_type.set(delivery_type_ids)
        
        return trade_point
    
    def update(self, instance, validated_data):
        """
        Обновление торговой точки
        """
        # Извлекаем ID типов доставки
        delivery_type_ids = validated_data.pop('possible_delivery_type', None)
        
        # Обновляем основные поля
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        
        # Обновляем типы доставки, если переданы
        if delivery_type_ids is not None:
            instance.possible_delivery_type.set(delivery_type_ids)
        
        return instance
    
    
class TradePointListSerializer(TradePointSerializer):
    """
    Сериализатор для списка торговых точек (упрощенный)
    """
    class Meta(TradePointSerializer.Meta):
        fields = [
            'id',
            'name',
            'city',
            'address',
        ]


class DeliveryTypeListSerializer(DeliveryTypeSerializer):
    """
    Сериализатор для списка типов доставки (упрощенный)
    """
    class Meta(DeliveryTypeSerializer.Meta):
        fields = ['id', 'name', 'is_express', 'price']


class DeliverySettingsListSerializer(DeliverySettingsSerializer):
    """
    Сериализатор для списка настроек доставки (упрощенный)
    """
    class Meta(DeliverySettingsSerializer.Meta):
        fields = ['id', 'name']