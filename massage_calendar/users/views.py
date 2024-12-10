from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import CustomUser
from .serializers import UserSerializer, UserRegistrationSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet to handle user-related actions, including registration, login,
    retrieving the currently authenticated user, and logout functionality.
    """
    queryset = CustomUser.objects.all()

    def get_serializer_class(self):
        """
        Determine which serializer to use based on the action being performed.
        - Use `UserRegistrationSerializer` for user creation (registration).
        - Use `UserSerializer` for all other actions.
        """
        if self.action == 'create':
            return UserRegistrationSerializer
        return UserSerializer

    def get_permissions(self):
        """
         Determine which permissions to apply based on the action being performed.
         - Allow unrestricted access (`AllowAny`) for `create` (registration) and `login` actions.
         - Require authentication (`IsAuthenticated`) for all other actions.
         """
        if self.action in ['create', 'login']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        """
        Register a new user.
        - Validates the provided user data using `UserRegistrationSerializer`.
        - Creates a new user if the data is valid.
        - Generates JWT tokens (access and refresh) for the newly registered user.
        - Returns a response with the user details and tokens upon successful registration.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'message': 'User registered successfully',
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        """
        Login a user and return JWT tokens.
        - Authenticates the user based on the provided username and password.
        - Returns the user's data and tokens if authentication is successful.
        - Returns an error response if authentication fails.
        """
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({
                'error': 'Please provide both username and password'
            }, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            })
        else:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )

    @action(detail=False, methods=['get'])
    def current_user(self, request):
        """
        Retrieve details of the currently authenticated user.
        - Returns the authenticated user's ID, username, and email.
        """
        user = request.user
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
        })

    @action(detail=False, methods=['post'])
    def logout(self, request):
        """
        Handle logout for authenticated users.
        - Currently, this only returns a success message.
        - Additional functionality (e.g., token blacklisting) can be added for JWT-based logout.
        """
        # Additional token blacklisting can be added here if using JWT.
        return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)
