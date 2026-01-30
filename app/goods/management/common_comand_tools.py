from typing import TypeVar, Optional
from sys import stdout
from django.contrib.auth.models import User
from django.core.management.color import color_style
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.db.models import Model
from goods.models.product_models import Product, Comment, Tag, ProductSpecification
from market.models import DeliveryType, TradePoint, DeliverySettings
from goods.models.order_models import Order, OrderItem, OrderStatus
from accounts.models import Profile


style = color_style()
MODEL_CHILD = TypeVar("MODEL_CHILD", bound=Model)


def get_or_create_simple_test_object(
    class_name: str,
    class_origin: Optional[MODEL_CHILD] = None,
    obj_name: Optional[str] = None,
    defaults_atr: Optional[dict] = None,
    for_complex_atr: Optional[dict] = None,
    creater: Optional[User] = None,
) -> tuple[MODEL_CHILD, bool] | tuple[None, None]:
    """
    Инетрфейс для создания  тестовых объктов.
    Возвращает экземпляр модели и флаг, создан или получен из БД
    Содержит словарь для работы с некоторыми обьектами:
            - DeliveryType
            - DeliverySettings
            - OrderStatus
            - Tag

    Ожидает class_name, ищет его в словаре и получает дефолтные значения, если не находит, то возвращает None.
    Для создания обьекта с внешними таблицами ожидает передачу for_complex_atr которым расширит дефолтные значения из словаря

    Args:
        class_name: Название класса для создания
        class_origin: Модель обькта для создания
        obj_name: Название объекта для создания
        defaults_atr: Словарь с атрибутами для создания
        for_complex_atr: Словарь с атрибутами для создания обьектов с связанными таблицами
        creater: Пользователь, создавший объект

    Returns:
        Кортеж с объектом и флагом создания (или None, None при ошибке)

    Raises:
        ValueError: Если передан неверный класс
        Exception: Если произошла неожиданная ошибка

    Examples:
        get_or_create_simple_test_object("delivery", "test_delivery", {"price": 100})
    """
    DEFAULT_VALUE_MAPVALUE_MAP = {
        "delivery": (
            DeliveryType,
            "test_delivery",
            {
                "price": 100,
            },
        ),
        "delivery_settings": (
            DeliverySettings,
            "test_delivery_settings",
            {
                "min_order_amount_for_free_delivery": 2000,
                "delivery_cost": 200,
                "express_delivery_cost": 500,
            },
        ),
        "trade_point": (
            TradePoint,
            "Test Store",
            {
                "city": "test sity",
                "address": "test addres",
            },
        ),
        "order_status": (
            OrderStatus,
            "Test_status",
            {},
        ),
        "tag": (Tag, "test_tag", {}),
    }

    origin: MODEL_CHILD
    map_values: tuple[MODEL_CHILD, str, dict]

    if class_origin and obj_name and defaults_atr:
        origin = class_origin

    else:
        map_values = DEFAULT_VALUE_MAPVALUE_MAP.get(class_name)
        if map_values is None:
            # Если класс не найден в словаре, но переданы class_origin, obj_name и defaults_atr — создаём объект напрямую
            if class_origin and obj_name and defaults_atr:
                origin = class_origin
            else:
                return None, None

        if obj_name is None:
            obj_name: str = map_values[1]
        if defaults_atr is None:
            defaults_atr: dict = map_values[2]
        if creater:
            defaults_atr["created_by"] = creater
        if for_complex_atr:
            defaults_atr.update(for_complex_atr)

        origin = map_values[0]

    object: origin
    created: bool
    try:
        object, created = origin.objects.get_or_create(
            name=obj_name, defaults=defaults_atr
        )
        return object, created

    except IntegrityError as e:
        stdout.write(style.ERROR(f"Ошибка уникальности при создании {origin}: {e}"))
        return None, None

    except ValidationError as e:
        stdout.write(style.ERROR(f"Ошибка валидации при создании {origin}: {e}"))
        return None, None

    except Exception as e:
        stdout.write(style.ERROR(f"Неожиданная ошибка при создании {origin}: {e}"))
        return None, None


def get_create_test_product_specification(
    product: Product, name, text
) -> tuple[Product, bool] | tuple[None, None]:
    """Создает тестовую характеристику продукта.

    Args:
        product: Продукт, к которому добавляется характеристика):
    """
    try:
        specification, created = ProductSpecification.objects.get_or_create(
            product=product, name=name, defaults={"value": text}
        )
        return specification, created
    except ValueError as e:
        stdout.write(style.ERROR(f"Ошибка валидации при создании комментария: {e}"))
        return None, None

    except IntegrityError as e:
        stdout.write(style.ERROR(f"Ошибка уникальности при создании комментария: {e}"))
        return None, None

    except ValidationError as e:
        stdout.write(style.ERROR(f"Ошибка валидации при создании комментария: {e}"))
        return None, None

    except Exception as e:
        stdout.write(style.ERROR(f"Неожиданная ошибка при создании комментария: {e}"))
        return None, None


