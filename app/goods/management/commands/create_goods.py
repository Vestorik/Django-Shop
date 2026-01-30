from typing import Any
from django.core.management import BaseCommand
from goods.management.common_comand_tools import create_test_product, get_or_create_test_user


class Command(BaseCommand):
    help = "Create test products, specification, tads and comment"

    def handle(self, *args: Any, **options: Any) -> str | None:

        self.stdout.write("Start create test goods")

        # create user
        user, created = get_or_create_test_user("testuser")
        del created
        for num in range(0, 10):
            try:
                
                #  Create test products, specification, tads and comment
                product, bool_creatd_product = create_test_product(user,num )
                del bool_creatd_product
                
                if product is None:
                    self.stdout.write(self.style.ERROR(f"Error create product {num}"))
                    continue
                self.stdout.write(self.style.SUCCESS(f"Product {product.name} created"))

            except Exception as eg:
                self.stdout.write(self.style.ERROR(f"Create product Error {eg}"))
        self.stdout.write(self.style.SUCCESS("End create test goods"))
