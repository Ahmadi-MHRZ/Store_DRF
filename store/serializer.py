from rest_framework import serializers
from decimal import Decimal
from .models import Product, Category, Comment
from django.utils.text import slugify


class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'title', 'description', 'products_count']

    def validate(self, data):
        if len(data['title']) < 3:
            raise serializers.ValidationError('title has to be longer than three word')
        return data


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'unit_price', 'inventory', 'category', 'price_after_tax', 'description', 'comments_count']
    # id = serializers.IntegerField()
    # name = serializers.CharField(max_length=255)
    #  unit_price = serializers.DecimalField(max_digits=5, decimal_places=2)
    price_after_tax = serializers.SerializerMethodField()
    comments_count = serializers.IntegerField(read_only=True)
    # inventory = serializers.IntegerField(validators=[MinValueValidator(0)])
    category = serializers.SerializerMethodField()

    def get_price_after_tax(self, product):
        return round(product.unit_price * Decimal(1.09), 2)

    def create(self, validated_data):
        product = Product(**validated_data)
        product.slug = slugify(product.name)
        product.save()
        return product


    def get_category(self, product):
        return product.category.title


    # def update(self, instance, validated_data):
    #     instance.inventory = validated_data.get('inventory')
    #     instance.save()
    #     return instance
    # def validate(self, data):
    #     if len(data['name']) <6:
    #         raise serializers.ValidationError('the lenth of name can not be lesss than 6')
    #     return data


class CommentSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'name', 'product_name', 'body']

    def get_product_name(self, comment):
        return comment.product.name

    def create(self, validated_data):
        product_id = self.context['product_pk']
        return Comment.objects.create(product_id=product_id, **validated_data)
