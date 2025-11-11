from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Sum
from .forms import SignupForm, ProfileUpdateForm, PasswordUpdateForm
from .models import Profile, LabTestRequest, LabTestItem, ConsultancyRequest
import json
from decimal import Decimal
from datetime import datetime

# Public pages

def home(request):
    return render(request, 'home.html', {'active_page': 'home'})


def about(request):
    return render(request, 'about.html', {'active_page': 'home'})


def test_rates(request):
    return render(request, 'tests.html', {'active_page': 'tests'})


def projects(request):
    return render(request, 'projects.html', {'active_page': 'projects'})


def experts(request):
    return render(request, 'experts.html', {'active_page': 'experts'})




def administration(request):
    return render(request, 'administration.html', {'active_page': 'administration'})


def faq(request):
    return render(request, 'faq.html', {'active_page': 'faq'})


@login_required(login_url='/login/')
def dashboard(request):
    profile = getattr(request.user, 'profile', None)
    is_admin = (request.user.is_staff or request.user.is_superuser)
    if is_admin:
        lab_qs = LabTestRequest.objects.all()
        cons_qs = ConsultancyRequest.objects.all()
    else:
        lab_qs = LabTestRequest.objects.filter(user=request.user)
        cons_qs = ConsultancyRequest.objects.filter(user=request.user)
    # Exclude delivered from the recent lists
    recent_lab = lab_qs.exclude(status='report-delivered').order_by('-created_at')[:5]
    recent_cons = cons_qs.exclude(status='report-delivered').order_by('-created_at')[:5]
    # Admin convenience: surface delivered lab reports to avoid long scrolling elsewhere
    delivered_lab = lab_qs.filter(status='report-delivered').order_by('-created_at')[:20]
    delivered_cons = cons_qs.filter(status='report-delivered').order_by('-created_at')[:20]
    completed_count = lab_qs.filter(status='report-delivered').count() + cons_qs.filter(status='report-delivered').count()
    return render(request, 'dashboard.html', {
        'active_page': 'dashboard',
        'profile': profile,
        'is_admin': is_admin,
        'recent_lab': recent_lab,
        'recent_consultancy': recent_cons,
        'delivered_lab': delivered_lab,
        'delivered_consultancy': delivered_cons,
        'completed_count': completed_count,
    })


@login_required(login_url='/login/')
def admin_overview(request):
    profile = getattr(request.user, 'profile', None)
    # Admin overview shows global summaries
    lab_qs = LabTestRequest.objects.all()
    cons_qs = ConsultancyRequest.objects.all()
    recent_lab = lab_qs.order_by('-created_at')[:5]
    recent_cons = cons_qs.order_by('-created_at')[:5]
    completed_count = lab_qs.filter(status='report-delivered').count() + cons_qs.filter(status='report-delivered').count()
    return render(request, 'admin_overview.html', {
        'active_page': 'dashboard',
        'profile': profile,
        'is_admin': True,
        'recent_lab': recent_lab,
        'recent_consultancy': recent_cons,
        'completed_count': completed_count,
        'status_choices_cons': ConsultancyRequest.STATUS_CHOICES,
    })


# New: Authenticated Lab Tests page within dashboard
@login_required(login_url='/login/')
def update_lab_test_status(request, request_id: int):
    # Admin/staff only
    if not (request.user.is_staff or request.user.is_superuser):
        return HttpResponseForbidden('Not allowed')
    if request.method != 'POST':
        return HttpResponseForbidden('Invalid method')
    req_obj = get_object_or_404(LabTestRequest, id=request_id)
    new_status = request.POST.get('status')
    allowed = {s for s, _ in LabTestRequest.STATUS_CHOICES}
    if new_status not in allowed:
        messages.error(request, 'Invalid status.')
    else:
        if new_status == 'report-delivered':
            code = (request.POST.get('verification_code') or '').strip()
            import re
            if not re.fullmatch(r"\d{8}", code or ''):
                messages.error(request, 'Provide a valid 8-digit verification code.')
            else:
                # Ensure code uniqueness across both LabTestRequest and ConsultancyRequest
                dup_lab = LabTestRequest.objects.filter(report_verification_code=code).exclude(id=req_obj.id).exists()
                dup_cons = ConsultancyRequest.objects.filter(report_verification_code=code).exists()
                if dup_lab or dup_cons:
                    messages.error(request, 'Verification code already in use. Choose a different code.')
                else:
                    req_obj.report_verification_code = code
                    req_obj.status = new_status
                    req_obj.save()
                    messages.success(request, 'Status updated with verification code.')
        else:
            req_obj.status = new_status
            req_obj.save()
            messages.success(request, 'Status updated.')
    next_url = request.POST.get('next') or reverse('dashboard_lab_tests')
    return redirect(next_url)

