from .models import Package,Index,Supplier
from rest_framework import serializers

class SupplierSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Supplier
        fields = ['name',]

class IndexSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Index
        fields = ['sap', 'name', 'country', 'werk', 'default_length',]

class PackageSerializer(serializers.HyperlinkedModelSerializer):
    #index = IndexSerializer
    #supplier = SupplierSerializer
    class Meta:
        model = Package
        fields = ['index', 'delivery_date', 'delivery_time', 'supplier', 'werk', 'localisation','length',]




