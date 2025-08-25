from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('group/<int:group_id>/', views.group_detail, name='group_detail'),
    path('group/<int:group_id>/add_expense/', views.add_expense, name='add_expense'),
    path('group/<int:group_id>/delete/', views.group_delete, name='group_delete'),
    path('create_group/', views.create_group, name='create_group'),
    path('profile/', views.profile_update, name='profile_update'),
    path('send-reminder/<int:group_id>/<int:user_id>/', views.send_reminder_email, name='send_reminder_email'),
]
