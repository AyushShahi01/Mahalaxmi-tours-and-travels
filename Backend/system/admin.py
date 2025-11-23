from django.contrib import admin
from .models import Traveler, Ticket, Payment


@admin.register(Traveler)
class TravelerAdmin(admin.ModelAdmin):
    list_display = ['traveler_id', 'name', 'email', 'phone_number', 'address']
    search_fields = ['name', 'email', 'phone_number']
    list_per_page = 20


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_id', 'get_traveler_name', 'get_package_title', 'get_package_price']
    list_filter = ['package']
    search_fields = ['traveler__name', 'package__title']
    raw_id_fields = ['traveler', 'package']
    list_per_page = 20
    
    def get_traveler_name(self, obj):
        return obj.traveler.name
    get_traveler_name.short_description = 'Traveler'
    
    def get_package_title(self, obj):
        return obj.package.title
    get_package_title.short_description = 'Package'
    
    def get_package_price(self, obj):
        return f'${obj.package.price}'
    get_package_price.short_description = 'Price'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'get_traveler_name', 'amount', 'date', 'get_ticket_id', 'get_package_title']
    list_filter = ['date', 'package']
    search_fields = ['traveler__name', 'package__title']
    raw_id_fields = ['traveler', 'ticket', 'package']
    date_hierarchy = 'date'
    list_per_page = 20
    readonly_fields = ['date']
    
    def get_traveler_name(self, obj):
        return obj.traveler.name
    get_traveler_name.short_description = 'Traveler'
    
    def get_ticket_id(self, obj):
        return obj.ticket.ticket_id
    get_ticket_id.short_description = 'Ticket ID'
    
    def get_package_title(self, obj):
        return obj.package.title
    get_package_title.short_description = 'Package'
