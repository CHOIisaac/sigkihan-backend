from rest_framework import serializers
from refriges.models import Refrigerator, RefrigeratorAccess


class RefrigeratorSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    member = serializers.SerializerMethodField()

    class Meta:
        model = Refrigerator
        # fields = ['id', 'name']
        fields = ['id', 'name', 'owner', 'member']


    def get_owner(self, obj) -> str:
        owner = obj.access_list.filter(role='owner').first()
        return {
            'id': owner.user.id,
            'email': owner.user.email,
            'name': owner.user.name
        } if owner else None

    def get_member(self, obj) -> list[str]:
        members = obj.access_list.filter(role='member')
        return [
            {
                'id': members.user.id,
                'email': members.user.email,
                'name': members.user.name
            }
            for member in members
        ]