# New: Authenticated Consultancy page inline status update
@login_required(login_url='/login/')
def update_consultancy_status(request, request_id: int):
    # Admin/staff only
    if not (request.user.is_staff or request.user.is_superuser):
        return HttpResponseForbidden('Not allowed')
    if request.method != 'POST':
        return HttpResponseForbidden('Invalid method')
    cons_obj = get_object_or_404(ConsultancyRequest, id=request_id)
    new_status = request.POST.get('status')
    allowed = {s for s, _ in ConsultancyRequest.STATUS_CHOICES}
    if new_status not in allowed:
        messages.error(request, 'Invalid status.')
    else:
        # Allow admin to set/update amount along with status changes
        amount_raw = (request.POST.get('amount') or '').strip()
        if amount_raw:
            try:
                cons_obj.amount = Decimal(amount_raw)
            except Exception:
                messages.error(request, 'Invalid amount. Please enter a valid number.')
        if new_status == 'report-delivered':
            code = (request.POST.get('verification_code') or '').strip()
            import re
            if not re.fullmatch(r"\d{8}", code or ''):
                messages.error(request, 'Provide a valid 8-digit verification code.')
            else:
                dup_cons = ConsultancyRequest.objects.filter(report_verification_code=code).exclude(id=cons_obj.id).exists()
                dup_lab = LabTestRequest.objects.filter(report_verification_code=code).exists()
                if dup_lab or dup_cons:
                    messages.error(request, 'Verification code already in use. Choose a different code.')
                else:
                    cons_obj.report_verification_code = code
                    cons_obj.status = new_status
                    cons_obj.save()
                    messages.success(request, 'Status updated with verification code.')
        else:
            cons_obj.status = new_status
            cons_obj.save()
            messages.success(request, 'Status updated.')
    next_url = request.POST.get('next') or reverse('dashboard_consultancy')
    return redirect(next_url)

