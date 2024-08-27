from django.contrib import admin
from django.urls import path, include

admin.site.site_header = 'Store'
admin.site.index_title = 'Special Access'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('store/', include('store.urls', namespace='store')),
    path("__debug__/", include("debug_toolbar.urls")),

]
