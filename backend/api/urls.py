from django.urls import path
from .views import (
    analyze, 
    dashboard, 
    check_number, 
    region_stats, 
    register, 
    user_login, 
    check_auth, 
    user_logout, 
    admin_summary, 
    all_reports, 
    delete_report,
    make_admin
)

urlpatterns = [
    path('analyze/', analyze),
    path('dashboard/', dashboard),
    path('check/', check_number),
    path('regions/', region_stats),
    path('register/', register),
    path('login/', user_login),
    path('check-auth/', check_auth),
    path('logout/', user_logout),
    path('admin-summary/', admin_summary),
    path('all-reports/', all_reports),
    path('delete-report/<int:report_id>/', delete_report),
    path("make-admin/", make_admin),
]