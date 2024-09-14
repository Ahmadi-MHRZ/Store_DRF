from rest_framework import serializers
from decimal import Decimal
from .models import Product, Category, Comment, Cart, CartItem, Customer, Order, OrderItem, Discount
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


class CaretProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ['id', 'name', 'unit_price']


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']


class AddCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity']

    def create(self, validated_data):
        product = validated_data.get('product')
        quantity = validated_data.get('quantity')
        cart_pk = self.context['cart_pk']
        try:
            cart_item = CartItem.objects.get(cart_id=cart_pk, product_id=product.id)
            cart_item.quantity += quantity
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(cart_id=cart_pk, **validated_data)
        self.instance = cart_item
        return cart_item


class CartItemSerializer(serializers.ModelSerializer):
    product = CaretProductSerializer()
    item_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'item_total']

    def get_item_total(self, cart_item):
        return cart_item.quantity * cart_item.product.unit_price



class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']
        read_only_fields = ['id']

    def get_total_price(self, cart):
        return sum([item.quantity * item.product.unit_price for item in cart.items.all()])


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'user', 'birth_date']
        read_only_fields = ['user']


class OrderItemProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'unit_price', 'name']


class OrderItemsSerializer(serializers.ModelSerializer):
    product = OrderItemProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['order', 'product', 'quantity', 'unit_price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemsSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'customer_id', 'status', 'datetime_created', 'items']

