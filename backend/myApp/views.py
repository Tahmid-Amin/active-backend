from django.contrib.auth import authenticate, alogin
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer, DeckSerializer, FlashcardSerializer
from rest_framework import status, viewsets, mixins, permissions, filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.authtoken.models import Token
from .models import Deck, Flashcard, Streak, SpacedRepetitionSchedule
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import HttpResponse

class UserRegistrationViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]  # Typically login does not require authentication

    @action(methods=['post'], detail=False)
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            print(f"User {user.username} is logging in")  # Debug output
            try:
                streak = Streak.objects.get(user=user)
                streak.update_streak()
                print(f"Streak for user {user.username} updated: Current streak is {streak.current_streak}")  # Debug output
            except Streak.DoesNotExist:
                Streak.objects.create(user=user, current_streak=1, last_activity_date=timezone.now().date())
                print(f"New streak created for user {user.username}")  # Debug output

            alogin(request, user)  # This line can be omitted if not using Django's session based authentication
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "message": "Login successful",
                "token": token.key
            }, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    
    
class DeckViewSet(viewsets.ModelViewSet):
    queryset = Deck.objects.all()
    serializer_class = DeckSerializer
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can interact
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']  # Searchable field

    def get_queryset(self):
        # Return decks that belong to the authenticated user
        return self.queryset.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        # do your customization here
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        print(serializer.data)
        return Response(serializer.data)

    def perform_create(self, serializer):
        # Pass request context to serializer
        serializer.save(user=self.request.user)

class FlashcardViewSet(viewsets.ModelViewSet):
    queryset = Flashcard.objects.all()
    serializer_class = FlashcardSerializer
    permission_classes = [IsAuthenticated]


    def perform_create(self, serializer):
        deck_id = self.kwargs.get('deck_pk', None)  # Ensure deck_pk is retrieved correctly
        if not deck_id:
            raise NotFound("Deck ID is required")
        try:
            deck = Deck.objects.get(id=deck_id)  # Confirm the deck exists
        except Deck.DoesNotExist:
            raise NotFound("Deck with the given ID does not exist")  # Return a more descriptive error
        serializer.save(deck=deck)  # Save with the correct deck reference

    def get_queryset(self):
    # Filter flashcards to those in decks owned by the authenticated user
        return Flashcard.objects.filter(deck__user=self.request.user)


class UserStreakView(APIView):
    permission_classes = [IsAuthenticated]  # Require authentication

    def get(self, request):
        user = request.user  # Get the authenticated user
        try:
            # Fetch the first Streak instance related to the user
            streak = user.streaks.first()  # Using 'streaks' as the related name
            return Response({
                'current_streak': streak.current_streak,
                'longest_streak': streak.longest_streak,
            })
        except (Streak.DoesNotExist, AttributeError):
            return Response(
                {'error': 'Streak data not found for this user'},
                status=status.HTTP_404_NOT_FOUND,
            )


class FlashcardReviewView(APIView):
    def get(self, request):
        user = request.user  # Get the authenticated user
        today = timezone.now().date()
        
        # Get flashcards due for review
        schedules = SpacedRepetitionSchedule.objects.filter(
            user=user, 
            next_review_date__lte=today
        ).order_by('next_review_date')  # Sort by the next review date
        
        flashcards = [schedule.flashcard for schedule in schedules]
        
        serializer = FlashcardSerializer(flashcards, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        flashcard_id = request.data.get('flashcard_id')
        score = request.data.get('score', 3)  # 1 to 5 scale, default to 3
        
        try:
            schedule = SpacedRepetitionSchedule.objects.get(
                user=user, 
                flashcard_id=flashcard_id
            )
            schedule.update_interval(score)
            return Response({"message": "Interval updated"}, status=status.HTTP_200_OK)
        except SpacedRepetitionSchedule.DoesNotExist:
            return Response({"error": "Flashcard schedule not found"}, status=status.HTTP_404_NOT_FOUND)

class UserDecksView(APIView):
    def get(self, request):
        user = request.user
        decks = Deck.objects.filter(user=user)
        serializer = DeckSerializer(decks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DeckFlashcardsView(APIView):
    def get(self, request, deck_id):
        user = request.user
        flashcards = Flashcard.objects.filter(deck__id=deck_id, deck__user=user)
        serializer = FlashcardSerializer(flashcards, many=True)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

class FlashcardRatingView(APIView):
    def post(self, request):
        user = request.user
        flashcard_id = request.data.get('flashcard_id')
        score = request.data.get('score', 3)  # Default score of 3 for neutral recall

        try:
            schedule = SpacedRepetitionSchedule.objects.get(user=user, flashcard_id=flashcard_id)
            schedule.update_interval(score)  # Update the interval based on the score
            return Response({"message": "Spaced repetition updated"}, status=status.HTTP_200_OK)
        except SpacedRepetitionSchedule.DoesNotExist:
            return Response({"error": "Spaced repetition schedule not found"}, status=status.HTTP_404_NOT_FOUND)                    