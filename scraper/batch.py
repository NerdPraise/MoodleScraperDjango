from .models import User, MoodleDetails
from .scraperfile import MoodleScraper
import request

def get_batch_items(request):
    user = User.objects.all()
    for person in user:
        if user.userprofile.paid:
            detail = MoodleDetails.objects.get(user=user)
            username = detail.username
            password = detail.password
            person = MoodleScraper(username, password)
            error = person.login_student()
            if "invalid" in error.lower():
                raise Exception(f"{user} + {username} is not working")
            if user.userprofile.plan == "BB":
                person.get_course_pages(check=True)
            else:
                person.get_course_pages()


get_batch_items()
    