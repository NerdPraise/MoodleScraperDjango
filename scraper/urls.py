from django.urls import path
from . import views
from .views import SigninView

urlpatterns = [
    path("", views.index, name="home"),
    path("register", views.register, name="register"),
    path("login", SigninView.as_view(), name="login"),
    path("logout", views.logout, name="logout"),
    path("student", views.student, name="student"),
    path("student/course/<int:id>", views.get_a_course_page, name="one_course"),
    path("student/allcourse", views.get_all_courses_page, name="all_course"),
    path("student/pay", views.make_payment, name="payment"),
    path("student/paid", views.check_payment, name="paid"),
    path("student/dwnld-<int:id>", views.download_course, name="download"),
    
]