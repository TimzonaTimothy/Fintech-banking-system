from django.shortcuts import render
from .models import *
from django.http import JsonResponse
import os
from account.models import *
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from datetime import datetime, timedelta
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from django.views import View
from django.conf import settings
from xhtml2pdf import pisa
import json
# Create your views here.

def generate_pdf(request):
    transaction_id = request.GET.get('transaction_id')

    try:
        transaction = Transaction.objects.get(transaction_id=transaction_id, sender=request.user)
    except Transaction.DoesNotExist:
        # Handle the case where the transaction doesn't exist or doesn't belong to the user
        return HttpResponse('Transaction not found or unauthorized', status=403)

    template_path = 'dashboard/transaction_detail_statement_template.html'
    context = {'transaction': transaction}

    template = get_template(template_path)
    html = template.render(context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{transaction.transaction_id}.pdf"'

    pisa_status = pisa.CreatePDF(
        html, dest=response)  # Removed reference to self.link_callback

    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

@login_required(login_url = 'sign_in')
def referral(request):
    currect_site = get_current_site(request)
    referral_link = f'https://{currect_site}/?ref_code={request.user.code}'
    return render(request, 'dashboard/referral.html', {'referral_link':referral_link})


@login_required(login_url = 'sign_in')
def deposit(request):
    if request.method == 'POST':
        crypto = request.POST['crypto']
        wallet_id = request.POST['wallet_id']
        amount = request.POST['amount']
        amount = float(amount)
        trn_id = request.POST['trn_id']
        trn_proof = request.FILES.get('trn_proof')

        if int(amount) < 100:
            messages.error(request, 'Amount less than 100')
            return HttpResponseRedirect(reverse('account:dashboard'))
        elif not request.user.kyc_confirmed:
            messages.error(request, 'Account Not Verified')
            return HttpResponseRedirect(reverse('account:kyc'))
        else:
            deposit = Deposit_Request(
                user=request.user,
                amount=amount,
                crypto=crypto,
                wallet_id=wallet_id,
                transaction_id=trn_id,
                transaction_image=trn_proof
            )
            deposit.save()

            # send_mail(
            #     'New crypto Deposite, Order ID '+ order_number,
            #     'Go to admin panel to confirm',
            #     'support@domain.net',
            #     ['support@domain.net',],
            #     fail_silently=False
            # )
            
            # mail_subject = 'Deposit Notification'
            # message = render_to_string('', {
            #     'user' : user,
            #     'amount':amount,
            #     '':,
            #     })
            
            # to_email = user.email
            # send_email = EmailMessage(mail_subject, message, to=[to_email])
            # send_email.content_subtype = "html"
            # send_email.send()
            
            messages.success(request, 'Please wait while we verify your deposit')
            return HttpResponseRedirect(reverse('account:dashboard'))
    return HttpResponseRedirect(reverse('account:dashboard'))


@login_required(login_url = 'sign_in')
def withdrawal(request):
    if request.method == 'POST':
        pin = request.POST['pin']
        amount = request.POST['amount']
        amount = float(amount)
        
        if not request.user.kyc_confirmed:
            messages.error(request, 'Account Not Verified')
            return HttpResponseRedirect(reverse('account:kyc'))
        elif request.user.pin is None:
            messages.error(request, 'Set Pin')
            return HttpResponseRedirect(reverse('account:set_pin'))
        elif request.user.pin != pin:
            messages.error(request, 'Wrong PIN')
            return HttpResponseRedirect(reverse('account:dashboard'))
        elif amount < 100:
            messages.error(request, 'Amount less than 100')
            return HttpResponseRedirect(reverse('account:dashboard'))
        elif amount > request.user.balance:
            messages.error(request, 'Insufficient Fund')
            return HttpResponseRedirect(reverse('account:dashboard'))
        
        deposit = Withdrawal_Request(
            user=request.user,
            amount=amount,
            )
        deposit.save()

        # send_mail(
        #     'New withrawal request,+ order_number,
        #     'Go to admin panel to confirm',
        #     'support@domain.net',
        #     ['support@domain.net',],
        #     fail_silently=False
        # )
            
        # mail_subject = 'Withdrawal Notification'
        # message = render_to_string('', {
        #     'user' : user,
        #     'amount':amount,
        #     '':,
        #     })
            
        # to_email = user.email
        # send_email = EmailMessage(mail_subject, message, to=[to_email])
        # send_email.content_subtype = "html"
        # send_email.send()
            
        messages.success(request, 'Please wait while we process your request')
        return HttpResponseRedirect(reverse('account:dashboard'))
    return HttpResponseRedirect(reverse('account:dashboard'))


@login_required(login_url = 'sign_in')
def transfer(request):
    if request.method == 'POST':
        pin = request.POST.get('pin')
        amount = request.POST.get('amount')
        recipient_identifier = request.POST.get('recipient_identifier').lower()
        description = request.POST.get('description', False)
        amount = float(amount)
        recipient= None
        recipient_full_name = ""
        recipient_profile_picture = ""
        try:
            recipient = Account.objects.get(Q(email=recipient_identifier))
            recipient_full_name = recipient.full_name()  
            if recipient.profile_picture:
                recipient_profile_picture = recipient.profile_picture.url
            else:
                # Handle the case where there's no profile picture associated with the recipient
                recipient_profile_picture = None
        except Account.DoesNotExist:
            messages.error(request, 'User Account Not Found')
            return HttpResponseRedirect(reverse('account:dashboard'))

        if not request.user.kyc_confirmed:
            messages.error(request, 'Account Not Verified')
            return HttpResponseRedirect(reverse('account:kyc'))
        elif request.user.pin is None:
            messages.error(request, 'Set Pin')
            return HttpResponseRedirect(reverse('account:set_pin'))
        elif request.user.pin != pin:
            messages.error(request, 'Wrong PIN')
            return HttpResponseRedirect(reverse('account:dashboard'))
        elif recipient == request.user:
            messages.error(request, 'Wrong Transaction')
            return HttpResponseRedirect(reverse('account:dashboard'))
        elif amount< 100:
            messages.error(request, 'Amount less than 100')
            return HttpResponseRedirect(reverse('account:dashboard'))
        elif pin is None or amount is None or recipient is None:
            messages.error(request, 'Please Provide Required Inputs')
            return HttpResponseRedirect(reverse('account:dashboard'))
        elif amount > request.user.balance:
            messages.error(request, 'Insufficient Fund')
            return HttpResponseRedirect(reverse('account:dashboard'))
        else:
            request.session['pin'] = pin
            request.session['amount'] = amount
            request.session['recipient_identifier'] = recipient_identifier
            request.session['description'] = description
            

            context = {
                'pin':pin,
                'amount':amount,
                'recipient':recipient,
                'description':description,
                'recipient_full_name':recipient_full_name,
                'recipient_profile_picture':recipient_profile_picture
            }
            
            return render(request, 'dashboard/app-transaction-verification.html', context)            
    return HttpResponseRedirect(reverse('account:dashboard'))

@login_required(login_url = 'sign_in')
def confirm_transfer(request):
    if request.method == 'POST':
        # Get session variables
        amount = request.session.get('amount')
        recipient_identifier = request.session.get('recipient_identifier')
        description = request.session.get('description')

        # Check if session has expired or required data is missing
        if not all([amount, recipient_identifier]):
            messages.error(request, 'Session Has Expired or Required Data Missing')
            return HttpResponseRedirect(reverse('account:dashboard'))
        
        recipient = None
        recipient_full_name = ''

        try:
            recipient = Account.objects.get(Q(email=recipient_identifier))
            recipient_full_name = recipient.full_name()  
        except Account.DoesNotExist:
            messages.error(request, 'User Account Not Found')
            return HttpResponseRedirect(reverse('account:dashboard'))
        
        try:
            amount = float(amount)
        except (TypeError, ValueError, ValidationError):
            messages.error(request, 'Invalid Amount Format')
            return HttpResponseRedirect(reverse('account:dashboard'))
        
        else:
            transfer_fund = Transaction(
                sender=request.user,
                amount=amount,
                recipient=recipient,
                transaction_type='Payment',
                description=description
            )
            transfer_fund.save()

            user = request.user
            user.balance -=amount
            recipient.balance +=amount
            user.save()
            recipient.save()

            sent_notification = Notification.objects.create(
                user=user,
                message=f"You sent ${amount} to {recipient_full_name}",
                message_type='Sent', 
                is_read=False
            )

            received_notification = Notification.objects.create(
                user=recipient,
                message=f"You received ${amount} from {user.full_name()}",
                message_type='Recieved', 
                is_read=False
            )

            sent_notification.save()
            received_notification.save()

            # mail_subject = 'Transfer Notification'
            # message = render_to_string('', {
            #     'user' : user,
            #     'amount':amount,
            #     '':,
            #     })
            
            # to_email = user.email
            # send_email = EmailMessage(mail_subject, message, to=[to_email])
            # send_email.content_subtype = "html"
            # send_email.send()

            # mail_subject = 'Transfer Notification'
            # message = render_to_string('', {
            #     'recipient' : recipient,
            #     'amount':amount,
            #     '':,
            #     })
            
            # to_email = user.email
            # send_email = EmailMessage(mail_subject, message, to=[to_email])
            # send_email.content_subtype = "html"
            # send_email.send()
            del request.session['amount']
            del request.session['recipient_identifier']
            del request.session['description']
            messages.success(request, 'Transaction Succesful')
            return HttpResponseRedirect(reverse('account:dashboard'))
        
    return render(request, 'dashboard/app-transaction-verification.html', {})


@login_required(login_url = 'sign_in')
def transactions(request):
    transactions = Transaction.objects.filter(sender=request.user).all()
    
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    grouped_transactions = {}
    for transaction in transactions:
        transaction_date = transaction.created_at.date()

        if transaction_date == today:
            date_key = "today"
        elif transaction_date == yesterday:
            date_key = "yesterday"
        else:
            date_key = transaction_date.strftime("%b %d, %Y")

        if date_key not in grouped_transactions:
            grouped_transactions[date_key] = []

        grouped_transactions[date_key].append(transaction)
    
    return render(request, 'dashboard/app-transactions.html',{"grouped_transactions": grouped_transactions})

@login_required(login_url = 'sign_in')
def transaction_detail(request, trn_id):
    transaction = Transaction.objects.get(pk=trn_id)
    recipient = None
    try:
        recipient = Account.objects.get(Q(email=transaction.recipient))
    except Account.DoesNotExist:
        pass
    return render(request, 'dashboard/app-transaction-detail.html', {'transaction':transaction,'recipient':recipient})

class TransactionStatementPDF(View):
    def get(self, request):
        user = request.user
        return render(request, 'dashboard/transaction_statement.html')

    def post(self, request):
        user = request.user
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)  

            transactions = Transaction.objects.filter(
                sender=user,
                created_at__range=[start_date, end_date],
            ).order_by('-created_at')

            # Generate PDF
            template_path = 'dashboard/transaction_statement_template.html'
            context = {'transactions': transactions, 'start_date': start_date, 'end_date': end_date,'user': user}

            template = get_template(template_path)
            html = template.render(context)
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'filename="{user.full_name()} TransactionStatement.pdf"'
            # response['Content-Disposition'] = 'filename="transaction_statement.pdf"'

            pisa_status = pisa.CreatePDF(
                html, dest=response, link_callback=self.link_callback)

            if pisa_status.err:
                return HttpResponse('We had some errors <pre>' + html + '</pre>')
            return response
        else:
            # Handle invalid form data here, e.g., show an error message or re-render the form
            return render(request, 'transaction_statement.html')

    @staticmethod
    def link_callback(uri, rel):
        # Convert HTML URIs to absolute system paths so ReportLab can access those resources
        s_url = settings.STATIC_URL
        s_root = settings.STATIC_ROOT
        m_url = settings.MEDIA_URL
        m_root = settings.MEDIA_ROOT

        if uri.startswith(m_url):
            path = os.path.join(m_root, uri.replace(m_url, ''))
        elif uri.startswith(s_url):
            path = os.path.join(s_root, uri.replace(s_url, ''))
        else:
            return uri

        if not os.path.isfile(path):
            raise Exception(
                'Media URI must start with {} or {}. '
                'Got {} instead.'.format(s_url, m_url, uri))
        return path

