from django.db import models
from toures.models import Package
class Traveler(models.Model):
    traveler_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    address = models.TextField()

    def __str__(self):
        return self.name


class Ticket(models.Model):
    ticket_id = models.AutoField(primary_key=True)
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='tickets')
    traveler = models.ForeignKey(Traveler, on_delete=models.CASCADE, related_name='tickets')

    def __str__(self):
        return f"Ticket {self.ticket_id} - {self.traveler.name}"


class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    traveler = models.ForeignKey(Traveler, on_delete=models.CASCADE, related_name='payments')
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='payments')
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='payments')
    
    # eSewa audit fields
    esewa_transaction_uuid = models.CharField(max_length=100, blank=True, null=True, help_text="eSewa transaction UUID")
    esewa_transaction_code = models.CharField(max_length=100, blank=True, null=True, help_text="eSewa transaction code/reference")
    esewa_status = models.CharField(max_length=50, blank=True, null=True, help_text="eSewa transaction status")
    esewa_signature = models.TextField(blank=True, null=True, help_text="eSewa payment signature")
    esewa_raw_response = models.TextField(blank=True, null=True, help_text="Full eSewa API response for audit")
    payment_method = models.CharField(max_length=50, default='esewa', help_text="Payment method used")

    def __str__(self):
        return f"Payment {self.payment_id} - {self.amount}"
