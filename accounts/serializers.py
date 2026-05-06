# accounts/serializers.py

from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Users, Office, Token, City, District, CrowdSnapshot


# ==========================================================
# USER SERIALIZER
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
# CITY & DISTRICT SERIALIZERS
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
# CROWD SNAPSHOT SERIALIZER (NEW)
# ==========================================================
class CrowdSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CrowdSnapshot
        fields = [
            'snapshot_id',
            'office',
            'people_count',
            'crowd_status',
            'captured_at',
        ]
        read_only_fields = ['snapshot_id', 'captured_at']


# ==========================================================
# OFFICE SERIALIZER
# (Updated: live crowd data now comes from CrowdSnapshot,
#  with a fallback to token-count when no camera data exists)
# ==========================================================
class OfficeSerializer(serializers.ModelSerializer):
    """
    Priority order for live crowd data:
      1. Latest CrowdSnapshot (real camera count) if available
      2. Active-token count (fallback when camera is offline)
    """

    # ── Token-based fallback fields ───────────────────────
    in_queue    = serializers.SerializerMethodField()
    wait_time   = serializers.SerializerMethodField()
    wait_status = serializers.SerializerMethodField()

    # ── Camera-based live crowd fields (NEW) ──────────────
    live_people_count  = serializers.SerializerMethodField()
    live_crowd_status  = serializers.SerializerMethodField()
    last_camera_update = serializers.SerializerMethodField()
    camera_online      = serializers.SerializerMethodField()

    # ── Nested location info ──────────────────────────────
    district_name = serializers.CharField(
        source='district.district_name', read_only=True
    )
    city_name = serializers.CharField(
        source='district.city.city_name', read_only=True
    )

    class Meta:
        model  = Office
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
            # ── Token-based (fallback) ──
            'in_queue',
            'wait_time',
            'wait_status',
            # ── Camera-based (live) ──
            'live_people_count',
            'live_crowd_status',
            'last_camera_update',
            'camera_online',
        ]

    # ── Token-based helpers (unchanged) ───────────────────
    def _active_token_count(self, obj):
        return Token.objects.filter(office=obj, status='Active').count()

    def get_in_queue(self, obj):
        return self._active_token_count(obj)

    def get_wait_time(self, obj):
        return self._active_token_count(obj) * 10   # minutes

    def get_wait_status(self, obj):
        wait = self.get_wait_time(obj)
        if wait < 30:
            return "Low"
        elif wait <= 60:
            return "Moderate"
        return "High"

    # ── Camera-based helpers (NEW) ────────────────────────
    def _latest_snapshot(self, obj):
        """Cache snapshot lookup per office in serializer context."""
        cache = self.context.setdefault('_snapshot_cache', {})
        if obj.office_id not in cache:
            cache[obj.office_id] = obj.latest_crowd_snapshot()
        return cache[obj.office_id]

    def get_live_people_count(self, obj):
        snap = self._latest_snapshot(obj)
        if snap:
            return snap.people_count
        # Fallback: token count as proxy
        return self._active_token_count(obj)

    def get_live_crowd_status(self, obj):
        snap = self._latest_snapshot(obj)
        if snap:
            return snap.crowd_status
        # Fallback: derive from token count
        return self.get_wait_status(obj)

    def get_last_camera_update(self, obj):
        snap = self._latest_snapshot(obj)
        if snap:
            return snap.captured_at.strftime("%Y-%m-%d %H:%M:%S")
        return None

    def get_camera_online(self, obj):
        """True if a snapshot was received in the last 2 minutes."""
        from django.utils import timezone
        from datetime import timedelta
        snap = self._latest_snapshot(obj)
        if not snap:
            return False
        age = timezone.now() - snap.captured_at
        return age <= timedelta(minutes=2)


# ==========================================================
# TOKEN SERIALIZER
# ==========================================================
class TokenSerializer(serializers.ModelSerializer):

    user_name    = serializers.CharField(source='user.full_name',       read_only=True)
    office_name  = serializers.CharField(source='office.branch_name',   read_only=True)

    city_name     = serializers.CharField(source='office.district.city.city_name',  read_only=True)
    district_name = serializers.CharField(source='office.district.district_name',   read_only=True)
    location_name = serializers.CharField(source='office.branch_name',              read_only=True)
    address       = serializers.CharField(source='office.google_address',           read_only=True)
    est_wait_time = serializers.CharField(source='estimated_wait_time',             read_only=True)

    date_time = serializers.DateTimeField(
        source='created_at',
        format="%d %b, %Y - %I:%M %p",
        read_only=True
    )
    people_ahead = serializers.SerializerMethodField()

    class Meta:
        model  = Token
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