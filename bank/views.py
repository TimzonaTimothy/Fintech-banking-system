from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy,reverse
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login,logout
from django.views.generic import TemplateView
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.contrib.auth import update_session_auth_hash
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from account.models import Account, Referral, KYC, UserDevice
from core.models import Contact
import pyotp
from datetime import datetime
from .utils import send_otp
from user_agents import parse
import requests

User = get_user_model()

def custom_404_view(request, exception):
    return render(request, '404.html', status=404)

def custom_500_view(request):
    return render(request, '500.html', status=500)

def home(request):
    ref_code = request.GET.get('ref_code')
    if ref_code:
        request.session['ref_code'] = ref_code
        request.session.set_expiry(86400)
    return render(request, 'index.html', {})

def about(request):
    return render(request, 'about-us.html', {})

def contact(request):
    current_site = get_current_site(request)
    up_current_site = f'https://{current_site}/admin'
    if request.method == "POST":
        name = request.POST['name'] 
        email = request.POST['email']
        subject = request.POST['subject']
        message = request.POST['message']
        contact = Contact.objects.create(name=name,email=email,subject=subject,message=message)
        contact.save();
        send_mail(
            'Contact Message',
            name + '. sent you a message, Sign in to admin panel for more information ' + up_current_site,
            'arizonatymothy@gmail.com',
            ['arizonatymothy@gmail.com',],
            fail_silently=False
            )
        messages.success(request, 'Your massage has been submitted ')
    return render(request, 'contact.html', {})

def services(request):
    return render(request, 'services.html', {})

def faq(request):
    return render(request, 'faq.html', {})

def terms(request):
    return render(request, 'terms.html', {})

