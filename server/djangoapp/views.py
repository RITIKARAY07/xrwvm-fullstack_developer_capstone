
import json
import logging

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import CarMake, CarModel
from .restapis import get_request, analyze_review_sentiments, post_review

logger = logging.getLogger(__name__)


def read_json_body(request):
    try:
        return json.loads(request.body or b"{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


@csrf_exempt
def login_user(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data = read_json_body(request)
    if not isinstance(data, dict):
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    username = data.get("userName", "")
    password = data.get("password", "")
    user = authenticate(request, username=username, password=password)

    if user is None:
        return JsonResponse({
            "userName": username,
            "status": "Invalid credentials",
        }, status=401)

    login(request, user)
    return JsonResponse({
        "userName": username,
        "status": "Authenticated",
    })


def logout_request(request):
    logout(request)
    return JsonResponse({"status": "Logged out"})


@csrf_exempt
def registration(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data = read_json_body(request)
    if not isinstance(data, dict):
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    username = data.get("userName", "").strip()
    password = data.get("password", "")
    first_name = data.get("firstName", "").strip()
    last_name = data.get("lastName", "").strip()

    if not username or not password:
        return JsonResponse({
            "status": "error",
            "message": "Username and password are required",
        }, status=400)

    if User.objects.filter(username=username).exists():
        return JsonResponse({
            "status": "error",
            "message": "Username already exists",
        }, status=409)

    user = User.objects.create_user(
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )

    return JsonResponse({
        "status": "Account created",
        "userName": user.username,
    }, status=201)


def get_dealerships(request, state=None):
    endpoint = f"fetchDealers/{state}" if state else "fetchDealers"
    dealers = get_request(endpoint)

    if dealers is None:
        return JsonResponse({
            "status": 503,
            "error": "Dealership service is unavailable",
            "dealers": [],
        }, status=503)

    return JsonResponse({"status": 200, "dealers": dealers})


def get_dealer_reviews(request, dealer_id):
    reviews = get_request(f"fetchReviews/dealer/{dealer_id}")

    if reviews is None:
        return JsonResponse({
            "status": 503,
            "error": "Review service is unavailable",
            "reviews": [],
        }, status=503)

    return JsonResponse({"status": 200, "reviews": reviews})


def get_dealer_details(request, dealer_id):
    dealer = get_request(f"fetchDealer/{dealer_id}")

    if dealer is None:
        return JsonResponse({
            "status": 503,
            "error": "Dealership service is unavailable",
            "dealer": [],
        }, status=503)

    if isinstance(dealer, dict):
        dealer = [dealer]

    return JsonResponse({"status": 200, "dealer": dealer})


@csrf_exempt
def add_review(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data = read_json_body(request)
    if not isinstance(data, dict):
        return JsonResponse({"status": 400, "error": "Invalid JSON"}, status=400)

    required = [
        "name", "dealership", "review", "purchase",
        "purchase_date", "car_make", "car_model", "car_year",
    ]
    if any(field not in data for field in required):
        return JsonResponse({
            "status": 400,
            "error": "Missing required review fields",
        }, status=400)

    sentiment = analyze_review_sentiments(data["review"])
    saved_review = post_review(data)

    if saved_review is None:
        return JsonResponse({
            "status": 503,
            "error": "Could not save review",
        }, status=503)

    return JsonResponse({
        "status": 200,
        "sentiment": sentiment,
        "review": saved_review,
    })


def get_cars(request):
    cars = CarModel.objects.select_related("car_make").all().order_by(
        "car_make__name", "name", "year"
    )

    return JsonResponse({
        "CarModels": [
            {
                "CarMake": car.car_make.name,
                "CarModel": car.name,
                "Year": car.year,
                "Type": car.type,
            }
            for car in cars
        ]
    })
