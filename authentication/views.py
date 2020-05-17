from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
import threading
from .utils import account_activation_token
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.conf import settings
from django.views.generic import View
from django.http import JsonResponse
from validate_email import validate_email
import json


class EmailThread(threading.Thread):
    def __init__(self, subject, html_content, from_email, recipient_list):
        self.subject = subject
        self.recipient_list = recipient_list
        self.html_content = html_content
        self.from_email = from_email
        threading.Thread.__init__(self)

    def run(self):
        send_mail(message=self.html_content, from_email=settings.EMAIL_HOST_USER, subject=self.subject,
                  recipient_list=[self.recipient_list])


class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data.get('username', '')
        if not str(username).isalnum():
            return JsonResponse({'error': 'username can  only contain letters and numbers'})
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'username is taken,please choose a new one'})
        return JsonResponse({'is_available': 'true'})


class CredentialsValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data.get('email', '')
        if not email:
            return JsonResponse({'error': 'Please enter an email'})
        is_valid = validate_email(email)
        if not is_valid:
            return JsonResponse({'error': 'Please enter a valid email'})
        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email is taken,please choose a new one'})
        # if not validate_email(email, check_mx=True):
        #     return JsonResponse({'error': 'The email domain server does not exist'})
        # if not validate_email(email, verify=True):
        #     return JsonResponse({'error': 'The email does not exist on the domain server'})
        return JsonResponse({'valid': True})


class RegistrationView(View):
    def post(self, request):
        # Get form values
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        # Check username
        if User.objects.filter(username=username).exists():
            messages.error(request, 'That username is taken')
            return redirect('register')
        else:
            if User.objects.filter(email=email).exists():
                messages.error(request, 'That email is being used')
                return redirect('register')
            else:
                user = User.objects.create_user(
                    username=username, password=password, email=email)
                user.is_active = False
                user.save()
                current_site = get_current_site(request)
                email_subject = 'Activate Your Account'
                message = render_to_string('authentication/activate_account.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })
                EmailThread(subject=email_subject, from_email=settings.EMAIL_HOST_USER,
                            html_content=message, recipient_list=user.email).start()
                messages.add_message(request, messages.SUCCESS, 'Account created successfully,please visit your email to '
                                                                'verify your Account')
                return redirect('login')

    def get(self, request):
        return render(request, 'authentication/register.html')


class LoginView(View):
    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            if user.is_active == True:
                auth.login(request, user)
                messages.success(request, 'You are now logged in')
                return redirect('expenses')
            else:
                messages.error(request, 'Email is not verified')
                return redirect('login')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login')

    def get(self, request):
        return render(request, 'authentication/login.html')


class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            messages.add_message(request, messages.INFO,
                                 "Account has been activated,you may login now")
            return redirect('login')
        messages.add_message(request, messages.WARNING,
                             "verification Link was used before,please login")
        return redirect('login')


class ProfileView(View):
    def get(self, request):
        return render(request, 'authentication/profile.html')


class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, 'You are now logged out')
        return redirect('login')


class RequestResetLinkView(View):
    def get(self, request):
        return render(request, 'authentication/reset-password.html')

    def post(self, request):
        context = {
            'data': request.POST
        }
        email = request.POST.get('email')
        if not email:
            messages.add_message(request, messages.ERROR,
                                 'please provide a valid email')
            return render(request, 'authentication/reset-password.html', context, status=400)
        current_site = get_current_site(request)
        user = User.objects.filter(email=email).first()
        if not user:
            messages.add_message(request, messages.ERROR,
                                 'Details not found,please consider a signup')
            return render(request, 'authentication/reset-password.html', context, status=404)

        email_subject = 'Reset your Password'
        message = render_to_string('authentication/finish-reset.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
        EmailThread(subject=email_subject, from_email=settings.EMAIL_HOST_USER,
                    html_content=message, recipient_list=user.email).start()
        messages.add_message(
            request, messages.INFO, 'We have sent you an email with a link to reset your password')
        return render(request, 'authentication/reset-password.html', context)


class CompletePasswordChangeView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is None or not account_activation_token.check_token(user, token):
            messages.add_message(
                request, messages.WARNING, 'Link is no longer valid,please request a new one')
            return render(request, 'authentication/reset-password.html', status=401)
        return render(request, 'authentication/change-password.html', context={'uidb64': uidb64, 'token': token})

    def post(self, request, uidb64, token):
        context = {'uidb64': uidb64, 'token': token}
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            password = request.POST.get('password')
            password2 = request.POST.get('password2')
            if len(password) < 6:
                messages.add_message(
                    request, messages.ERROR, 'Password should be at least 6 characters long')
                return render(request, 'authentication/change-password.html', context, status=400)
            if password != password2:
                messages.add_message(
                    request, messages.ERROR, 'Passwords must match')
                return render(request, 'authentication/change-password.html', context, status=400)
            user.set_password(password)
            user.save()
            messages.add_message(
                request, messages.INFO, 'Password changed successfully,login with your new password')
            return redirect('login')
        except DjangoUnicodeDecodeError:
            messages.add_message(
                request, messages.ERROR, 'Something went wrong,you could not update your password')
            return render(request, 'authentication/change-password.html', context, status=401)
