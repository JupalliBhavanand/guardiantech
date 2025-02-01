from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import FreeTrialForm,ContactForm
from .models import FreeTrialRegistration, Contact


# Create your views here.
def index(request):
    return render(request, 'dashboard/main.html')

def contact(request):
    return render(request, 'dashboard/contactus.html')

def trial(request):
    return render(request, 'dashboard/freetrial.html')


def project(request):
    return render(request, 'dashboard/projects.html')

def detail1(request):
    return render(request, 'dashboard/detail1.html')

def detail2(request):
    return render(request, 'dashboard/detail2.html')

def detail3(request):
    return render(request, 'dashboard/detail3.html')

def learn1(request):
    return render(request, 'dashboard/learn1.html')

def learn2(request):
    return render(request, 'dashboard/learn2.html')

def learn3(request):
    return render(request, 'dashboard/learn3.html')

def learn4(request):
    return render(request, 'dashboard/learn4.html')



def free_trial_view(request):
    if request.method == 'POST':
        form = FreeTrialForm(request.POST)
        if form.is_valid():
            # Save form data to the database
            registration = form.save()

            # Redirect with a success message
            messages.success(request, "Your free trial registration has been submitted successfully.")
            return redirect('free_trial')
    else:
        form = FreeTrialForm()

    return render(request, 'dashboard/freetrial.html', {'form': form})



def registration_list_view(request):
    # Fetch all records from the FreeTrialRegistration model
    registrations = FreeTrialRegistration.objects.all()
    return render(request, 'dashboard/registration_list.html', {'registrations': registrations})


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()  # Save form data to the database
            return redirect('contact_success')  # Redirect to a success page
    else:
        form = ContactForm()
    return render(request, 'dashboard/contactus.html', {'form': form})

# Display submitted data
def contact_success(request):
    contacts = Contact.objects.all()  # Fetch all submitted contacts
    return render(request, 'dashboard/contact_success.html', {'contacts': contacts})

