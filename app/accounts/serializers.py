from rest_framework import serializers
from market.serializers import TradePointSerializer
from market.models import TradePoint
from .models import Profile, BankCart




class BankCartSerializer(serializers.ModelSerializer):
    """
    Сериализатор для банковской карты
    """

    # Добавляем masked_number для безопасности
    masked_number = serializers.SerializerMethodField()

    class Meta:
        model = BankCart
        fields = [
            "id",
            "number",
            "masked_number",
            "expiry_date",
            "cvv",
            "cardholder_name",
            "is_default",
            "created_at",
            "updated_at",
        ]
        # Скрываем чувствительные данные при чтении
        read_only_fields = ["created_at", "updated_at"]
        extra_kwargs = {
            "number": {"write_only": True},
            "cvv": {"write_only": True},
        }

    def get_masked_number(self, obj):
        """
        Возвращает замаскированный номер карты
        Пример: "**** **** **** 1234"
        """
        if obj.number:
            return f"**** **** **** {obj.number.replace(' ', '')[-4:]}"
        return "**** **** **** ****"

    def validate_number(self, value):
        """
        Валидация номера карты
        """
        # Удаляем пробелы и проверяем формат
        cleaned_number = value.replace(" ", "")

        if not cleaned_number.isdigit():
            raise serializers.ValidationError("Номер карты должен содержать только цифры")

        if len(cleaned_number) not in [13, 14, 15, 16, 17, 18, 19]:
            raise serializers.ValidationError("Номер карты должен содержать от 13 до 19 цифр")

        return value

    def validate_expiry_date(self, value):
        """
        Валидация срока действия
        Формат: MM/YY
        """
        if not value or len(value) != 5:
            raise serializers.ValidationError("Срок действия должен быть в формате MM/YY")

        if value[2] != "/":
            raise serializers.ValidationError("Срок действия должен быть в формате MM/YY")

        try:
            month = int(value[0:2])
            year = int(value[3:5])
        except ValueError:
            raise serializers.ValidationError("Срок действия должен быть в формате MM/YY")

        if month < 1 or month > 12:
            raise serializers.ValidationError("Месяц должен быть от 01 до 12")

        # Можно добавить проверку на истекший срок

        return value

    def validate_cvv(self, value):
        """
        Валидация CVV
        """
        if not value.isdigit():
            raise serializers.ValidationError("CVV должен содержать только цифры")

        if len(value) not in [3, 4]:
            raise serializers.ValidationError("CVV должен содержать 3 или 4 цифры")

        return value

    def create(self, validated_data):
        """
        Создание банковской карты
        """
        # Проверяем, есть ли уже основная карта
        user = validated_data["user"]

        if validated_data.get("is_default", False):
            # Снимаем флаг is_default со всех других карт
            BankCart.objects.filter(user=user, is_default=True).update(is_default=False)

        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Обновление банковской карты
        """
        # Если карта становится основной, снимаем флаг с других карт
        if validated_data.get("is_default", False):
            BankCart.objects.filter(user=instance.user, is_default=True).exclude(
                id=instance.id
            ).update(is_default=False)

        return super().update(instance, validated_data)


class ProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор для профиля пользователя
    """

    # Добавляем информацию о пользователе
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    # Добавляем банковские карты
    bank_carts = BankCartSerializer(many=True, read_only=True)
    bank_cart_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=BankCart.objects.all(),
        source="bank_carts",
        write_only=True,
        required=False,
        help_text="Список ID банковских карт",
    )

    # Добавляем торговые точки
    select_trade_points = TradePointSerializer(many=True, read_only=True)
    select_trade_point_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=TradePoint.objects.all(),
        source="select_trade_point",
        write_only=True,
        required=False,
        help_text="Список ID торговых точек",
    )

    # Добавляем полное имя
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            "id",
            "user_id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "phone",
            "select_trade_points",
            "select_trade_point_ids",
            "bank_carts",
            "bank_cart_ids",
        ]
        read_only_fields = ["id", "user_id", "username", "email"]

    def get_full_name(self, obj):
        """Полное имя пользователя"""
        return f"{obj.first_name} {obj.last_name}"

    def validate_phone(self, value):
        """
        Повторная валидация телефона
        """
        # Проверяем формат телефона
        import re

        pattern = r"^\+?7?\d{10,11}$"
        if not re.match(pattern, value):
            raise serializers.ValidationError(
                "Неверный формат телефона. Допустимые форматы: +79991234567, 89991234567, 9991234567"
            )
        return value

    def validate(self, attrs):
        """
        Дополнительная валидация профиля
        """
        # Проверяем, что first_name и last_name не пустые
        first_name = attrs.get("first_name", "").strip()
        last_name = attrs.get("last_name", "").strip()

        if not first_name:
            raise serializers.ValidationError({"first_name": "Имя не может быть пустым"})

        if not last_name:
            raise serializers.ValidationError({"last_name": "Фамилия не может быть пустой"})

        return attrs

    def create(self, validated_data):
        """
        Создание профиля
        """
        # Извлекаем данные торговых точек
        trade_point_ids = validated_data.pop("select_trade_point", [])

        # Создаем профиль
        profile = Profile.objects.create(**validated_data)

        # Добавляем торговые точки
        if trade_point_ids:
            profile.select_trade_point.set(trade_point_ids)

        return profile

    def update(self, instance, validated_data):
        """
        Обновление профиля
        """
        # Извлекаем данные торговых точек
        trade_point_ids = validated_data.pop("select_trade_point", None)

        # Обновляем основные поля
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # Обновляем торговые точки, если переданы
        if trade_point_ids is not None:
            instance.select_trade_point.set(trade_point_ids)

        return instance


class ProfileListSerializer(ProfileSerializer):
    """
    Сериализатор для списка профилей (упрощенный) 
    """

    class Meta(ProfileSerializer.Meta):
        fields = [
            "id",
            "user_id",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "phone",
        ]


class BankCartListSerializer(BankCartSerializer):
    """
    Сериализатор для списка банковских карт (упрощенный)
    """

    class Meta(BankCartSerializer.Meta):
        fields = [
            "id",
            "masked_number",
            "expiry_date",
            "cardholder_name",
            "is_default",
            "created_at",
        ]
