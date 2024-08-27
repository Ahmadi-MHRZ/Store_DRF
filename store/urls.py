from django.urls import path

from store import views

app_name = 'store'

urlpatterns = [
    path('detail/<int:pk>/', views.product_detail),
    path('products/', views.products_list),
    path('categories/<int:pk>/', views.category_detail, name='category_detail'),
    path('category_list/', views.category_list)

]
