from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta, date
from .models import ProductionLine, YieldRecord, MaterialPurchase, SensorEvent
import json


def get_date_range(range_key):
    today = timezone.now().date()
    if range_key == 'today':
        return today, today
    elif range_key == 'week':
        return today - timedelta(days=6), today
    elif range_key == 'month':
        return today.replace(day=1), today
    elif range_key == 'quarter':
        q_start_month = ((today.month - 1) // 3) * 3 + 1
        return today.replace(month=q_start_month, day=1), today
    return today, today


@login_required
def index(request):
    # Filter parameters
    line_code = request.GET.get('line', 'all')
    date_range = request.GET.get('range', 'today')
    shift = request.GET.get('shift', 'all')

    date_from, date_to = get_date_range(date_range)

    # Base queryset
    qs = YieldRecord.objects.filter(
        recorded_at__date__gte=date_from,
        recorded_at__date__lte=date_to,
    )
    if line_code != 'all':
        qs = qs.filter(line__code=line_code)
    if shift != 'all':
        qs = qs.filter(shift=shift)

    # KPIs
    totals = qs.aggregate(
        total_units=Sum('units_produced'),
        total_defective=Sum('units_defective'),
        avg_oee=Avg('oee_efficiency'),
    )
    total_units = totals['total_units'] or 0
    total_defective = totals['total_defective'] or 0
    defect_rate = round(total_defective / total_units * 100, 2) if total_units else 0
    avg_oee = round(float(totals['avg_oee'] or 0), 1)

    # Material spend
    material_spend = MaterialPurchase.objects.filter(
        ordered_at__date__gte=date_from,
    ).aggregate(total=Sum('total_cost'))['total'] or 0

    # Production lines summary
    lines = ProductionLine.objects.all()
    line_summaries = []
    for line in lines:
        lqs = qs.filter(line=line)
        lagg = lqs.aggregate(
            units=Sum('units_produced'),
            defects=Sum('units_defective'),
            oee=Avg('oee_efficiency'),
        )
        units = lagg['units'] or 0
        defects = lagg['defects'] or 0
        yield_rate = round((units - defects) / units * 100, 1) if units else 0
        line_summaries.append({
            'line': line,
            'units': units,
            'yield_rate': yield_rate,
            'oee': round(float(lagg['oee'] or 0), 1),
        })

    # Hourly trend data for chart (last 8 hours)
    now = timezone.now()
    hourly_labels = []
    hourly_datasets = {line.code: [] for line in lines}
    for i in range(7, -1, -1):
        hour_start = now - timedelta(hours=i+1)
        hour_end = now - timedelta(hours=i)
        hourly_labels.append(hour_start.strftime('%H:00'))
        for line in lines:
            val = YieldRecord.objects.filter(
                line=line,
                recorded_at__gte=hour_start,
                recorded_at__lt=hour_end,
            ).aggregate(total=Sum('units_produced'))['total'] or 0
            hourly_datasets[line.code].append(val)

    # Sensor feed
    sensor_events = SensorEvent.objects.select_related('line').order_by('-received_at')[:10]

    # Materials
    materials = MaterialPurchase.objects.order_by('-ordered_at')[:6]

    # All lines for filter dropdown
    all_lines = ProductionLine.objects.all()

    context = {
        'total_units': total_units,
        'defect_rate': defect_rate,
        'material_spend': material_spend,
        'avg_oee': avg_oee,
        'line_summaries': line_summaries,
        'sensor_events': sensor_events,
        'materials': materials,
        'all_lines': all_lines,
        'hourly_labels': json.dumps(hourly_labels),
        'hourly_datasets': json.dumps(hourly_datasets),
        'line_codes': json.dumps([l.code for l in lines]),
        # Active filter state
        'active_line': line_code,
        'active_range': date_range,
        'active_shift': shift,
        'session_timeout': 900,
    }
    return render(request, 'dashboard/index.html', context)


@login_required
def yield_input(request):
    """Factory floor manager daily yield input form."""
    lines = ProductionLine.objects.filter(status__in=['run', 'warn'])
    error = None
    success = None

    if request.method == 'POST':
        try:
            line_id = request.POST['line']
            line = ProductionLine.objects.get(pk=line_id)
            units = int(request.POST['units_produced'])
            defects = int(request.POST['units_defective'])
            oee = float(request.POST['oee_efficiency'])
            shift = request.POST['shift']

            if defects > units:
                raise ValueError("Defective units cannot exceed produced units.")
            if not (0 <= oee <= 100):
                raise ValueError("OEE must be between 0 and 100.")

            YieldRecord.objects.create(
                line=line,
                units_produced=units,
                units_defective=defects,
                oee_efficiency=oee,
                shift=shift,
                submitted_by=request.user,
                notes=request.POST.get('notes', ''),
            )
            success = f"Yield data for {line.name} ({shift} shift) submitted successfully."
        except (KeyError, ValueError, ProductionLine.DoesNotExist) as e:
            error = str(e)

    return render(request, 'dashboard/yield_input.html', {
        'lines': lines,
        'error': error,
        'success': success,
    })
