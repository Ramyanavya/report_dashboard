from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from accounts.models import User


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email.')
            return render(request, 'accounts/login.html')

        if not user.check_password(password):
            messages.error(request, 'Incorrect password.')
            return render(request, 'accounts/login.html')

        # Generate and send OTP
        otp = user.generate_otp()
        try:
            send_mail(
                subject='Your ReportPortal OTP',
                message=f'''Hello {user.full_name or user.email},

Your one-time password (OTP) for ReportPortal login is:

  {otp}

This OTP is valid for 10 minutes. Do not share it with anyone.

— ReportPortal Team''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as e:
            messages.error(request, f'Failed to send OTP email: {str(e)}')
            return render(request, 'accounts/login.html')

        request.session['otp_user_id'] = user.id
        messages.success(request, f'OTP sent to {email}. Please check your inbox.')
        return redirect('verify_otp')

    return render(request, 'accounts/login.html')


def verify_otp_view(request):
    user_id = request.session.get('otp_user_id')
    if not user_id:
        return redirect('login')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('login')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp', '').strip()
        if user.verify_otp(entered_otp):
            user.clear_otp()
            del request.session['otp_user_id']
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Welcome back, {user.full_name or user.email}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid or expired OTP. Please try again.')

    return render(request, 'accounts/verify_otp.html', {'user_email': user.email})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')


def dashboard_redirect(request):
    if not request.user.is_authenticated:
        return redirect('login')
    role = request.user.role
    if role == 'author':
        return redirect('author_dashboard')
    elif role == 'convener':
        return redirect('convener_dashboard')
    elif role == 'reviewer':
        return redirect('reviewer_dashboard')
    return redirect('login')
