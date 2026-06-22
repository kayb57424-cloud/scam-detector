import json
import logging

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .models import Report

logger = logging.getLogger(__name__)


# ==========================
# SERVE FRONTEND PAGES
# ==========================
def frontend_view(request, page='login'):
    allowed_pages = ['login', 'register', 'index', 'dashboard', 'admin']
    if page not in allowed_pages:
        page = 'login'
    return render(request, f'{page}.html')


# ==========================
# CHECK ADMIN
# ==========================
def is_admin(user):
    return user.is_authenticated and user.is_staff


# ==========================
# ANALYZE MESSAGE
# ==========================
@csrf_exempt
def analyze(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body or b'{}')

        # REPORT DATA
        reported_contact = data.get("reported_contact", "")
        message = data.get("message", "")
        reporter_region = data.get("reporter_region", "Unknown")
        source_type = data.get("source_type", "SMS")
        phone_country = data.get("phone_country", "Unknown")

        # VALIDATION
        if not reported_contact or not message:
            return JsonResponse({"error": "Contact and message required"}, status=400)

        # SCAM KEYWORDS
        scam_keywords = [
            "loan", "win", "prize", "urgent", "money", "click", "free", "offer",
            "bank", "bonus", "verify", "cash", "gift", "password", "account"
        ]

        # SCORING
        score = sum(1 for word in scam_keywords if word in message.lower())

        # RESULT
        if score >= 3:
            result = "Scam"
            reason = "Contains multiple scam-related keywords"
        elif score == 2:
            result = "Suspicious"
            reason = "Contains suspicious wording patterns"
        else:
            result = "Safe"
            reason = "No strong scam indicators detected"

        # SAVE REPORT
        Report.objects.create(
            reporter=(request.user if request.user.is_authenticated else None),
            reporter_region=reporter_region,
            source_type=source_type,
            phone_country=phone_country,
            phone_number=reported_contact,
            message=message,
            result=result
        )

        # REPORT COUNT
        total_reports = Report.objects.filter(phone_number=reported_contact).count()

        return JsonResponse({
            "result": result,
            "reason": reason,
            "reports": total_reports,
            "reporter": (request.user.username if request.user.is_authenticated else "Anonymous")
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.exception("Error in analyze")
        return JsonResponse({"error": "Server error", "detail": str(e)}, status=500)


# ==========================
# CHECK NUMBER
# ==========================
def check_number(request):
    phone = request.GET.get("phone")
    if not phone:
        return JsonResponse({"error": "No phone provided"}, status=400)

    reports = Report.objects.filter(phone_number=phone)
    total_reports = reports.count()

    # RISK LEVEL
    if total_reports >= 5:
        risk = "Scam"
    elif total_reports >= 2:
        risk = "Suspicious"
    else:
        risk = "Safe"

    # MOST COMMON REGION
    top_region = (reports.values("reporter_region").annotate(total=Count("reporter_region")).order_by("-total").first())
    reporter_region = (top_region["reporter_region"] if top_region else "Unknown")

    # COUNTRY
    top_country = (reports.values("phone_country").annotate(total=Count("phone_country")).order_by("-total").first())
    country = (top_country["phone_country"] if top_country else "Unknown")

    return JsonResponse({
        "phone": phone,
        "reports": total_reports,
        "risk": risk,
        "reporter_region": reporter_region,
        "country": country
    })


# ==========================
# REGISTER USER
# ==========================
@csrf_exempt
def register(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body or b'{}')

        username = data.get("username")
        email = data.get("email")
        phone = data.get("phone")
        password = data.get("password")

        # VALIDATION
        if not all([username, email, phone, password]):
            return JsonResponse({"error": "All fields are required"}, status=400)

        # USER EXISTS
        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username already exists"}, status=409)

        # EMAIL EXISTS
        if User.objects.filter(email=email).exists():
            return JsonResponse({"error": "Email already exists"}, status=409)

        # CREATE USER
        user = User.objects.create_user(username=username, email=email, password=password)

        # SAVE PHONE (stored in first_name for now)
        user.first_name = phone
        user.save()

        logger.info("Registered new user: %s (%s)", username, email)

        return JsonResponse({
            "message": "Registration successful",
            "user": {"username": user.username, "email": user.email, "phone": user.first_name}
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.exception("Error during registration")
        return JsonResponse({"error": "Server error", "detail": str(e)}, status=500)


# ==========================
# LOGIN USER
# ==========================
@csrf_exempt
def user_login(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body or b'{}')
        username = data.get("username")
        password = data.get("password")

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({
                "message": "Login successful",
                "user": user.username,
                "email": user.email,
                "phone": user.first_name,
                "is_admin": user.is_staff
            })
        return JsonResponse({"error": "Invalid credentials"}, status=401)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.exception("Error during login")
        return JsonResponse({"error": "Server error", "detail": str(e)}, status=500)


# ==========================
# CHECK AUTH
# ==========================
@csrf_exempt
def check_auth(request):
    return JsonResponse({
        "authenticated": request.user.is_authenticated,
        "user": request.user.username if request.user.is_authenticated else None,
        "email": request.user.email if request.user.is_authenticated else None,
        "phone": request.user.first_name if request.user.is_authenticated else None,
        "is_admin": request.user.is_staff if request.user.is_authenticated else False
    })


# ==========================
# LOGOUT
# ==========================
@csrf_exempt
def user_logout(request):
    logout(request)
    return JsonResponse({"message": "Logged out successfully"})


# ==========================
# DASHBOARD
# ==========================
def dashboard(request):
    if not is_admin(request.user):
        return JsonResponse({"error": "Admin login required"}, status=403)

    data = (Report.objects.values("phone_number").annotate(total=Count("phone_number")).order_by("-total"))
    return JsonResponse(list(data), safe=False)


# ==========================
# REGION STATS
# ==========================
def region_stats(request):
    if not is_admin(request.user):
        return JsonResponse({"error": "Admin login required"}, status=403)
    data = (Report.objects.values("reporter_region").annotate(total=Count("reporter_region")).order_by("-total"))
    return JsonResponse(list(data), safe=False)


# ==========================
# ALL REPORTS
# ==========================
def all_reports(request):
    if not is_admin(request.user):
        return JsonResponse({"error": "Admin login required"}, status=403)

    reports = Report.objects.all().values(
        "id", "phone_number", "phone_country", "source_type", "message",
        "result", "reporter_region", "created_at"
    )
    return JsonResponse(list(reports), safe=False)


# ==========================
# ADMIN SUMMARY
# ==========================
def admin_summary(request):
    if not is_admin(request.user):
        return JsonResponse({"error": "Admin login required"}, status=403)

    total = Report.objects.count()
    scams = Report.objects.filter(result="Scam").count()
    suspicious = Report.objects.filter(result="Suspicious").count()
    safe = Report.objects.filter(result="Safe").count()

    return JsonResponse({"total": total, "scam": scams, "suspicious": suspicious, "safe": safe})


# ==========================
# DELETE REPORT
# ==========================
@csrf_exempt
def delete_report(request, report_id):
    if not is_admin(request.user):
        return JsonResponse({"error": "Admin login required"}, status=403)

    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        report = Report.objects.get(id=report_id)
        report.delete()
        return JsonResponse({"message": "Report deleted"})
    except Report.DoesNotExist:
        return JsonResponse({"error": "Report not found"}, status=404)
    except Exception as e:
        logger.exception("Error deleting report")
        return JsonResponse({"error": "Server error", "detail": str(e)}, status=500)


# ==========================
# MAKE ADMIN (protected)
# ==========================
def make_admin(request):
    if not is_admin(request.user):
        return JsonResponse({"error": "Admin login required"}, status=403)

    users = User.objects.all()
    return JsonResponse({"users": list(users.values("id", "username", "email"))})