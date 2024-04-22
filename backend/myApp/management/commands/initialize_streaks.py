# myApp/management/commands/initialize_streaks.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from myApp.models import Streak

class Command(BaseCommand):
    help = "Create missing streaks for existing users"

    def handle(self, *args, **kwargs):
        for user in User.objects.all():
            if not Streak.objects.filter(user=user).exists():
                Streak.objects.create(user=user)
                self.stdout.write(self.style.SUCCESS(f"Created streak for {user.username}"))
            else:
                self.stdout.write(self.style.NOTICE(f"Streak already exists for {user.username}"))