def sign_in(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')
    else:
        if request.method == 'POST':
            email = request.POST['email']
            password = request.POST['password']

            if Account.objects.filter(email=email, is_active=False).exists():
                messages.warning(request, 'Please verify your mail')
                return redirect('/sign_in')
            
            if Account.objects.filter(email=email, is_restricted=True):
                messages.warning(request, 'Account is restricted')
                return redirect('/sign_in')
            
            user = auth.authenticate(email=email, password=password)

            if user is not None:
                if user.two_step_verification ==True:
                    send_otp(request, email)
                    request.session['email'] = email
                    return redirect('otp')
                user_agent = request.META.get('HTTP_USER_AGENT', '')  
                user_agent_info = parse(user_agent)
                existing_device = UserDevice.objects.filter(user=user).last()
                
                
                if existing_device:
                    if user_agent_info.os.family.strip() != existing_device.device_os.strip():
                        send_otp(request, email)
                        request.session['email'] = email
                        return redirect('otp')
                    else:
                        existing_device.last_login = timezone.now()
                        existing_device.save()
                        auth.login(request,user)
                        url = request.META.get('HTTP_REFFERER')
                        try:
                            query = requests.utils.urlparse(url).query
                            params = dict(x.split('=') for x in query.split('&'))
                            if 'next' in params:
                                nextpage = params['next']
                                return redirect(nextpage)
                        except:
                            return redirect('account:dashboard')  
                    
                else:
                    user = get_object_or_404(User, email=email)
                    auth.login(request,user)
                    UserDevice.objects.create(
                        user=user,
                        device_name='New Device',  
                        device_type=user_agent_info.device.family,
                        device_os=user_agent_info.os.family,
                        device_browser=user_agent_info.browser.family,
                        last_login=timezone.now(),
                        )
                    return redirect('account:kyc')
        
            else:
                messages.error(request, 'Invalid credentials')
                return redirect('/sign_in')
        else:
            return render(request, 'user/login.html',{})
        

def otp_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')
    else:
        if request.method == 'POST':
            otp = request.POST['otp']
            email = request.session['email']

            otp_secret_key = request.session['otp_secret_key']
            otp_valid_time = request.session['otp_valid_date']

            if otp_secret_key and otp_valid_time is not None:
                otp_valid_time = datetime.fromisoformat(otp_valid_time)

                if otp_valid_time > datetime.now():
                    totp = pyotp.TOTP(otp_secret_key, interval=480)
                    if totp.verify(otp):
                        user = get_object_or_404(User, email=email)
                        auth.login(request,user)
                        user_agent = request.META.get('HTTP_USER_AGENT', '')  
                        user_agent_info = parse(user_agent)
                        UserDevice.objects.create(
                            user=user,
                            device_name='New Device',  
                            device_type=user_agent_info.device.family,
                            device_os=user_agent_info.os.family,
                            device_browser=user_agent_info.browser.family,
                            last_login=timezone.now(),
                        )
                        del request.session['otp_secret_key']
                        del request.session['otp_valid_date']

                        if request.user.is_authenticated:
                        # Check if KYC has not been submitted
                            try:
                                user_kyc = KYC.objects.get(user=request.user)
                                if not user_kyc.is_kyc_submitted():
                                    return redirect('account:kyc')  # Redirect to KYC page
                                else:
                                    return redirect('account:dashboard')
                            except KYC.DoesNotExist:
                                pass  # KYC record not found, handle this case

                                return redirect('account:dashboard')
                    else:
                        messages.error(request,'OTP Invalid')
                else:
                    messages.error(request,'OTP Has Expired')
            else:
                messages.error('Something went wrong')
        return render(request, 'user/otp.html', {})
    

def sign_up(request, referred='',bot=''):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')
    else:
        if request.method == 'POST':
            #bot restriction from signing up
            try:
                bot = request.POST.get('bot-c')
                if bot == '':
                    pass
                else:
                    return redirect('/sign_up')
            except Account.DoesNotExist:
                pass
                        
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            email = request.POST['email']
            phone = request.POST['phone']
            country = request.POST['country']
            password = request.POST['password']
            confirm_password = request.POST['confirm_password']
            account_type = request.POST['account_type']
            gender = request.POST['gender']
            username = email
                    
            if Account.objects.filter(email=email).exists():
                messages.warning(request, 'Email already exists')
                return redirect('/sign_up')
            if Account.objects.filter(email=email, is_active=False).exists():
                messages.warning(request, 'Email already exists, Please verify your mail')
                return redirect('/sign_up')
            if password != confirm_password:
                messages.warning(request, "Password does not match with the confirm password !")
                return redirect('/sign_up')
                        
            if len(password) < 8 or password.lower() == password or password.upper() == password or password.isalnum() or not any(i.isdigit() for i in password):
                messages.warning(request, "Password is too weak!")
                return redirect('/sign_up')   
                            
                        
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, 
                                            username=username,password=password)
            
            try:
                code = request.POST.get('ref_code')
                if not code:
                    code = request.session.get('ref_code')
                    print(code)
                if code:
                    referrer = Account.objects.get(code=code)
                    Referral.objects.create(referrer=referrer, referred=user)
                    referrer.referral_balance = float(referrer.referral_balance) + 5
                    referrer.save()
                    del request.session['ref_code']
                else:
                    pass
            except Account.DoesNotExist:
                messages.warning(request, "Referral code does not exist")
                return redirect('/sign_up')
            
            user.phone=phone
            user.country=country
            user.gender = gender
            user.account_type = account_type
            user.ip_address = request.META.get("REMOTE_ADDR")
            

            user.save()
        
            # user_activation
            current_site = get_current_site(request)
            mail_subject = 'Welcome To '
            message = render_to_string('user/account_verification_email.html', {
                'user' : user,
                'domain' : current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user)
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.content_subtype = "html"
            send_email.send()
           
            messages.success(request, 'Verification email sent.')
            return redirect('/sign_in')
                
        else:      
    
            return render(request, 'user/register.html', {})
        
def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('/sign_in')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('/sign_up')

def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))


def forgetpassword(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')
    else:
        if request.method == 'POST':
            email = request.POST['email']
            if Account.objects.filter(email=email).exists():
                user = Account.objects.get(email__exact=email)


                current_site = get_current_site(request)
                mail_subject = 'Reset your password'
                message = render_to_string('user/reset_password_mail.html', {
                    'user' : user,
                    'domain' : current_site,
                    'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                    'token' : default_token_generator.make_token(user)
                })
                to_email = email
                send_email = EmailMessage(mail_subject, message, to=to_email)
                send_email.content_subtype = "html"
                send_email.send()

                messages.success(request, 'Password reset email has been sent to your email address.')
                return redirect('/sign_in')


            else:
                messages.error(request, 'Account does not exists!')
                return redirect('/forgetpassword')
        return render(request, 'user/forgetpassword.html', {})


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('/resetpassword')
    
    else:
        messages.error(request, 'This link has expired!')
        return redirect('/sign_in')



def resetpassword(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')
    else:
        if request.method == 'POST':
                password = request.POST['password']
                confirm_password = request.POST['confirm_password']

                if password == confirm_password:
                    uid = request.session.get('uid')
                    user = Account.objects.get(pk=uid)
                    user.set_password(password)
                    user.save()
                    messages.success(request, 'Password reset successful')
                    return redirect('/sign_in')

                else:
                    messages.error(request, 'Password do not match')
                    return redirect('/resetpassword')
        else:
            return render(request, 'user/resetpassword.html')