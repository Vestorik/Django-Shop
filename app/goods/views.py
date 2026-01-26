"""Views for goods app"""

from collections import OrderedDict
from django.db.models import Q, Prefetch, Case, When, Value, DecimalField, F

from typing import Any
from django.http import HttpRequest, QueryDict
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Product, Tag, Category
from .serializers import ProductSerializer


# Пагинация
class StandardResultsSetPagination(PageNumberPagination):
    """
    Пагинатор для постраничного отображения результатов.

    Этот класс наследуется от `PageNumberPagination` и настраивает параметры пагинации
    для использования в API. Позволяет клиенту управлять размером страницы через
    параметр запроса, при этом ограничивая максимальное количество элементов
    на одной странице для предотвращения перегрузки.

    Атрибуты:
        page_size (int): Количество элементов на одной странице по умолчанию.
        page_size_query_param (str): Имя параметра в URL, через который клиент
            может указать желаемое количество элементов на странице.
        max_page_size (int): Максимально допустимое количество элементов
            на одной странице, независимо от значения, переданного клиентом.
    """

    page_size = 9
    page_size_query_param = "limit"
    max_page_size = 100


class CatalogView(TemplateView):
    """Класс для отображения шаблона каталога товаров"""

    template_name = "frontend/catalog.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return super().get_context_data(**kwargs)


class ProductView(TemplateView):
    """Класс для отоброжения шаблона товара"""

    template_name = "frontend/product.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        product_id = self.kwargs.get("id")
        context["product_id"] = product_id
        return context


