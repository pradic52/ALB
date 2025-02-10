from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from .views import ProductListView, ProductCreateView, ProductDeleteView, ProductUpdateView
urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('create/', ProductCreateView.as_view(), name='product_create'),
    path('<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),
    path('<int:pk>/update/', ProductUpdateView.as_view(), name='product_update'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)