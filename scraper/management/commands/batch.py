from django.core.management.base import BaseCommand
from scraper.models import User, MoodleDetails
from scraper.scraperfile import MoodleScraper



class Command(BaseCommand):
    help = "Get all users and their respective courses and go to their pages "

    def handle(self, *args, **options):
        users = User.objects.all()
        for user in users:
            print(user)
            if user.userprofile.paid:
                detail = MoodleDetails.objects.get(user=user)
                username = detail.username
                password = detail.password
                person = MoodleScraper(username, password)
                error = person.login_student()
                if "invalid" in error.lower():
                    with open("user_error.txt") as user_error:
                        user_error.write(f"{user} + {username} is not working")
                    continue
                if user.userprofile.plan == "BB":
                    person.get_course_pages(check=True)
                else:
                    person.get_course_pages()
