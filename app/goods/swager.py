# api_endpoints.py

API_ENDPOINTS = {
    # 🔐 auth — Авторизация
    "auth": {
        "sign_in": {
            "method": "POST",
            "url": "/sign-in",
            "description": "Вход в систему",
            "params": {
                "username": {"type": "string", "required": True},
                "password": {"type": "string", "required": True},
            },
            "responses": [200, 500]
        },
        "sign_up": {
            "method": "POST",
            "url": "/sign-up",
            "description": "Регистрация пользователя",
            "params": {
                "name": {"type": "string", "required": True},
                "username": {"type": "string", "required": True},
                "password": {"type": "string", "required": True},
            },
            "responses": [200, 500]
        },
        "sign_out": {
            "method": "POST",
            "url": "/sign-out",
            "description": "Выход из системы",
            "params": {},
            "responses": [200]
        },
    },

    # 🛒 catalog — Каталог
    "catalog": {
        "get_categories": {
            "method": "GET",
            "url": "/categories",
            "description": "Получить меню категорий",
            "params": {},
            "response_schema": "CatalogItems"
        },
        "get_catalog": {
            "method": "GET",
            "url": "/catalog",
            "description": "Получить товары с фильтрацией и пагинацией",
            "params": {
                "filter[name]": {"type": "string", "required": False},
                "filter[minPrice]": {"type": "number", "required": False},
                "filter[maxPrice]": {"type": "number", "required": False},
                "filter[freeDelivery]": {"type": "boolean", "default": False},
                "filter[available]": {"type": "boolean", "default": True},
                "currentPage": {"type": "number", "default": 1},
                "category": {"type": "number", "required": False},
                "sort": {"type": "string", "enum": ["rating", "price", "reviews", "date"], "default": "date"},
                "sortType": {"type": "string", "enum": ["dec", "inc"], "default": "dec"},
                "tags": {"type": "array", "items": "Tag", "required": False},
                "limit": {"type": "number", "default": 20},
            },
            "response_schema": {
                "items": "Products",
                "currentPage": "number",
                "lastPage": "number"
            }
        },
        "get_popular_products": {
            "method": "GET",
            "url": "/products/popular",
            "description": "Получить популярные товары",
            "params": {},
            "response_schema": "Products"
        },
        "get_limited_products": {
            "method": "GET",
            "url": "/products/limited",
            "description": "Получить ограниченные товары",
            "params": {},
            "response_schema": "Products"
        },
        "get_sales": {
            "method": "GET",
            "url": "/sales",
            "description": "Получить акционные товары",
            "params": {
                "currentPage": {"type": "number", "default": 1}
            },
            "response_schema": {
                "items": "Sales",
                "currentPage": "number",
                "lastPage": "number"
            }
        },
        "get_banners": {
            "method": "GET",
            "url": "/banners",
            "description": "Получить баннеры (рекомендуемые товары)",
            "params": {},
            "response_schema": "Products"
        },
    },

    # 📦 basket — Корзина
    "basket": {
        "get_basket": {
            "method": "GET",
            "url": "/basket",
            "description": "Получить товары в корзине",
            "params": {},
            "response_schema": "Basket"
        },
        "add_to_basket": {
            "method": "POST",
            "url": "/basket",
            "description": "Добавить товар в корзину",
            "params": {},
            "request_body": {
                "id": {"type": "number"},
                "count": {"type": "number"}
            },
            "response_schema": "Basket"
        },
        "remove_from_basket": {
            "method": "DELETE",
            "url": "/basket",
            "description": "Удалить товар из корзины",
            "params": {},
            "request_body": {
                "id": {"type": "number"},
                "count": {"type": "number"}
            },
            "response_schema": "Basket"
        },
    },

    # 📦 order — Заказы
    "order": {
        "get_orders": {
            "method": "GET",
            "url": "/orders",
            "description": "Получить активные заказы",
            "params": {},
            "response_schema": ["Order"]
        },
        "create_order": {
            "method": "POST",
            "url": "/orders",
            "description": "Создать заказ",
            "params": {},
            "request_body": "Basket",
            "response_schema": {
                "orderId": "number"
            }
        },
        "get_order": {
            "method": "GET",
            "url": "/orders/{id}",
            "description": "Получить информацию о заказе",
            "path_params": ["id"],
            "response_schema": "Order"
        },
        "confirm_order": {
            "method": "POST",
            "url": "/orders/{id}",
            "description": "Подтвердить заказ",
            "path_params": ["id"],
            "request_body": "Order",
            "responses": [200]
        },
    },

    # 💳 payment — Оплата
    "payment": {
        "pay_order": {
            "method": "POST",
            "url": "/payment",
            "description": "Оплатить заказ",
            "path_params": ["id"],
            "request_body": {
                "number": {"type": "string"},
                "name": {"type": "string"},
                "month": {"type": "string"},
                "year": {"type": "string"},
                "code": {"type": "string"}
            },
            "responses": [200]
        }
    },

    # 👤 profile — Профиль
    "profile": {
        "get_profile": {
            "method": "GET",
            "url": "/profile",
            "description": "Получить профиль пользователя",
            "params": {},
            "response_schema": "User"
        },
        "update_profile": {
            "method": "POST",
            "url": "/profile",
            "description": "Обновить данные профиля",
            "request_body": "User",
            "response_schema": "User"
        },
        "update_password": {
            "method": "POST",
            "url": "/profile/password",
            "description": "Сменить пароль",
            "request_body": {
                "currentPassword": {"type": "string"},
                "newPassword": {"type": "string"}
            },
            "responses": [200]
        },
        "update_avatar": {
            "method": "POST",
            "url": "/profile/avatar",
            "description": "Загрузить аватар (files: avatar)",
            "responses": [200]
        },
    },

    # 🏷️ tags — Теги
    "tags": {
        "get_tags": {
            "method": "GET",
            "url": "/tags",
            "description": "Получить теги",
            "params": {
                "category": {"type": "number", "required": False}
            },
            "response_schema": ["Tag"]
        }
    },

    # 📦 product — Продукт
    "product": {
        "get_product": {
            "method": "GET",
            "url": "/product/{id}",
            "description": "Получить полную информацию о товаре",
            "path_params": ["id"],
            "response_schema": "ProductFull"
        },
        "post_review": {
            "method": "POST",
            "url": "/product/{id}/review",
            "description": "Оставить отзыв на товар",
            "path_params": ["id"],
            "request_body": {
                "author": {"type": "string"},
                "email": {"type": "string"},
                "text": {"type": "string"},
                "rate": {"type": "integer"},
                "date": {"type": "string"}
            },
            "response_schema": ["Review"]
        }
    }
}

# Пример использования:
# print(API_ENDPOINTS["auth"]["sign_in"]["url"])
# print(API_ENDPOINTS["catalog"]["get_catalog"]["params"])
