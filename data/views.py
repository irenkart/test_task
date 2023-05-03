from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.response import Response

from data.models import CustomerKeys
from data.serializers import SaveKeySerializer, ValidateSourceInputSerializer, ValidateSourceOutputSerializer, \
    IndexCustomerInputSerializer, IndexCustomerOutputSerializer
from data.services.customer_service import CustomerService
from data.services.google_docs_client_mock import GoogleDocsClientMock
from data.services.sfkb_mock import SFKBMock
from data.tasks import save_to_cloud


class SaveKeyAPIView(GenericAPIView):
    """
    Save key to database
    """
    serializer_class = SaveKeySerializer
    queryset = CustomerKeys.objects.all()

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        key_customer = serializer.validated_data.get('key_customer')
        key_source = serializer.validated_data.get('key_source')
        customer, created = CustomerKeys.objects.get_or_create(customer_name=key_customer)
        if key_source == 'sfkb_user_name':
            customer.sfkb_user_name = serializer.validated_data.get('key_value')
        elif key_source == 'google_docs':
            customer.google_docs = serializer.validated_data.get('key_value')
        elif key_source == 'sfkb_password':
            customer.sfkb_password = serializer.validated_data.get('key_value')
        customer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ValidateSourceAPIView(GenericAPIView):
    """
    Validate source
    """
    serializer_class = ValidateSourceInputSerializer
    output_serializer_class = ValidateSourceOutputSerializer
    queryset = CustomerKeys.objects.all()

    @swagger_auto_schema(responses={200: ValidateSourceOutputSerializer()})
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        key_source = serializer.validated_data.get('key_source')
        key_customer = serializer.validated_data.get('key_customer')
        customer = get_object_or_404(CustomerKeys, customer_name__iexact=key_customer)
        status_string = 'VALIDATED'
        if customer.__getattribute__(key_source) is None:
            status_string = 'NO_KEY'
        else:
            if key_source == 'google_docs':
                try:
                    GoogleDocsClientMock(customer=customer.customer_name,
                                         secret=customer.google_docs).get_docs_call()
                except ValueError:
                    status_string = 'NO_ACCESS'
            elif key_source in ['sfkb_user_name', 'sfkb_password']:
                try:
                    SFKBMock().authenticate(customer=customer.customer_name, username=customer.sfkb_user_name,
                                            password=customer.sfkb_password)
                except ValueError:
                    status_string = 'NO_ACCESS'
        serializer = self.output_serializer_class({'source_validated': status_string})
        return Response(serializer.data)


class IndexCustomerAPIView(GenericAPIView):
    """
    Index customer
    """
    serializer_class = IndexCustomerInputSerializer
    output_serializer_class = IndexCustomerOutputSerializer
    queryset = CustomerKeys.objects.all()

    @swagger_auto_schema(responses={200: IndexCustomerOutputSerializer()})
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        key_customer = serializer.validated_data.get('customer')
        customer = get_object_or_404(CustomerKeys, customer_name__iexact=key_customer)
        output_data = CustomerService(customer_id=customer.id).get_and_index_customer_files()
        output_serializer = self.output_serializer_class(output_data, many=True)
        return Response(output_serializer.data)
