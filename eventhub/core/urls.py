from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('events/', views.event_list_view, name='event_list'),
    path('events/<int:pk>/', views.event_detail_view, name='event_detail'),
    path('events/create/', views.event_create_view, name='event_create'),
    path('events/<int:pk>/register/', views.event_register_view, name='event_register'),
    path('my-registrations/', views.my_registrations_view, name='my_registrations'),
    path('host/events/<int:pk>/registrations/', views.admin_event_registrations_view, name='admin_event_registrations'),
    path('host/my-events/', views.admin_my_events_view, name='admin_my_events'),
    path('host/events/<int:pk>/delete/', views.delete_event, name='delete_event'),
    path('host/events/<int:pk>/edit/', views.edit_event, name='edit_event'),
    path('host/event/<int:pk>/registrations/export/', views.export_event_registrations_csv, name='export_event_registrations_csv'),


]
