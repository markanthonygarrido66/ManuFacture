from rest_framework import serializers
from .models import MaterialPurchase

class MaterialPurchaseSerializer(serializers.ModelSerializer):
    unit_cost = serializers.SerializerMethodField()
    supplier = serializers.SerializerMethodField()

    class Meta:
        model = MaterialPurchase
        fields = ['id', 'material_name', 'quantity', 'unit', 'unit_cost', 'supplier', 'status']

    def get_unit_cost(self, obj):
        request = self.context.get('request')
        # Kukunin natin kung may idinagdag na "?role=" sa URL bar ng browser
        role_param = request.query_params.get('role', None) if request else None

        # Kung ang param ay 'operator', sasadyaing i-mask para sa demo
        if role_param == 'operator':
            return "XXXX"
            
        # Default behavior: Kung Admin ka (at walang ?role=operator), makikita ang totoong presyo
        if request and request.user and request.user.is_superuser:
            return str(obj.unit_cost)
        return "XXXX"

    def get_supplier(self, obj):
        request = self.context.get('request')
        role_param = request.query_params.get('role', None) if request else None

        if role_param == 'operator':
            return "XXXX"

        if request and request.user and request.user.is_superuser:
            return obj.supplier
        return "XXXX"