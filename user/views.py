from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Employee, Manager, Task, OfferLetter, Payroll,Attendance,Leave
from .forms import EmployeeForm, TaskForm, OfferLetterForm, PayrollForm,LeaveForm
from .forms import EmployeeForm,AttendanceForm,BannerForm
from django.contrib.auth.decorators import user_passes_test
from datetime import date
from django.contrib import messages
from dashboard.models import Contact
from django.core.exceptions import PermissionDenied
from datetime import datetime
from django.db.models import Q
from django.db.models import Count
from django.utils.timezone import now
from datetime import date, timedelta
from django.http import HttpResponse
from calendar import monthrange
from django.contrib.auth.models import User
from .utils import calculate_monthly_attendance  # Assuming you saved the attendance calculation logic in utils.py







# Create your views here.
def register(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully!')
            return redirect('user-login')  # Redirect to login page or desired URL
    else:
        form = CreateUserForm()
    return render(request, 'user/register.html', {'form': form})
@login_required
def mark_task_completed(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    # Ensure only the assigned employee can mark the task as completed
    if hasattr(request.user, 'employee') and task.assigned_to == request.user.employee:
        task.completed = True  # Mark as completed
        task.save()  # Save the changes
        messages.success(request, f"Task '{task.title}' has been marked as completed.")
    else:
        messages.error(request, "You are not authorized to complete this task.")

    return redirect('profile')  # Redirect back to the profile page






@login_required
def profile(request):
    employee = None  # Initialize employee to None to avoid reference errors
    attendance_data = None  # Initialize attendance data to None

    if hasattr(request.user, 'employee'):
        # Employee-specific profile
        profile = request.user.employee
        employee = request.user.employee

        # Calculate attendance for the logged-in employee
        today = datetime.now()
        attendance_data = calculate_monthly_attendance(employee, year=today.year, month=today.month)

        tasks = Task.objects.filter(assigned_to=profile, completed=False)  # Only incomplete tasks
        completed_tasks = Task.objects.filter(assigned_to=profile, completed=True)  # Completed tasks
        offer_letters = OfferLetter.objects.filter(employee=profile)
        payrolls = Payroll.objects.filter(employee=profile)

    elif hasattr(request.user, 'manager'):
        # Manager-specific profile
        profile = request.user.manager

        # Managers do not have specific attendance, but you can extend logic to show team attendance
        # Aggregate attendance data for all managed employees
        attendance_data = Attendance.objects.values('employee__user__username').annotate(
            total_working_days=Count('id'),
            attended_days=Count('id', filter=Q(status='Present')),
            leaves=Count('id', filter=Q(status='Absent'))
        )

        tasks = Task.objects.filter(completed=False)  # Managers can view all incomplete tasks
        completed_tasks = Task.objects.filter(completed=True)  # All completed tasks for managers
        offer_letters = OfferLetter.objects.all()  # Managers can view all offer letters
        payrolls = Payroll.objects.all()  # Managers can view all payrolls
    else:
        return redirect('unauthorized')  # Redirect if user is neither employee nor manager

    return render(request, 'user/profile.html', {
        'employee': employee,
        'profile': profile,
        'tasks': tasks,  # Incomplete tasks
        'completed_tasks': completed_tasks,  # Completed tasks
        'offer_letters': offer_letters,
        'payrolls': payrolls,
        'is_manager': hasattr(request.user, 'manager'),
        'attendance_data': attendance_data,  # Attendance data
    })


def edit_personal_details(request):
    # Check if the user is an employee or manager
    if hasattr(request.user, 'employee'):
        profile = request.user.employee
    elif hasattr(request.user, 'manager'):
        profile = request.user.manager
    else:
        return redirect('unauthorized')  # Handle unauthorized users

    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to the profile page after saving
    else:
        form = EmployeeForm(instance=profile)

    return render(request, 'user/edit_personal_details.html', {'form': form})

def is_manager(user):
    return hasattr(user, 'manager')  # Check if user has a manager profile


# Employee View: Edit personal details
@login_required
def edit_employee_details(request):
    employee = get_object_or_404(Employee, user=request.user)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('employee_dashboard')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'employee/edit_details.html', {'form': form})


# Manager View: Assign tasks
@login_required
@user_passes_test(is_manager, login_url='unauthorized')
def assign_task(request):
    # Fetch all employees to populate the dropdown
    employees = Employee.objects.all()

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)  # Don't save to the database yet
            # Get the Manager object associated with the current user
            manager = get_object_or_404(Manager, user=request.user)
            task.assigned_by = manager  # Set the current manager as the one who assigned the task
            task.save()  # Save to the database
            return redirect('profile')  # Redirect to the user profile or another appropriate page
    else:
        form = TaskForm()

    return render(request, 'manager/assign_task.html', {'form': form, 'employees': employees})


