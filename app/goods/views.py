"""Views for goods app"""

from typing import Any
from django.http import HttpRequest, QueryDict
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Product, Tag
from .serializers import ProductSerializer

# Create your views here.


class CatalogView(TemplateView):
    template_name = "frontend/catalog.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return super().get_context_data(**kwargs)


class ProductView(TemplateView):
    template_name = "frontend/product.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        product_id = self.kwargs.get("id")
        context["product_id"] = product_id
        return context


@method_decorator(csrf_exempt, name="dispatch")
class CatalogAPIView(APIView):
    # Обрабатываем запросы
    # без фильтрации
    def get(self, request: HttpRequest):
        return self._process(request)

    # с фильтрацией запрос становится post
    def post(self, request: HttpRequest):
        return self._process(request)

    def _process(self, request: HttpRequest):

        if request.method == "POST":
            # Если это POST, но не JSON — используем request.POST
            data: QueryDict = request.POST
        else:
            data: QueryDict = request.GET

        #  Фильтры
        # filter[minPrice] → data.get('filter[minPrice]')
        min_price: str | None = data.get("filter[minPrice]")
        max_price: str | None = data.get("filter[maxPrice]")
        name: str = data.get("filter[name]", "")
        available: str | bool = data.get("filter[available]") == "true"
        free_delivery: str | bool = data.get("filter[freeDelivery]") == "true"

        #  Сортировка
        sort_field: str = data.get("sort", "id")
        sort_type: str = data.get("sortType", "inc")
        order_by: str = "id"

        sort_mapping: dict = {
            ("price", "inc"): "price",
            ("price", "dec"): "-price",
            ("rating", "dec"): "-rating",
            ("name", "inc"): "name",
            ("name", "dec"): "-name",
            ("reviews", "dec"): "-comments_count",  # если посчитаем
            ("date", "dec"): "-created_at",
        }
        order_by: str = sort_mapping.get((sort_field, sort_type), "id")

        # Пагинация
        page = int(data.get("currentPage", 1))
        limit = int(data.get("limit", 9))
        offset: int = (page - 1) * limit

        #  Теги
        # tags[]=1&tags[]=2 → request.GET.getlist('tags[]') или request.POST
        tag_ids: list = data.getlist("tags[]") or []
        try:
            tag_ids = [int(tid) for tid in tag_ids if tid]
        except (ValueError, TypeError):
            tag_ids = []

        # Запрос
        products = Product.objects.filter(is_active=True)

        if min_price:
            try:
                products = products.filter(price__gte=float(min_price))
            except (ValueError, TypeError):
                pass
        if max_price:
            try:
                products = products.filter(price__lte=float(max_price))
            except (ValueError, TypeError):
                pass
        if name:
            products = products.filter(name__icontains=name)
        if available:
            products = products.filter(quantity__gt=0)
        if free_delivery:
            products = products.filter(free_delivery=True)

        # === Фильтр по тегам ===
        if tag_ids:
            products = products.filter(tags__id__in=tag_ids).distinct()

        # Сортировка
        products = products.order_by(order_by)

        # === Пагинация ===
        total = products.count()
        products = products[offset : offset + limit]

        # === Сериализация ===
        items = []
        for p in products:
            main_image = p.images.first()
            items.append(
                {
                    "id": p.id,
                    "title": p.name,
                    "price": float(p.final_price),
                    "images": (
                        [
                            {
                                "src": (
                                    main_image.src.url
                                    if main_image
                                    else "/static/frontend/assets/img/no-image.png"
                                ),
                                "alt": main_image.alt or p.name,
                            }
                        ]
                        if main_image
                        else {
                            "src": "/static/frontend/assets/img/no-image.png",
                            "alt": "Нет изображения",
                        }
                    ),
                }
            )

        return Response(
            {
                "items": items,
                "currentPage": page,
                "lastPage": (total - 1) // limit + 1 if limit else 1,
                "total": total,
            }
        )


class ProductApiView(APIView):

    def get(self, request, id):
        product = get_object_or_404(
            Product.objects.prefetch_related(
                "images", "specifications", "comments__created_by", "tags"
            ),
            pk=id,
        )
        setattr(product, "number_comments", product.comments.count())

        serializer = ProductSerializer(product, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def tags_api(request):
    tags = Tag.objects.all().values("id", "name")
    return Response([{**tag, "selected": False} for tag in tags])


@api_view(["GET"])
def categories_api(request):
    return Response([])  # или пусто


@api_view(["GET"])
def basket_api(request):
    return Response({"items": [], "total": 0})
