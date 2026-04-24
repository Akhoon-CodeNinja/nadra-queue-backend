# accounts/serializers.py

from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Users, Office, Token, City, District


# ==========================================================
# USER SERIALIZER (SAB PURANA VALIDATION LOGIC MAUJOOD HAI)
# ==========================================================
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = Users
        fields = [
            'user_id',
            'full_name',
            'CNIC',
            'password',
            'DOB',
            'Mobile_number',
            'email',
            'created_at'
        ]
        read_only_fields = ['user_id', 'created_at']

    def validate_CNIC(self, value):
        value = value.strip()
        from .models import validate_cnic
        validate_cnic(value)
        return value

    def validate_Mobile_number(self, value):
        value = value.strip()
        from .models import validate_mobile
        validate_mobile(value)
        return value

    def validate_full_name(self, value):
        value = value.strip()
        if not all(c.isalpha() or c.isspace() for c in value):
            raise serializers.ValidationError(
                "Full name must contain letters and spaces only."
            )
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long."
            )
        return value

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


# ==========================================================
# CITY & DISTRICT SERIALIZERS (NAYE ADD KIYE GAYE HAIN)
# ==========================================================
class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['city_id', 'city_name']


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ['district_id', 'district_name', 'city']


# ==========================================================
# OFFICE SERIALIZER (UPDATED: DISTRICT AUR CITY INFO ADDED)
# ==========================================================
class OfficeSerializer(serializers.ModelSerializer):
    """
    Live queue stats are derived from the Token table — NOT from capacity.
    """

    # ── Live Token-based fields ───────────────────────────
    in_queue    = serializers.SerializerMethodField()
    wait_time   = serializers.SerializerMethodField()
    wait_status = serializers.SerializerMethodField()
    
    # ── Nested Info fields (Flutter Cascading ke liye) ─────
    district_name = serializers.CharField(source='district.district_name', read_only=True)
    city_name = serializers.CharField(source='district.city.city_name', read_only=True)

    class Meta:
        model = Office
        fields = [
            'office_id',
            'district',
            'district_name',
            'city_name',
            'branch_name',
            'google_address',
            'capacity',
            'open_time',
            'close_time',
            'open_days',
            # ── Token-based live fields ──
            'in_queue',      
            'wait_time',     
            'wait_status',   
        ]

    # ── How many active tokens are queued right now ───────
    def get_in_queue(self, obj):
        return Token.objects.filter(office=obj, status='Active').count()

    # ── Estimated wait: each token ≈ 10 minutes ───────────
    def get_wait_time(self, obj):
        return self.get_in_queue(obj) * 10          # returns minutes (int)

    # ── Status label driven purely by Token table ─────────
    def get_wait_status(self, obj):
        wait_minutes = self.get_wait_time(obj)
        if wait_minutes < 30:
            return "Low"        # 0–2 active tokens
        elif wait_minutes <= 60:
            return "Moderate"   # 3–6 active tokens
        else:
            return "High"       # 7+ active tokens


# ==========================================================
# TOKEN SERIALIZER (UPDATED: LOCATION DETAILS ADDED)
# ==========================================================
class TokenSerializer(serializers.ModelSerializer):

    user_name    = serializers.CharField(source='user.full_name',       read_only=True)
    office_name  = serializers.CharField(source='office.branch_name',   read_only=True)
    
    # ── Flutter MyTokensScreen fields (Extra Details) ──────
    city_name     = serializers.CharField(source='office.district.city.city_name', read_only=True)
    district_name = serializers.CharField(source='office.district.district_name', read_only=True)
    location_name = serializers.CharField(source='office.branch_name',   read_only=True)
    address       = serializers.CharField(source='office.google_address', read_only=True)
    est_wait_time = serializers.CharField(source='estimated_wait_time',   read_only=True)
    
    date_time     = serializers.DateTimeField(
        source='created_at',
        format="%d %b, %Y - %I:%M %p",
        read_only=True
    )
    people_ahead  = serializers.SerializerMethodField()

    class Meta:
        model = Token
        fields = [
            'token_id',
            'token_number',
            'user',
            'user_name',
            'office',
            'office_name',
            'city_name',
            'district_name',
            'status',
            'created_at',
            'estimated_wait_time',
            'location_name',
            'address',
            'est_wait_time',
            'date_time',
            'people_ahead',
        ]
        read_only_fields = ['token_id', 'created_at']

    def get_people_ahead(self, obj):
        """Active tokens with a lower token_number = people ahead of this user."""
        if obj.status == 'Active':
            return Token.objects.filter(
                office=obj.office,
                status='Active',
                token_number__lt=obj.token_number
            ).count()
        return 0