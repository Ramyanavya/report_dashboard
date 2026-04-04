from django.urls import path
from reports.views import (
    author_dashboard, submit_report,
    convener_dashboard, assign_reviewer, update_status, report_detail_convener,
    reviewer_dashboard, submit_review,
)

urlpatterns = [
    # Author
    path('author/', author_dashboard, name='author_dashboard'),
    path('author/submit/', submit_report, name='submit_report'),

    # Convener
    path('convener/', convener_dashboard, name='convener_dashboard'),
    path('convener/assign/<int:report_id>/', assign_reviewer, name='assign_reviewer'),
    path('convener/status/<int:report_id>/', update_status, name='update_status'),

    # 🔥 ADD THIS LINE (IMPORTANT FIX)
    path('convener/report/<int:report_id>/', report_detail_convener, name='report_detail_convener'),

    # Reviewer
    path('reviewer/', reviewer_dashboard, name='reviewer_dashboard'),
    path('reviewer/review/<int:report_id>/', submit_review, name='submit_review'),
]