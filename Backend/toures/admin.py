from django.contrib import admin
from .models import Package


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ['package_id', 'title', 'duration', 'group_size', 'price', 'start_date', 'get_tickets_count']
    search_fields = ['title', 'package_id', 'description']
    list_filter = ['start_date', 'price', 'duration']
    date_hierarchy = 'start_date'
    list_per_page = 20
    fieldsets = (
        ('Basic Information', {
            'fields': ('package_id', 'title', 'description')
        }),
        ('Pricing & Schedule', {
            'fields': ('price', 'duration', 'group_size', 'start_date')
        }),
        ('Media', {
            'fields': ('cover_image',)
        }),
        ('Tour Details', {
            'fields': ('tour_highlights', 'tour_details'),
            'classes': ('collapse',)
        }),
    )
    
    def get_tickets_count(self, obj):
        return obj.tickets.count()
    get_tickets_count.short_description = 'Tickets Sold'
