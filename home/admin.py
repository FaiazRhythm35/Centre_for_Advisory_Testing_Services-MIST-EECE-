from django.contrib import admin
from .models import Profile, LabTestRequest, LabTestItem, ConsultancyRequest

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'account_type', 'org_name', 'role_in_org', 'phone')
    search_fields = ('user__username', 'full_name', 'org_name', 'role_in_org', 'phone')
    list_filter = ('account_type',)

# Inline to manage test items within a request
class LabTestItemInline(admin.TabularInline):
    model = LabTestItem
    extra = 0

@admin.register(LabTestRequest)
class LabTestRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'project_name', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('project_name', 'user__username', 'reference_number', 'client_name', 'project_location')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [LabTestItemInline]

@admin.register(LabTestItem)
class LabTestItemAdmin(admin.ModelAdmin):
    list_display = ('request', 'lab', 'subcategory', 'test_name', 'price')
    list_filter = ('lab', 'subcategory')
    search_fields = ('test_name', 'request__project_name', 'request__user__username')

@admin.register(ConsultancyRequest)
class ConsultancyRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'project_name', 'organization', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('project_name', 'user__username', 'organization', 'location', 'reference_number')
    readonly_fields = ('created_at', 'updated_at')
