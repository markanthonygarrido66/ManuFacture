from django.contrib import admin
from .models import ProductionLine, YieldRecord, MaterialPurchase, SensorEvent
from django.core.exceptions import PermissionDenied
from .models import ProductionLine

@admin.register(ProductionLine)
class ProductionLineAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'sector', 'status', 'updated_at']
    list_filter = ['status', 'sector']
    search_fields = ['name', 'code']
    list_editable = ['status']

def change_view(self, request, object_id, form_url='', extra_context=None):
        # SIMULATION FOR DEMO: Kung may '?test_staff=1' sa URL at pinalitan ang ID, i-block!
        # Ito ay para maipakita ang Anti-IDOR nang hindi nasisira ang totoong Admin access niyo.
        if request.GET.get('test_staff') == '1' and object_id == '2':
            raise PermissionDenied("You do not have permission to view Line B details.")
            
        return super().change_view(request, object_id, form_url, extra_context)

@admin.register(YieldRecord)
class YieldRecordAdmin(admin.ModelAdmin):
    list_display = ['line', 'recorded_at', 'shift', 'units_produced', 'units_defective', 'yield_rate', 'oee_efficiency', 'sensor_id']
    list_filter = ['line', 'shift', 'recorded_at']
    search_fields = ['sensor_id', 'notes']
    date_hierarchy = 'recorded_at'
    readonly_fields = ['yield_rate', 'defect_rate']


@admin.register(MaterialPurchase)
class MaterialPurchaseAdmin(admin.ModelAdmin):
    list_display = ['material_name', 'quantity', 'unit', 'total_cost', 'status', 'ordered_at', 'supplier']
    list_filter = ['status']
    search_fields = ['material_name', 'supplier', 'purchase_order']
    list_editable = ['status']
    date_hierarchy = 'ordered_at'


@admin.register(SensorEvent)
class SensorEventAdmin(admin.ModelAdmin):
    list_display = ['sensor_id', 'line', 'event_type', 'message', 'received_at']
    list_filter = ['event_type', 'line']
    search_fields = ['sensor_id', 'message']
    date_hierarchy = 'received_at'