@login_required(login_url = 'sign_in')
def loan_request(request):
    if request.method == 'POST':
        amount = request.POST['amount']
        term = request.POST['term']

        if request.user.status == 'IN-ACTIVE' or 'PENDING':
            messages.error(request, 'Account Not Verified')
            return HttpResponseRedirect(reverse('account:kyc'))
        
        loan = Loan.objects.create(
            user=request.user,
            amount=amount,
            term=term    
        )
        loan.save()
        messages.success(request, 'Submitted Successfully')
        return HttpResponseRedirect(reverse('core:loan_request'))
    loans = Loan.objects.filter(user=request.user).all().order_by('-date_applied')
    return render(request, 'dashboard/loan.html', {'loans':loans})


@login_required(login_url='sign_in')
def chart_support_list(request):
    adms = Account.objects.filter(is_support=True).last()
    if request.user.is_superadmin:
        users = Account.objects.all()
    return render(request,'dashboard/chart_support_list.html',{'adms':adms,"users":users})


@login_required(login_url='sign_in')
def chart_support(request, pk:int):
    adm = get_object_or_404(Account, pk=pk)
    user = request.user

    # Check if the request is a JSON POST request
    if request.method == "POST" and request.content_type == 'application/json':
        try:
            # Handle the JSON POST request for sending a message
            message_data = json.loads(request.body)
            message_text = message_data.get('message', '')
            

            if message_text.strip():
                # Create and save the new message
                new_message = chatMessages.objects.create(
                    sender=request.user,
                    receiver=adm,  # Assuming the message is sent to 'adm'
                    message=message_text
                )

                # Respond with a success JSON response if needed
                return JsonResponse({'status': 'Message sent successfully'})

        except json.JSONDecodeError as e:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)

    # If it's not a JSON POST request or for rendering the chat interface
    messages = chatMessages.objects.filter(
        Q(sender=adm, receiver=user)
    )
    messages.update(is_read=True)
    messages = messages | chatMessages.objects.filter(Q(sender=adm, receiver=user))

    return render(request, 'dashboard/chart_support.html', {'adm':adm, 'users': Account.objects.all(), "user_messages": messages})


@login_required(login_url='sign_in')
def ajax_load_messages(request, pk):
    other_user = get_object_or_404(Account, pk=pk)
    last_message_id = request.GET.get('last_message_id')
    messages = chatMessages.objects.filter(receiver=request.user,
                                           id__gt=last_message_id if last_message_id else 0  # Only get messages with IDs greater than the last_message_id
    ).order_by('id')
    
    print("messages")
    message_list = [{
        "sender": message.sender.username,
        "message": message.message,
        "sent": message.sender == request.user,
        # "picture": other_user.profile_picture.url,

        "date_created": message.date_created,

    } for message in messages]
    messages.update(is_read=True)
    
    if request.method == "POST":
        message = json.loads(request.body)['message']
        
        m = chatMessages.objects.create(receiver=other_user, sender=request.user, message=message)
        message_list.append({
            "sender": request.user.username,
            "username": request.user.username,
            "message": m.message,
            "date_created": m.date_created,

            "picture": request.user.profile_picture.url,
            "is_read": True,
        })
    print(message_list)
    return JsonResponse(message_list, safe=False)

