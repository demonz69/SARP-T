import functools
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Avg

from .models import CustomUser, BusLocation, TripLog, Feedback, SpeedAlert


def admin_required(view_func):
    @functools.wraps(view_func)
    @login_required(login_url='login')
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'admin':
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def admin_dashboard(request):
    # Stats
    active_buses = BusLocation.objects.values('device_id').distinct().count()
    student_count = CustomUser.objects.filter(role='student').count()
    driver_count = CustomUser.objects.filter(role='driver').count()
    speed_alerts_today = SpeedAlert.objects.filter(triggered_at__date=timezone.now().date()).count()
    unread_alerts = SpeedAlert.objects.filter(acknowledged=False).count()
    avg_rating = round(Feedback.objects.aggregate(avg=Avg('rating'))['avg'] or 0, 1)

    # Latest location per bus
    seen = {}
    for entry in BusLocation.objects.all():
        if entry.device_id not in seen:
            seen[entry.device_id] = entry
    buses = list(seen.values())

    # Users with filter/search
    role_filter = request.GET.get('role', '')
    search = request.GET.get('q', '')
    users = CustomUser.objects.all().order_by('-date_joined')
    if role_filter:
        users = users.filter(role=role_filter)
    if search:
        users = users.filter(username__icontains=search) | users.filter(full_name__icontains=search)

    context = {
        'active_buses': active_buses,
        'student_count': student_count,
        'driver_count': driver_count,
        'speed_alerts_today': speed_alerts_today,
        'unread_alerts': unread_alerts,
        'avg_rating': avg_rating,
        'buses': buses,
        'users': users,
        'recent_feedback': Feedback.objects.select_related('user').all()[:8],
        'recent_alerts': SpeedAlert.objects.all()[:10],
        'recent_trips': TripLog.objects.all().order_by('-departure_time')[:10],
        'role_filter': role_filter,
        'search': search,
    }
    return render(request, 'myapp/admin_dashboard.html', context)


@admin_required
def user_edit(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        user.full_name = request.POST.get('full_name', user.full_name)
        user.email = request.POST.get('email', user.email)
        user.role = request.POST.get('role', user.role)
        user.is_active = request.POST.get('is_active') == 'on'
        user.save()
        return JsonResponse({'status': 'ok', 'message': f'User {user.username} updated.'})
    return JsonResponse({'status': 'error'}, status=400)


@admin_required
def user_delete(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if user == request.user:
        return JsonResponse({'status': 'error', 'message': "You can't delete yourself."}, status=400)
    user.delete()
    return JsonResponse({'status': 'ok', 'message': 'User deleted.'})


@admin_required
def bus_list(request):
    return redirect('admin_dashboard')


@admin_required
def trip_list(request):
    return redirect('admin_dashboard')


@admin_required
def trip_create(request):
    if request.method == 'POST':
        TripLog.objects.create(
            device_id=request.POST.get('device_id'),
            route_name=request.POST.get('route_name'),
            departure_time=request.POST.get('departure_time') or None,
            arrival_time=request.POST.get('arrival_time') or None,
            notes=request.POST.get('notes', ''),
        )
        return JsonResponse({'status': 'ok', 'message': 'Trip log created.'})
    return JsonResponse({'status': 'error'}, status=400)


@admin_required
def trip_edit(request, trip_id):
    trip = get_object_or_404(TripLog, id=trip_id)
    if request.method == 'POST':
        trip.device_id = request.POST.get('device_id', trip.device_id)
        trip.route_name = request.POST.get('route_name', trip.route_name)
        trip.departure_time = request.POST.get('departure_time') or None
        trip.arrival_time = request.POST.get('arrival_time') or None
        trip.notes = request.POST.get('notes', '')
        trip.save()
        return JsonResponse({'status': 'ok', 'message': 'Trip updated.'})
    return JsonResponse({'status': 'error'}, status=400)


@admin_required
def trip_delete(request, trip_id):
    get_object_or_404(TripLog, id=trip_id).delete()
    return JsonResponse({'status': 'ok', 'message': 'Trip deleted.'})


@admin_required
def alert_list(request):
    return redirect('admin_dashboard')


@admin_required
def alert_ack(request, alert_id):
    SpeedAlert.objects.filter(id=alert_id).update(acknowledged=True)
    return JsonResponse({'status': 'ok', 'message': 'Alert dismissed.'})


@admin_required
def alert_ack_all(request):
    SpeedAlert.objects.filter(acknowledged=False).update(acknowledged=True)
    return JsonResponse({'status': 'ok', 'message': 'All alerts dismissed.'})


@admin_required
def feedback_list(request):
    return redirect('admin_dashboard')


@admin_required
def feedback_delete(request, fb_id):
    get_object_or_404(Feedback, id=fb_id).delete()
    return JsonResponse({'status': 'ok', 'message': 'Feedback deleted.'})
