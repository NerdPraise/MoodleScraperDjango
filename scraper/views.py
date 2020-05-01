import json
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .scraperfile import MoodleScraper
from django.contrib.auth import views, login, authenticate
from .forms import RegisterForm, MoodleDetailsForm, SignInForm
from .models import Course, User, MoodleDetails
from django.contrib.auth.decorators import login_required
from python_paystack.objects.transactions import Transaction
from python_paystack.managers import TransactionsManager
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime



def index(request):
    return render(request, "scraper/index.html")

class SigninView(views.LoginView):
    template_name = "registration/login.html"
    authentication_form = SignInForm
     

def register(request):
    if request.POST:
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data["email"] 
            password =  form.cleaned_data["password1"]
            user = authenticate(request, email=email, password=password)
            login(request, user)
            return redirect("student") 
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form":form})

def logout(request):
    return views.logout_then_login(request)

@login_required()
def student(request):
    user = request.user
    if request.POST:
        form = MoodleDetailsForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["matric_num"]
            password = form.cleaned_data["password"]
            context = {}
            
            try:
                MoodleDetails.objects.get(user=user)
            except MoodleDetails.DoesNotExist:
                MoodleDetails.objects.create(user=user, username=username, password=password)
                person, error = create_session(request)
                if "invalid" in error:
                    print(f"Invalid login : {error}" )
                    context["error"] = error
                    return render(request, "scraper/student.html", context)
                details = person.get_course_links()
                for index in range(0, len(details), 2):
                    Course.objects.create(user=user, course_name=details[index+1], course_url=details[index])
    else:
        form = MoodleDetailsForm()
    user_courses = Course.objects.filter(user=user)
    user_course_one = [course for course in user_courses[::2]]
    print(user_course_one)
    user_course_two = [course for course in user_courses[1::2]]
    last_login = user.last_login
    last_login = last_login.strftime("%b %d, %Y")
    print(last_login)
    context = {
        "course_one":user_course_one,
        "course_two":user_course_two,
        "user": user,
        "form":form,
        "last_login":last_login,
    }
    return render(request, "scraper/student.html", context)

def create_session(request):
    user = request.user
    detail = MoodleDetails.objects.get(user=user)
    username = detail.username
    password = detail.password
    person = MoodleScraper(username, password)
    error = person.login_student()
    return person, error

@login_required()
def get_a_course_page(request, id):
    user = request.user
    user_points = user.userprofile.points
    if user_points != 0:
        course = get_object_or_404(Course, id=id)
        course_name = (course.course_name)[:6]
        person, error = create_session(request)
        if "invalid" in error:
            data = {"error":error}
            return JsonResponse(data)           
        person.get_course_pages(course=course_name)
        user.userprofile.points -= 1
        user.userprofile.save()
        data = {"success":f"Just went to {course.course_name}"}
    else:
        data = {"error":"No more points, You need to purchase"}
    return JsonResponse(data)

@login_required()
def get_all_courses_page(request): # Make this a form
    if request.POST:
        check = request.POST.get("check-quiz")
        user = request.user
        user_points = user.userprofile.points
        context={"courses":Course.objects.filter(user=user),"user": user}
        print(check)

        if user_points != 0:
            person, error = create_session(request)
            if "invalid" in error:
                print(f"Invalid login : {error}" )
                context["error"] = error
                return render(request, "scraper/student.html", context)
            if check:
                person.get_course_pages(True)
            else:
                person.get_course_pages()
        else:
            context["error"] = "No more points, You need to purchase"
        return render(request, "scraper/student.html", context)


def download_course(request, id):
    course = course = get_object_or_404(Course, id=id)
    course_name = (course.course_name)[:6]
    person, error = create_session()
    context={"courses":Course.objects.filter(user=user),"user": user}
    if "invalid" in error:
        print(f"Invalid login : {error}" )
        context["error"] = error
        return render(request, "scraper/student.html", context)
    person.download_course(course_name)
    return render(request, "scraper/student.html", context)


@login_required()
def make_payment(request, id):
    user = request.user
    email = user.email
    if id == 1:
        transaction = Transaction(50000, email)
    elif id == 2:
        transaction = Transaction(70000, email)
    transaction_manager = TransactionsManager()
    transaction = transaction_manager.initialize_transaction('STANDARD', transaction)
    return redirect(transaction.authorization_url)


@csrf_exempt
@require_http_methods(["POST"])
def check_payment(request):
    if request.method == "POST":
        response = json.loads(request.body)
        event = response["event"]
        status = response["data"]["status"]
        sent_email = response["data"]["customer"]["email"]
        plan = response["data"]["plan"]["name"]
        amount_paid = response["data"]["amount"]
        try:
            user = get_object_or_404(User, email=sent_email)
            if event == "charge.success" and status == "success":
                print("paid")
                user.userprofile.points = 10000000000
                if plan == "basic" and amount_paid == 70000:
                    user.userprofile.plan = "BC"
                else:
                    user.userprofile.plan == "BB"
                user.userprofile.paid = True
                user.save()
        except:
            HttpResponse(status_code=400)       
    
    return HttpResponse('success')

def show_download(request):
    pass

"""
Make sure redirecting in Studdent doesn't cause errors-checked
Create error channel when logging in create_session, done, remains test
"""


