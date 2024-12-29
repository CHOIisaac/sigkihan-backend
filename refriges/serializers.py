from rest_framework import serializers
from refriges.models import Refrigerator, RefrigeratorAccess, RefrigeratorMemo, RefrigeratorInvitation


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


class RefrigeratorMemoSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = RefrigeratorMemo
        fields = ['id', 'title', 'content', 'created_at', 'updated_at', 'user']


class RefrigeratorInvitationSerializer(serializers.ModelSerializer):
    inviter = serializers.StringRelatedField()  # 초대한 사람의 이름
    refrigerator = serializers.StringRelatedField()  # 냉장고 이름

    class Meta:
        model = RefrigeratorInvitation
        fields = ['id', 'inviter', 'refrigerator', 'status', 'created_at']