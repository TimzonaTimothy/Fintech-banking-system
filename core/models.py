from django.db import models
from datetime import datetime
from account.models import Account,Notification
# Create your models here.


class Contact(models.Model):
    name = models.CharField(max_length=300)
    email = models.EmailField(max_length=300)
    phone = models.IntegerField(blank=True)
    subject = models.CharField(max_length=300, blank=True)
    message = models.TextField(blank=True)
    contact_date = models.DateTimeField(default=datetime.now, blank=True)
    

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'


class Deposit_Request(models.Model):
    STATUS = (
        ('Pending','Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    amount = models.IntegerField(blank=False, default='0', null=True)
    crypto = models.CharField(max_length=100, blank=False, null=True)
    wallet_id = models.CharField(max_length=200, blank=False, null=True)
    reference_id = models.CharField(blank=True, max_length=500, null=True)
    transaction_id = models.CharField(blank=True, max_length=500, null=True)
    transaction_image = models.ImageField(blank=True, upload_to='useridentity/%Y%m%d/')
    status = models.CharField(max_length=20, choices=STATUS, default='Pending',null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    added_to_balance = models.BooleanField(default=False, null=True)
    
    class Meta:
        verbose_name = 'Fund Deposit'
        verbose_name_plural = 'Fund Deposits'

    def __str__(self):
        return str(self.user)
    
    def save(self):
        if self.id:
            old = Deposit_Request.objects.get(pk=self.id)
            if old.status == 'Pending' and self.status == 'Confirmed':
                amount = self.amount
                user = self.user
                update_user_balance = Account.objects.get(username=user.username)
                if self.added_to_balance == True:
                    pass
                else:
                    update_user_balance.balance +=amount
                    update_user_balance.deposits +=amount
                    self.added_to_balance=True
                    update_user_balance.save()
                
                sent_notification = Notification.objects.create(
                    user=user,
                    message=f"Your deposit of ${amount}, with reference ${self.reference_id}, has been approved",
                    message_type='Message', 
                    is_read=False
                    )
                sent_notification.save()
                mail_subject = 'Fund Approval Notification'
                # message = render_to_string('', {
                #     'user' : user,
                #     'amount':amount,
                #     'reference_id':self.reference_id,
                #     })
            
                # to_email = user.email
                # send_email = EmailMessage(mail_subject, message, to=[to_email])
                # send_email.content_subtype = "html"
                # send_email.send()
            if old.status == 'Pending' and self.status == 'Cancelled':
                amount = self.amount
                user = self.user
                sent_notification = Notification.objects.create(
                    user=user,
                    message=f"Your deposit of ${amount}, with reference ${self.reference_id}, was cancelled",
                    message_type='Message', 
                    is_read=False
                    )
                sent_notification.save()
                mail_subject = 'Fund Approval Notification'
                # message = render_to_string('', {
                #     'user' : user,
                #     'amount':amount,
                #     'reference_id':self.reference_id,
                #     'date' : self.created_at
                #     })
            
                # to_email = user.email
                # send_email = EmailMessage(mail_subject, message, to=[to_email])
                # send_email.content_subtype = "html"
                # send_email.send()
        super(Deposit_Request, self).save()



class Withdrawal_Request(models.Model):
    STATUS = (
        ('Pending','Pending'),
        ('Paid','Paid'),
    )
    user = models.ForeignKey(Account, on_delete=models.CASCADE,  null=True)
    amount = models.IntegerField(blank=False, default='0', null=True)
    status = models.CharField(max_length=20, choices=STATUS, default='Pending',null=True)
    remove_from_balance = models.BooleanField(default=False,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Withdrawal'
        verbose_name_plural = 'Withdrawals'

    def __str__(self):
        return str(self.user)
    
    def save(self):
        if self.id:
            old = Withdrawal_Request.objects.get(pk=self.id)
            if old.status == 'Pending' and self.status == 'Paid':
                amount = self.amount
                user = self.user
                update_user_balance = Account.objects.get(username=user.username)
                if self.remove_from_balance == True:
                    pass
                else:
                    update_user_balance.balance -=amount
                    update_user_balance.withdrawals +=amount
                    self.remove_from_balance = True
                    update_user_balance.save()
                sent_notification = Notification.objects.create(
                    user=user,
                    message=f"Your withdrawal of ${amount} has been approved",
                    message_type='Message', 
                    is_read=False
                    )
                sent_notification.save()
                
                # mail_subject = 'Payment Notification'
                # message = render_to_string('', {
                #     'user' : user,
                #     'amount':amount,
                #     'date' : self.created_at
                #     })
            
                # to_email = user.email
                # send_email = EmailMessage(mail_subject, message, to=[to_email])
                # send_email.content_subtype = "html"
                # send_email.send()
        super(Withdrawal_Request, self).save()


class Loan(models.Model):
    STATUS = (
        ('Pending','Pending'),
        ('Approved','Approved'),
        ('Rejected','Rejected'),
        ('Repaid', 'Repaid')
    )

    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    term = models.PositiveIntegerField(help_text="Loan term in months", null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='Pending', null=True)
    added_to_balance = models.BooleanField(default=False, null=True)
    date_applied = models.DateTimeField(auto_now_add=True)
    date_approved = models.DateTimeField(null=True, blank=True)
    date_disbursed = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Loan'
        verbose_name_plural = 'Loans'

    def __str__(self):
        return str(self.user)
    
    # def save(self):
    #     if self.id:
    #         old = Loan.objects.get(pk=self.id)
    #         if old.status == 'Pending' and self.status == 'Approved':
    #             amount = self.amount
    #             user = self.user
    #             update_user_loan_balance = Account.objects.get(username=user.username)
    #             if self.added_to_balance == True:
    #                 pass
    #             else:
    #                 update_user_loan_balance.loan_balance +=amount
    #                 # update_user_loan_balance.withdrawals +=amount
    #                 self.added_to_balance = True
    #                 update_user_loan_balance.save()
    #             sent_notification = Notification.objects.create(
    #                 user=user,
    #                 message=f"Your loan request of ${amount} has been approved",
    #                 message_type='Message', 
    #                 is_read=False
    #                 )
    #             sent_notification.save()
                
    #             # mail_subject = 'Payment Notification'
    #             # message = render_to_string('', {
    #             #     'user' : user,
    #             #     'amount':amount,
    #             #     'date' : self.created_at
    #             #     })
            
    #             # to_email = user.email
    #             # send_email = EmailMessage(mail_subject, message, to=[to_email])
    #             # send_email.content_subtype = "html"
    #             # send_email.send()
    #     super(Loan, self).save()
