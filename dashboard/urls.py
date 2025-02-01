from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='dashboard-index'),
    path('contact/', views.contact, name='contact'),
    path('trial/', views.trial, name='trial'),  # Add trailing slash here
    path('registrations/', views.registration_list_view, name='registration_list'),
    path('free-trial/', views.free_trial_view, name='free_trial'),
    path('connect/', views.contact_view, name='contact_view'),
    path('success/', views.contact_success, name='contact_success'),
    path('projects/', views.project, name='project'),
    path('project1/', views.detail1, name='detail1'),
    path('project2/', views.detail2, name='detail2'),
    path('project3/', views.detail3, name='detail3'),
    path('service1/', views.learn1, name='learn1'),
    path('service2/', views.learn2, name='learn2'),
    path('service3/', views.learn3, name='learn3'),
    path('service4/', views.learn4, name='learn4'),







]