from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import StudyMaterial
from django.contrib.auth.decorators import login_required

from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.paginator import Paginator
from django.db.models import Q

from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def pending_materials(request):
    materials = StudyMaterial.objects.filter(is_approved=False)
    return render(request, 'pending_materials.html', {'materials': materials})

@staff_member_required
def approve_material(request, material_id):
    material = StudyMaterial.objects.get(id=material_id)
    material.is_approved = True
    material.save()
    return redirect('pending_materials')

def index(request):
    return render(request, 'index.html')


def register(request):
    if request.method == 'POST':
        user = User.objects.create_user(
            username=request.POST['username'],
            password=request.POST['password'],
            email=request.POST['email'],
            is_active=False  # Temporarily deactivate until email is verified
        )

        current_site = get_current_site(request)
        subject = 'Activate Your Study Portal Account'
        message = render_to_string('activate_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
        })

        send_mail(subject, message, 'noreply@studyportal.com', [user.email])
        return render(request, 'verify_notice.html')
    return render(request, 'register.html')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('login')
    else:
        return render(request, 'activation_failed.html')


def login_view(request):
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user:
            login(request, user)
            return redirect('dashboard')
    return render(request, 'login.html')


@login_required
def dashboard(request):
    query = request.GET.get('q')
    materials = StudyMaterial.objects.filter(is_approved=True)

    if query:
        materials = materials.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    paginator = Paginator(materials.order_by('-uploaded_at'), 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'dashboard.html', {
        'page_obj': page_obj,
        'query': query,
    })


@login_required
def upload_material(request):
    if request.method == 'POST':
        StudyMaterial.objects.create(
            title=request.POST['title'],
            description=request.POST['description'],
            file=request.FILES['file'],
            uploaded_by=request.user
        )
        return redirect('dashboard')
    return render(request, 'upload.html')


def logout_view(request):
    logout(request)
    return redirect('index')
