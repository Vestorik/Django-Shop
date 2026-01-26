from typing import Any
from django.core.management import BaseCommand
from app.goods.models.product_models import Product, Comment, Tag, ProductSpecification
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Create test products, specification, tads and comment"

    def handle(self, *args: Any, **options: Any) -> str | None:
        """Create test products, specification, tads and comment"""
        self.stdout.write("Start create test goods")

        # create user
        user, created = User.objects.get_or_create(
            username=f"testuser{1}",
            defaults={
                "email": "test@example.com",
                "is_active": True,
            },
        )
        if created:
            user.set_password("testpassword")
            user.save()
            self.stdout.write(self.style.SUCCESS("Пользователь testuser создан"))
        else:
            self.stdout.write(
                self.style.SUCCESS("Пользователь testuser уже существует")
            )

        for num in range(0, 10):
            try:
                name_product = f"test_product{num}"
                name_tag = f"test_tag{num}"
                name_specific = f"test_specific{num}"

                product, bool_creatd_product = Product.objects.get_or_create(
                    name=name_product,
                    defaults={
                        "price": 1000,
                        "discount": 10,
                        "limited": True,
                        "quantity": 100,
                        "rating": 5,
                        "is_active": True,
                        "full_description": "test Product",
                        "created_by": user,
                    },
                )

                if bool_creatd_product is None:
                    try:
                        product.price = 1000.0
                        product.discount = 10
                        product.limited = True
                        product.quantity = 100
                        product.rating = 5
                        product.is_active = True
                        product.full_description = "test Product"
                        product.created_by = user

                        product.save(
                            update_fields=[
                                "price",
                                "discount",
                                "limited",
                                "quantity",
                                "rating",
                                "is_active",
                                "full_description",
                                "created_by",
                            ]
                        )
                    except Exception as e:
                        print(f"Не удалось сохранить продукт: {e}")

                tag, bool_creatd_tag = Tag.objects.get_or_create(name=name_tag)
                product.tags.add(tag)

                comment = Comment.objects.create(
                    product=product,
                    created_by=user,
                    product_estimation=5,
                    description="Its test comment",
                )

                specification = ProductSpecification.objects.create(
                    name=name_specific, value="100% test", product=product
                )

            except Exception as eg:
                self.stdout.write(self.style.ERROR(f"Create product Error {eg}"))
        self.stdout.write(self.style.SUCCESS("End create test goods"))
