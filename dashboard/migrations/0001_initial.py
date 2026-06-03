from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductionLine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('code', models.CharField(max_length=20, unique=True)),
                ('sector', models.CharField(choices=[('press', 'Press'), ('mold', 'Mold'), ('weld', 'Weld'), ('pack', 'Pack')], max_length=20)),
                ('status', models.CharField(choices=[('run', 'Running'), ('warn', 'Warning'), ('stop', 'Halted')], default='run', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['code']},
        ),
        migrations.CreateModel(
            name='MaterialPurchase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('material_name', models.CharField(max_length=200)),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=10)),
                ('unit', models.CharField(max_length=20)),
                ('unit_cost', models.DecimalField(decimal_places=2, max_digits=12)),
                ('total_cost', models.DecimalField(decimal_places=2, max_digits=14)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('in_transit', 'In Transit'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('ordered_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('delivered_at', models.DateTimeField(blank=True, null=True)),
                ('supplier', models.CharField(blank=True, max_length=200)),
                ('purchase_order', models.CharField(blank=True, max_length=100)),
            ],
            options={'ordering': ['-ordered_at']},
        ),
        migrations.CreateModel(
            name='YieldRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recorded_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('shift', models.CharField(choices=[('morning', 'Morning'), ('afternoon', 'Afternoon'), ('night', 'Night')], max_length=20)),
                ('units_produced', models.PositiveIntegerField()),
                ('units_defective', models.PositiveIntegerField(default=0)),
                ('oee_efficiency', models.DecimalField(decimal_places=2, help_text='Percentage 0-100', max_digits=5)),
                ('sensor_id', models.CharField(blank=True, help_text='IoT sensor identifier', max_length=50)),
                ('notes', models.TextField(blank=True)),
                ('line', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='yield_records', to='dashboard.productionline')),
                ('submitted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user')),
            ],
            options={'ordering': ['-recorded_at']},
        ),
        migrations.CreateModel(
            name='SensorEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sensor_id', models.CharField(max_length=50)),
                ('event_type', models.CharField(choices=[('ok', 'OK'), ('warn', 'Warning'), ('err', 'Error')], max_length=10)),
                ('message', models.TextField()),
                ('payload', models.JSONField(blank=True, default=dict)),
                ('received_at', models.DateTimeField(auto_now_add=True)),
                ('line', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sensor_events', to='dashboard.productionline')),
            ],
            options={'ordering': ['-received_at']},
        ),
    ]
