from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Contact)

class Deposit_RequestAdmin(admin.ModelAdmin):
    list_display = ('user','transaction_id', 'amount', 'status','created_at')
    list_display_links = ('user','amount','transaction_id')
    readonly_fields = ('created_at','crypto','added_to_balance', 'wallet_id','reference_id','transaction_image','transaction_id',)
    ordering = ('-created_at',)

    filter_horizontal = ()
    list_filter = ('user', 'amount','crypto','created_at',)
    list_per_page = 25

admin.site.register(Deposit_Request,Deposit_RequestAdmin)

class Withdrawal_RequestAdmin(admin.ModelAdmin):
    list_display = ('user','amount', 'status','created_at')
    list_display_links = ('user', 'amount')
    readonly_fields = ('created_at','remove_from_balance',)
    ordering = ('-created_at',)

    filter_horizontal = ()
    list_filter = ('user', 'amount','created_at',)
    list_per_page = 25

admin.site.register(Withdrawal_Request, Withdrawal_RequestAdmin)
admin.site.register(Loan)