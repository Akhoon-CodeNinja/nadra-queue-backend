# accounts/views.py

import logging
import random
import string

from django.core.mail import send_mail
from django.conf import settings as django_settings
from django.contrib.auth.hashers import check_password, make_password
from django.db.models import Max

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

from services.rag_chain import get_rag_answer
from services.whisper_service import transcribe_audio

from .models import Users, Office, Token, DocumentGuide, City, District
from .serializers import (
    UserSerializer,
    OfficeSerializer,
    TokenSerializer,
    CitySerializer,
    DistrictSerializer,
)
from .utils import normalize_query

logger = logging.getLogger(__name__)


# ── HELPER ────────────────────────────────────────────────────────────────────
def _generate_password(length=10):
    """Generate a random alphanumeric password."""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


# ==========================================================
# REGISTER USER
# POST /api/register/
# ==========================================================
@api_view(['POST'])
def register_user(request):

    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()

        return Response(
            {
                "success": True,
                "message": "User registered successfully.",
                "user_id": serializer.data.get("user_id"),
                "email": serializer.data.get("email"),
            },
            status=status.HTTP_201_CREATED
        )

    return Response(
        {
            "success": False,
            "message": "Registration failed.",
            "errors": serializer.errors
        },
        status=status.HTTP_400_BAD_REQUEST
    )


