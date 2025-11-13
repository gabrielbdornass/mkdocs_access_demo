from django.contrib import admin
from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from access.views import serve_page, logout_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", auth_views.LoginView.as_view(redirect_authenticated_user=True), name="login"),
    path("logout/", logout_view, name="logout"),
    re_path(r"^(?P<path>.*)$", serve_page),  # serve any page dynamically
]
