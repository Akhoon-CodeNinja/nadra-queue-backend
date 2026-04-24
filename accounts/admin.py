from django.contrib import admin
from .models import Users, Office, Token, DocumentGuide, City, District

# ==========================================
# CITY ADMIN
# ==========================================
@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('city_id', 'city_name')
    search_fields = ('city_name',)
    readonly_fields = ('city_id',)
    ordering = ('city_id',)

# ==========================================
# DISTRICT ADMIN
# ==========================================
@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('district_id', 'district_name', 'city')
    search_fields = ('district_name', 'city__city_name')
    list_filter = ('city',)
    readonly_fields = ('district_id',)
    ordering = ('district_id',)

# ==========================================
# OFFICE ADMIN
# ==========================================
@admin.register(Office)
class OfficeAdmin(admin.ModelAdmin):
    list_display = (
        'office_id',
        'branch_name',
        'district',         # <--- District add kar diya takay list mein nazar aaye
        'google_address',
        'capacity',
        'open_time',
        'close_time',
        'open_days',
    )

    search_fields = (
        'branch_name',
        'district__district_name',
        'google_address',
    )

    list_filter = (
        'district',         # <--- District ke hisab se filter karne ke liye
        'capacity',
        'open_days',
    )

    readonly_fields = (
        'office_id',
    )

    ordering = ('office_id',)

# ==========================================
# USERS ADMIN
# ==========================================
@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = (
        'user_id',
        'full_name',
        'CNIC',
        'email',
        'Mobile_number',
        'DOB',
        'created_at',
    )

    search_fields = (
        'full_name',
        'CNIC',
        'email',
    )

    list_filter = (
        'DOB',
        'created_at',
    )

    readonly_fields = (
        'user_id',
        'created_at',
    )

    ordering = ('-created_at',)

# ==========================================
# TOKEN ADMIN
# ==========================================
@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = (
        'token_id',
        'token_number',
        'user',
        'office',
        'status',
        'estimated_wait_time',
        'created_at',
    )

    search_fields = (
        'token_number',
        'user__full_name',
        'user__CNIC',
        'office__branch_name',
    )

    list_filter = (
        'status',
        'office',
        'created_at',
    )

    readonly_fields = (
        'token_id',
        'created_at',
    )

    ordering = ('-created_at',)

# ==========================================
# DOCUMENT GUIDE ADMIN
# ==========================================
@admin.register(DocumentGuide)
class DocumentGuideAdmin(admin.ModelAdmin):
    list_display = (
        'guide_id',
        'service_name',
        'created_at'
    )

    search_fields = (
        'service_name',
        'keywords'
    )

    readonly_fields = (
        'guide_id',
        'created_at',
        'updated_at'
    )

    ordering = ('guide_id',)