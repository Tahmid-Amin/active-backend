from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from datetime import date, timedelta

class Deck(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='decks')
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

class Flashcard(models.Model):
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='flashcards')
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

class Streak(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='streaks')
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)

    def update_streak(self):
        # Calculate the difference between today and the last activity date
        today = date.today()
        if self.last_activity_date == today:
            # If the user has already interacted today, return without updating
            return
        elif self.last_activity_date == today - timedelta(days=1):
            # If the user interacted yesterday, increase the streak
            self.current_streak += 1
        else:
            # If the user missed a day, reset the current streak
            self.current_streak = 1
        
        # Update the longest streak if necessary
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak

        # Update the last activity date
        self.last_activity_date = today
        self.save()

    def __str__(self):
        return f"{self.user.username} - Current: {self.current_streak}, Longest: {self.longest_streak}"

# @receiver(post_save, sender=User)
# def create_streak(sender, instance, created, **kwargs):
#     if created:
#         Streak.objects.create(user=instance)

# Connect signal to update streak on user login
# def update_streak_on_login(sender, user, **kwargs):
#     try:
#         streak = Streak.objects.get(user=user)
#         streak.update_streak()
#     except Streak.DoesNotExist:
#         pass  # No streak found for user

# def update_streak_on_login(sender, user, **kwargs):
#     print(f"User {user.username} is logging in")  # Debug output
#     try:
#         streak = Streak.objects.get(user=user)
#         streak.update_streak()
#         print(f"Streak for user {user.username} updated: Current streak is {streak.current_streak}")  # Debug output
#     except Streak.DoesNotExist:
#         # Create a new streak if it doesn't exist
#         Streak.objects.create(user=user, current_streak=1, last_activity_date=timezone.now().date())
#         print(f"New streak created for user {user.username}")  # Debug output

# user_logged_in.connect(update_streak_on_login)


# Spaced Repetition Schedule Model
class SpacedRepetitionSchedule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='repetition_schedules')
    flashcard = models.ForeignKey(Flashcard, on_delete=models.CASCADE)
    next_review_date = models.DateField()  # Date for the next review
    interval = models.IntegerField(default=1)  # Initial interval, in days
    easiness_factor = models.FloatField(default=2.5)  # Easiness factor for the repetition

    def calculate_next_review_date(self):
        return datetime.date.today() + datetime.timedelta(days=self.interval)

    def update_interval(self, score):
        # Calculate the new interval using SM2 formula (from SuperMemo)
        self.interval = max(1, int(self.interval * self.easiness_factor))
        self.easiness_factor = max(1.3, self.easiness_factor + (0.1 - (5 - score) * (0.08 + (5 - score) * 0.02)))
        self.next_review_date = self.calculate_next_review_date()
        self.save()

    def __str__(self):
        return f"{self.flashcard.question} - Next review: {self.next_review_date}"


# Create your models here.