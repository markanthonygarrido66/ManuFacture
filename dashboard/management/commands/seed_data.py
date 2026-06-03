from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from dashboard.models import ProductionLine, YieldRecord, MaterialPurchase, SensorEvent
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Seed the database with demo manufacturing data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding demo data...')

        # Create superuser
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@plant-a.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('  Created superuser: admin / admin123'))

        # Sensor user for JWT
        if not User.objects.filter(username='iot_sensor').exists():
            User.objects.create_user('iot_sensor', 'iot@plant-a.com', 'sensor_secret_42')
            self.stdout.write(self.style.SUCCESS('  Created IoT user: iot_sensor / sensor_secret_42'))

        # Production lines
        lines_data = [
            {'name': 'Line A – Alpha', 'code': 'LINE-A', 'sector': 'press', 'status': 'run'},
            {'name': 'Line B – Beta',  'code': 'LINE-B', 'sector': 'mold',  'status': 'warn'},
            {'name': 'Line C – Gamma', 'code': 'LINE-C', 'sector': 'weld',  'status': 'run'},
            {'name': 'Line D – Delta', 'code': 'LINE-D', 'sector': 'pack',  'status': 'stop'},
        ]
        lines = {}
        for ld in lines_data:
            line, _ = ProductionLine.objects.get_or_create(code=ld['code'], defaults=ld)
            lines[ld['code']] = line
        self.stdout.write(self.style.SUCCESS(f'  Created {len(lines)} production lines'))

        # Yield records (past 7 days, 3 shifts per line)
        admin = User.objects.get(username='admin')
        shifts = ['morning', 'afternoon', 'night']
        line_configs = {
            'LINE-A': {'base': 680, 'defect_rate': 0.018, 'oee': 91},
            'LINE-B': {'base': 545, 'defect_rate': 0.032, 'oee': 78},
            'LINE-C': {'base': 485, 'defect_rate': 0.059, 'oee': 85},
            'LINE-D': {'base': 260, 'defect_rate': 0.107, 'oee': 42},
        }
        records_created = 0
        for day_offset in range(7):
            day = timezone.now() - timedelta(days=day_offset)
            for shift_i, shift in enumerate(shifts):
                hour_offset = shift_i * 8
                for code, cfg in line_configs.items():
                    line = lines[code]
                    units = int(cfg['base'] * random.uniform(0.88, 1.12))
                    defects = int(units * cfg['defect_rate'] * random.uniform(0.7, 1.4))
                    oee = cfg['oee'] + random.uniform(-3, 3)
                    record_time = day.replace(hour=6 + hour_offset, minute=0, second=0, microsecond=0)
                    if not YieldRecord.objects.filter(line=line, recorded_at=record_time, shift=shift).exists():
                        YieldRecord.objects.create(
                            line=line, recorded_at=record_time, shift=shift,
                            units_produced=units, units_defective=defects,
                            oee_efficiency=round(oee, 2),
                            submitted_by=admin,
                            sensor_id=f"S-{code.split('-')[1]}-{shift_i+1:02d}",
                        )
                        records_created += 1
        self.stdout.write(self.style.SUCCESS(f'  Created {records_created} yield records'))

        # Material purchases
        materials = [
            {'material_name': 'Alloy steel sheet', 'quantity': 4200, 'unit': 'kg', 'unit_cost': 74.3, 'total_cost': 312060, 'status': 'delivered', 'supplier': 'Steelco PH'},
            {'material_name': 'Polymer resin',     'quantity': 1800, 'unit': 'kg', 'unit_cost': 48.9, 'total_cost': 88020,  'status': 'in_transit','supplier': 'ChemLine Inc'},
            {'material_name': 'Copper wiring',     'quantity': 620,  'unit': 'kg', 'unit_cost': 87.1, 'total_cost': 54002,  'status': 'delivered', 'supplier': 'MetalPro Manila'},
            {'material_name': 'Hydraulic fluid',   'quantity': 200,  'unit': 'L',  'unit_cost': 60.0, 'total_cost': 12000,  'status': 'pending',   'supplier': 'LubeTech'},
            {'material_name': 'Welding electrodes','quantity': 500,  'unit': 'kg', 'unit_cost': 112.0,'total_cost': 56000,  'status': 'delivered', 'supplier': 'WeldMax PH'},
        ]
        for m in materials:
            MaterialPurchase.objects.get_or_create(
                material_name=m['material_name'],
                supplier=m.get('supplier', ''),
                defaults=m
            )
        self.stdout.write(self.style.SUCCESS(f'  Created {len(materials)} material purchases'))

        # Sensor events
        events = [
            {'sensor_id': 'S-14', 'line': lines['LINE-A'], 'event_type': 'ok',   'message': 'Sensor S-14 yield batch committed via JWT'},
            {'sensor_id': 'S-B3', 'line': lines['LINE-B'], 'event_type': 'warn', 'message': 'Temp spike 84°C on press station B-3'},
            {'sensor_id': 'S-D1', 'line': lines['LINE-D'], 'event_type': 'err',  'message': 'Line D conveyor fault — auto-halted'},
            {'sensor_id': 'S-C2', 'line': lines['LINE-C'], 'event_type': 'ok',   'message': 'OEE target met for Gamma shift block'},
            {'sensor_id': 'SYS',  'line': None,            'event_type': 'warn', 'message': 'Material buffer low: Polymer resin < 15%'},
        ]
        for i, e in enumerate(events):
            SensorEvent.objects.get_or_create(
                sensor_id=e['sensor_id'],
                message=e['message'],
                defaults={**e, 'received_at': timezone.now() - timedelta(minutes=i*8)}
            )
        self.stdout.write(self.style.SUCCESS(f'  Created {len(events)} sensor events'))

        self.stdout.write(self.style.SUCCESS('\nSeed complete! Run the server and visit http://127.0.0.1:8000'))
        self.stdout.write('  Login: admin / admin123')
