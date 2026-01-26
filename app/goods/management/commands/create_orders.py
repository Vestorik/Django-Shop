from typing import Any
from django.core.management import BaseCommand
from django.contrib.auth.models import User
from app.goods.models.order_models import Order, OrderItem, OrderStatus
from app.market.models import DeliveryType, TradePoint, DeliverySettings
from app.accounts.models import Profile
from app.goods.models.product_models import Product

class Command(BaseCommand):
    """The command class for create a orders."""

    help = "Create test user orders"

    def handle(self, *args: Any, **options: Any) -> str | None:
        """
        func create test profiles
        """
        # variables
        delivery: DeliveryType
        delivery_settings: DeliverySettings
        trade_point: TradePoint

        self.stdout.write("Start create test profiles")

        delivery, created_del = DeliveryType.objects.get_or_create(
            name="test_delivery",
            defaults={
                "price": 100,
            },
        )
        # Создаем настройки доставки
        delivery_settings, created_pol = DeliverySettings.objects.get_or_create(
            name="test_delivery_settings",
            defaults={
                "min_order_amount_for_free_delivery": 2000,
                "delivery_cost": 200,
                "express_delivery_cost": 500,
            },
        )
        # Создаем торговую точку
        trade_point, created_trade = TradePoint.objects.get_or_create(
            name="test_trade_point",
            defaults={
                "city": "test sity",
                "address": "test addres",
                "possible_delivery_type": delivery,
                "delivery_policy": delivery_settings,
            },
        )

        for num in range(0, 10):
            # Создаем или получаем пользователя
            user, created = User.objects.get_or_create(
                username=f"testuser{num}",
                defaults={
                    "email": f"testuser{num}@example.com",  # Уникальный email для каждого пользователя
                    "is_active": True,
                },
            )

            if created:
                user.set_password("testpassword")
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Пользователь testuser{num} создан"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Пользователь testuser{num} уже существует"))

            # Создаем или получаем профиль для пользователя
            profile, profile_created = Profile.objects.get_or_create(
                user=user,
                defaults={
                    "first_name": f"testprofile{num}",
                    "last_name": f"profile{num}",
                    "email": f"testuser{num}@example.com",
                    "phone": f"+79{num}12345678",
                },
            )

            if profile_created:
                self.stdout.write(self.style.SUCCESS(f"Профиль для testuser{num} создан"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Профиль для testuser{num} уже существует"))

            # Создайм заказы
            
            
"""
from typing import Any
from django.core.management import BaseCommand
from django.contrib.auth.models import User
from app.goods.models.order_models import Order, OrderItem, OrderStatus
from app.market.models import DeliveryType, TradePoint, DeliverySettings
from app.accounts.models import Profile
from app.goods.models.product_models import Product

class Command(BaseCommand):
    """The command class for create orders."""

    help = "Create test user orders"

    def handle(self, *args: Any, **options: Any) -> str | None:
        """
        Создает тестовые заказы
        """
        self.stdout.write("Starting to create test orders...")

        try:
            # Создаем или получаем тип доставки
            delivery, created_del = DeliveryType.objects.get_or_create(
                name="Standard Delivery",
                defaults={
                    "price": 200,
                    "is_express": False,
                },
            )
            if created_del:
                self.stdout.write(self.style.SUCCESS("Delivery type created"))
            else:
                self.stdout.write("Delivery type already exists")

            # Создаем настройки доставки
            delivery_settings, created_pol = DeliverySettings.objects.get_or_create(
                name="Default Delivery Settings",
                defaults={
                    "min_order_amount_for_free_delivery": 2000,
                    "delivery_cost": 200,
                    "express_delivery_cost": 500,
                },
            )
            if created_pol:
                self.stdout.write(self.style.SUCCESS("Delivery settings created"))
            else:
                self.stdout.write("Delivery settings already exist")

            # Создаем торговую точку
            trade_point, created_trade = TradePoint.objects.get_or_create(
                name="Main Store",
                city="Moscow",
                address="Red Square, 1",
                defaults={
                    "delivery_policy": delivery_settings,
                },
            )
            
            # Добавляем тип доставки к возможным типам торговой точки
            if delivery not in trade_point.possible_delivery_type.all():
                trade_point.possible_delivery_type.add(delivery)
                self.stdout.write(self.style.SUCCESS("Delivery type added to trade point"))
            
            if created_trade:
                self.stdout.write(self.style.SUCCESS("Trade point created"))
            else:
                self.stdout.write("Trade point already exists")

            # Создаем статус заказа "Новый" если его нет
            order_status, created_status = OrderStatus.objects.get_or_create(
                name="New",
                defaults={
                    "description": "New order, not processed yet"
                }
            )
            if created_status:
                self.stdout.write(self.style.SUCCESS("Order status 'New' created"))
            else:
                self.stdout.write("Order status 'New' already exists")

            # Получаем все активные товары
            products = list(Product.objects.filter(is_active=True))
            if not products:
                self.stdout.write(self.style.ERROR("No active products found! Create products first."))
                return

            # Создаем заказы для 10 пользователей
            for num in range(0, 10):
                # Создаем или получаем пользователя
                user, created = User.objects.get_or_create(
                    username=f"testuser{num}",
                    defaults={
                        "email": f"testuser{num}@example.com",
                        "is_active": True,
                    },
                )

                if created:
                    user.set_password("testpassword")
                    user.save()
                    self.stdout.write(self.style.SUCCESS(f"User testuser{num} created"))
                else:
                    self.stdout.write(f"User testuser{num} already exists")

                # Создаем или получаем профиль для пользователя
                profile, profile_created = Profile.objects.get_or_create(
                    user=user,
                    defaults={
                        "first_name": f"Test",
                        "last_name": f"User{num}",
                        "email": f"testuser{num}@example.com",
                        "phone": f"+79{num:02d}1234567",
                    },
                )

                if profile_created:
                    self.stdout.write(self.style.SUCCESS(f"Profile for testuser{num} created"))
                else:
                    self.stdout.write(f"Profile for testuser{num} already exists")

                # Создаем несколько заказов для каждого пользователя
                for order_num in range(1, 4):  # По 3 заказа на пользователя
                    order, order_created = Order.objects.get_or_create(
                        created_by=profile,
                        first_name=profile.first_name,
                        last_name=profile.last_name,
                        email=profile.email,
                        phone=profile.phone,
                        delivery_type=delivery,
                        trade_point=trade_point,
                        status=order_status,
                        defaults={
                            "comment": f"Test order #{order_num} for user {num}"
                        }
                    )

                    if order_created:
                        self.stdout.write(self.style.SUCCESS(f"Order #{order.id} created for user {num}"))
                        
                        # Добавляем случайные товары в заказ
                        import random
                        from decimal import Decimal
                        
                        # Случайное количество позиций в заказе (1-5)
                        num_items = random.randint(1, 5)
                        
                        # Выбираем случайные товары (без дубликатов в одном заказе)
                        selected_products = random.sample(products, min(num_items, len(products)))
                        
                        total_items = 0
                        for product in selected_products:
                            # Случайное количество товара (1-3)
                            quantity = random.randint(1, 3)
                            
                            # Учитываем доступное количество на складе
                            actual_quantity = min(quantity, product.quantity)
                            
                            if actual_quantity > 0:
                                order_item, item_created = OrderItem.objects.get_or_create(
                                    order=order,
                                    product=product,
                                    defaults={
                                        'quantity': actual_quantity,
                                        'price_at_time': product.final_price
                                    }
                                )
                                
                                if not item_created:
                                    # Если элемент уже существует, обновляем количество
                                    order_item.quantity = actual_quantity
                                    order_item.save()
                                
                                total_items += actual_quantity
                                self.stdout.write(f"  Added {actual_quantity}x {product.name}")
                        
                        # Обновляем общую сумму заказа
                        order.update_total_amount()
                        self.stdout.write(f"  Order #{order.id} has {total_items} items, total: {order.total_amount}")
                    else:
                        self.stdout.write(f"Order for user {num} already exists")

            self.stdout.write(self.style.SUCCESS("Successfully created test orders!"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
            return str(e)
"""