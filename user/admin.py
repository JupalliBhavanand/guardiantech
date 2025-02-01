from django.contrib import admin
# Register your models here.
from django.contrib import admin
from .models import Manager, Employee, Attendance, OfferLetter, Payroll
from django.core.exceptions import ValidationError

# Register your models here
admin.site.register(Manager)
admin.site.register(Employee)
admin.site.register(OfferLetter)
admin.site.register(Payroll)



class AttendanceAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, change):
        if Attendance.objects.filter(employee=obj.employee, date=obj.date).exists():
            raise ValidationError(f"Attendance for {obj.employee.name} on {obj.date} already exists.")
        super().save_model(request, obj, change)

admin.site.register(Attendance, AttendanceAdmin)