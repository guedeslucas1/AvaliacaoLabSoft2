from rest_framework import serializers
from .models import TimeSlot
from django.contrib.auth.models import User

class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ['professional_id', 'time']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'id')
