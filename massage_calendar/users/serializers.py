from rest_framework import serializers
from .models import CustomUser


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for registering new users.
    - Handles validation for passwords and uniqueness of email/username.
    - Creates a new user after validation.
    """
    password2 = serializers.CharField(write_only=True)

    class Meta:
        """
        Meta class to define model and fields for the serializer.
        """
        model = CustomUser
        fields = ('id', 'username', 'email', 'password', 'password2')
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }

    def validate(self, data):
        """
        Custom validation logic:
        - Ensure passwords match.
        - Check if the email is already registered.
        - Check if the username is already taken.
        """
        # Check if passwords match
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords don't match")

        # Check if email already exists
        if CustomUser.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Email already registered")

        # Check if username already exists
        if CustomUser.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError("Username already taken")

        return data

    def create(self, validated_data):
        """
        Custom user creation logic:
        - Remove password2 from the validated data.
        - Hash the user's password before saving it to the database.
        """
        validated_data.pop('password2')
        password = validated_data.pop('password')

        # Create user
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving user information.
    - Used for non-sensitive user data like ID, username, and email.
    - Read-only fields ensure no accidental modification of data.
    """
    class Meta:
        """
        Meta class to define model and fields for the serializer.
        """
        model = CustomUser
        fields = ('id', 'username', 'email')
        read_only_fields = ('id',)