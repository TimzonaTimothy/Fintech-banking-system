from django.urls import path, re_path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

app_name = 'account'

urlpatterns = [
    path('dashboard', views.dashboard, name='dashboard'),
    path('settings', views.settings, name='settings'),
    path('profile_details',views.profile_details, name="profile_details"),
    path('kyc', views.kyc, name='kyc'),
    path('change_password',views.change_password,name='change_password'),
    path('set_pin', views.set_pin, name="set_pin"),
    path('change_pin', views.change_pin, name="change_pin"),
    path('notifications/mark_as_read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('notifications',views.all_notifications, name="all_notifications"),
    # path('load_more_notification', views.load_more_notification, name='load_more_notification'),
    path('two_step_verification', views.two_step_verification, name='two_step_verification'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

