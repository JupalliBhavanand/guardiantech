from django.urls import path
from . import views


urlpatterns = [
    path('edit/', views.edit_employee_details, name='edit_employee_details'),
    path('manager/assign-task/', views.assign_task, name='assign_task'),
    path('manager/issue-offer-letter/', views.issue_offer_letter, name='issue_offer_letter'),
    path('manager/handle-payroll/', views.handle_payroll, name='handle_payroll'),
    path('employee/dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('manager/dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('submit-attendance/', views.submit_attendance, name='submit_attendance'),
    path('attendance/', views.attendance, name='dashboard'),

]
