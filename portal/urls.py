from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload/', views.upload_material, name='upload'),
    path('logout/', views.logout_view, name='logout'),

    # 🔐 Admin Approval URLs
    path('pending/', views.pending_materials, name='pending_materials'),
    path('approve/<int:material_id>/', views.approve_material, name='approve_material'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
]
