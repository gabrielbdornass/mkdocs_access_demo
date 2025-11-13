from django.contrib import admin
from .models import PageAccess

@admin.register(PageAccess)
class PageAccessAdmin(admin.ModelAdmin):
    list_display = ("user", "page")
    search_fields = ("user__username", "page")