@login_required(login_url='/login/')
def lab_tests_dashboard(request):
    profile = getattr(request.user, 'profile', None)
    if request.method == 'POST':
        # Handle new lab test request submission
        if request.POST.get('form') == 'lab_request':
            project_name = request.POST.get('project_name', '').strip()
            if not project_name:
                return HttpResponseForbidden('Project name is required.')
            ref_no = request.POST.get('reference_number', '').strip()
            client_name = request.POST.get('client_name', '').strip()
            location = request.POST.get('project_location', '').strip()
            description_html = request.POST.get('description_html', '')
            sample_by = request.POST.get('sample_by', '').strip()
            receiving_date_raw = (request.POST.get('receiving_date') or '').strip()
            receiving_date = None
            if receiving_date_raw:
                try:
                    receiving_date = datetime.strptime(receiving_date_raw, '%d/%m/%Y').date()
                except ValueError:
                    messages.error(request, 'Invalid receiving date format. Use dd/mm/yyyy.')
                    return redirect('dashboard_lab_tests')
            sample_description = request.POST.get('sample_description', '')

            req_obj = LabTestRequest.objects.create(
                user=request.user,
                project_name=project_name,
                reference_number=ref_no,
                client_name=client_name,
                project_location=location,
                description_html=description_html,
                sample_by=sample_by,
                receiving_date=receiving_date,
                sample_description=sample_description,
            )
            # handle optional file
            if 'spec_document' in request.FILES:
                req_obj.spec_document = request.FILES['spec_document']
                req_obj.save()
            # parse items_json
            items_json = request.POST.get('items_json')
            if items_json:
                try:
                    items = json.loads(items_json)
                    for it in items:
                        LabTestItem.objects.create(
                            request=req_obj,
                            lab=it.get('lab',''),
                            subcategory=it.get('subcategory',''),
                            test_name=it.get('name',''),
                            price=int(it.get('price',0) or 0)
                        )
                except Exception:
                    # ignore bad payloads for now
                    pass
            return redirect('dashboard_lab_tests')
    # GET: list previous requests
    base_qs = LabTestRequest.objects.all().order_by('-created_at') if (request.user.is_staff or request.user.is_superuser) else LabTestRequest.objects.filter(user=request.user).order_by('-created_at')
    requests_qs = base_qs.annotate(total_amount=Sum('items__price'))
    return render(request, 'lab_tests_dashboard.html', {
        'active_page': 'dashboard',
        'profile': profile,
        'requests': requests_qs,
        'status_choices': LabTestRequest.STATUS_CHOICES,
    })


# Upload payment receipt for lab test request (admins can upload for any request)
@login_required(login_url='/login/')
def upload_lab_test_receipt(request, request_id: int):
    # POST only: upload a payment receipt for a specific lab test request
    if request.method != 'POST':
        return HttpResponseForbidden('Invalid method')
    if request.user.is_staff or request.user.is_superuser:
        req_obj = get_object_or_404(LabTestRequest, id=request_id)
    else:
        req_obj = get_object_or_404(LabTestRequest, id=request_id, user=request.user)
    if 'payment_receipt' in request.FILES:
        req_obj.payment_receipt = request.FILES['payment_receipt']
        req_obj.save()
        messages.success(request, 'Payment receipt uploaded. Thanks for the payment.')
    return redirect('dashboard_lab_tests')


# Admin: Update a single lab test item price
@login_required(login_url='/login/')
def update_lab_test_item_price(request, item_id: int):
    if not (request.user.is_staff or request.user.is_superuser):
        return HttpResponseForbidden('Not allowed')
    if request.method != 'POST':
        return HttpResponseForbidden('Invalid method')
    item = get_object_or_404(LabTestItem.objects.select_related('request'), id=item_id)
    price_raw = (request.POST.get('price') or '').strip()
    try:
        new_price = int(price_raw)
        if new_price < 0:
            raise ValueError('Negative')
    except Exception:
        messages.error(request, 'Invalid price. Enter a non-negative integer.')
    else:
        item.price = new_price
        item.save()
        messages.success(request, 'Item price updated.')
    next_url = request.POST.get('next') or reverse('dashboard_lab_test_detail', args=[item.request_id])
    return redirect(next_url)


