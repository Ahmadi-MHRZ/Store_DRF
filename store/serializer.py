from rest_framework import serializers
from decimal import Decimal
from .models import Product, Category, Comment, Cart, CartItem, Customer, Order, OrderItem, Discount
from django.utils.text import slugify
from django.db import transaction


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
        fields = ['id', 'name', 'unit_price']


class OrderItemsSerializer(serializers.ModelSerializer):
    product = OrderItemProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'quantity', 'unit_price']


class OrderCustomerSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=255, source='user.first_name')
    last_name = serializers.CharField(max_length=255, source='user.last_name')
    email = serializers.EmailField(source='user.email')

    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name', 'email', 'birth_date']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemsSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'status', 'datetime_created', 'items']


class OrderAdminSerializer(serializers.ModelSerializer):
    items = OrderItemsSerializer(many=True)
    customer = OrderCustomerSerializer()

    class Meta:
        model = Order
        fields = ['id', 'customer', 'status', 'datetime_created', 'items']


class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']


class OrderCreateSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validated_cart_data(self, cart_id):
        try:
            if Cart.objects.prefetch_related('items').get(id=cart_id).items.count() == 0:
                raise serializers.ValidationError('Your cart is empty. please add at least one item yo your cart')
        except Cart.DoesNotExist:
            raise serializers.ValidationError('There is no such a cart')

    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']
            user_id = self.context['user_id']
            customer = Customer.objects.get(user_id=user_id)

            order = Order()
            order.customer = customer
            order.save()

            cart_items = CartItem.objects.select_related('product').filter(cart_id=cart_id)

            order_items = [
                OrderItem(
                    order=order,
                    product=cart_item.product,
                    unit_price=cart_item.product.unit_price,
                    quantity=cart_item.quantity,
                ) for cart_item in cart_items
            ]

            OrderItem.objects.bulk_create(order_items)
            Cart.objects.get(id=cart_id).delete()
            return order

            # order_items = list()
            # for cart_item in cart_items:
            #     order_item = OrderItem()
            #     order_item.order = order
            #     order_item.product_id = cart_item.product_id
            #     order_item.unit_price = cart_item.product.unit_price
            #     order_item.quantity = cart_item.quantity
            #
            #     order_items.append(order_item)




