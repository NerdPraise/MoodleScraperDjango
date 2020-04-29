from django.contrib import admin
from .models import Course, User, MoodleDetails, UserProfile
# Register your models here.


class CourseAdmin(admin.ModelAdmin):
    fields = ("user", "course_name", "course_url","refresh_time")
    list_display = ("user", "course_name")

class MoodleDetailsAdmin(admin.ModelAdmin):
    list_display=("username", "password")

admin.site.register(User)
admin.site.register(Course, CourseAdmin)
admin.site.register(MoodleDetails, MoodleDetailsAdmin)
admin.site.register(UserProfile)