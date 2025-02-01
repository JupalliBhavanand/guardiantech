from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

# Role-based system: employee and manager
class Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100, null=True)

    def __str__(self):
        return f"Manager: {self.user.username}"

    def employee_count(self):
        return Employee.objects.filter(manager=self).count()

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    manager = models.ForeignKey(Manager, on_delete=models.SET_NULL, null=True, blank=True)
    father_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True)
    gender = models.CharField(max_length=10)
    phone = models.CharField(max_length=15, validators=[RegexValidator(r'^\d{10,15}$', 'Enter a valid phone number')])
    email = models.EmailField(unique=True)  # Ensure email is unique
    local_address = models.CharField(max_length=255)
    permanent_address = models.CharField(max_length=255)
    department = models.CharField(max_length=50)
    employee_id = models.CharField(max_length=10, unique=True)  # Ensure employee ID is unique
    photo = models.ImageField(upload_to='employee_photos/', default='employee_photos/avatar.jpg', null=True, blank=True)
    banner = models.ImageField(upload_to='employee_banner/',null=True, blank=True)


    def __str__(self):
        return f"Employee: {self.user.username}"

class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[('Present', 'Present'), ('Absent', 'Absent')])
    check_in_time = models.TimeField(null=True, blank=True)  # Allow NULL values
    check_out_time = models.TimeField(null=True, blank=True)  

    class Meta:
        unique_together = ('employee', 'date')  # Ensures that an employee can only mark attendance once per day

    def clean(self):
        # Ensure check-out time is after check-in time
        if self.check_in_time is not None and self.check_out_time is not None:
            if self.check_out_time <= self.check_in_time:
                raise ValidationError("Check-out time must be after check-in time.")
            
    def save(self, *args, **kwargs):
        # Ensure that attendance is only marked once per day for the same employee
        if Attendance.objects.filter(employee=self.employee, date=self.date).exists():
            raise ValidationError(f"Attendance for {self.employee.user.username} on {self.date} already exists.")
        super().save(*args, **kwargs)


   

# Task assigned by managers to employees
class Task(models.Model):
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High')
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    assigned_to = models.ForeignKey(Employee, on_delete=models.CASCADE)
    assigned_by = models.ForeignKey(Manager, on_delete=models.CASCADE)
    due_date = models.DateField()
    priority = models.CharField(max_length=6, choices=PRIORITY_CHOICES, default='Medium')  # Add priority field
    completed = models.BooleanField(default=False)  # Track if the task is completed

    def __str__(self):
        return f"Task: {self.title} for {self.assigned_to.user.username}"

# Offer letters issued by the manager
class OfferLetter(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    issued_by = models.ForeignKey(Manager, on_delete=models.CASCADE)
    offer_details = models.TextField()
    date_issued = models.DateField(auto_now_add=True)
    file = models.FileField(upload_to='offer_letters/', null=True, blank=True)  # File upload location

    def __str__(self):
        return f"Offer Letter for {self.employee.user.username}"

# Monthly payroll for employees
class Payroll(models.Model):
    

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    issued_by = models.ForeignKey(Manager, on_delete=models.CASCADE)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    date_issued = models.DateField(auto_now_add=True)
    month = models.CharField(max_length=7, null=True, blank=True)  # Restrict to valid month options
    file = models.FileField(upload_to='payrolls/', null=True, blank=True)  # File upload location

    class Meta:
        unique_together = ('employee', 'month')

    def __str__(self):
        return f"Payroll for {self.employee.user.username} on {self.date_issued}"

class Leave(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    applied_on = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Leave ({self.status}) for {self.employee.user.username} from {self.start_date} to {self.end_date}"

    def clean(self):
        # Ensure that the end date is after the start date
        if self.start_date > self.end_date:
            raise ValidationError("End date cannot be before start date.")