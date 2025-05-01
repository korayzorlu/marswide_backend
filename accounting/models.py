from django.db import models,transaction

from django.utils.translation import gettext_lazy as _
import uuid
from decimal import Decimal

from partners.models import Partner
from common.models import Currency
from companies.models import Company

# Create your models here.

class Account(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="accounts")

    TYPES = [
        ('receivable', 'Receivable'),
        ('payable', 'Payable'),
        ('bank', 'Bank')
    ]
    type = models.CharField(_("Type"), max_length=10, choices=TYPES, default = "receivable")

    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name="partner_accounts")
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, blank=True, null=True, related_name="currency_accounts")

    balance = models.DecimalField(_("Balance"), default = 0.00, max_digits=14, decimal_places=2)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['partner', 'currency'], name='unique_partner_currency')
        ]

    def __str__(self):
        return str(self.partner.name)
    
class Transaction(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="transactions")

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="account_transactions")

    ref_uuid = models.CharField(_("Ref UUID"), max_length=140, unique=True)

    TYPES = [
        ('debit', 'Debit'),
        ('credit', 'Credit')
    ]
    type = models.CharField(_("Type"), max_length=10, choices=TYPES, default = "debit")
    amount = models.DecimalField(_("Amount"), default = 0.00, max_digits=14, decimal_places=2)
    date = models.DateTimeField(_("Date"), auto_now_add=True, null=True)

    description = models.TextField(_("Description"), blank = True, null = True)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(f"{self.account.partner.name} -  {self.type} - {self.amount}")
    
    def save(self, *args, **kwargs):
        with transaction.atomic():
            is_new = self._state.adding

            if not is_new:
                # Önce eski veriyi al
                old = Transaction.objects.get(pk=self.pk)
                self._reverse_balance(old)

            # Yeni değeri uygula
            self._apply_balance()
            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            self._reverse_balance(self)
            super().delete(*args, **kwargs)

    def _apply_balance(self):
        self.account.balance = Decimal(self.account.balance)
        if self.account.type == 'receivable':
            if self.type == 'debit':
                self.account.balance += self.amount  # Alacak arttı
            elif self.type == 'credit':
                self.account.balance -= self.amount  # Tahsilat yapıldı

        elif self.account.type == 'payable':
            if self.type == 'debit':
                self.account.balance -= self.amount  # Borç ödendi
            elif self.type == 'credit':
                self.account.balance += self.amount  # Borç oluştu

        self.account.save()

    def _reverse_balance(self, txn):
        self.account.balance = Decimal(self.account.balance)
        if txn.account.type == 'receivable':
            if txn.type == 'debit':
                self.account.balance -= txn.amount  # Önceki etkisini tersine al
            elif txn.type == 'credit':
                self.account.balance += txn.amount

        elif txn.account.type == 'payable':
            if txn.type == 'debit':
                self.account.balance += txn.amount
            elif txn.type == 'credit':
                self.account.balance -= txn.amount

        self.account.save()

class Invoice(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="invoices")

    invoice_no = models.CharField(_("Invoice No"), max_length=140, blank = True, null=True)

    TYPES = [
        ('sale', 'Sales Invoice'),
        ('purchase', 'Purchase Invoice'),
    ]
    type = models.CharField(_("Type"), max_length=10, choices=TYPES, default = "sale")

    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name="partner_invoices")
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, blank=True, null=True, related_name="currency_invoices")

    amount = models.DecimalField(_("Amount"), default = 0.00, max_digits=14, decimal_places=2)
    date = models.DateTimeField(_("Date"), auto_now_add=True, null=True)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(f"{self.partner.name} - {self.invoice_no}")
    
    def save(self, *args, **kwargs):
        with transaction.atomic():
            is_new = self._state.adding

            if is_new:
                has_account = Account.objects.filter(partner = self.partner, currency = self.currency).exists()
                if not has_account:
                    if self.type == 'sale':
                        new_account_type = 'receivable'
                    elif self.type == 'purchase':
                        new_account_type = 'payable'
                    new_account = Account.objects.create(
                        company = self.company,
                        partner = self.partner,
                        currency = self.currency,
                        type = new_account_type
                    )
                    new_account.save()

                if self.type == 'sale':
                    new_txn_type = 'debit'
                elif self.type == 'purchase':
                    new_txn_type = 'credit'

                new_txn = Transaction.objects.create(
                    company = self.company,
                    type = new_txn_type,
                    account = Account.objects.filter(partner = self.partner, currency = self.currency).first() or new_account,
                    amount = self.amount,
                    ref_uuid = self.uuid,
                    description = f"{self.get_type_display()} - {self.invoice_no or ''}"
                )
                new_txn.save()
            else:
                txn = Transaction.objects.filter(ref_uuid = str(self.uuid)).first()
                old_invoice = Invoice.objects.get(pk=self.pk)

                partner_changed = self.partner != old_invoice.partner
                currency_changed = self.currency != old_invoice.currency

                if partner_changed or currency_changed:
                    # Eski Transaction'ın etkisini kaldır
                    txn.delete()

                    # Yeni Account oluştur veya mevcut olanı al
                    account = Account.objects.filter(partner=self.partner, currency=self.currency).first()
                    if not account:
                        if self.type == 'sale':
                            account_type = 'receivable'
                        elif self.type == 'purchase':
                            account_type = 'payable'
                        account = Account.objects.create(
                            company=self.company,
                            partner=self.partner,
                            currency=self.currency,
                            type=account_type
                        )
                    
                    if self.type == 'sale':
                        txn_type = 'debit'
                    elif self.type == 'purchase':
                        txn_type = 'credit'
                    
                    new_txn = Transaction.objects.create(
                        company=self.company,
                        type=txn_type,
                        account=account,
                        amount=self.amount,
                        ref_uuid=self.uuid,
                        description=f"{self.get_type_display()} - {self.invoice_no or ''}"
                    )
                    new_txn.save()
                else:
                    txn.amount = self.amount
                    txn.save()

            super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        with transaction.atomic():
            txn = Transaction.objects.filter(ref_uuid = str(self.uuid)).first()
            txn.delete()
            super().delete(*args, **kwargs)

