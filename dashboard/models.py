from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ProductionLine(models.Model):
    SECTOR_CHOICES = [
        ('press', 'Press'),
        ('mold', 'Mold'),
        ('weld', 'Weld'),
        ('pack', 'Pack'),
    ]
    STATUS_CHOICES = [
        ('run', 'Running'),
        ('warn', 'Warning'),
        ('stop', 'Halted'),
    ]

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    sector = models.CharField(max_length=20, choices=SECTOR_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='run')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        ordering = ['code']


class YieldRecord(models.Model):
    SHIFT_CHOICES = [
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('night', 'Night'),
    ]

    line = models.ForeignKey(ProductionLine, on_delete=models.CASCADE, related_name='yield_records')
    recorded_at = models.DateTimeField(default=timezone.now)
    shift = models.CharField(max_length=20, choices=SHIFT_CHOICES)
    units_produced = models.PositiveIntegerField()
    units_defective = models.PositiveIntegerField(default=0)
    oee_efficiency = models.DecimalField(max_digits=5, decimal_places=2, help_text='Percentage 0-100')
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    sensor_id = models.CharField(max_length=50, blank=True, help_text='IoT sensor identifier')
    notes = models.TextField(blank=True)

    @property
    def yield_rate(self):
        if self.units_produced == 0:
            return 0
        return round((self.units_produced - self.units_defective) / self.units_produced * 100, 2)

    @property
    def defect_rate(self):
        if self.units_produced == 0:
            return 0
        return round(self.units_defective / self.units_produced * 100, 2)

    def __str__(self):
        return f"{self.line.code} | {self.recorded_at.date()} | {self.shift} | {self.units_produced} units"

    class Meta:
        ordering = ['-recorded_at']


class MaterialPurchase(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    material_name = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20, help_text='e.g. kg, tons, liters')
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2)
    total_cost = models.DecimalField(max_digits=14, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    ordered_at = models.DateTimeField(default=timezone.now)
    delivered_at = models.DateTimeField(null=True, blank=True)
    supplier = models.CharField(max_length=200, blank=True)
    purchase_order = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.material_name} — {self.quantity}{self.unit} ({self.status})"

    class Meta:
        ordering = ['-ordered_at']


class SensorEvent(models.Model):
    EVENT_TYPES = [
        ('ok', 'OK'),
        ('warn', 'Warning'),
        ('err', 'Error'),
    ]

    sensor_id = models.CharField(max_length=50)
    line = models.ForeignKey(ProductionLine, on_delete=models.CASCADE, related_name='sensor_events', null=True, blank=True)
    event_type = models.CharField(max_length=10, choices=EVENT_TYPES)
    message = models.TextField()
    payload = models.JSONField(default=dict, blank=True)
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.event_type.upper()}] {self.sensor_id} — {self.received_at}"

    class Meta:
        ordering = ['-received_at']
