from django.urls import path
from .views import submit_report, my_reports, report_detail,all_reports, resolve_report, reject_report, review_report

urlpatterns = [
    path('submit/', submit_report, name='submit-report'),
    path('my-reports/', my_reports, name='my-reports'),
    path('<int:report_id>/', report_detail, name='report_detail'),


    path('all/', all_reports, name='all-reports'),
    path('<int:report_id>/review/', review_report, name='review-report'),
    path('<int:report_id>/resolve/',resolve_report, name='resolve-report'),
    path('<int:report_id>/reject/', reject_report, name='reject-report')
]