# Manager View: Issue offer letter



# Manager View: Handle Payroll
@login_required
@user_passes_test(is_manager, login_url='unauthorized')
def handle_payroll(request):
    if not hasattr(request.user, 'manager'):
        return redirect('unauthorized')  # Only managers can handle payroll
    if request.method == 'POST':
        form = PayrollForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manager_dashboard')
    else:
        form = PayrollForm()
    return render(request, 'manager/handle_payroll.html', {'form': form})




@login_required
def employee_dashboard(request):
    # Check if the logged-in user is an employee
    if hasattr(request.user, 'employee'):
        employee = get_object_or_404(Employee, user=request.user)
        profile = request.user.employee  # Use employee-specific profile
    elif hasattr(request.user, 'manager'):
        profile = request.user.manager  # Use manager-specific profile
        employee = None  # Manager doesn't need employee data
    else:
        return redirect('unauthorized')  # Handle unauthorized access

    # Calculate attendance, tasks, offer letters, and payrolls for the employee
    if employee:
        attendance_days = Attendance.objects.filter(employee=employee, status='present').count()
        tasks = Task.objects.filter(assigned_to=employee)
        offer_letters = OfferLetter.objects.filter(employee=employee)
        payrolls = Payroll.objects.filter(employee=employee)
    else:
        attendance_days, tasks, offer_letters, payrolls = 0, [], [], []  # Managers don't have these

    total_working_days = 28  # Example logic
    total_leaves = 0  # Logic for leaves
    total_awards = 0  # Logic for awards

    # Handle the form for editing personal details
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('employee_dashboard')
    else:
        form = EmployeeForm(instance=profile)



    context = {
        'profile': profile,
        'employee': employee,
        'attendance_days': attendance_days,
        'total_working_days': total_working_days,
        'total_leaves': total_leaves,
        'total_awards': total_awards,
        'tasks': tasks,
        'offer_letters': offer_letters,
        'payrolls': payrolls,
        'form': form,
    }

    return render(request, 'user/profile.html', context)



@login_required
def manager_dashboard(request):
    if not hasattr(request.user, 'manager'):
        return redirect('unauthorized')  # Ensure only managers can access this

    # Get all employees the manager oversees
    employees = Employee.objects.filter(manager__user=request.user)

    context = {
        'employees': employees,
    }
    return render(request, 'manager/dashboard.html', context)


from django.shortcuts import render

def unauthorized(request):
    return render(request, 'user/unauthorized.html')



# View for submitting attendance
@login_required
def submit_attendance(request, attendance_id=None):
    if hasattr(request.user, 'employee'):
        employee = request.user.employee  # Get the employee instance for a logged-in employee
    elif request.user.is_superuser:
        employee = None  # Superuser can modify any attendance record
    else:
        return redirect('unauthorized')

    # Check if it's an edit or a new attendance entry
    if attendance_id and request.user.is_superuser:
        # Superuser editing an existing attendance record
        attendance = get_object_or_404(Attendance, pk=attendance_id)
        form = AttendanceForm(request.POST or None, instance=attendance)
    else:
        # Employee marking their own attendance
        form = AttendanceForm(request.POST or None)
    
    if request.method == 'POST':
        if form.is_valid():
            attendance = form.save(commit=False)
            if employee:
                # Only employees can mark their own attendance
                attendance.employee = employee
            attendance.date = datetime.today().date()  # Automatically set today's date
            attendance.save()
            return redirect('view_attendance')  # Redirect to attendance viewing page

    return render(request, 'employee/submit_attendance.html', {
        'form': form,
        'is_edit': attendance_id is not None
    })

@login_required
def search_attendance(request):
    date = request.GET.get('date')
    month = request.GET.get('month')
    year = request.GET.get('year')
    attendance_records = Attendance.objects.all()

    if date:
        attendance_records = attendance_records.filter(date=date)
    if month:
        attendance_records = attendance_records.filter(date__month=month)
    if year:
        attendance_records = attendance_records.filter(date__year=year)

    context = {
        'attendance_records': attendance_records,
    }
    return render(request, 'your_template_name.html', context)


