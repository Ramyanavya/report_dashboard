from django.db import models
from accounts.models import User


class Report(models.Model):
    REPORT_TYPE_CHOICES = [
        ('technical', 'Technical Report'),
        ('verification', 'Verification Report'),
        ('research', 'Research Report'),
    ]
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('revision_required', 'Revision Required'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    report_type = models.CharField(max_length=30, choices=REPORT_TYPE_CHOICES)
    title = models.CharField(max_length=300)
    author_name = models.CharField(max_length=200)
    contributors = models.TextField(blank=True, help_text='Comma-separated contributor names')
    abstract = models.TextField()
    keywords = models.CharField(max_length=500)
    plagiarism_doc = models.FileField(upload_to='plagiarism/', null=True, blank=True)
    paper_doc = models.FileField(upload_to='papers/')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='submitted')
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    convener_notes = models.TextField(blank=True)
    assigned_reviewer = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_reports'
    )
    reviewer_feedback = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.title} by {self.author_name} [{self.get_status_display()}]"

    def get_status_color(self):
        colors = {
            'submitted': 'blue',
            'under_review': 'amber',
            'revision_required': 'coral',
            'accepted': 'green',
            'rejected': 'red',
        }
        return colors.get(self.status, 'gray')
