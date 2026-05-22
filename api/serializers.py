from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Inbox, Email, Attachment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class InboxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inbox
        fields = ('id', 'name', 'email_address', 'smtp_username', 'smtp_password', 'created_at')
        read_only_fields = ('id', 'created_at')

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ('id', 'filename', 'content_type', 'file', 'size')

class EmailSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Email
        fields = ('id', 'inbox', 'sender', 'recipient', 'subject', 'body_text', 'body_html', 'received_at', 'attachments')
