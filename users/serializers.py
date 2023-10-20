from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

from rest_framework import viewsets, permissions, status, generics, serializers
from rest_framework.views import APIView
from rest_framework.response import Response

from knox.views import LoginView as KnoxLoginView
from knox.auth import TokenAuthentication
from knox.models import AuthToken

from django_countries.serializers import CountryFieldMixin

from users.models import Profile, ProfileStatus, UserRelationship


User = get_user_model()


class ProfileStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileStatus
        fields = ["status",]


class ProfileSerializer(CountryFieldMixin, serializers.ModelSerializer):
    followers_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)
    status = ProfileStatusSerializer(read_only=False)
    class Meta:
        model = Profile
        fields = ["country", "bio", "display_image", "status", "followers_count", "following_count"]


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=False)
    class Meta:
        model = User
        fields = ["id", "username", "phone_number", "first_name", "last_name", "email", "is_developer", "is_moderator", "date_joined", "last_login", "profile"]
        #fields = "__all__"


class UserRelationshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRelationship
        fields = '__all__'



class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'phone_number', 'password')
        extra_kwargs = {
            'password': {
                'write_only': True,
              'style': {'input_type': 'password'}
            }
        }
    
    def validate_phone_number(self, phone_number):
        if User.objects.filter(phone_number=phone_number).exists():
            raise ValidationError("Phone number '%s' already exists")
        return phone_number
    
    def validate_username(self, username):
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username '%s already exists" % username)
        return username

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            phone_number=validated_data['phone_number'],
            password=validated_data['password']
        )
        return user




