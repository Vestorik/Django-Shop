from typing import Any
from django.core.management import BaseCommand
from goods.models.order_models import Order, OrderItem
from goods.models.product_models import Product
from ..common_comand_tools import (
    get_or_create_test_user,
    get_or_create_test_profile_for_user,
    get_or_create_simple_test_object,
)


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
            delivery, created_del = get_or_create_simple_test_object("delivery")

            # Создаем настройки доставки
            delivery_settings, created_pol = get_or_create_simple_test_object(
                "delivery_settings"
            )

            # Создаем торговую точку
            trade_point, created_trade = get_or_create_simple_test_object(
                class_name="trade_point",
                for_complex_atr={"delivery_policy": delivery_settings},
            )

            # Добавляем тип доставки к возможным типам торговой точки
            if delivery not in trade_point.possible_delivery_type.all():
                trade_point.possible_delivery_type.add(delivery)

            if created_trade:
                self.stdout.write(self.style.SUCCESS("Trade point created"))
            else:
                self.stdout.write("Trade point already exists")

            # Создаем статус заказа
            order_status, created_status = get_or_create_simple_test_object(
                "order_status"
            )

            # Получаем все активные товары
            products = list(Product.objects.filter(is_active=True))
            if not products:
                self.stdout.write(
                    self.style.ERROR("No active products found! Create products first.")
                )
                return

            # Создаем заказы для 10 пользователей
            for num in range(0, 10):
                # Создаем или получаем пользователя
                user, created = get_or_create_test_user(f"testuser{num}")

                # Создаем или получаем профиль для пользователя
                profile, profile_created = get_or_create_test_profile_for_user(user)

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
                        defaults={"comment": f"Test order #{order_num} for user {num}"},
                    )

                    if order_created:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Order #{order.id} created for user {num}"
                            )
                        )

                        # Добавляем случайные товары в заказ
                        import random
                        from decimal import Decimal

                        # Случайное количество позиций в заказе (1-5)
                        num_items = random.randint(1, 5)

                        # Выбираем случайные товары (без дубликатов в одном заказе)
                        selected_products = random.sample(
                            products, min(num_items, len(products))
                        )

                        total_items = 0
                        for product in selected_products:
                            # Случайное количество товара (1-3)
                            quantity = random.randint(1, 3)

                            # Учитываем доступное количество на складе
                            actual_quantity = min(quantity, product.quantity)

                            if actual_quantity > 0:
                                order_item, item_created = (
                                    OrderItem.objects.get_or_create(
                                        order=order,
                                        product=product,
                                        defaults={
                                            "quantity": actual_quantity,
                                            "price_at_time": product.final_price,
                                        },
                                    )
                                )

                                if not item_created:
                                    # Если элемент уже существует, обновляем количество
                                    order_item.quantity = actual_quantity
                                    order_item.save()

                                total_items += actual_quantity
                                self.stdout.write(
                                    f"  Added {actual_quantity}x {product.name}"
                                )

                        # Обновляем общую сумму заказа
                        order.update_total_amount()
                        self.stdout.write(
                            f"  Order #{order.id} has {total_items} items, total: {order.total_amount}"
                        )
                    else:
                        self.stdout.write(f"Order for user {num} already exists")

            self.stdout.write(self.style.SUCCESS("Successfully created test orders!"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
            return str(e)
