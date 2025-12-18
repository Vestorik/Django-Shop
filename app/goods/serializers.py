"""
serializers for goods app
"""

from rest_framework import serializers
from rest_framework.request import Request
from .models import Product, ProductImage, ProductSpecification, Comment, Tag


class ImageSerializer(serializers.ModelSerializer):
    """Serializer for ProductImage

    serialize fields src (path to file) and alt (text) model ProductImage

    model: ProductImage
    filds: src, alt

    get_url:
        if the object belongs src, return the src url, else None

        request: Request
        get request from context

        src: ImageField
        url is an attribyte of the ImageField containing the url of image
    """

    src = serializers.SerializerMethodField()

    class Meta:
        """Meta class for ProductImageSerializer"""

        model = ProductImage
        fields = ["src", "alt"]

    def get_url(self, object: ProductImage) -> str | None:
        """get url of image
        if the object belongs src, return the src url, else None

        object: ProductImage
        return: str | None
        """
        request: Request = self.context.get("request")  # type: ignore
        if object.src:
            return request.build_absolute_uri(object.src.url)
        return None


class ProductSpecificationSerializer(serializers.ModelSerializer):
    """
    Serializer for ProductSpecification

    serialize fields name (Materials:) and value (cotton 95 %) of model ProductSpecification

    model: ProductSpecification
    filds: name, value
    """

    class Meta:
        """Meta class for ProductSpecificationSerializer"""

        model = ProductSpecification
        fields = ["name", "value"]


class CommentSerializer(serializers.ModelSerializer):
    """
    Serialzer for Comment

    serialise fields author, rate, text, date of model Comment

    model: Comment
    fields: author, rate, text, date

    the field author uses the method get_author to get author's name
    other fields use source for get value from model

    def get_author:
        if the comment creater exists, return the username, else a message that the user does not exist
    """

    author = serializers.SerializerMethodField()
    rate = serializers.DecimalField(
        source="product_estimation", max_digits=3, decimal_places=2
    )
    text = serializers.CharField(source="description")
    date = serializers.DateTimeField(source="created_at")

    class Meta:
        """Meta class for CommentSerializer"""

        model = Comment
        fields = ["author", "rate", "text", "date"]

    def get_author(self, object: Comment):
        """get author's name
        if the comment creater exists, return the username, else a message that the user does not exist

        object: Comment
        return: str
        """
        if object.created_by is None:
            return "Пользователь больше не существует"
        return object.created_by.get_username()


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag

    serialize fields name of model Tag

    model: Tag
    filds: name
    """

    class Meta:
        """Meta class for TagSerializer"""

        model = Tag
        fields = ["name"]


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product

    serialize fields name, images, specifications, reviews, tags, description, price, rating, number_comments of model Product

    model: Product
    fields: id, title, images, specifications, reviews, tags, description, price, rating, number_comments
    """

    title = serializers.CharField(source="name")
    images = ImageSerializer(many=True, read_only=True)
    specifications = ProductSpecificationSerializer(many=True, read_only=True)
    reviews = CommentSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    description = serializers.CharField(source="full_description", allow_blank=True)
    price = serializers.SerializerMethodField()
    rating = serializers.DecimalField(source="rating", max_digits=3, decimal_places=2)
    number_comments = serializers.IntegerField(read_only=True)

    class Meta:
        """Meta class for ProductSerializer"""

        model = Product
        fields = [
            "id",
            "title",
            "price",
            "description",
            "full_description",
            "images",
            "specifications",
            "reviews",
            "tags",
            "rating",
            "number_comments",
        ]

    def get_price(self, obj):
        """get price of product with discount"""
        return obj.final_price