class Payment(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="payments")

    payment_no = models.CharField(_("Payment No"), max_length=140, blank = True, null=True)

    TYPES = [
        ('incoming', 'Incoming Payment'),
        ('outgoing', 'Outgoing Payment'),
    ]
    type = models.CharField(_("Type"), max_length=10, choices=TYPES, default = "incoming")

    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name="partner_payments")
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, blank=True, null=True, related_name="currency_payments")

    amount = models.DecimalField(_("Amount"), default = 0.00, max_digits=14, decimal_places=2)
    date = models.DateTimeField(_("Date"), auto_now_add=True, null=True)

    description = models.TextField(_("Description"), blank = True, null = True)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(f"{self.partner.name} - {self.invoice_no}")
    
    def save(self, *args, **kwargs):
        with transaction.atomic():
            is_new = self._state.adding

            if is_new:
                has_account = Account.objects.filter(partner = self.partner, currency = self.currency).exists()
                if not has_account:
                    if self.type == 'incoming':
                        new_account_type = 'receivable'
                    elif self.type == 'outgoing':
                        new_account_type = 'payable'
                    new_account = Account.objects.create(
                        company = self.company,
                        partner = self.partner,
                        currency = self.currency,
                        type = new_account_type
                    )
                    new_account.save()

                if self.type == 'incoming':
                    new_txn_type = 'credit'
                elif self.type == 'outgoing':
                    new_txn_type = 'debit'

                new_txn = Transaction.objects.create(
                    company = self.company,
                    type = new_txn_type,
                    account = Account.objects.filter(partner = self.partner, currency = self.currency).first() or new_account,
                    amount = self.amount,
                    ref_uuid = self.uuid,
                    description = f"{self.get_type_display()} - {self.payment_no or ''}"
                )
                new_txn.save()
            else:
                txn = Transaction.objects.filter(ref_uuid = str(self.uuid)).first()
                old_payment = Payment.objects.get(pk=self.pk)

                partner_changed = self.partner != old_payment.partner
                currency_changed = self.currency != old_payment.currency

                if partner_changed or currency_changed:
                    # Eski Transaction'ın etkisini kaldır
                    txn.delete()

                    # Yeni Account oluştur veya mevcut olanı al
                    account = Account.objects.filter(partner=self.partner, currency=self.currency).first()
                    if not account:
                        if self.type == 'incoming':
                            account_type = 'receivable'
                        elif self.type == 'outgoing':
                            account_type = 'payable'
                        account = Account.objects.create(
                            company=self.company,
                            partner=self.partner,
                            currency=self.currency,
                            type=account_type
                        )
                    
                    if self.type == 'incoming':
                        txn_type = 'credit'
                    elif self.type == 'outgoing':
                        txn_type = 'debit'
                    
                    new_txn = Transaction.objects.create(
                        company=self.company,
                        type=txn_type,
                        account=account,
                        amount=self.amount,
                        ref_uuid=self.uuid,
                        description=f"{self.get_type_display()} - {self.payment_no or ''}"
                    )
                    new_txn.save()
                else:
                    txn.amount = self.amount
                    txn.save()

            super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        with transaction.atomic():
            txn = Transaction.objects.filter(ref_uuid = str(self.uuid)).first()
            txn.delete()
            super().delete(*args, **kwargs)