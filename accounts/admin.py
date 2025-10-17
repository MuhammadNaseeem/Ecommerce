from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Address

class AddressInline(admin.TabularInline):
    model = Address
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    can_delete = True

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['username', 'email', 'is_buyer', 'is_business_customer', 'is_seller', 'is_staff']
    inlines = [AddressInline]  # ✅ Show addresses inline in user admin

admin.site.register(User, CustomUserAdmin)
admin.site.register(Address)


