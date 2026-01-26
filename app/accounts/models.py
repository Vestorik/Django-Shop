from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext as _
from market.models import TradePoint


class Profile(models.Model):
    class Meta:
        verbose_name = _("Профиль")
        verbose_name_plural = _("Профили")

    user = models.OneToOneField("auth.User", related_name="profile", on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, blank=False, null=False)
    last_name = models.CharField(max_length=255, blank=False, null=False)
    email = models.EmailField(blank=False)
    phone = models.CharField(
        _("Телефон"),
        max_length=15,
        validators=[RegexValidator(regex=r"^\+?7?\d{10,11}$")],
        blank=False,
        null=False,
    )
    #  Выбранные торговые точки
    select_trade_point = models.ManyToManyField(
        TradePoint,
        related_name="profiles",
        verbose_name=_("Торговая точка"),
        blank=True,
    )

    @property
    def username(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __str__(self) -> str:
        return f"{_('Аккаунт пользователя')} {self.username}"

    def save(self, *args, **kwargs):
        """Сохраняем профиль"""
        super().save(*args, **kwargs)


class BankCart(models.Model):
    """
    Банковская карта пользователя
    """

    user = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="bank_carts",
        verbose_name=_("Пользователь"),
    )

    number = models.CharField(
        _("Номер карты"),
        max_length=19,  # XXXX XXXX XXXX XXXX
        help_text=_("Введите номер карты в формате XXXX XXXX XXXX XXXX"),
    )

    expiry_date = models.CharField(_("Срок действия"), max_length=5, help_text=_("Формат: MM/YY"))

    cvv = models.CharField(_("CVV"), max_length=3, help_text=_("3-х значный код на обороте карты"))
    cardholder_name = models.CharField(_("Имя держателя карты"), max_length=100)
    is_default = models.BooleanField(
        _("Основная карта"), default=False, help_text=_("Использовать по умолчанию для оплаты")
    )
    created_at = models.DateTimeField(_("Дата создания"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Дата обновления"), auto_now=True)

    class Meta:
        verbose_name = _("Банковская карта")
        verbose_name_plural = _("Банковские карты")
        ordering = ["-is_default", "-created_at"]

    def __str__(self) -> str:
        return f"Карта {self.cardholder_name} ({self.number[-4:]})"  
