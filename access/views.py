import os
from pathlib import Path
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseForbidden, Http404
from django.shortcuts import render, redirect
from access.models import PageAccess
from django.http import FileResponse

# Directory where your .html pages live
PAGES_DIR = settings.BASE_DIR / 'pages'

# -----------------------------------------------------------------------------
# Login / Logout Views
# -----------------------------------------------------------------------------
def login_view(request):
    """Render and handle login form."""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("/")  # Redirect to homepage after login
        else:
            return render(request, "login.html", {"error": "Invalid credentials"})

    return render(request, "login.html")


def logout_view(request):
    """Logs the user out and redirects to homepage."""
    logout(request)
    return redirect("/")


# -----------------------------------------------------------------------------
# Page Serving View
# -----------------------------------------------------------------------------
def serve_page(request, path="index.html"):
    """
    Serve HTML pages with access control:
      - Public pages (marked with <!-- access: public -->): accessible to everyone
      - Private pages (<!-- access: private --> or default): only to authorized users
      - Admins (superusers) can access everything
    """

    # Default path
    if path == "":
        path = "index.html"

    # Resolve and normalize path
    full_path = os.path.normpath(os.path.join(PAGES_DIR, path))

    # Prevent directory traversal
    if not full_path.startswith(os.path.abspath(PAGES_DIR)):
        raise Http404("Invalid path")

    # Directory → index.html
    if os.path.isdir(full_path):
        full_index_path = os.path.join(full_path, "index.html")
    else:
        full_index_path = full_path

    if not os.path.exists(full_path):
        raise Http404(f"Page not found: {path}")


    # detecta mime type básico
    if Path(full_index_path).suffix == ".html":
        content_type = "text/html"
    elif Path(full_index_path).suffix == ".css":
        content_type = "text/css"
    elif Path(full_index_path).suffix == ".js":
        content_type = "application/javascript"
    elif Path(full_index_path).suffix in [".png", ".jpg", ".jpeg", ".gif", ".ico"]:
        return FileResponse(open(full_index_path, "rb"))
    else:
        content_type = "text/plain"

    # Read HTML content
    with open(full_index_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Detect access level from HTML comment
    if "<!-- access: public -->" in content:
        access_level = "public"
    elif "<!-- access: private -->" in content:
        access_level = "private"
    else:
        access_level = "private"  # default if not specified

    filename = os.path.basename(full_path)

    # Access control
    if access_level == "private":
        if not request.user.is_authenticated:
            return redirect("/login/?next=/" + path)

        if not request.user.is_superuser:
            has_access = PageAccess.objects.filter(user=request.user, page=filename).exists()
            if not has_access:
                return HttpResponseForbidden(
                    "<h1>403 Forbidden</h1><p>You don't have permission to access this page.</p>"
                )

    return HttpResponse(content, content_type=content_type)
