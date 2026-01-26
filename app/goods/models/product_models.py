from django.db import models
from django.utils.translation import gettext_lazy as _
from app.settings import BASE_DIR



def product_image_directory_path(instance: "Product", filename: str) -> str:
    """
        Генерирует путь для сохранения превью товара.
        Формат: products/product_<id>/image/<filename>
    """
    create_path = f"loads/products/product_{instance.pk}/image/{filename}"
    full_path = BASE_DIR.parent / create_path
    return str(full_path)


class Category(models.Model):
    """
    Модель категории товара
    """

    class Meta:
        verbose_name = _("Категория")
        verbose_name_plural = _("Категории")
        ordering = ["order", "name"]

    name = models.CharField(verbose_name=_("Название"), max_length=100)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subcategories",
        verbose_name=_("Родительская категория"),
    )
    image = models.ImageField(
        verbose_name="Изображение", upload_to="categories/", null=True, blank=True
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок отображения")

    def __str__(self):
        return f'{_("Модель категории товара")} {self.name}'

    @property
    def title(self) -> str:
        return str(self.name)


class Product(models.Model):
    """
        Основная модель товара интернет-магазина.

        Содержит:
        - Название, описание, цену, скидку
        - Данные о наличии и рейтинге
        - Превью, теги, изображения, характеристики
        - Связь с пользователем-создателем

        Поля:
        - name: название товара;
        - full_description: подробное описание;
        - created_at: дата создания записи;
        - created_by: пользователь, создавший товар;
        - price: базовая цена;
        - discount: размер скидки в процентах;
        - limited: флаг ограниченного товара;
        - quantity: количество на складе;
        - rating: рейтинг товара;
        - preview: превью‑изображение.

        Вычисляемые свойства:
        - final_price — цена со скидкой
        - title — совместимость с шаблоном
        - number_comments — количество отзывов
    """

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    # Основная информация о продукте
    name = models.CharField(verbose_name="Название", max_length=100)
    full_description = models.TextField(verbose_name="Описание", null=True, blank=True)

    created_at = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True)
    created_by = models.ForeignKey(
        "auth.User", on_delete=models.SET_NULL, blank=True, null=True, related_name="products"
    )

    price = models.DecimalField(verbose_name="Цена", max_digits=10, decimal_places=2)
    discount = models.DecimalField(
        verbose_name="Скиддка", max_digits=5, decimal_places=2, default=0
    )

    # Статус продукта
    limited = models.BooleanField(verbose_name="Ограниченный товар", default=False)
    is_active = models.BooleanField(verbose_name="Активен", default=True)
    quantity = models.PositiveIntegerField(verbose_name="Количество на складе", default=0)

    rating = models.DecimalField(
        verbose_name="Рейтинг", max_digits=3, decimal_places=2, default=0.0  # type: ignore
    )
    # Транспортировка и доставка
    free_delivery = models.BooleanField(verbose_name="Бесплатная доставка", default=False)
    transport_class = models.PositiveIntegerField(
        verbose_name="Класс транспортировки продукта", default=0
    )  # для расчёта стоимости доставки, имитирует массу и габариты товара

    # Другое
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
        verbose_name="Категория",
    )
    preview = models.ImageField(
        verbose_name="Превью товара",
        null=True,
        blank=True,
        upload_to=product_image_directory_path,  # type: ignore
    )

    def __str__(self):
        return f'{_("Модель товара")} {self.name}'

    @property
    def final_price(self) -> float:
        """Цена со скидкой"""

        try:
            # Самый простой и надежный способ
            price = (
                float(self.price)
                if self.price is not None
                else 0.0  # ty:ignore[invalid-argument-type]
            )
            if self.discount is not None:
                try:
                    discount = float(str(self.discount))
                except (ValueError, TypeError):
                    discount = 0.0
            else:
                discount = 0.0
            # Ограничиваем значение скидки
            discount = max(0.0, min(100.0, discount))

            return price * (1 - discount / 100)

        except Exception:
            # Фолбэк на случай любых других ошибок
            return (
                float(self.price)
                if self.price is not None
                else 0.0  # ty:ignore[invalid-argument-type]
            )

    @property
    def title(self):
        """Совместимость с шаблоном: product.title → product.name"""
        return self.name

    @property
    def number_comments(self):
        """Возвращает количество отзывов"""
        return self.comments.count()

    @property
    def description(self):
        if not self.full_description:
            return "Описание отсутствует"
        elif len(self.full_description) < 100:  # ty:ignore[invalid-argument-type]
            return self.full_description
        return str(self.full_description)[:100]


class ProductSpecification(models.Model):
    """
    Характеристика товара — гибкий способ описания параметров.
    Позволяет добавлять пары 'Название: Значение' без привязки к жёсткой схеме.
    Пример: Материал → Хлопок 100%, Цвет → Синий.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="specifications",
        verbose_name="Товар",
    )
    name = models.CharField("Название", max_length=100)  # Например: "Материал"
    value = models.CharField("Значение", max_length=255)  # Например: "Хлопок 100%"

    class Meta:
        verbose_name = "Характеристика"
        verbose_name_plural = "Характеристики"


class Comment(models.Model):
    """
    Отзыв пользователя на товар.
    Содержит оценку (product_estimation) и текст.
    """

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="comments", verbose_name="Товар"
    )

    created_at = models.DateTimeField("Дата", auto_now_add=True)
    created_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        related_name="comments",
        blank=True,
        null=True,
        verbose_name="Автор отзыва",
    )

    product_estimation = models.DecimalField("Оценка товара", max_digits=3, decimal_places=2)
    description = models.TextField("Текст отзыва", blank=True)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Отзыв от {self.created_by} на {self.product}"


class ProductImage(models.Model):
    """
    Изображение для товара. Поддерживает несколько фото с указанием порядка.
    Привязано к Product через ForeignKey.
    """

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images", verbose_name="Товар"
    )
    src = models.ImageField("Изображение", upload_to=product_image_directory_path)
    alt = models.CharField("Описание изображения", max_length=200, blank=True)
    order = models.PositiveIntegerField("Порядок отображения", default=0)

    class Meta:
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товаров"
        ordering = ["order"]

    def __str__(self):
        return f"Изображение {self.product.name}"


class Tag(models.Model):
    """
    Метка для классификации товаров (например: 'Хит продаж', 'Новинка', 'Экологичный').
    Связана с товарами через ManyToMany.
    """

    name = models.CharField(max_length=50)
    product = models.ManyToManyField(Product, related_name="tags")

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self) -> str:
        return f"{_('Метка для классификации товаров')}  {self.name}"
