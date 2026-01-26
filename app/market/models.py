from django.db import models
from django.utils.translation import gettext as _
from django.core.validators import MinValueValidator


# Доставка и торговые точки
class DeliverySettings(models.Model):
    """
    Настройки доставки (управляются через админку)
    """
    name = models.CharField(blank=False, max_length=100)

    min_order_amount_for_free_delivery = models.DecimalField(
        verbose_name=_("Минимальная сумма для бесплатной доставки"),
        max_digits=10,
        decimal_places=2,
        default=2000,
        help_text=_("При заказе дороже этой суммы доставка бесплатная"),
    )
    delivery_cost = models.DecimalField(
        verbose_name=_("Стоимость доставки"),
        max_digits=10,
        decimal_places=2,
        default=200,
        help_text=_("Стоимость обычной доставки при заказе дешевле мин. суммы"),
    )
    express_delivery_cost = models.DecimalField(
        verbose_name=_("Стоимость экспресс-доставки"),
        max_digits=10,
        decimal_places=2,
        default=500,
        help_text=_("Фиксированная стоимость экспресс-доставки"),
    )

    class Meta:
        verbose_name = _("Настройки доставки")
        verbose_name_plural = _("Настройки доставки")

    def __str__(self):
        return _("Настройки доставки")


class DeliveryType(models.Model):
    """
    Тип доставки
    """

    is_express = models.BooleanField(default=False,     
        verbose_name=_("Экспресс-доставка"),
        help_text=_("Отметьте, если это тип экспресс-доставки")
    )
    name = models.CharField(_("Название"), max_length=100)
    price = models.DecimalField(
        _("Стоимость"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        verbose_name = _("Тип доставки")
        verbose_name_plural = _("Типы доставки")

    def __str__(self):
        return f'{_("Тип доставки")} {self.name}'


class TradePoint(models.Model):
    class Meta:
        verbose_name = _("Торговая точка")
        verbose_name_plural = _("Торговые точки")

    name = models.CharField(
    _("Название"), 
    max_length=100, 
    blank=True, 
    null=True
    )
    city = models.CharField(_("Город"), max_length=100)
    address = models.TextField(_("Адрес"))
    possible_delivery_type = models.ManyToManyField(
        DeliveryType,
        blank=True,
        related_name="trade_points",
        verbose_name=_("Возможные типы доставки"),
    )
    delivery_policy = models.ForeignKey(
        DeliverySettings, on_delete=models.PROTECT, related_name="trade_points"
    )

    def __str__(self):
        trade_pount_text = _("Торговая точка")
        return f"{trade_pount_text} {self.name} - {self.city} - {self.address}"
