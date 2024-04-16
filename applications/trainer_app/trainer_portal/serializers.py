from rest_framework import serializers
from .models import TimeSlot
from django.contrib.auth.models import User

class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ['professional_id', 'time']


class UserSerializer(serializers.ModelSerializer):
    #rename username to name to make applications compatible
    name = serializers.CharField(source='username')

    class Meta:
        model = User
        fields = ('name', 'email', 'id')
