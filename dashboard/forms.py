from django import forms
from .models import FreeTrialRegistration, Contact

class FreeTrialForm(forms.ModelForm):
    class Meta:
        model = FreeTrialRegistration
        fields = ['name', 'email', 'phone']

from django import forms
from .models import Contact

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter your name', 'required': True}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email', 'required': True}),
            'message': forms.Textarea(attrs={'placeholder': 'Enter your message'}),
        }