# View for displaying the dashboard with attendance records
@login_required
def view_attendance(request):
    if hasattr(request.user, 'employee'):
        # Employee viewing their own attendance
        employee = request.user.employee
        attendance_records = Attendance.objects.filter(employee=employee).order_by('-date')
    elif request.user.is_superuser:
        # Superuser viewing all attendance records
        employee = None
        attendance_records = Attendance.objects.all().order_by('-date')
    else:
        return redirect('unauthorized')

    # Optional filtering by month
    month = request.GET.get('month')
    if month:
        try:
            # Assuming the month format is YYYY-MM
            year, month = map(int, month.split('-'))
            attendance_records = attendance_records.filter(date__year=year, date__month=month)
        except ValueError:
            pass  # Ignore invalid month formats

    return render(request, 'employee/view_attendance.html', {
        'attendance_records': attendance_records,
        'employee': employee
    })

def is_manager(user):
    return user.groups.filter(name='Manager').exists() or user.is_superuser

# Upload offer letter view for managers
@user_passes_test(is_manager)
def upload_offer_letter(request):
    if request.method == 'POST':
        form = OfferLetterForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Offer letter uploaded successfully!')
            return redirect('upload_offer_letter')
    else:
        form = OfferLetterForm()

    return render(request, 'user/upload_offer_letter.html', {'form': form})

# Upload payroll view for managers
@user_passes_test(is_manager)
def upload_payroll(request):
    if request.method == 'POST':
        form = PayrollForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Payroll uploaded successfully!')
                return redirect('upload_payroll')
            except Exception as e:
                messages.error(request, str(e))
    else:
        form = PayrollForm()

    return render(request, 'user/upload_payroll.html', {'form': form})


def search_payrolls(request):
    month = request.GET.get('month')
    year = request.GET.get('year')
    payrolls = Payroll.objects.all()

    if month:
        payrolls = payrolls.filter(date__month=month)
    if year:
        payrolls = payrolls.filter(date__year=year)

    context = {
        'payrolls': payrolls,
    }
    return render(request, 'your_template_name.html', context)
# View for employees to download their offer letter
@login_required
def view_offer_letter(request):
    offer_letter = get_object_or_404(OfferLetter, employee=request.user.employee)
    return render(request, 'user/view_offer_letter.html', {'offer_letter': offer_letter})

# View for employees to view and download their payrolls
@login_required
def view_payrolls(request):
    payrolls = Payroll.objects.filter(employee=request.user.employee).order_by('-month')
    query_month = request.GET.get('month')  # Expected format: yyyy-mm

    if query_month:
        # Filter payrolls by exact match on the month field
        payrolls = payrolls.filter(month=query_month)
    # Adjust based on how the 'month' field is stored
    return render(request, 'user/view_payrolls.html',{'payrolls': payrolls})
   


def not_authorized(request):
    return render(request, 'not_authorized.html')

@login_required
def view_contact_forms(request):
    # Ensure only employees can access this view
    try:
        employee = request.user.employee  # Check if the user has an associated employee profile
    except Employee.DoesNotExist:
        return redirect('not_authorized')  # Redirect unauthorized users

    # Retrieve search query from the request
    query = request.GET.get('query', '')

    # Filter contacts based on the search query
    if query:
        contacts = Contact.objects.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(message__icontains=query)
        )
    else:
        contacts = Contact.objects.all()

    # Track new contacts since last visit
    total_contacts = Contact.objects.count()
    last_seen_contact_count = request.session.get('last_seen_contact_count', 0)
    new_contacts_count = max(0, total_contacts - last_seen_contact_count)

    # Update session with the latest contact count
    request.session['last_seen_contact_count'] = total_contacts

    # Notify user about the number of new contacts
    if new_contacts_count > 0:
        messages.info(request, f"You have {new_contacts_count} new contact(s) since your last visit!")

    context = {
        'contacts': contacts,
        'query': query,
        'new_contacts_count': new_contacts_count,
    }

    return render(request, 'user/contacts.html', context)  # Create a 'not_authorized' page or redirect them somewhere else
    


def is_superuser(user):
    return user.is_superuser
    

