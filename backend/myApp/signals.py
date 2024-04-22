from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from myApp.models import Streak

@receiver(post_save, sender=User)
def create_streak(sender, instance, created, **kwargs):
    if created:
        Streak.objects.create(user=instance)

# @receiver(user_logged_in)
# def update_streak_on_login(sender, user, **kwargs):
#     print(f"User {user.username} is logging in")  # Debug output
#     try:
#         streak = Streak.objects.get(user=user)
#         streak.update_streak()
#         print(f"Streak for user {user.username} updated: Current streak is {streak.current_streak}")  # Debug output
#     except Streak.DoesNotExist:
#         Streak.objects.create(user=user, current_streak=1, last_activity_date=timezone.now().date())
#         print(f"New streak created for user {user.username}")  # Debug output