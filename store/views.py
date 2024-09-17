from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from django.shortcuts import get_object_or_404
from .models import Product, Category, Comment, Cart, CartItem, Customer, Order, OrderItem
from django.db.models import Count, Prefetch
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializer import ProductSerializer, CartSerializer, CategorySerializer, CommentSerializer, CartItemSerializer, \
    AddCartItemSerializer, UpdateCartItemSerializer, CustomerSerializer, OrderSerializer, OrderItemsSerializer, \
    OrderAdminSerializer, OrderCreateSerializer
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from .filter import ProductFilter
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination
from .paginations import DefaultPagination
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, RetrieveModelMixin
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .permissions import IsStaffOrReadOnly, SendPrivetEmail, CustomDjangoPermission


class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.select_related('category').annotate(comments_count=Count('comments')).order_by('id')
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    search_fields = ['name', 'category__title']
    ordering_fields = ['name', 'unit_price', 'inventory']
    # filterset_fields = ['category_id', 'inventory']
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    permission_classes = [IsStaffOrReadOnly]

    def get_serializer_context(self):
        return {'request': self.request}

    # fiter by input in URLs
    # def get_queryset(self):
    #     queryset = Product.objects.select_related('category').annotate(comments_count=Count('comments')).all()
    #     category_id_params = self.request.query_params.get('category_id')
    #     if category_id_params is not None:
    #         queryset = queryset.filter(category_id=category_id_params)
    #     return queryset

    def destroy(self, request, pk):
        product = get_object_or_404(Product.objects.select_related('category'), pk=pk)
        if product.order_items.count() > 0:
            return Response('error:'"you need to delete remove orderitems first",
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryViewSet(ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.annotate(products_count=Count('products'))
    permission_classes = [IsStaffOrReadOnly]

    def destroy(self, request, pk):
        category = get_object_or_404(Category.objects.annotate(products_count=Count('products')), pk=pk)
        if category.products.count() > 0:
            return Response("error: this category related to some products u need to delete them first ",
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        product_pk = self.kwargs['product_pk']
        return Comment.objects.filter(product_id=product_pk).all()

    def get_serializer_context(self):
        return {'product_pk': self.kwargs['product_pk']}


class CartViewSet(CreateModelMixin,
                  RetrieveModelMixin,
                  DestroyModelMixin,
                  GenericViewSet):
    serializer_class = CartSerializer
    queryset = Cart.objects.prefetch_related('items__product')
    lookup_value_regex = '[0-9a-fA-F]{8}\-?[0-9a-fA-F]{4}\-?[0-9a-fA-F]{4}\-?[0-9a-fA-F]{4}\-?[0-9a-fA-F]{12}'


class CartItemsViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        if self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_queryset(self):
        cart_pk = self.kwargs['cart_pk']
        return CartItem.objects.select_related('product').filter(cart_id=cart_pk).all()

    def get_serializer_context(self):
        return {'cart_pk': self.kwargs['cart_pk']}


class CustomerViewSet(ModelViewSet):
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['PUT', 'GET'], permission_classes=[IsAuthenticated])
    def me(self, request):
        user_id = request.user.id
        customer = Customer.objects.get(user_id=user_id)
        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    @action(detail=True, permission_classes=[SendPrivetEmail])
    def privet_email(self, request, pk):
        return Response(f'sending email to customer:{pk}')


class OrderViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderCreateSerializer

        if self.request.user.is_staff:
            return OrderAdminSerializer
        return OrderSerializer

    def get_queryset(self):
        queryset = Order.objects.prefetch_related(
            Prefetch(
                'items', queryset=OrderItem.objects.select_related('product'))).select_related('customer__user').all()
        user = self.request.user
        if user.is_staff:
            return queryset
        return queryset.filter(customer__user_id=user.id)

    def get_serializer_context(self):
        return {'user_id': self.request.user.id}


class OrderItemViewSet(ModelViewSet):
    serializer_class = OrderItemsSerializer
    def get_queryset(self):
        order_pk = self.kwargs['order_pk']
        return OrderItem.objects.select_related('product').filter(order_id=order_pk)

