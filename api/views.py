from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from django.contrib.auth.models import User
from .models import Inbox, Email
from .serializers import UserSerializer, InboxSerializer, EmailSerializer
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

class InboxViewSet(viewsets.ModelViewSet):
    serializer_class = InboxSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Inbox.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['delete'])
    def clear(self, request, pk=None):
        """Delete all emails in this inbox."""
        inbox = self.get_object()
        Email.objects.filter(inbox=inbox).delete()
        return Response({'status': 'inbox cleared'}, status=status.HTTP_200_OK)

class EmailViewSet(viewsets.ModelViewSet):
    serializer_class = EmailSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'delete', 'head', 'options']

    def get_queryset(self):
        # Users can only see emails from their own inboxes
        qs = Email.objects.filter(inbox__user=self.request.user)
        inbox_id = self.request.query_params.get('inbox')
        if inbox_id:
            qs = qs.filter(inbox__id=inbox_id)
        return qs


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_test_email(request):
    inbox_id  = request.data.get('inbox_id')
    from_addr = request.data.get('from_addr', '').strip()
    to_addr   = request.data.get('to_addr', '').strip()
    subject   = request.data.get('subject', '(no subject)').strip()
    body_text = request.data.get('body_text', '').strip()
    body_html = request.data.get('body_html', '').strip()

    if not inbox_id or not to_addr:
        return Response({'error': 'inbox_id and to_addr are required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        inbox = Inbox.objects.get(id=inbox_id, user=request.user)
    except Inbox.DoesNotExist:
        return Response({'error': 'Inbox not found.'}, status=status.HTTP_404_NOT_FOUND)

    if not from_addr:
        from_addr = inbox.email_address

    # Build MIME message
    if body_html:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From']    = from_addr
        msg['To']      = to_addr
        if body_text:
            msg.attach(MIMEText(body_text, 'plain'))
        msg.attach(MIMEText(body_html, 'html'))
    else:
        msg = MIMEText(body_text or '(empty)', 'plain')
        msg['Subject'] = subject
        msg['From']    = from_addr
        msg['To']      = to_addr

    try:
        smtp_host = os.environ.get('SMTP_HOST', '127.0.0.1')
        smtp_port = int(os.environ.get('SMTP_PORT', '2525'))
        with smtplib.SMTP(smtp_host, smtp_port, timeout=5) as server:
            server.login(inbox.smtp_username, inbox.smtp_password)
            server.sendmail(from_addr, [to_addr], msg.as_string())
    except smtplib.SMTPException as e:
        return Response({'error': f'SMTP error: {str(e)}'}, status=status.HTTP_502_BAD_GATEWAY)
    except OSError as e:
        return Response({'error': f'Could not connect to SMTP server: {str(e)}'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    return Response({'status': 'sent', 'inbox': inbox.name}, status=status.HTTP_200_OK)
