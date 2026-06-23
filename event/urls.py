from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('type/<slug:category_slug>/', views.event_list, name='event_list_by_type'),
    path('event/<int:pk>/', views.event_detail, name='event_detail'),
    path('register/<int:event_id>/', views.register_event, name='register_event'),
    path('pay/<int:event_id>/', views.event_payment, name='event_payment'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
]