@method_decorator(csrf_exempt, name="dispatch")
class CatalogAPIView(APIView):
    """
    API для работы с каталогом товаров.
    
    Поддерживает GET и POST запросы для получения отфильтрованных и отсортированных товаров.
    Реализует пагинацию, фильтрацию по различным критериям и сортировку.
    """
    
    def get(self, request):
        """Обработка GET запросов"""
        return self.process_request(request, request.query_params)
    
    def post(self, request):
        """Обработка POST запросов"""
        return self.process_request(request, request.data)
    
    def process_request(self, request, params):
        """
        Основной метод обработки запроса.
        
        Args:
            request: HTTP запрос
            params: Параметры запроса (из query_params или data)
            
        Returns:
            Response: JSON ответ с товарами и метаданными пагинации
        """
        try:
            # Получаем базовый queryset с предзагрузкой связанных данных
            queryset = self.get_base_queryset()
            
            # Применяем фильтры
            queryset = self.apply_filters(queryset, params)
            
            # Применяем сортировку
            queryset = self.apply_sorting(queryset, params)
            
            # Пагинация
            return self.paginate_and_respond(queryset, request)
            
        except Exception as e:
            # Логируем ошибку (в реальном проекте используйте proper logging)
            print(f"Error in CatalogAPIView: {str(e)}")
            return Response(
                {
                    "items": [],
                    "currentPage": 1,
                    "lastPage": 1,
                    "total": 0
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_base_queryset(self):
        """
        Возвращает базовый queryset с предзагрузкой связанных данных.
        
        Returns:
            QuerySet: Базовый queryset продуктов
        """
        return Product.objects.filter(is_active=True).prefetch_related(
            "images", 
            "tags", 
            "specifications",
            "category",
            "comments"
        )
    
    def apply_filters(self, queryset, params):
        """
        Применяет фильтры к queryset.
        
        Args:
            queryset: Исходный queryset
            params: Параметры фильтрации
            
        Returns:
            QuerySet: Отфильтрованный queryset
        """
        # Поиск по названию
        if filter_name := params.get("filter"):
            queryset = queryset.filter(name__icontains=filter_name)
        
        # Фильтрация по цене
        if min_price := params.get("minPrice"):
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except (ValueError, TypeError):
                pass
                
        if max_price := params.get("maxPrice"):
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except (ValueError, TypeError):
                pass
        
        # Фильтрация по наличию
        if available := params.get("available"):
            if available in ["true", True, "1"]:
                queryset = queryset.filter(quantity__gt=0)
        
        # Фильтрация по бесплатной доставке
        if free_delivery := params.get("freeDelivery"):
            if free_delivery in ["true", True, "1"]:
                queryset = queryset.filter(free_delivery=True)
        
        # Фильтрация по категории
        if category_id := params.get("category"):
            if category_id not in ["null", "", None]:
                try:
                    queryset = queryset.filter(category__id=int(category_id))
                except (ValueError, TypeError):
                    pass
        
        # Фильтрация по тегам
        tags = self.get_tags_from_params(params)
        for tag_id in tags:
            try:
                queryset = queryset.filter(tags__id=int(tag_id))
            except (ValueError, TypeError):
                pass
        
        return queryset
    
    def get_tags_from_params(self, params):
        """
        Извлекает ID тегов из параметров запроса.
        
        Args:
            params: Параметры запроса
            
        Returns:
            list: Список ID тегов
        """
        tags = []
        
        if hasattr(params, "getlist"):
            # QueryDict (GET запрос)
            tags = params.getlist("tags")
        else:
            # Dict (POST запрос)
            tags_data = params.get("tags", [])
            if isinstance(tags_data, list):
                tags = tags_data
            elif tags_data:
                tags = [tags_data]
                
        return tags
    
    def apply_sorting(self, queryset, params):
        """
        Применяет сортировку к queryset.
        
        Args:
            queryset: Исходный queryset
            params: Параметры сортировки
            
        Returns:
            QuerySet: Отсортированный queryset
        """
        sort_field = params.get("sort", "date")
        sort_type = params.get("sortType", "desc")
        
        # Определяем поле для сортировки
        sort_mapping = {
            "price": "price",
            "rating": "rating",
            "reviews": "number_comments",
            "date": "created_at",
        }
        
        order_by_field = sort_mapping.get(sort_field, "created_at")
        
        # Для сортировки по цене со скидкой используем аннотацию
        if sort_field == "final_price":
            queryset = queryset.annotate(
                final_price_calc=Case(
                    When(discount__gt=0, then=(F("price") * (1 - F("discount") / 100))),
                    default=F("price"),
                    output_field=DecimalField(max_digits=10, decimal_places=2),
                )
            )
            order_by_field = "final_price_calc"
        
        # Определяем направление сортировки
        prefix = "-" if sort_type == "dec" else ""
        
        try:
            return queryset.order_by(f"{prefix}{order_by_field}")
        except:
            # В случае ошибки возвращаем сортировку по умолчанию
            return queryset.order_by("-created_at")
    
    def paginate_and_respond(self, queryset, request):
        """
        Выполняет пагинацию и формирует ответ.
        
        Args:
            queryset: QuerySet для пагинации
            request: HTTP запрос
            
        Returns:
            Response: JSON ответ с пагинированными данными
        """
        paginator = StandardResultsSetPagination()
        
        try:
            page = paginator.paginate_queryset(queryset, request)
            serializer = ProductSerializer(page, many=True, context={"request": request})
            
            return Response(OrderedDict([
                ("items", serializer.data),
                ("currentPage", paginator.page.number),
                ("lastPage", paginator.page.paginator.num_pages),
                ("total", paginator.page.paginator.count),
            ]))
            
        except Exception as e:
            # Если ошибка пагинации, возвращаем пустой результат
            return Response(OrderedDict([
                ("items", []),
                ("currentPage", 1),
                ("lastPage", 1),
                ("total", 0),
            ]))



class ProductApiView(APIView):

    def get(self, request, id):
        product = get_object_or_404(
            Product.objects.prefetch_related(
                "images", "specifications", "comments__created_by", "tags"
            ),
            pk=id,
        )

        serializer = ProductSerializer(product, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def tags_api(request):
    tags = Tag.objects.all().values("id", "name")
    return Response([{**tag, "selected": False} for tag in tags])


@api_view(["GET"])
def categories_api(request):
    categories = Category.objects.prefetch_related(
        Prefetch(
            "subcategories", queryset=Category.objects.filter(parent__isnull=False)
        )
    ).filter(parent__isnull=True)

    def build_category_tree(category):
        result = {
            "id": category.id,
            "title": category.name,
            "image": {
                "src": (
                    request.build_absolute_uri(category.image.url)
                    if category.image
                    else ""
                ),
                "alt": category.name,
            },
            "subcategories": [],
        }

        for subcategory in category.subcategories.all():
            result["subcategories"].append(
                {
                    "id": subcategory.id,
                    "title": subcategory.name,
                    "image": {
                        "src": (
                            request.build_absolute_uri(subcategory.image.url)
                            if subcategory.image
                            else ""
                        ),
                        "alt": subcategory.name,
                    },
                }
            )

        return result

    return Response([build_category_tree(cat) for cat in categories])  # или пусто


@api_view(["GET"])
def basket_api(request):
    return Response({"items": [], "total": 0})
