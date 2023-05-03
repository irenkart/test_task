from django.urls import path
from data.views import SaveKeyAPIView, IndexCustomerAPIView, ValidateSourceAPIView

urlpatterns = [
    path('save_key/', SaveKeyAPIView.as_view(), name='save_key'),
    path('is_source_validated/', ValidateSourceAPIView.as_view(), name='validate_source'),
    path('index_customer/', IndexCustomerAPIView.as_view(), name='index_customer'),
]