def create_test_comment(product: Product, creater: User) -> bool:
    """Создает тестовый комментарий к продукту.

    Args:
        product: Продукт, к которому добавляется комментарий
        creator: Пользователь, создающий комментарий

    Returns:
        Успешно ли создание комментария
    """
    try:
        comment = Comment.objects.create(
            product=product,
            created_by=creater,
            product_estimation=5,
            description="Its test comment",
        )
        return True

    except ValueError as e:
        stdout.write(style.ERROR(f"Ошибка валидации при создании комментария: {e}"))
        return False

    except IntegrityError as e:
        stdout.write(style.ERROR(f"Ошибка уникальности при создании комментария: {e}"))
        return False

    except ValidationError as e:
        stdout.write(style.ERROR(f"Ошибка валидации при создании комментария: {e}"))
        return False

    except Exception as e:
        stdout.write(style.ERROR(f"Неожиданная ошибка при создании комментария: {e}"))
        return False


def create_test_product(
    creater: User, product_number: int = 1
) -> tuple[Product, bool] | tuple[None, None]:
    """Создает тестовый продукт или обновляет существующий.

    Args:
        product_number: Номер продукта для уникальности имени
        creator: Пользователь, создающий продукт

    Returns:
        Кортеж с объектом продукта и флагом создания (или None, None при ошибке)
    """
    name_product = f"test_product{product_number}"
    name_tag = f"test_tag{product_number}"
    name_specific = f"test_specific{product_number}"

    try:
        product, created = Product.objects.get_or_create(
            name=name_product,
            defaults={
                "price": 1000,
                "discount": 10,
                "limited": True,
                "quantity": 100,
                "rating": 5,
                "is_active": True,
                "full_description": "test Product",
                "created_by": creater,
            },
        )

        # Создаем тег для продукта
        tag, tag_created = get_or_create_simple_test_object('tag', obj_name=name_tag)
        stdout.write(style.SUCCESS(f"{name_tag} {tag_created}"))
        if tag:
            product.tags.add(tag)
            stdout.write(style.SUCCESS(f"{name_tag} added"))
        # Создаем характеристики для продукта

        spec_value = f"Test 100% {product_number}"
        specification, spec_created = get_create_test_product_specification(
            product, name_specific, spec_value
        )

        if created:
            #  Создаем комментарий для продукта
            create_test_comment(product, creater)

        return product, created

    except IntegrityError as e:
        stdout.write(
            style.ERROR(
                f"Ошибка уникальности при создании продукта {name_product}: {e}"
            )
        )
        return None, None

    except ValidationError as e:
        stdout.write(
            style.ERROR(f"Ошибка валидации при создании продукта {name_product}: {e}")
        )
        return None, None

    except Exception as e:
        stdout.write(
            style.ERROR(f"Неожиданная ошибка при создании продукта {name_product}: {e}")
        )
        return None, None


def get_or_create_test_user(username):
    try:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": f"{username}@example.com",  # Уникальный email для каждого пользователя
                "is_active": True,
            },
        )

        if created:
            user.set_password("testpassword")
            user.save()
            stdout.write(style.SUCCESS("Пользователь testuser создан"))
        else:
            stdout.write(style.SUCCESS("Пользователь testuser уже существует"))

        return user, created
    except Exception as e:
        stdout.write(style.ERROR(f"Неожиданная ошибка при создании user: {e}"))
        return None, None


def get_or_create_test_profile_for_user(user: User) -> tuple[Profile, bool] | tuple[None, None]:
    """Создает или получает профиль для тестового пользователя.

    Args:
        user (User): Пользователь, для которого создается профиль

    Returns:
        tuple[Profile, bool]: Кортеж с объектом профиля и флагом создания,
        или (None, None) при ошибке

    Examples:
        >>> profile, created = get_or_create_test_profile_for_user(user)
        >>> if profile:
        ...     print(f"Профиль {'создан' if created else 'уже существует'}")
    """
    try:
        profile, profile_created = Profile.objects.get_or_create(
            user=user,
            defaults={
                "first_name": "testprofile",
                "last_name": "profile",
                "email": "testuser@example.com",
                "phone": "+7912345678",
            },
        )
        return profile, profile_created
    except Exception as e:
        stdout.write(style.ERROR(f"Неожиданная ошибка при создании профиля: {e}"))
        return None, None