# ==========================================================
# LOGIN USER
# POST /api/login/
# ==========================================================
@api_view(['POST'])
def login_user(request):

    cnic = request.data.get("CNIC")
    password = request.data.get("password")

    if not cnic or not password:
        return Response(
            {
                "success": False,
                "message": "CNIC and password are required."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = Users.objects.get(CNIC=cnic)

        if check_password(password, user.password):
            return Response(
                {
                    "success": True,
                    "message": "Login successful.",
                    "user_id": user.pk,
                    "full_name": user.full_name,
                    "email": user.email
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "success": False,
                "message": "Invalid CNIC or password."
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    except Users.DoesNotExist:
        return Response(
            {
                "success": False,
                "message": "Invalid CNIC or password."
            },
            status=status.HTTP_401_UNAUTHORIZED
        )


# ==========================================================
# USER PROFILE
# GET /api/profile/<user_id>/
# ==========================================================
@api_view(['GET'])
def user_profile(request, user_id):

    try:
        user = Users.objects.get(pk=user_id)

        return Response(
            {
                "success": True,
                "message": "Profile fetched successfully.",
                "user_id": user.pk,
                "full_name": user.full_name,
                "CNIC": user.CNIC,
                "email": user.email,
                "DOB": user.DOB,
                "Mobile_number": user.Mobile_number
            },
            status=status.HTTP_200_OK
        )

    except Users.DoesNotExist:
        return Response(
            {
                "success": False,
                "message": "User not found."
            },
            status=status.HTTP_404_NOT_FOUND
        )


# ==========================================================
# FORGOT PASSWORD
# POST /api/forgot-password/
#
# Request body:
#   { "CNIC": "XXXXX-XXXXXXX-X", "email": "user@example.com" }
#
# Flow:
#   1. Verify CNIC + email both match the same account
#   2. Generate a new random password
#   3. Save it hashed to the database
#   4. Email the user their CNIC and the new plain-text password
# ==========================================================
@api_view(['POST'])
def forgot_password(request):

    cnic  = request.data.get('CNIC', '').strip()
    email = request.data.get('email', '').strip()

    # ── Step 1: Validate inputs ───────────────────────────
    if not cnic or not email:
        return Response(
            {
                "success": False,
                "message": "CNIC and email are required."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # ── Step 2: Look up the user ──────────────────────────
    try:
        user = Users.objects.get(CNIC=cnic, email=email)

    except Users.DoesNotExist:
        # Do NOT reveal which field was wrong — generic message only
        return Response(
            {
                "success": False,
                "message": "No account found with the provided CNIC and email."
            },
            status=status.HTTP_404_NOT_FOUND
        )

    # ── Step 3: Generate + save new password ─────────────
    new_password      = _generate_password(length=10)
    user.password     = make_password(new_password)
    user.save(update_fields=['password'])

    # ── Step 4: Send email ────────────────────────────────
    subject = "NADRA Queue App – Your New Password"

    message = f"""
Assalam-o-Alaikum {user.full_name},

You requested a password reset for your NADRA Queue App account.
A new password has been generated for you. Please use the details
below to log in, and change your password afterwards.

  CNIC     : {user.CNIC}
  Password : {new_password}

If you did not request this, please contact support immediately.

Regards,
NADRA Queue App Team
"""

    try:
        send_mail(
            subject=subject,
            message=message.strip(),
            from_email=django_settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

    except Exception as e:
        logger.error("forgot_password: email sending failed: %s", str(e))
        return Response(
            {
                "success": False,
                "message": "Password was reset but the email could not be sent. "
                           "Please contact support."
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return Response(
        {
            "success": True,
            "message": f"A new password has been sent to {user.email}."
        },
        status=status.HTTP_200_OK
    )


# ==========================================================
# ALL OFFICES (supports ?city_id= and ?district_id= filters)
# GET /api/offices/
# ==========================================================
@api_view(['GET'])
def office_list(request):

    city_id     = request.query_params.get('city_id')
    district_id = request.query_params.get('district_id')

    offices = Office.objects.all().order_by("office_id")

    if district_id:
        offices = offices.filter(district_id=district_id)
    elif city_id:
        offices = offices.filter(district__city_id=city_id)

    serializer = OfficeSerializer(offices, many=True)

    return Response(
        {
            "success": True,
            "count": len(serializer.data),
            "data": serializer.data
        },
        status=status.HTTP_200_OK
    )


# ==========================================================
# SINGLE OFFICE
# GET /api/offices/<office_id>/
# ==========================================================
@api_view(['GET'])
def office_detail(request, office_id):

    try:
        office = Office.objects.get(pk=office_id)
        serializer = OfficeSerializer(office)

        return Response(
            {
                "success": True,
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

    except Office.DoesNotExist:
        return Response(
            {
                "success": False,
                "message": "Office not found."
            },
            status=status.HTTP_404_NOT_FOUND
        )


# ==========================================================
# ALL TOKENS
# GET /api/tokens/
# ==========================================================
@api_view(['GET'])
def token_list(request):

    tokens = Token.objects.all().order_by('-created_at')
    serializer = TokenSerializer(tokens, many=True)

    return Response(
        {
            "success": True,
            "count": len(serializer.data),
            "data": serializer.data
        },
        status=status.HTTP_200_OK
    )


# ==========================================================
# CREATE TOKEN
# POST /api/tokens/create/
# ==========================================================
@api_view(['POST'])
def create_token(request):

    user_id   = request.data.get("user_id")
    office_id = request.data.get("office_id")

    if not user_id or not office_id:
        return Response(
            {
                "success": False,
                "message": "user_id and office_id are required."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user   = Users.objects.get(pk=user_id)
        office = Office.objects.get(pk=office_id)

        last_token  = Token.objects.filter(office=office).aggregate(Max("token_number"))
        next_number = (last_token["token_number__max"] or 0) + 1

        active_count = Token.objects.filter(office=office, status="Active").count()
        wait_time    = active_count * 10

        token = Token.objects.create(
            token_number       = next_number,
            user               = user,
            office             = office,
            status             = "Active",
            estimated_wait_time= wait_time
        )

        serializer = TokenSerializer(token)

        return Response(
            {
                "success": True,
                "message": "Token created successfully.",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    except Users.DoesNotExist:
        return Response({"success": False, "message": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    except Office.DoesNotExist:
        return Response({"success": False, "message": "Office not found."}, status=status.HTTP_404_NOT_FOUND)


# ==========================================================
# USER TOKENS
# GET /api/my-tokens/<user_id>/
# ==========================================================
@api_view(['GET'])
def user_tokens(request, user_id):

    tokens     = Token.objects.filter(user_id=user_id).order_by('-created_at')
    serializer = TokenSerializer(tokens, many=True)

    return Response(
        {
            "success": True,
            "count": len(serializer.data),
            "data": serializer.data
        },
        status=status.HTTP_200_OK
    )


# ==========================================================
# CANCEL TOKEN
# PATCH /api/token/<token_id>/cancel/
# ==========================================================
@api_view(['PATCH'])
def cancel_token(request, token_id):

    try:
        token        = Token.objects.get(pk=token_id)
        token.status = "Cancelled"
        token.save()

        return Response(
            {
                "success": True,
                "message": "Token cancelled successfully."
            },
            status=status.HTTP_200_OK
        )

    except Token.DoesNotExist:
        return Response(
            {
                "success": False,
                "message": "Token not found."
            },
            status=status.HTTP_404_NOT_FOUND
        )


# ==========================================================
# NADRA AI ASSISTANT (Voice & Text RAG)
# POST /api/document-guide/
# ==========================================================
@api_view(['POST'])
def document_guide(request):
    try:
        query_text = ""

        # SCENARIO 1: Agar Flutter app ne Audio / Voice Note bheja hai
        if 'audio' in request.FILES:
            audio_file = request.FILES['audio']
            
            # Asal file ka extension nikalo (jaise .ogg, .wav, .m4a)
            ext = os.path.splitext(audio_file.name)[1]
            if not ext:
                ext = ".m4a" # Fallback
                
            # Temporary save karo Sahi extension ke sath
            file_name = default_storage.save(f'audio/tmp_audio{ext}', ContentFile(audio_file.read()))
            tmp_file_path = os.path.join(settings.MEDIA_ROOT, file_name)
            
            # Whisper se text mein convert karo
            query_text = transcribe_audio(tmp_file_path)
            
            # Conversion ke baad temporary file delete kar do
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)
        
        # SCENARIO 2: Agar Flutter app ne normally Text type kiya hai
        elif 'query' in request.data:
            query_text = request.data.get('query', '').strip()

        if not query_text:
            return Response(
                {"success": False, "message": "Query text ya audio file required hai."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Ab us text query ka NADRA PDF se jawab nikalo
        answer = get_rag_answer(query_text)

        return Response(
            {
                "success": True,
                "query": query_text,
                "answer": answer
            },
            status=status.HTTP_200_OK
        )

    except Exception as e:
        logger.error("AI RAG Error: %s", str(e))
        return Response(
            {"success": False, "message": "Backend par koi error aagaya hai."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==========================================================
# GET ALL CITIES
# GET /api/cities/
# ==========================================================
@api_view(['GET'])
def city_list(request):
    cities     = City.objects.all().order_by("city_name")
    serializer = CitySerializer(cities, many=True)
    return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)


# ==========================================================
# GET DISTRICTS (optionally filtered by ?city_id=)
# GET /api/districts/
# ==========================================================
@api_view(['GET'])
def district_list(request):
    city_id   = request.query_params.get('city_id')
    districts = District.objects.all().order_by("district_name")

    if city_id:
        districts = districts.filter(city_id=city_id)

    serializer = DistrictSerializer(districts, many=True)
    return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

# accounts/views.py
# ── NEW imports for crowd detection ──────────────────────────────────────────
import logging

from django.views.decorators.csrf import csrf_exempt

from rest_framework          import status
from rest_framework.decorators import api_view
from rest_framework.response   import Response

from .models      import (
    Users, Office, Token, DocumentGuide,
    City, District,
    CrowdSnapshot,          # ← NEW
)
from .serializers import (
    UserSerializer, OfficeSerializer, TokenSerializer,
    CitySerializer, DistrictSerializer,
    CrowdSnapshotSerializer,   # ← NEW
)

# ── Keep your existing imports / views below this line ───────────────────────
# (paste your original views.py content here; only the crowd section is new)

logger = logging.getLogger(__name__)


# ==========================================================
# CROWD DETECTION ENDPOINT  ← NEW
# POST /api/crowd/detect/
#
# Called every N seconds by live_people_counter.py
# Payload:  { "office": <id>, "people_count": 7, "crowd_status": "Moderate" }
# Returns:  201 Created + saved snapshot
# ==========================================================
@csrf_exempt
@api_view(['POST'])
def crowd_detect(request):
    """
    Receives a crowd snapshot from the YOLO camera script and saves it.
    The OfficeSerializer will automatically pick up the latest snapshot
    via Office.latest_crowd_snapshot() on the next office list call.
    """
    serializer = CrowdSnapshotSerializer(data=request.data)

    if serializer.is_valid():
        snapshot = serializer.save()
        logger.info(
            "[CrowdDetect] Office %s | %s people | %s",
            snapshot.office_id,
            snapshot.people_count,
            snapshot.crowd_status,
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    logger.warning("[CrowdDetect] Bad payload: %s", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==========================================================
# LATEST CROWD STATUS FOR ONE OFFICE  ← NEW
# GET /api/crowd/latest/<office_id>/
#
# Flutter can poll this every few seconds for a live badge.
# ==========================================================
@api_view(['GET'])
def crowd_latest(request, office_id):
    """Returns the most recent CrowdSnapshot for the given office."""
    try:
        office = Office.objects.get(pk=office_id)
    except Office.DoesNotExist:
        return Response(
            {'error': 'Office not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    snap = office.latest_crowd_snapshot()
    if snap is None:
        return Response(
            {
                'office_id'   : office_id,
                'people_count': 0,
                'crowd_status': 'Unknown',
                'captured_at' : None,
                'camera_online': False,
            },
            status=status.HTTP_200_OK
        )

    from django.utils import timezone
    from datetime import timedelta
    age = timezone.now() - snap.captured_at
    camera_online = age <= timedelta(minutes=2)

    return Response(
        {
            'office_id'   : office_id,
            'people_count': snap.people_count,
            'crowd_status': snap.crowd_status,
            'captured_at' : snap.captured_at.strftime("%Y-%m-%d %H:%M:%S"),
            'camera_online': camera_online,
        },
        status=status.HTTP_200_OK
    )


# ==========================================================
# CROWD HISTORY FOR ONE OFFICE  ← NEW (optional / analytics)
# GET /api/crowd/history/<office_id>/
#
# Returns last 20 snapshots — useful for a Flutter chart widget.
# ==========================================================
@api_view(['GET'])
def crowd_history(request, office_id):
    try:
        office = Office.objects.get(pk=office_id)
    except Office.DoesNotExist:
        return Response(
            {'error': 'Office not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    snapshots = CrowdSnapshot.objects.filter(office=office)[:20]
    serializer = CrowdSnapshotSerializer(snapshots, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)