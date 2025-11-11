from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    ACCOUNT_CHOICES = (
        ('organization', 'Organization'),
        ('self', 'Self'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=150, blank=True)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_CHOICES, default='organization')
    org_name = models.CharField(max_length=200, blank=True)
    role_in_org = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    client_id = models.CharField(max_length=12, unique=True, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    city = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return f"{self.user.username} profile"


# New models for Lab Test Requests
class LabTestRequest(models.Model):
    STATUS_CHOICES = (
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
        ('on-test', 'On-Test'),
        ('ready-collect', 'Ready To Collect'),
        ('report-delivered', 'Report Delivered'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lab_requests')
    project_name = models.CharField(max_length=200)
    reference_number = models.CharField(max_length=120, blank=True)
    client_name = models.CharField(max_length=200, blank=True)
    project_location = models.CharField(max_length=200, blank=True)
    description_html = models.TextField(blank=True)
    sample_by = models.CharField(max_length=200, blank=True)
    receiving_date = models.DateField(blank=True, null=True)
    sample_description = models.TextField(blank=True)

    spec_document = models.FileField(upload_to='lab_requests/', blank=True, null=True)
    payment_receipt = models.FileField(upload_to='payment_receipts/', blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    # 8-digit verification code assigned when report is delivered
    report_verification_code = models.CharField(max_length=8, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Request #{self.id} by {self.user.username}"


class LabTestItem(models.Model):
    request = models.ForeignKey(LabTestRequest, on_delete=models.CASCADE, related_name='items')
    lab = models.CharField(max_length=50)
    subcategory = models.CharField(max_length=120)
    test_name = models.CharField(max_length=255)
    price = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.lab} - {self.test_name} (৳{self.price})"


class ConsultancyRequest(models.Model):
    STATUS_CHOICES = (
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
        ('on-test', 'On-Test'),
        ('ready-collect', 'Ready To Collect'),
        ('report-delivered', 'Report Delivered'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consultancy_requests')
    project_name = models.CharField(max_length=200)
    organization = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=200, blank=True)
    reference_number = models.CharField(max_length=120, blank=True)
    description_html = models.TextField(blank=True)

    attachment = models.FileField(upload_to='consultancy_requests/', blank=True, null=True)
    # NEW: amount to be set by admin upon approval
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    # NEW: receipt uploaded by user after amount set
    payment_receipt = models.FileField(upload_to='payment_receipts/', blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    # 8-digit verification code assigned when report is delivered
    report_verification_code = models.CharField(max_length=8, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Consultancy #{self.id} by {self.user.username}"
