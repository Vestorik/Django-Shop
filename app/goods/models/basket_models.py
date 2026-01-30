from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from accounts.models import Profile
from goods.models import Product



class BasketItem(models.Model):
    """
    Элемент корзины — промежуточная модель для связи Basket и Product
    """

    basket = models.ForeignKey(
        "Basket",
        on_delete=models.CASCADE,
        related_name="basket_items",
        verbose_name=_("Корзина"),
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, verbose_name=_("Товар")
    )
    quantity = models.PositiveIntegerField(
        _("Количество"), default=1, validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = _("Элемент корзины")
        verbose_name_plural = _("Элементы корзины")
        unique_together = ("basket", "product")

    def __str__(self):
        return f"{self.product.name} — {self.quantity} шт."

    def get_total_price(self):
        return self.quantity * self.product.final_price


class Basket(models.Model):
    """
    Модель корзины
    """

    class Meta:
        verbose_name = _("Корзина")

    id = models.AutoField(primary_key=True)
    updated_at = models.DateTimeField(_("Дата обновления"), auto_now=True)
    owner = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        verbose_name=_("Владелец"),
        null=True,
        blank=False,
    )

    # Поля для хранения контактной информации (дублируем из профиля на случай удаления)

    products = models.ManyToManyField(
        Product,
        through="BasketItem",
        through_fields=("basket", "product"),
        verbose_name=_("Товары"),
    )

    def __str__(self):
        """Строковое представление заказа"""
        return f"{_('Корзина польщователя')} №{self.id} - {self.owner.username}"
