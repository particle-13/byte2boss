from django.contrib import admin
from .models import Resume

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('user', 'file', 'uploaded_at')
    search_fields = ('user__email',)
    list_filter = ('uploaded_at',)
