from django.urls import path
from rest_framework_nested import routers
from store import views
from django.urls import include

app_name = 'store'

router = routers.DefaultRouter()
router.register('products', views.ProductViewSet, basename='product')
router.register('categories', views.CategoryViewSet, basename='category')

products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
products_router.register('comments', views.CommentViewSet, basename='product-comments')

urlpatterns = [
    path('', include(router.urls)),    #urlpatterns=router.urls
    path('', include(products_router.urls)),
]


# urlpatterns = [
#     path('detail/<int:pk>/', views.ProductDetail.as_view()),
#     path('products/', views.ProductList.as_view()),
#     path('categories/<int:pk>/', views.CategoryDetail.as_view(), name='category_detail'),
#     path('category_list/', views.CategoryList.as_view())
#
# ]
