from datetime import datetime
from django.db.models import Q
from .models import Attendance

def calculate_monthly_attendance(employee, year=None, month=None):
    """
    Calculate the monthly attendance data for a specific employee.

    Args:
        employee: The employee object for whom attendance is being calculated.
        year: The year for the attendance (default is the current year).
        month: The month for the attendance (default is the current month).

    Returns:
        A dictionary containing total working days, attended days, and leaves for the month.
    """
    # Default to the current year and month if not provided
    if year is None or month is None:
        today = datetime.now()
        year = today.year
        month = today.month

    # Filter attendance records for the given employee and month
    attendance_records = Attendance.objects.filter(
        employee=employee,
        date__year=year,
        date__month=month
    )

    # Calculate the total working days (days in the attendance table for the month)
    total_working_days = attendance_records.count()

    # Count the number of attended days
    attended_days = attendance_records.filter(status='Present').count()

    # Calculate the leaves (total working days - attended days)
    leaves = total_working_days - attended_days

    return {
        'year': year,
        'month': month,
        'total_working_days': total_working_days,
        'attended_days': attended_days,
        'leaves': leaves
    }
