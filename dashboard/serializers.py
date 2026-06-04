from rest_framework import serializers
from .models import MaterialPurchase

class MaterialPurchaseSerializer(serializers.ModelSerializer):
    unit_cost = serializers.SerializerMethodField()
    supplier = serializers.SerializerMethodField()

    class Meta:
        model = MaterialPurchase
        # Siguraduhing tumutugma ito sa mga field names ng MaterialPurchase mo
        fields = ['id', 'material_name', 'quantity', 'unit', 'unit_cost', 'supplier', 'status']

    def get_unit_cost(self, obj):
        request = self.context.get('request')
        # Tinitiyak kung Admin ba ang may-ari ng JWT token
        if request and request.user and request.user.is_superuser:
            return str(obj.unit_cost)
        return "XXXX" # Masked kapag regular staff/operator

    def get_supplier(self, obj):
        request = self.context.get('request')
        if request and request.user and request.user.is_superuser:
            return obj.supplier
        return "XXXX" # Masked kapag hiram na access lang