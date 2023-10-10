import pyotp
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from account.models import UserDevice
from user_agents import parse

User = get_user_model()

def send_otp(request, email):
    totp = pyotp.TOTP(pyotp.random_base32(), interval=480)
    otp = totp.now()
    request.session['otp_secret_key'] = totp.secret
    valid_date = datetime.now() + timedelta(minutes=2)
    request.session['otp_valid_date'] = str(valid_date)
    user = get_object_or_404(User, email=email)
    msg = ''
    user_agent = request.META.get('HTTP_USER_AGENT', '')  
    user_agent_info = parse(user_agent)
    existing_device = UserDevice.objects.filter(user=user).last()
    if existing_device:
        if user_agent_info.os.family.strip() != existing_device.device_os.strip():
            msg = 'For security reasons, we noticed you signed up with another device or browser'
    mail_subject = 'OTP Code'
    message = render_to_string('user/otp-mail.html', {
        'user':user,
        'otp':otp,
        'msg':msg,
        })
            
    to_email = user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.content_subtype = "html"
    send_email.send()



    print(f"Your OTP is {otp}")