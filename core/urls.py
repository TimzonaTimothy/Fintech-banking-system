from django.urls import path, re_path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

app_name = 'core'

urlpatterns = [
    path('deposit', views.deposit, name='deposit'),
    path('withdrawal', views.withdrawal, name='withdrawal'),
    path('transfer', views.transfer, name='transfer'),
    path('confirm_transfer',views.confirm_transfer, name="confirm_transfer"),
    path('transactions',views.transactions, name='transactions'),
    path('transaction_detail/<int:trn_id>/', views.transaction_detail, name='transaction_detail'),
    path('generate_transaction_statement/', views.TransactionStatementPDF.as_view(), name='generate_transaction_statement'),
    path('generate_pdf/', views.generate_pdf, name='generate_pdf'),
    path('referral', views.referral, name="referral"),
    path('loan', views.loan_request, name="loan_request"),
    path('chart_support_list', views.chart_support_list, name="chart_support_list"),
    path('chart_support/<int:pk>/', views.chart_support, name="chart_support"),
    path('ajax_load_messages/<int:pk>/', views.ajax_load_messages, name='ajax_load_messages'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

