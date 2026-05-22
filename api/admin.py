from django.contrib import admin

from .models import Inbox, Email,Attachment

# Register your models here.


admin.site.register(Inbox)
admin.site.register(Email)
admin.site.register(Attachment)