# New: Authenticated Consultancy page within dashboard
@login_required(login_url='/login/')
def consultancy_dashboard(request):
    profile = getattr(request.user, 'profile', None)
    if request.method == 'POST':
        if request.POST.get('form') == 'consultancy_request':
            project_name = request.POST.get('project_name', '').strip()
            if not project_name:
                return HttpResponseForbidden('Project name is required.')
            organization = request.POST.get('organization', '').strip()
            location = request.POST.get('location', '').strip()
            reference_number = request.POST.get('reference_number', '').strip()
            description_html = request.POST.get('description_html', '')

            cons = ConsultancyRequest.objects.create(
                user=request.user,
                project_name=project_name,
                organization=organization,
                location=location,
                reference_number=reference_number,
                description_html=description_html,
            )
            if 'attachment' in request.FILES:
                cons.attachment = request.FILES['attachment']
                cons.save()
            return redirect(f"{reverse('dashboard_consultancy')}?view=previous")

    # GET: list previous consultancy requests
    if request.user.is_staff or request.user.is_superuser:
        cons_qs = ConsultancyRequest.objects.all().order_by('-created_at')
    else:
        cons_qs = ConsultancyRequest.objects.filter(user=request.user).order_by('-created_at')

    # Prepare lightweight data for client-side table rendering
    cons_data = []
    for c in cons_qs:
        details = f"{c.project_name} — {c.organization or ''}".strip()
        created = c.created_at.strftime('%d/%m/%Y %H:%M')
        cons_data.append({
            'id': c.id,
            'details': details,
            'status': c.status,
            'status_label': c.get_status_display(),
            'created': created,
            'view_url': reverse('dashboard_consultancy_detail', args=[c.id]),
            'update_url': reverse('dashboard_consultancy_update_status', args=[c.id]),
            'report_verification_code': c.report_verification_code or '',
            # NEW: amount and receipt info
            'amount': (str(c.amount) if c.amount is not None else ''),
            'has_receipt': bool(c.payment_receipt),
            'upload_receipt_url': reverse('dashboard_consultancy_upload_receipt', args=[c.id]),
            'receipt_url': (c.payment_receipt.url if c.payment_receipt else ''),
        })

    return render(request, 'consultancy_dashboard.html', {
        'active_page': 'dashboard',
        'profile': profile,
        'consultancies': cons_qs,
        'consultancies_json': json.dumps(cons_data),
        'status_choices': ConsultancyRequest.STATUS_CHOICES,
        'status_choices_json': json.dumps(ConsultancyRequest.STATUS_CHOICES),
        'is_admin': (request.user.is_staff or request.user.is_superuser),
    })

# New: Authenticated How to Pay static page within dashboard
@login_required(login_url='/login/')
def how_to_pay_dashboard(request):
    profile = getattr(request.user, 'profile', None)
    return render(request, 'how_to_pay.html', {'active_page': 'dashboard', 'profile': profile})

# New: Authenticated Get Help static page within dashboard
@login_required(login_url='/login/')
def help_dashboard(request):
    profile = getattr(request.user, 'profile', None)
    return render(request, 'help_dashboard.html', {'active_page': 'dashboard', 'profile': profile})


# Explicit logout view to ensure deterministic redirect
def logout_view(request):
    auth_logout(request)
    return redirect('login')

@login_required(login_url='/login/')
def upload_consultancy_receipt(request, request_id: int):
    # POST only: upload a payment receipt for a specific consultancy request
    if request.method != 'POST':
        return HttpResponseForbidden('Invalid method')
    if request.user.is_staff or request.user.is_superuser:
        cons_obj = get_object_or_404(ConsultancyRequest, id=request_id)
    else:
        cons_obj = get_object_or_404(ConsultancyRequest, id=request_id, user=request.user)
    if 'payment_receipt' in request.FILES:
        cons_obj.payment_receipt = request.FILES['payment_receipt']
        cons_obj.save()
        messages.success(request, 'Payment receipt uploaded. Thanks for the payment.')
    return redirect('dashboard_consultancy')