@login_required
@user_passes_test(lambda u: u.is_superuser, login_url='unauthorized')  # Restrict to superusers
def issue_offer_letter(request):
    existing_offer_letter = None

    if request.method == 'POST':
        form = OfferLetterForm(request.POST, request.FILES)
        if form.is_valid():
            employee = form.cleaned_data['employee']
            # Check if an offer letter already exists for this employee
            if OfferLetter.objects.filter(employee=employee).exists():
                existing_offer_letter = employee
                messages.error(request, f"An offer letter already exists for {employee.user.get_full_name()}.")
            else:
                try:
                    offer_letter = form.save(commit=False)
                    # Ensure the user has a manager role
                    if hasattr(request.user, 'manager'):
                        offer_letter.issued_by = request.user.manager
                    else:
                        messages.error(request, "You are not authorized to issue an offer letter.")
                        return redirect('unauthorized')

                    offer_letter.save()
                    messages.success(request, f"Offer letter issued successfully for {employee.user.get_full_name()}!")
                    return redirect('view_offer_letters')
                except Exception as e:
                    messages.error(request, f"Error saving offer letter: {e}")
        else:
            messages.error(request, "Please correct the errors in the form.")
            print(form.errors)  # Debugging: print form errors
    else:
        form = OfferLetterForm()

    return render(request, 'employee/issue_offer_letter.html', {
        'form': form,
        'existing_offer_letter': existing_offer_letter,
    })



@login_required
def view_offer_letters(request):
    if hasattr(request.user, 'employee'):
        # Employee can only view their own offer letters
        offer_letters = OfferLetter.objects.filter(employee=request.user.employee)
    elif request.user.is_superuser:
        # Superuser can view all offer letters
        offer_letters = OfferLetter.objects.all()
    else:
        return redirect('unauthorized')

    return render(request, 'employee/view_offer_letters.html', {'offer_letters': offer_letters})





def is_manager(user):
    return hasattr(user, 'manager')

@user_passes_test(is_manager)
def employee_list(request):
    search_query = request.GET.get('search', '')  # Get the search query from the URL
    if search_query:
        employees = Employee.objects.filter(
            Q(user__first_name__icontains=search_query) |  # Match first name
            Q(user__last_name__icontains=search_query) |   # Match last name
            Q(user__username__icontains=search_query)      # Match username
        )
    else:
        employees = Employee.objects.all()  # Default: Show all employees if no search query

    return render(request, 'manager/employee_list.html', {'employees': employees, 'search_query': search_query})

