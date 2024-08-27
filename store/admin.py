from django.contrib import admin, messages
from django.db.models import Count
from django.http.request import HttpRequest
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

from store.models import Category, Comment, Customer, Order, OrderItem, Product


class InventoryFilter(admin.SimpleListFilter):
    LESS_THAN_3 = '<3'
    BETWEEN_3_AND_10 = '3<=10'
    MORE_THAN_10 = '>10'
    title = 'Critical Inventory Status'
    parameter_name = 'inventory'

    def lookups(self, request, model_admin):
        return [
            (InventoryFilter.LESS_THAN_3, 'High'),
            (InventoryFilter.BETWEEN_3_AND_10, 'Medium'),
            (InventoryFilter.MORE_THAN_10, 'OK')
        ]

    def queryset(self, request, queryset):
        if self.value() == InventoryFilter.LESS_THAN_3:
            return queryset.filter(inventory__lt=3)
        if self.value() == InventoryFilter.BETWEEN_3_AND_10:
            return queryset.filter(inventory__range=(3, 10))
        if self.value() == InventoryFilter.MORE_THAN_10:
            return queryset.filter(inventory__gt=10)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'inventory',
        'unit_price',
        'inventory_status',
        'product_category',
        'num_of_comments',
        ]
    list_per_page = 10
    list_editable = ['unit_price']
    list_select_related = ['category']
    list_filter = ['datetime_created', InventoryFilter]
    actions = ['clear_inventory']
    prepopulated_fields = {
        'slug': ['name', ]
    }
    search_fields = ['name']

    def inventory_status(self, product: Product):
        if product.inventory < 10:
            return 'Low'
        elif product.inventory > 50:
            return 'Hight'
        return 'Medium'

    @admin.display(ordering='category__title')
    def product_category(self, product: Product):
        return product.category.title

    def get_queryset(self, request):
        return super().get_queryset(request) \
            .prefetch_related('comments') \
            .annotate(comments_count=Count('comments'))

    @admin.display(ordering='comments_count', description='# comments')
    def num_of_comments(self, product: Product):
        url = (
            reverse('admin:store_comment_changelist')
            +
            '?'
            +
            urlencode({
                'product__id': product.id
            })
        )
        return format_html('<a href="{}">{}</a>', url, product.comments_count)

    @admin.action(description='Clear Inventory')
    def clear_inventory(self, request, queryset):
        update_count = queryset.update(inventory=0)
        self.message_user(
            request,
            f'{update_count} of products inventories cleard to zero.',
            messages.ERROR,
        )


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ['product', 'quantity', 'unit_price']
    extra = 0
    min_num = 1
    max_num = 10


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'customer',
        'status',
        'datetime_created',
        'num_of_items'
        ]
    list_per_page = 10
    list_editable = ['status']
    ordering = ['-datetime_created']
    search_fields = ['id']
    inlines = [OrderItemInline]

    def get_queryset(self, request: HttpRequest):
        return super()\
                .get_queryset(request)\
                .prefetch_related('items') \
                .annotate(items_count=Count('items'))

    @admin.display(ordering='items_count', description='# items')
    def num_of_items(self, order: Order):
        return order.items_count


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'status', 'datetime_created']
    list_per_page = 10
    list_editable = ['status']
    ordering = ['-datetime_created']
    autocomplete_fields = ['product']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'phone_number']
    list_per_page = 10
    ordering = ['last_name', 'first_name']
    search_fields = ['first_name__istartswith', 'last_name__istartswith']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order',
                    'product',
                    'quantity',
                    'unit_price',
                    ]
    list_per_page = 10
    autocomplete_fields = ['product']


admin.site.register(Category)