# New: Authenticated User Profile page within dashboard
@login_required(login_url='/login/')
def profile_dashboard(request):
    def _next_client_id():
        try:
            existing = Profile.objects.exclude(client_id__isnull=True).exclude(client_id='').values_list('client_id', flat=True)
            nums = []
            for cid in existing:
                try:
                    nums.append(int(cid))
                except Exception:
                    continue
            next_num = (max(nums) + 1) if nums else 1
            return f"{next_num:06d}"
        except Exception:
            from datetime import datetime as _dt
            return _dt.utcnow().strftime('%y%m%d%H%M')

    profile, created = Profile.objects.get_or_create(user=request.user, defaults={'client_id': _next_client_id()})
    if not profile.client_id:
        try:
            profile.client_id = _next_client_id()
            profile.save(update_fields=['client_id'])
        except Exception:
            pass

    if request.method == 'POST':
        form_type = request.POST.get('form')
        if form_type == 'profile':
            pform = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
            pwform = PasswordUpdateForm()
            if pform.is_valid():
                email = pform.cleaned_data.get('email')
                if email:
                    request.user.email = email
                    request.user.save()
                pform.save()
                messages.success(request, 'Profile updated successfully.')
                return redirect(f"{reverse('dashboard_profile')}?view=details")
        elif form_type == 'password':
            pwform = PasswordUpdateForm(request.POST, user=request.user)
            pform = ProfileUpdateForm(instance=profile, initial={'email': request.user.email})
            if pwform.is_valid():
                new_password = pwform.cleaned_data['new_password']
                request.user.set_password(new_password)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Password updated successfully.')
                return redirect(f"{reverse('dashboard_profile')}?view=password")
            else:
                messages.error(request, 'Password not updated. Please fix the errors below.')
        else:
            pform = ProfileUpdateForm(instance=profile, initial={'email': request.user.email})
            pwform = PasswordUpdateForm()
    else:
        pform = ProfileUpdateForm(instance=profile, initial={'email': request.user.email})
        pwform = PasswordUpdateForm()

    return render(request, 'profile_dashboard.html', {
        'active_page': 'dashboard',
        'profile': profile,
        'profile_form': pform,
        'password_form': pwform,
    })


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form, 'active_page': 'dashboard'})


@login_required(login_url='/login/')
def consultancy_request_detail(request, request_id: int):
    profile = getattr(request.user, 'profile', None)
    if request.user.is_staff or request.user.is_superuser:
        cons = get_object_or_404(ConsultancyRequest, id=request_id)
    else:
        cons = get_object_or_404(ConsultancyRequest, id=request_id, user=request.user)
    return render(request, 'consultancy_request_detail.html', {
        'active_page': 'dashboard',
        'profile': profile,
        'req': cons,
        'status_choices': ConsultancyRequest.STATUS_CHOICES,
    })


@login_required(login_url='/login/')
def lab_test_request_detail(request, request_id: int):
    profile = getattr(request.user, 'profile', None)
    # Admins can view any request; users only their own
    if request.user.is_staff or request.user.is_superuser:
        req_obj = get_object_or_404(LabTestRequest, id=request_id)
    else:
        req_obj = get_object_or_404(LabTestRequest, id=request_id, user=request.user)
    items = req_obj.items.all()
    total_amount = items.aggregate(total=Sum('price')).get('total') or 0
    return render(request, 'lab_test_request_detail.html', {
        'active_page': 'dashboard',
        'profile': profile,
        'req': req_obj,
        'items': items,
        'total_amount': total_amount,
        'status_choices': LabTestRequest.STATUS_CHOICES,
    })


def verify_report(request):
    code = (request.GET.get('code') or '').strip()
    import re
    if not re.fullmatch(r"\d{8}", code or ''):
        return JsonResponse({'ok': False, 'error': 'Invalid code format'}, status=400)

    lab = LabTestRequest.objects.filter(report_verification_code=code).first()
    if lab:
        if lab.status == 'report-delivered':
            return JsonResponse({
                'ok': True,
                'type': 'lab',
                'id': lab.id,
                'project_name': lab.project_name,
                'reference_number': lab.reference_number or '',
                'status': lab.get_status_display(),
            })
        else:
            return JsonResponse({'ok': False, 'type': 'lab', 'status': lab.get_status_display()})

    cons = ConsultancyRequest.objects.filter(report_verification_code=code).first()
    if cons:
        if cons.status == 'report-delivered':
            return JsonResponse({
                'ok': True,
                'type': 'consultancy',
                'id': cons.id,
                'project_name': cons.project_name,
                'organization': cons.organization or '',
                'reference_number': cons.reference_number or '',
                'status': cons.get_status_display(),
            })
        else:
            return JsonResponse({'ok': False, 'type': 'consultancy', 'status': cons.get_status_display()})

    return JsonResponse({'ok': False})
