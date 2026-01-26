from typing import Any
from django.core.management import BaseCommand
from accounts.models import Profile, BankCart
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Create test user profiles"

    def handle(self, *args: Any, **options: Any) -> str | None:
        self.stdout.write("Start create test profiles")

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

            # Создаем банковские карты для профиля
            card_numbers = [
                f"4111 1111 1111 1{num}01",
                f"5500 0000 0000 0{num}02",
                f"3782 822463 1{num}003",
            ]

            for i, card_number in enumerate(card_numbers):
                bank_cart, cart_created = BankCart.objects.get_or_create(
                    user=profile,
                    number=card_number,
                    defaults={
                        "expiry_date": "12/25",
                        "cvv": "123",
                        "cardholder_name": f"{profile.first_name} {profile.last_name}",
                        "is_default": i == 0,  # Первая карта по умолчанию
                    },
                )

                if cart_created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Банковская карта {card_number[-4:]} создана для {profile.username}"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Банковская карта {card_number[-4:]} уже существует для {profile.username}"
                        )
                    )

        self.stdout.write(self.style.SUCCESS("End create test profiles"))
