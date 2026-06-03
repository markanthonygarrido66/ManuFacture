from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db.models import Sum, Avg
from django.utils import timezone
from datetime import timedelta
from .models import YieldRecord, ProductionLine, SensorEvent
import logging

logger = logging.getLogger(__name__)


class YieldPushView(APIView):
    """
    POST /api/v2/yield/push
    JWT-authenticated endpoint for IoT sensors to push yield data.

    Payload:
    {
        "sensor_id": "S-14",
        "line_code": "LINE-A",
        "units_produced": 680,
        "units_defective": 12,
        "oee_efficiency": 91.4,
        "shift": "morning"
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        required = ['sensor_id', 'line_code', 'units_produced', 'oee_efficiency', 'shift']
        missing = [f for f in required if f not in data]
        if missing:
            return Response({'error': f"Missing fields: {', '.join(missing)}"}, status=400)

        try:
            line = ProductionLine.objects.get(code=data['line_code'])
        except ProductionLine.DoesNotExist:
            return Response({'error': f"Production line '{data['line_code']}' not found."}, status=404)

        units = int(data['units_produced'])
        defects = int(data.get('units_defective', 0))
        oee = float(data['oee_efficiency'])

        if defects > units:
            return Response({'error': 'Defective units exceed produced units.'}, status=400)
        if not (0 <= oee <= 100):
            return Response({'error': 'OEE must be 0–100.'}, status=400)

        record = YieldRecord.objects.create(
            line=line,
            units_produced=units,
            units_defective=defects,
            oee_efficiency=oee,
            shift=data['shift'],
            sensor_id=data['sensor_id'],
            submitted_by=request.user,
            notes=data.get('notes', ''),
        )

        SensorEvent.objects.create(
            sensor_id=data['sensor_id'],
            line=line,
            event_type='ok',
            message=f"Sensor {data['sensor_id']} committed {units} units (OEE {oee}%) via JWT.",
            payload=data,
        )

        logger.info(f"IoT push: sensor={data['sensor_id']} line={line.code} units={units}")

        return Response({
            'status': 'accepted',
            'record_id': record.pk,
            'yield_rate': record.yield_rate,
            'defect_rate': record.defect_rate,
        }, status=201)


class YieldStreamView(APIView):
    """
    GET /api/v2/yield/stream
    Returns aggregated yield data for the last N hours.
    Query params: hours=8, line=LINE-A
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        hours = int(request.query_params.get('hours', 8))
        line_code = request.query_params.get('line')
        since = timezone.now() - timedelta(hours=hours)

        qs = YieldRecord.objects.filter(recorded_at__gte=since)
        if line_code:
            qs = qs.filter(line__code=line_code)

        agg = qs.aggregate(
            total_units=Sum('units_produced'),
            total_defects=Sum('units_defective'),
            avg_oee=Avg('oee_efficiency'),
        )

        records = list(qs.values(
            'id', 'line__code', 'line__name', 'units_produced',
            'units_defective', 'oee_efficiency', 'shift', 'recorded_at', 'sensor_id'
        ).order_by('-recorded_at')[:100])

        return Response({
            'period_hours': hours,
            'summary': {
                'total_units': agg['total_units'] or 0,
                'total_defects': agg['total_defects'] or 0,
                'avg_oee': round(float(agg['avg_oee'] or 0), 2),
            },
            'records': records,
        })


class LineStatusView(APIView):
    """
    GET /api/v2/lines/status
    Returns current status of all production lines.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        lines = ProductionLine.objects.all()
        data = []
        for line in lines:
            latest = YieldRecord.objects.filter(line=line).first()
            data.append({
                'code': line.code,
                'name': line.name,
                'sector': line.sector,
                'status': line.status,
                'last_record': {
                    'units': latest.units_produced if latest else None,
                    'oee': float(latest.oee_efficiency) if latest else None,
                    'yield_rate': latest.yield_rate if latest else None,
                    'recorded_at': latest.recorded_at.isoformat() if latest else None,
                } if latest else None,
            })
        return Response({'lines': data, 'count': len(data)})


class SensorEventView(APIView):
    """
    POST /api/v2/sensors/event
    IoT sensors push arbitrary events (warnings, errors, diagnostics).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        line = None
        if 'line_code' in data:
            line = ProductionLine.objects.filter(code=data['line_code']).first()

        event = SensorEvent.objects.create(
            sensor_id=data.get('sensor_id', 'unknown'),
            line=line,
            event_type=data.get('event_type', 'ok'),
            message=data.get('message', ''),
            payload=data,
        )
        return Response({'status': 'logged', 'event_id': event.pk}, status=201)
