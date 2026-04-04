from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from reports.models import Report
from accounts.models import User


def role_required(*roles):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.role not in roles:
                messages.error(request, 'Access denied.')
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# ─── AUTHOR VIEWS ───────────────────────────────────────────────

@login_required
@role_required('author')
def author_dashboard(request):
    reports = Report.objects.filter(author=request.user)
    stats = {
        'total': reports.count(),
        'submitted': reports.filter(status='submitted').count(),
        'under_review': reports.filter(status='under_review').count(),
        'accepted': reports.filter(status='accepted').count(),
        'revision': reports.filter(status='revision_required').count(),
    }
    return render(request, 'reports/author_dashboard.html', {
        'reports': reports,
        'stats': stats,
    })


@login_required
@role_required('author')
def submit_report(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        author_name = request.POST.get('author_name', '').strip()
        contributors = request.POST.get('contributors', '').strip()
        abstract = request.POST.get('abstract', '').strip()
        keywords = request.POST.get('keywords', '').strip()
        report_type = request.POST.get('report_type', '').strip()
        paper_doc = request.FILES.get('paper_doc')
        plagiarism_doc = request.FILES.get('plagiarism_doc')

        if not all([title, author_name, abstract, keywords, report_type, paper_doc]):
            messages.error(request, 'Please fill all required fields.')
            return render(request, 'reports/submit_report.html')

        report = Report.objects.create(
            author=request.user,
            title=title,
            author_name=author_name,
            contributors=contributors,
            abstract=abstract,
            keywords=keywords,
            report_type=report_type,
            paper_doc=paper_doc,
            plagiarism_doc=plagiarism_doc,
        )

        # Notify conveners
        conveners = User.objects.filter(role='convener')
        send_mail(
            subject=f'New Report Submitted: {title}',
            message=f'A new report "{title}" has been submitted.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=list(conveners.values_list('email', flat=True)),
            fail_silently=True,
        )

        messages.success(request, 'Report submitted successfully!')
        return redirect('author_dashboard')

    return render(request, 'reports/submit_report.html')


# ─── CONVENER VIEWS ─────────────────────────────────────────────

@login_required
@role_required('convener')
def convener_dashboard(request):
    reports = Report.objects.all()
    reviewers = User.objects.filter(role='reviewer')

    stats = {
        'total': reports.count(),
        'submitted': reports.filter(status='submitted').count(),
        'under_review': reports.filter(status='under_review').count(),
        'accepted': reports.filter(status='accepted').count(),
        'revision': reports.filter(status='revision_required').count(),
        'rejected': reports.filter(status='rejected').count(),
    }

    return render(request, 'reports/convener_dashboard.html', {
        'reports': reports,
        'reviewers': reviewers,
        'stats': stats,
    })


@login_required
@role_required('convener')
def assign_reviewer(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    if request.method == 'POST':
        reviewer_id = request.POST.get('reviewer_id')
        reviewer = get_object_or_404(User, id=reviewer_id)

        report.assigned_reviewer = reviewer
        report.status = 'under_review'
        report.save()

        send_mail(
            subject=f'Review Assigned: {report.title}',
            message=f'You have been assigned to review "{report.title}".',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[reviewer.email],
            fail_silently=True,
        )

        messages.success(request, 'Reviewer assigned!')
        return redirect('convener_dashboard')

    reviewers = User.objects.filter(role='reviewer')
    return render(request, 'reports/assign_reviewer.html', {
        'report': report,
        'reviewers': reviewers,
    })


# 🔥 UPDATED FUNCTION (IMPORTANT)
@login_required
@role_required('convener')
def update_status(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')

        if new_status in dict(Report.STATUS_CHOICES):
            report.status = new_status
            report.save()

            # 🔥 IF REJECTED → SPECIAL EMAIL
            if new_status == 'rejected':
                send_mail(
                    subject=f'Report Rejected: {report.title}',
                    message=f'''Dear {report.author_name},

Your report "{report.title}" has been rejected.

Reviewer Feedback:
{report.reviewer_feedback or "No feedback provided."}

Regards,
ReportPortal Team
''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[report.author.email],
                    fail_silently=True,
                )

            else:
                send_mail(
                    subject=f'Report Status Updated: {report.title}',
                    message=f'''Dear {report.author_name},

Your report "{report.title}" status is now: {report.get_status_display()}.

Regards,
ReportPortal Team
''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[report.author.email],
                    fail_silently=True,
                )

            messages.success(request, 'Status updated!')

    return redirect('convener_dashboard')


@login_required
@role_required('reviewer')
def reviewer_dashboard(request):
    reports = Report.objects.filter(assigned_reviewer=request.user)
    return render(request, 'reports/reviewer_dashboard.html', {'reports': reports})
@login_required
@role_required('convener')
def report_detail_convener(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    reviewers = User.objects.filter(role='reviewer')

    return render(request, 'reports/report_detail_convener.html', {
        'report': report,
        'reviewers': reviewers,
    })

# 🔥 UPDATED FUNCTION
@login_required
@role_required('reviewer')
def submit_review(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    if request.method == 'POST':
        feedback = request.POST.get('feedback')
        decision = request.POST.get('decision')

        report.reviewer_feedback = feedback
        report.reviewed_at = timezone.now()
        report.status = decision
        report.save()

        # 🔥 IF REJECTED → EMAIL AUTHOR
        if decision == 'rejected':
            send_mail(
                subject=f'Report Rejected: {report.title}',
                message=f'''Dear {report.author_name},

Your report "{report.title}" has been rejected by the reviewer.

Feedback:
{feedback}

Regards,
ReportPortal Team
''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[report.author.email],
                fail_silently=True,
            )

        messages.success(request, 'Review submitted!')
        return redirect('reviewer_dashboard')

    return render(request, 'reports/submit_review.html', {'report': report})