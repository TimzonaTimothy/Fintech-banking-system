from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from datetime import datetime, timedelta
from django.utils.safestring import mark_safe
import threading
from django.conf import settings
from django.http import HttpResponse
from django.core.mail import (send_mail, BadHeaderError, EmailMessage)
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
User = get_user_model()

# Register your models here.

def send_broadcast_email(modeladmin, request, queryset):
    subject = 'Your Broadcast Subject'
    message = 'This is your broadcast message.'
    html_message = render_to_string('email_template.html', {'message': message})

    for user in queryset:
        send_mail(
            subject,
            strip_tags(html_message),
            'arizonatymothy@gmail.com',  # Replace with your email address
            [user.email],  # Recipient's email address
            fail_silently=False,
            html_message=html_message,
        )

    modeladmin.message_user(request, mark_safe(f'Successfully sent broadcast email to {len(queryset)} users.'))

send_broadcast_email.short_description = 'Send Broadcast Email'



class AccountAdmin(UserAdmin):
    def thumbnail(self, object):
        return format_html('<img src="{}" width="30" style="border-raduis:50%;">'.format(object.profile_picture.url))
    thumbnail.short_description = 'Profile Picture'
    
    def recommend_by_username(self, obj):
        if hasattr(obj, 'referral'):
            return obj.referral.referrer.username
        return None
    recommend_by_username.short_description = 'Recommended By'
    
    list_display = ('email', 'first_name', 'last_name','balance','kyc_submitted', 'kyc_confirmed', 'recommend_by_username','last_login', 'date_joined', 'last_activity', 'is_active')
    actions = [send_broadcast_email]
    list_display_links = ('email', 'first_name', 'last_name')
    readonly_fields = ('last_login', 'date_joined')
    ordering = ('-date_joined',)

    filter_horizontal = ()
    list_filter = ('date_joined','status','is_active','kyc_confirmed','kyc_submitted','country',)
    fieldsets = (
        ('Authenticators', {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'username','pin','status', 'phone','account_type','gender','date_of_birth', 'profile_picture', 'city', 'state', 'country','two_step_verification', 'code','ip_address','bitcoin_address')}),
        ('Balance', {'fields': ('balance','loan_balance','referral_balance','deposits','withdrawals',)}),
        ('KYC', {'fields':('is_restricted','kyc_submitted','kyc_confirmed')}),
        ('Checks', {'fields': ('is_support','date_joined', 'last_login', 'is_admin', 'is_staff', 'is_active', 'is_superadmin')}),
    )
    list_per_page = 25


admin.site.register(Account, AccountAdmin)

class KYCAdmin(admin.ModelAdmin):
    list_display = ('user', 'kyc_submitted','kyc_confirmed')
    list_display_links = ('user',)
    # readonly_fields = ('user',)
    ordering = ('-created_at',)

    filter_horizontal = ()
    list_filter = ('user','created_at',)
    list_per_page = 25

admin.site.register(KYC, KYCAdmin)



class TransactionAdmin(admin.ModelAdmin):
    list_display = ('sender','amount', 'recipient','transaction_id', 'transaction_type','created_at')
    list_display_links = ('sender', 'amount','transaction_id')
    # readonly_fields = ('created_at', 'description')
    ordering = ('-created_at',)

    filter_horizontal = ()
    list_filter = ('sender', 'amount',)
    list_per_page = 25

admin.site.register(Transaction, TransactionAdmin)

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_read', 'message','message_type','created_at')
    list_display_links = ('user', 'is_read')
    readonly_fields = ('is_read', 'created_at','message','message_type')
    ordering = ('-created_at',)

    filter_horizontal = ()
    list_filter = ('user',)
    list_per_page = 25

admin.site.register(Notification, NotificationAdmin)

class ReferralAdmin(admin.ModelAdmin):
    list_display = ('referrer', 'referred')
    list_display_links = ('referrer','referred',)
    readonly_fields = ('referrer',)
    ordering = ('-created',)

    filter_horizontal = ()
    list_filter = ('referrer','created',)
    list_per_page = 25
admin.site.register(Referral, ReferralAdmin)


class UserDeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'last_login')
    list_display_links = ('user',)
    # readonly_fields = ('user',)
    ordering = ('-last_login',)

    filter_horizontal = ()
    list_filter = ('user','device_browser','device_os',)
    list_per_page = 25
    search_fields = ['user',]

admin.site.register(UserDevice,UserDeviceAdmin)

class chatMessagesAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver')
    list_display_links = ('sender','receiver',)
    # readonly_fields = ('sender','receiver',)
    ordering = ('-date_created',)

    filter_horizontal = ()
    list_filter = ('sender','receiver',)
    list_per_page = 25
    search_fields = ['sender','receiver',]
admin.site.register(chatMessages, chatMessagesAdmin)

admin.site.site_header = 'ADMIN'
admin.site.site_title = 'ADMINISTRATION'