from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from accounts.models import Profile
from market.models import DeliveryType, TradePoint
from .product_models import Product


class OrderStatus(models.Model):
    """
    Статус заказа
    """

    class Meta:
        verbose_name = _("Статус заказа")
        verbose_name_plural = _("Статусы заказов")

    name = models.CharField(_("Название"), max_length=50)

    def __str__(self):
        return f'{_("Статус заказа")} {self.name}'


class OrderItem(models.Model):
    """
    Элемент заказа (связующая модель для ManyToMany между Order и Product)
    """

    class Meta:
        verbose_name = _("Элемент заказа")
        verbose_name_plural = _("Элементы заказа")
        unique_together = ["order", "product"]

    # Fields
    order = models.ForeignKey(
        "Order",
        on_delete=models.CASCADE,
        related_name="order_items",
        verbose_name=_("Заказ"),
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_("Товар"))
    quantity = models.PositiveIntegerField(
        _("Количество"), default=1, validators=[MinValueValidator(1)]
    )
    price_at_time = models.DecimalField(
        _("Цена на момент заказа"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    def __str__(self):
        return f"{self.product.name} - {self.quantity} шт."

    def get_unit_price(self):
        """Возвращает цену за единицу товара на момент заказа"""
        return self.price_at_time

    def get_total_price(self):
        """Возвращает общую стоимость товара в заказе"""
        return self.quantity * self.price_at_time  # ty:ignore[unsupported-operator]

    def save(self, *args, **kwargs):
        """При сохранении устанавливаем цену на момент заказа"""
        if not self.price_at_time:
            self.price_at_time = self.product.final_price
        super().save(*args, **kwargs)


class Order(models.Model):
    """
    Модель заказа
    """

    class Meta:
        verbose_name = _("Заказ")
        verbose_name_plural = _("Заказы")
        ordering = ["-created_at"]

    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(_("Дата создания"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Дата обновления"), auto_now=True)
    created_by = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        verbose_name=_("Создан пользователем"),
        null=True,
        blank=False,
    )

    # Поля для хранения контактной информации (дублируем из профиля на случай удаления)
    first_name = models.CharField(_("Имя"), max_length=50)
    last_name = models.CharField(_("Фамилия"), max_length=50)
    email = models.EmailField(_("Email"))
    phone = models.CharField(_("Телефон"), max_length=20)

    delivery_type = models.ForeignKey(
        DeliveryType, on_delete=models.PROTECT, verbose_name=_("Тип доставки")
    )
    trade_point = models.ForeignKey(
        TradePoint, on_delete=models.PROTECT, verbose_name=_("Торговая точка"), blank=False
    )
    comment = models.TextField(_("Комментарий к заказу"), blank=True, null=True)

    products = models.ManyToManyField(Product, through="OrderItem", verbose_name=_("Товары"))
    status = models.ForeignKey(OrderStatus, on_delete=models.PROTECT, verbose_name=_("Статус"))

    # Финансовые поля
    delivery_cost = models.DecimalField(
        _("Стоимость доставки"),
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    total_amount = models.DecimalField(
        _("Общая сумма"),
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    def __str__(self):
        """Строковое представление заказа"""
        if self.created_by:
            return f"{_('Заказ')} №{self.id} - {self.created_by.username}"
        return f"{_('Заказ')} №{self.id}"

    def calculate_total_price(self):
        """Рассчитывает общую стоимость заказа"""
        # Сумма стоимости всех товаров
        items_total = sum(item.get_total_price() for item in self.order_items.all())

        # Проверяем, бесплатна ли доставка
        delivery_policy = self.trade_point.delivery_policy  # Получаем настройки доставки

        # Если настройки доставки получены, применяем минимальную сумму, иначе устанавливаем значение по умолчанию
        free_delivery_amount = (
            delivery_policy.min_order_amount_for_free_delivery
            if delivery_policy
            else Decimal("2000")
        )

        if items_total >= free_delivery_amount:
            delivery_cost = Decimal("0")
        else:
            delivery_cost = self.delivery_type.price

        # Добавляем стоимость экспресс-доставки если выбрана
        if self.delivery_type.is_express and delivery_policy:
            delivery_cost += delivery_policy.express_delivery_cost

        return items_total + delivery_cost

    def update_total_amount(self):
        """Обновляет общую сумму заказа"""
        self.total_amount = self.calculate_total_price()
        self.save()

    def change_status(self, status_name):
        """
        Изменяет статус заказа

        Args:
            status_name: Название статуса

        Returns:
            bool: True если статус успешно изменен, False в противном случае
        """
        try:
            status = OrderStatus.objects.get(name=status_name)
            self.status = status
            self.save()
            return True
        except OrderStatus.DoesNotExist:
            print(f"Статус '{status_name}' не существует")
            return False
        except Exception as e:
            print(f"Ошибка при изменении статуса: {e}")
            return False