@user_passes_test(is_manager)
def employee_detail(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    attendance_records = Attendance.objects.filter(employee=employee)
    offer_letters = OfferLetter.objects.filter(employee=employee)
    payrolls = Payroll.objects.filter(employee=employee)
    tasks = Task.objects.filter(assigned_to=employee)
    completed_tasks = Task.objects.filter(assigned_to=employee, completed=True)  # Completed tasks


    context = {
        'employee': employee,
        'attendance_records': attendance_records,
        'offer_letters': offer_letters,
        'payrolls': payrolls,
        'tasks': tasks,
        'completed_tasks': completed_tasks, 
    }
    return render(request, 'manager/employee_detail.html', context)


@user_passes_test(is_manager)
def edit_attendance(request, attendance_id):
    attendance_record = get_object_or_404(Attendance, id=attendance_id)
    
    if request.method == 'POST':
        form = AttendanceForm(request.POST, instance=attendance_record)
        if form.is_valid():
            form.save()
            messages.success(request, "Attendance record updated successfully.")
            return redirect('employee_detail', employee_id=attendance_record.employee.id)
    else:
        form = AttendanceForm(instance=attendance_record)

    return render(request, 'manager/edit_attendance.html', {'form': form, 'attendance': attendance_record})



@user_passes_test(is_manager)
def delete_attendance(request, attendance_id):
    attendance_record = get_object_or_404(Attendance, id=attendance_id)
    employee_id = attendance_record.employee.id  # Store employee ID for redirection
    attendance_record.delete()
    messages.success(request, "Attendance record deleted successfully.")
    return redirect('employee_attendance', employee_id=employee_id)  # Redirect to employee detail page



@user_passes_test(is_manager)
def delete_offer_letter(request, offer_letter_id):
    offer_letter = get_object_or_404(OfferLetter, id=offer_letter_id)
    employee_id = offer_letter.employee.id  # Store employee ID for redirection
    offer_letter.delete()
    messages.success(request, "Offer letter deleted successfully.")
    return redirect('employee_offer_letters', employee_id=employee_id) 




@user_passes_test(is_manager)
def delete_payroll(request, payroll_id):
    payroll = get_object_or_404(Payroll, id=payroll_id)
    employee_id = payroll.employee.id  # Store employee ID for redirection
    payroll.delete()
    messages.success(request, "Payroll deleted successfully.")
    return redirect('employee_payrolls', employee_id=employee_id)  #


@user_passes_test(is_manager)
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Task updated successfully.")
            return redirect('employee_detail', employee_id=task.assigned_to.id)  # Redirect to employee detail page
    else:
        form = TaskForm(instance=task)

    context = {
        'form': form,
        'task': task
    }
    return render(request, 'user/edit_task.html', context)


@user_passes_test(is_manager)
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    assigned_employee_id = task.assigned_to.id  # Capture employee ID for redirection
    task.delete()
    messages.success(request, "Task deleted successfully.")
    return redirect('employee_assigned_tasks', employee_id=assigned_employee_id)


def checking(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    attendance_records = Attendance.objects.filter(employee=employee)
    context = {
        'employee': employee,
        'attendance_records': attendance_records,
    }
    return render(request, 'manager/full_attendance.html', context)



@login_required
def search_attendance(request):
    date = request.GET.get('date')
    month = request.GET.get('month')
    year = request.GET.get('year')
    
    # Filter based on the search criteria
    attendance_records = Attendance.objects.all()
    if date:
        attendance_records = attendance_records.filter(date=date)
    if month:
        attendance_records = attendance_records.filter(date__month=month)
    if year:
        attendance_records = attendance_records.filter(date__year=year)

    context = {
        'attendance_records': attendance_records
    }
    
    # Replace 'employee/attendance_search_results.html' with the actual path to your results template
    return render(request, 'manager/employee_detail.html', context)



@login_required
def search_tasks(request):
    tasks = Task.objects.filter(assigned_to=request.user.employee).order_by('due_date')

    # Get search parameters
    query_name = request.GET.get('title', '')
    query_date = request.GET.get('due_date', '')

    if query_name:
        tasks = tasks.filter(title__icontains=query_name)
    if query_date:
        tasks = tasks.filter(due_date=query_date)

    context = {
        'tasks': tasks,
        'query_name': query_name,
        'query_date': query_date,
    }
    return render(request, 'manager/employee_detail.html', context)

@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('search_tasks')  # Redirect to the task list/search page
    else:
        form = TaskForm(instance=task)

    context = {
        'form': form,
        'task': task,
    }
    return render(request, 'user/edit_task.html', context)






@login_required
def employee_overview(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    return render(request, 'manager/employee_detail.html', {'employee': employee})


@login_required
def personal_details(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    return render(request, 'manager/personal_details.html', {'employee': employee})


@login_required
def search_attendance(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    attendance_records = Attendance.objects.filter(employee=employee).order_by('-date')

    # Get the month filter from the request
    month = request.GET.get('month')
    if month:
        try:
            # Extract year and month from the `month` input (e.g., "2024-11")
            year, month = map(int, month.split('-'))
            attendance_records = attendance_records.filter(date__year=year, date__month=month)
        except ValueError:
            messages.error(request, "Invalid date format. Please use YYYY-MM format.")

    return render(request, 'manager/attendance.html', {
        'employee': employee,
        'attendance_records': attendance_records
    })

@login_required
def attendance(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    attendance_records = Attendance.objects.filter(employee=employee).order_by('-date')

    # Search attendance by month
    month = request.GET.get('month')
    if month:
        try:
            # Parse the month to filter records (format: YYYY-MM)
            year, month = map(int, month.split('-'))
            attendance_records = attendance_records.filter(date__year=year, date__month=month)
        except ValueError:
            messages.error(request, "Invalid month format. Please use YYYY-MM.")

    return render(
        request,
        'manager/attendance.html',
        {
            'employee': employee,
            'attendance_records': attendance_records,
        }
    )

@login_required
def payrolls(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    payrolls = Payroll.objects.filter(employee=employee).order_by('-month')

    query_month = request.GET.get('month')  # Expected format: yyyy-mm

    if query_month:
        try:
            payrolls = payrolls.filter(month__startswith=query_month)  # Use string filtering for CharField
        except ValueError:
            messages.error(request, "Invalid month format. Please use 'YYYY-MM'.")

    context = {
        'employee': employee,
        'payrolls': payrolls,
        'query_month': query_month,
    }
    return render(request, 'manager/payrolls.html', context)



@login_required
def offer_letters(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    offer_letters = OfferLetter.objects.filter(employee=employee)
    return render(request, 'manager/offer_letters.html', {'employee': employee, 'offer_letters': offer_letters})


@login_required
def assigned_tasks(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    tasks = Task.objects.filter(assigned_to=employee, completed=False)

    # Get search parameters
    query_title = request.GET.get('title', '')
    query_due_date = request.GET.get('due_date', '')

    # Filter by title and due date if search parameters are provided
    if query_title:
        tasks = tasks.filter(title__icontains=query_title)
    if query_due_date:
        tasks = tasks.filter(due_date=query_due_date)

    context = {
        'employee': employee,
        'tasks': tasks,
        'query_title': query_title,
        'query_due_date': query_due_date,
    }
    return render(request, 'manager/assigned_tasks.html', context)




@login_required
def completed_tasks(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)

    # Get all completed tasks for the employee
    tasks = Task.objects.filter(assigned_to=employee, completed=True).order_by('-due_date')

    # Get search parameters
    query_title = request.GET.get('title', '')
    query_date = request.GET.get('completed_date', '')

    # Filter by title and completed date if search parameters are provided
    if query_title:
        tasks = tasks.filter(title__icontains=query_title)
    if query_date:
        tasks = tasks.filter(updated_at__date=query_date)

    context = {
        'employee': employee,
        'tasks': tasks,
        'query_title': query_title,
        'query_date': query_date,
    }
    return render(request, 'manager/completed_tasks.html', context)





@login_required
def banner(request):
    employee = request.user.employee  # Assuming Employee is linked to the user
    if request.method == 'POST' and 'banner' in request.FILES:
        employee.banner = request.FILES['banner']
        employee.save()
        messages.success(request, 'Your banner has been updated successfully!')
        return redirect('profile')  # Redirect to the profile page after updating
    else:
        messages.error(request, 'There was an error uploading your banner. Please try again.')
    return redirect('profile')  # Fallback redirect



@login_required
def apply_leave(request):
    try:
        # Ensure the logged-in user has an associated employee profile
        employee = request.user.employee  

        # Get the superuser (admin) who will handle leave approvals
        superuser = User.objects.filter(is_superuser=True).first()
        if not superuser:
            return render(request, 'not_authorized.html', {
                'message': 'No superuser found to handle leave requests. Please contact the system administrator.'
            })
        
        if request.method == 'POST':
            form = LeaveForm(request.POST)
            if form.is_valid():
                leave = form.save(commit=False)
                leave.employee = employee
                leave.manager = superuser.manager  # Assign the superuser as the manager handling the leave
                leave.save()
                return redirect('employee_dashboard')  # Redirect to employee dashboard
        else:
            form = LeaveForm()
        return render(request, 'user/apply_leave.html', {'form': form})
    except AttributeError:
        # If the user does not have an associated employee profile
        return render(request, 'not_authorized.html', {
            'message': 'You do not have an associated employee profile. Please contact the admin.'
        })

# Manager reviews leave requests

@login_required
@user_passes_test(lambda u: u.is_superuser, login_url='/error/')  # Restrict access to superusers
def review_leave(request):
    # Superuser reviews all pending leave requests
    leave_requests = Leave.objects.filter(status='Pending')
    return render(request, 'user/review_leave.html', {'leave_requests': leave_requests})
# Manager approves/rejects leave
@login_required
@user_passes_test(lambda u: u.is_superuser, login_url='/error/')  # Restrict access to superusers
def update_leave_status(request, leave_id, status):
    # Superuser approves/rejects leave requests
    leave = get_object_or_404(Leave, id=leave_id)
    leave.status = status
    leave.save()
    return redirect('review_leave')  # Redirect to superuser's leave review page


@login_required
def employee_leave_history(request):
    # Fetch the leave history for the logged-in employee
    employee = request.user.employee
    leave_requests = Leave.objects.filter(employee=employee).order_by('-applied_on')  # Order by most recent
    return render(request, 'employee/employee_leave_history.html', {'leave_requests': leave_requests})
