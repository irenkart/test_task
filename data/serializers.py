from rest_framework import serializers


class SaveKeySerializer(serializers.Serializer):
    key_customer = serializers.CharField(max_length=100)
    key_source = serializers.CharField(max_length=100)
    key_value = serializers.CharField(max_length=100)


class ValidateSourceInputSerializer(serializers.Serializer):
    key_customer = serializers.CharField(max_length=100)
    key_source = serializers.CharField(max_length=100)


class ValidateSourceOutputSerializer(serializers.Serializer):
    source_validated = serializers.CharField(max_length=100)


class IndexCustomerInputSerializer(serializers.Serializer):
    customer = serializers.CharField(max_length=100)


class IndexCustomerOutputSerializer(serializers.Serializer):
    source = serializers.CharField(max_length=100)
    count = serializers.IntegerField()
