from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from .models import *
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect
from datetime import datetime, timedelta
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.urls import reverse
# Create your views here.

@login_required(login_url = 'sign_in')
def dashboard(request):
    if 'email' in request.session:
        del request.session['email']

    transactions = Transaction.objects.filter(sender=request.user).all()[0:5]
    
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

        
    context = {
         "grouped_transactions": grouped_transactions,
    }
    return render(request, 'dashboard/index.html',context)


@login_required(login_url = 'sign_in')
def kyc(request):
    if request.user.kyc_submitted:
        return HttpResponseRedirect(reverse('account:dashboard'))
    if request.method == 'POST':
        picture = request.FILES.get('image')
        full_name = request.POST['full_name']
        gender = request.POST['gender']
        city = request.POST['city']
        country = request.POST['state']
        date_of_birth = request.POST['date_of_birth']
        marrital_status = request.POST['marrital_status']
        identity_type = request.POST['identity_type']
        identity_picture = request.FILES.get('picture')
        signature_image = request.FILES.get('signature_image')
        phone = request.POST['phone']
        state = request.POST['state']

       
        user_account = KYC(user=request.user)


        user_account.full_name = full_name
        user_account.marrital_status = marrital_status
        user_account.gender = gender
        user_account.identity_type = identity_type
        if identity_picture:
            user_account.identity_picture = identity_picture
        if signature_image:
            user_account.signature_image = signature_image
        user_account.date_of_birth = date_of_birth
        user_account.phone = phone
        user_account.city = city
        user_account.state = state
        user_account.country = country
        if picture:
            user_account.picture = picture
        user_account.kyc_submitted = True
        user_account.save()
        messages.success(request, 'KYC Submitted Successfully')
        # return HttpResponseRedirect(reverse('account:kyc'))
    return render(request, 'dashboard/kyc.html', {})


def send_notification(user, message):
    notification = Notification(user=user, message=message)
    notification.save()

@login_required(login_url = 'sign_in')
def mark_notification_as_read(request, notification_id):
    notification = Notification.objects.get(pk=notification_id)
    if notification.user == request.user:
        notification.mark_as_read()
    return render(request, 'dashboard/app-notifications.html',{})

@login_required(login_url = 'sign_in')
def all_notifications(request):
    post_obj = Notification.objects.filter(user=request.user).all().order_by('-created_at')  
     
    total_obj = Notification.objects.filter(user=request.user).count() 
    return render(request, 'dashboard/app-notifications.html',{'posts': post_obj, 'total_obj': total_obj})

@login_required(login_url = 'sign_in')
def settings(request):
    return render(request, 'dashboard/settings.html', {})

@login_required(login_url = 'sign_in')
def profile_details(request):
    if request.method == 'POST':
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        phone = request.POST["phone"]
        gender = request.POST['gender']
        date_of_birth = request.POST['date_of_birth']
        city = request.POST["city"]
        state = request.POST["state"]
        country = request.POST["country"]
        profile_picture = request.FILES.get('profile_picture')

        user = request.user

        user.first_name = first_name
        user.last_name = last_name
        user.phone = phone
        user.date_of_birth = date_of_birth
        user.gender = gender
        user.city = city
        user.state = state
        user.country = country
        if profile_picture:
            
            user.profile_picture = profile_picture
        user.save()
        return HttpResponseRedirect(reverse('account:profile_details'))

    else:
        return render(request, 'dashboard/profile_details.html', {})


@login_required(login_url = 'sign_in')
def change_password(request):
    if request.method == 'POST':
        
        new_password = request.POST["new_password"]
        confirmed_new_password = request.POST["confirm_password"]
        current_password = request.POST['old_password']
        
        if  new_password and confirmed_new_password:
            if request.user.is_authenticated:
                user = Account.objects.get(username= request.user.username)
                
                if not check_password(current_password, user.password):
                    messages.warning(request, 'Old Password does not match')
                    return HttpResponseRedirect(reverse('account:change_password'))
                elif new_password != confirmed_new_password:
                    messages.warning(request, "Password does not match with the confirm password !")
                    return HttpResponseRedirect(reverse('account:change_password'))
                    
                elif len(new_password) < 8 or new_password.lower() == new_password or \
                    new_password.upper() == new_password or new_password.isalnum() or \
                    not any(i.isdigit() for i in new_password):
                    messages.warning(request, "Password is too weak!")
                    return HttpResponseRedirect(reverse('account:change_password'))

                    

                else:
                    user.set_password(new_password)
                    user.save()
                    update_session_auth_hash(request, user)

                    notification = Notification.objects.create(
                        user=request.user,
                        message=f"Password Changed",
                        message_type='Password_Change', 
                        is_read=False
                    )
                    messages.success(request, "Password changed successfully.!")

                    return redirect('/account/change_password')

        else:
            pass
 
    return render(request, 'dashboard/change_password.html', {})


@login_required(login_url = 'sign_in')
def change_pin(request):
    if request.method == 'POST':
        
        current_password = request.POST['current_password']
        old_pin = request.POST['old_pin']
        new_pin = request.POST["new_pin"]
        
        if  new_pin and old_pin:
            if request.user.is_authenticated:
                user = Account.objects.get(username= request.user.username)
                
                if not check_password(current_password, user.password):
                    messages.warning(request, 'Wrong Password!')
                    return HttpResponseRedirect(reverse('account:change_pin'))
                elif old_pin != user.pin:
                    messages.warning(request, "Wrong Old Pin!")
                    return HttpResponseRedirect(reverse('account:change_pin'))
                    
                elif len(new_pin) != 4:
                    messages.warning(request, "Pin Should Be 4 Digits!")
                    return HttpResponseRedirect(reverse('account:change_pin'))

                else:
                    user.pin = (new_pin)
                    user.save()
                    messages.success(request, "Pin changed successfully.!")
                    return HttpResponseRedirect(reverse('account:change_pin'))

        else:
            pass
    return render(request, 'dashboard/change_pin.html', {})



@login_required(login_url = 'sign_in')
def set_pin(request):
    if request.method == 'POST':
        
        pin = request.POST["pin"]
        
        if len(pin) == 4:
            if request.user.is_authenticated:
                user = request.user
                user.pin = (pin)
                user.save()
                messages.success(request, "Pin set successfully.!")
                return HttpResponseRedirect(reverse('account:set_pin'))
        else:
            messages.warning(request, "Pin Should Be 4 Digits!")
            return HttpResponseRedirect(reverse('account:set_pin'))
           
    return render(request, 'dashboard/set_pin.html', {})

@login_required(login_url = 'sign_in')
def two_step_verification(request):
    if request.method == 'POST':
        
        two_step_verification = request.POST.get("two_step_verification")
        if request.user.is_authenticated:
            user = Account.objects.get(username= request.user.username)
            user.two_step_verification = bool(two_step_verification)
            user.save()
            messages.success(request, "Two Step Verification set successfully.!")
            return HttpResponseRedirect(reverse('account:settings'))
    else:
        pass
           
    return render(request, 'dashboard/settings.html', {})