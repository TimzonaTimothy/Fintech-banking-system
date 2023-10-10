from django.db import models, transaction
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models import Q
from django.utils import timezone

class MyAccountManager(BaseUserManager):
    def create_user(self,email, first_name,last_name,username,password=None):
        if not email:
            raise ValueError('User must have an email address')

        if not username:
            raise ValueError('User must have username')

        user = self.model(
            email = self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name = last_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name,email,last_name,username,password):
        user = self.create_user(
            email = self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name = last_name,
            password=password,
        )

        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):

    STATUS = (
        ('ACTIVE','ACTIVE'),
        ('IN-ACTIVE','IN-ACTIVE'),
        ('PENDING','PENDING'),
    )

    first_name    = models.CharField(max_length=100)
    last_name     = models.CharField(max_length=100)
    username     = models.CharField(max_length=100, unique=True)
    email         = models.EmailField(max_length=100, unique=True)
    bitcoin_address = models.CharField(blank=True, max_length=200)
    balance = models.FloatField(blank=True, null=True, default=00.00)
    loan_balance = models.FloatField(blank=True, null=True, default=00.00)
    deposits = models.FloatField(blank=True, null=True, default=00.00)
    withdrawals = models.FloatField(blank=True, null=True, default=00.00)
    referral_balance = models.FloatField(blank=True, null=True, default=00.00)
    pin =  models.CharField(max_length=4, verbose_name="PIN CODE",unique=True,blank=True, null=True)
    phone = models.CharField(blank=True, max_length=100) 
    account_type = models.CharField(blank=True, max_length=100)
    gender = models.CharField(blank=True, max_length=100)
    date_of_birth = models.CharField(blank=True, max_length=10)  
    profile_picture = models.ImageField(blank=True, upload_to='userprofile/%Y%m%d/')
    city = models.CharField(blank=True, max_length=100) 
    state = models.CharField(blank=True, max_length=100) 
    country = models.CharField(blank=True, max_length=100)
    kyc_submitted = models.BooleanField(default=False,blank=True)
    kyc_confirmed = models.BooleanField(default=False,blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='IN-ACTIVE',null=True)
    ip_address = models.GenericIPAddressField(blank=True,null=True)
    code = models.CharField(max_length=8, verbose_name="Referral code",blank=True,null=True)
    recommend_by = models.CharField(max_length=300, blank=True)
    is_restricted = models.BooleanField(default=False,blank=True)
    two_step_verification = models.BooleanField(default=False,blank=True)
    last_activity = models.DateTimeField(auto_now=True)

    date_joined   = models.DateTimeField(auto_now_add=True) 
    last_login    = models.DateTimeField(auto_now_add=True)   
    is_admin      = models.BooleanField(default=False)
    is_staff      = models.BooleanField(default=False)
    is_active     = models.BooleanField(default=False)
    is_support = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','first_name', 'last_name', ]

    objects = MyAccountManager()


    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return str(self.username)

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, add_label):
        return True

    @property
    def total_referrals(self):
        if not hasattr(self, "referrals"):
            return None
        return self.referrals.all()

    @property
    def total_referrals_count(self):
        if self.total_referrals == None:
            return 0
        return self.referrals.all().count()


    @property
    def unread_notification_count(self):
        return self.notification_set.filter(is_read=False).count()
    
    @property
    def recommend_by(self):
        if not hasattr(self, 'referral'):
            return None
        return self.referral.referrer.username

class UserDevice(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE,null=True)
    device_name = models.CharField(max_length=255,null=True)
    device_type = models.CharField(max_length=255,null=True)
    device_os = models.CharField(max_length=255,null=True)
    device_browser = models.CharField(max_length=255,null=True)
    last_login = models.DateTimeField(null=True)

    def __str__(self):
        return str(self.user)
    
class Referral(models.Model):
    referrer = models.ForeignKey(Account, related_name="referrals",on_delete=models.CASCADE, null=True)
    referred = models.OneToOneField(Account, on_delete=models.CASCADE, null=True)
    withdrawn = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now=True, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)

    def  __str__(self):
        return f"Referrer: {self.referrer.username} || Referred: {self.referred.username}"
    
    
class Notification(models.Model):
    STATUS = (
        ('Sent','Sent'),
        ('Recieved','Recieved'),
        ('Password_Change','Password_Change'),
        ('Message','Message'),
    )
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    message = models.CharField(max_length=255)
    message_type = models.CharField(blank=True, choices=STATUS,max_length=100, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user)
    
    def mark_as_read(self):
        self.is_read = True
        self.save()


class KYC(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE,  null=True)
    full_name    = models.CharField(max_length=200)
    marrital_status = models.CharField(blank=True, max_length=100)
    gender = models.CharField(blank=True, max_length=100)
    identity_type = models.CharField(blank=True, max_length=100) 
    identity_picture = models.ImageField(blank=True, upload_to='useridentity/%Y%m%d/')
    signature_image = models.ImageField(blank=True, upload_to='useridentity/%Y%m%d/')
    date_of_birth = models.CharField(blank=True, max_length=10)  
    picture = models.ImageField(blank=True, upload_to='userkyc/%Y%m%d/')
    phone = models.CharField(blank=True, max_length=100)
    city = models.CharField(blank=True, max_length=100) 
    state = models.CharField(blank=True, max_length=100) 
    country = models.CharField(blank=True, max_length=100)
    kyc_submitted = models.BooleanField(default=False,blank=True)
    kyc_confirmed = models.BooleanField(default=False,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.full_name)
    
    def is_kyc_submitted(self):
        return self.kyc_submitted

    def is_kyc_confirmed(self):
        return self.kyc_confirmed

    def save(self, *args, **kwargs):
        if self.kyc_confirmed and not self.kyc_submitted:
            self.kyc_confirmed = False  # Reset kyc_confirmed if not submitted

        super().save(*args, **kwargs)
        self.update_account_status()

    def update_account_status(self):
        user = self.user
        if user:
            kyc_entries = KYC.objects.filter(user=user)
            kyc_submitted = any(entry.kyc_submitted for entry in kyc_entries)
            kyc_confirmed = any(entry.kyc_confirmed for entry in kyc_entries)

            if kyc_submitted and kyc_confirmed:
                user.status = 'ACTIVE'
                user.kyc_submitted = True
                user.kyc_confirmed = True
                user.save()
                notification = Notification.objects.filter(user=user).create(
                    user=user,
                    message=f"Your KYC has been confirmed, and your account is now verified",
                    message_type='Message',
                    is_read=False
                )
            elif kyc_submitted and not kyc_confirmed:
                user.status = 'PENDING'
                user.kyc_submitted = True
                user.save()
            else:
                user.status = 'IN-ACTIVE'
                user.save()
        # user.save()


class Transaction(models.Model):
    STATUS = (
        ('Payment','Payment'),
        ('Bill','Bill'),
    )
    sender = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, related_name='sent_transactions')
    amount = models.FloatField(blank=True, null=True, default=00.00)
    recipient = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    description = models.CharField(blank=True, max_length=100, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=12, editable=False,verbose_name="Transaction ID",unique=True, null=True)
    transaction_type = models.CharField(blank=True, choices=STATUS,max_length=100, null=True)

    def __str__(self):
        return str(self.sender)
    
    class Meta:
        ordering = ["-created_at"]
    
   
class chatMessages(models.Model):
    sender = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="+", null=True)
    receiver = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="+", null=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True,null=True)

    class Meta:
        ordering = ('-date_created',)

    def __str__(self):
        return str(self.sender.full_name()) 