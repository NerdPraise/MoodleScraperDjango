from django.shortcuts import render, redirect, get_object_or_404
from .scraperfile import MoodleScraper
from django.contrib.auth import views, login, authenticate
from .forms import RegisterForm, MoodleDetailsForm
from .models import Course, User, MoodleDetails
from django.contrib.auth.decorators import login_required
from python_paystack.objects.transactions import Transaction
from python_paystack.managers import TransactionsManager
from django.views.decorators.http import require_http_methods



def index(request):
    return render(request, "scraper/index.html")

class SigninView(views.LoginView):
    template_name = "registration/login.html"
    # authentication_form = form 
     

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
            MoodleDetails.objects.create(user=user, username=username, password=password)
            person = create_session(request)
            details = person.get_course_links()
            for index in range(0, len(details), 2):
                Course.objects.create(user=user, course_name=details[index+1], course_url=details[index])
    else:
        form = MoodleDetailsForm()
    user_courses = Course.objects.filter(user=user)
    context = {
        "courses":user_courses,
        "user": user,
        "form":form
    }
    return render(request, "scraper/student.html", context)

def create_session(request):
    user = request.user
    detail = MoodleDetails.objects.get(user=user)
    username = detail.username
    password = detail.password
    person = person = MoodleScraper(username, password)
    person.login_student()
    return person

@login_required()
def get_a_course_page(request, id):
    user = request.user
    user_points = user.userprofile.points
    context={"courses":Course.objects.filter(user=user),"user": user}
    if user_points != 0:
        course = get_object_or_404(Course, id=id)
        course_name = (course.course_name)[:6]
        person = create_session(request)
        person.get_course_pages(course=course_name)
        user.userprofile.points -= 1
        user.userprofile.save()
        context["course_name"] = course.course_name
    else:
        context["error"] = "No more points, You need to purchase"
    return render(request, "scraper/student.html", context)

@login_required()
def get_all_courses_page(request):
    user = request.user
    user_points = user.userprofile.points
    context={"courses":Course.objects.filter(user=user),"user": user}
    if user_points != 0:
        person = create_session(request)
        person.get_course_pages()
    else:
        context["error"] = "No more points, You need to purchase"
    return render(request, "scraper/student.html", context)

@login_required()
def make_payment(request):
    user = request.user
    email = user.email
    transaction = Transaction(5000, email)
    transaction_manager = TransactionsManager()
    transaction = transaction_manager.initialize_transaction('STANDARD', transaction)
    return redirect(transaction.authorization_url)

@require_http_methods(["POST"])
def check_payment(request):
    event = request.POST.get("event")
    print(request)
    user = request.user
    email = user.email
    sent_email = request.POST.get("data")["customer"]["email"]
    if email == sent_email and event == "charge.success":
        print("paid")
        user.userprofile.points = 10000000000
        user.userprofile.paid = True
        user.save()
        return redirect("student")
    else:
        return redirect("failure")

"""
Create error channel when logging in create_session, 
"""