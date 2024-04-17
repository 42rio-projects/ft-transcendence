from rest_framework import serializers
from pong.models import User, Game, Tournament
from django.contrib.auth.hashers import make_password


class UserSerializer(serializers.HyperlinkedModelSerializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        try:
            validated_data['password'] = make_password(
                validated_data['password'])
            return super(UserSerializer, self).create(validated_data)
        except Exception as e:
            raise serializers.ValidationError({'error': str(e)}) from e

    def update(self, instance, validated_data):
        try:
            validated_data['password'] = make_password(
                validated_data['password'])
            return super(UserSerializer, self).update(instance, validated_data)
        except Exception as e:
            raise serializers.ValidationError({'error': str(e)}) from e


class GameSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Game
        fields = '__all__'


class TournamentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tournament
        fields = '__all__'
        extra_kwargs = {
            'url': {'lookup_field': 'name'},
        }
