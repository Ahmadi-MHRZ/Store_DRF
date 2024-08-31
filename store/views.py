from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from django.shortcuts import get_object_or_404
from .models import Product, Category, Comment
from django.db.models import Count
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializer import ProductSerializer, CategorySerializer, CommentSerializer
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from .filter import ProductFilter
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination
from .paginations import DefaultPagination


class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.select_related('category').annotate(comments_count=Count('comments'))
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    search_fields = ['name', 'category__title']
    ordering_fields = ['name', 'unit_price', 'inventory']
    # filterset_fields = ['category_id', 'inventory']
    filterset_class = ProductFilter
    pagination_class = DefaultPagination

    def get_serializer_context(self):
        return {'request': self.request}




    #fiter by input in URLs
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



