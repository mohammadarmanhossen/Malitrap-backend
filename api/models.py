from django.db import models
from django.contrib.auth.models import User
import uuid
import random
import string

def generate_smtp_username():
    return uuid.uuid4().hex[:10]

def generate_smtp_password():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

class Inbox(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inboxes')
    name = models.CharField(max_length=255)
    email_address = models.EmailField(unique=True, help_text="The email address mapped to this inbox")
    smtp_username = models.CharField(max_length=50, default=generate_smtp_username, unique=True)
    smtp_password = models.CharField(max_length=50, default=generate_smtp_password)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.email_address})"

class Email(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inbox = models.ForeignKey(Inbox, on_delete=models.CASCADE, related_name='emails')
    sender = models.CharField(max_length=255)
    recipient = models.CharField(max_length=255)
    subject = models.CharField(max_length=512, blank=True, null=True)
    body_text = models.TextField(blank=True, null=True)
    body_html = models.TextField(blank=True, null=True)
    raw_source = models.TextField(blank=True, null=True)
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-received_at']

    def __str__(self):
        return f"{self.subject} from {self.sender}"

class Attachment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.ForeignKey(Email, on_delete=models.CASCADE, related_name='attachments')
    filename = models.CharField(max_length=255)
    content_type = models.CharField(max_length=100)
    file = models.FileField(upload_to='attachments/%Y/%m/%d/')
    size = models.IntegerField(default=0)

    def __str__(self):
        return self.filename
