from django.urls import path
from django.contrib.auth.views import LoginView
from django.contrib.auth import views as auth_views
from . import views
from .forms import StrictPasswordResetForm, UsernameOrEmailPasswordResetForm, UsernameOrEmailAuthenticationForm

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('tests/', views.test_rates, name='test_rates'),
    path('projects/', views.projects, name='projects'),
    path('experts/', views.experts, name='experts'),

    path('administration/', views.administration, name='administration'),
    path('faq/', views.faq, name='faq'),

    path('login/', LoginView.as_view(template_name='login.html', redirect_authenticated_user=True, authentication_form=UsernameOrEmailAuthenticationForm), name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Password reset routes
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html', form_class=UsernameOrEmailPasswordResetForm), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),

    path('signup/', views.signup, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/lab-tests/', views.lab_tests_dashboard, name='dashboard_lab_tests'),
    path('dashboard/lab-tests/<int:request_id>/', views.lab_test_request_detail, name='dashboard_lab_test_detail'),
    path('dashboard/lab-tests/<int:request_id>/update-status/', views.update_lab_test_status, name='dashboard_lab_test_update_status'),
    path('dashboard/lab-tests/<int:request_id>/upload-receipt/', views.upload_lab_test_receipt, name='dashboard_labtests_upload_receipt'),
    path('dashboard/lab-tests/item/<int:item_id>/update-price/', views.update_lab_test_item_price, name='dashboard_lab_test_update_item_price'),
    path('dashboard/consultancy/', views.consultancy_dashboard, name='dashboard_consultancy'),
    path('dashboard/consultancy/<int:request_id>/', views.consultancy_request_detail, name='dashboard_consultancy_detail'),
    path('dashboard/consultancy/<int:request_id>/update-status/', views.update_consultancy_status, name='dashboard_consultancy_update_status'),
    path('dashboard/consultancy/<int:request_id>/upload-receipt/', views.upload_consultancy_receipt, name='dashboard_consultancy_upload_receipt'),
    path('dashboard/profile/', views.profile_dashboard, name='dashboard_profile'),
    path('dashboard/how-to-pay/', views.how_to_pay_dashboard, name='dashboard_how_to_pay'),
    path('dashboard/get-help/', views.help_dashboard, name='dashboard_help'),
    path('admin/overview/', views.admin_overview, name='admin_overview'),

    # Public report verification endpoint
    path('verify-report/', views.verify_report, name='verify_report'),
]