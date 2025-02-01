"""
URL configuration for consultency project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from user import views as user_view  # Import views from your user app
from django.conf import settings
from django.conf.urls.static import static
from user.forms import CustomAuthenticationForm

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),  # Assuming you have a dashboard app with its own urls.py

    # User management URLs
    path('register/', user_view.register, name='user-register'),
    path('profile/', user_view.profile, name='profile'),
    path('edit-personal-details/', user_view.edit_personal_details, name='edit_personal_details'),
   
    path('login/', auth_views.LoginView.as_view(template_name='user/login.html',authentication_form=CustomAuthenticationForm), name='user-login'),
    path('logout/', auth_views.LogoutView.as_view(), name='user-logout'),

    # Employee-specific URLs
    path('edit/', user_view.edit_employee_details, name='edit_employee_details'),
    path('employee/dashboard/', user_view.employee_dashboard, name='employee_dashboard'),

    # Manager-specific URLs
    path('assign-task/', user_view.assign_task, name='assign_task'),
    path('issue-offer-letter/', user_view.issue_offer_letter, name='issue_offer_letter'),
    path('handle-payroll/', user_view.handle_payroll, name='handle_payroll'),
    path('manager/dashboard/', user_view.manager_dashboard, name='manager_dashboard'),
    path('unauthorized/', user_view.unauthorized, name='unauthorized'),
    path('upload-offer-letter/', user_view.upload_offer_letter, name='upload_offer_letter'),
    path('upload-payroll/', user_view.upload_payroll, name='upload_payroll'),
    path('view-payrolls/', user_view.view_payrolls, name='view_payrolls'),
    path('view-contacts/', user_view.view_contact_forms, name='view_contact_forms'),
    path('not-authorized/', user_view.not_authorized, name='not_authorized'),
    path('attendance/', user_view.view_attendance, name='view_attendance'),
    path('attendance/submit/', user_view.submit_attendance, name='submit_attendance'),
    path('attendance/edit/<int:attendance_id>/', user_view.submit_attendance, name='edit_attendance'),
    path('issue-offer-letter/', user_view.issue_offer_letter, name='issue_offer_letter'),
    path('offer-letters/', user_view.view_offer_letters, name='view_offer_letter'),
    path('employees/', user_view.employee_list, name='employee_list'),
    path('employee/<int:employee_id>/', user_view.employee_detail, name='employee_detail'),
    path('edit-attendance/<int:attendance_id>/', user_view.edit_attendance, name='edit_attendance'),
    path('delete-attendance/<int:attendance_id>/', user_view.delete_attendance, name='delete_attendance'),
    path('delete-offer-letter/<int:offer_letter_id>/', user_view.delete_offer_letter, name='delete_offer_letter'),
    path('delete-payroll/<int:payroll_id>/', user_view.delete_payroll, name='delete_payroll'),
    path('edit-task/<int:task_id>/', user_view.edit_task, name='edit_task'),
    path('delete-task/<int:task_id>/', user_view.delete_task, name='delete_task'),
    path('search-attendance/', user_view.search_attendance, name='search_attendance'),
    path('search-payrolls/', user_view.search_payrolls, name='search_payrolls'),
    path('employee/<int:employee_id>/', user_view.employee_detail, name='employee_detail'),
    path('search-tasks/', user_view.search_tasks, name='search_tasks'),
    path('tasks/<int:task_id>/complete/', user_view.mark_task_completed, name='mark_task_completed'),
    path('employee/<int:employee_id>/', user_view.employee_overview, name='employee_overview'),
    path('employee/<int:employee_id>/personal-details/', user_view.personal_details, name='employee_personal_details'),
    path('employee/<int:employee_id>/attendance/', user_view.attendance, name='employee_attendance'),
    path('employee/<int:employee_id>/payrolls/', user_view.payrolls, name='employee_payrolls'),
    path('employee/<int:employee_id>/offer-letters/', user_view.offer_letters, name='employee_offer_letters'),
    path('employee/<int:employee_id>/assigned-tasks/', user_view.assigned_tasks, name='employee_assigned_tasks'),
    path('employee/<int:employee_id>/completed-tasks/', user_view.completed_tasks, name='employee_completed_tasks'),
    path('employee/<int:employee_id>/attendance/search/', user_view.search_attendance, name='search_attendance'),
    path('edit-banner/', user_view.banner, name='edit'),
    path('apply-leave/', user_view.apply_leave, name='apply_leave'),
    path('review-leave/', user_view.review_leave, name='review_leave'),
    path('update-leave/<int:leave_id>/<str:status>/', user_view.update_leave_status, name='update_leave_status'),
    path('leave-history/', user_view.employee_leave_history, name='employee_leave_history'),









]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Static and media file handling during development

