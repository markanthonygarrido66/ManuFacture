from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from dashboard.api_views import YieldPushView, YieldStreamView, LineStatusView, SensorEventView

urlpatterns = [
    # JWT token endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # IoT sensor endpoints
    path('v2/yield/push', YieldPushView.as_view(), name='yield_push'),
    path('v2/yield/stream', YieldStreamView.as_view(), name='yield_stream'),
    path('v2/lines/status', LineStatusView.as_view(), name='lines_status'),
    path('v2/sensors/event', SensorEventView.as_view(), name='sensor_event'),
]
