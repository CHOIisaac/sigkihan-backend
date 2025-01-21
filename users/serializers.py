from rest_framework import serializers

from .models import ProfileImage, CustomUser


class ProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileImage
        fields = ['id', 'name', 'image']


class UserSerializer(serializers.ModelSerializer):
    image = ProfileImageSerializer()

    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'image']


class UserDetailSerializer(serializers.ModelSerializer):
    image = ProfileImageSerializer()

    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'email', 'image']
        # fields = ['id', 'name', 'email', 'password', 'kakao_id', 'image', 'is_social', 'is_active', 'is_staff', 'is_superuser', 'created_at', 'updated_at']
        # read_only_fields = ['is_social', 'created_at', 'updated_at']


class UserUpdateSerializer(serializers.ModelSerializer):
    image_id = serializers.IntegerField(write_only=True, required=False, help_text="ProfileImage ID")
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['name', 'image_id', 'profile_image']

    def get_profile_image(self, obj) -> str:
        """
        프로필 이미지 정보를 반환
        """
        if obj.image:
            return {
                "id": obj.image.id,
                "name": obj.image.name,
                "image_url": obj.image.image.url,
            }
        return None

    def validate_image_id(self, value):
        """
        image_id 유효성 검사
        """
        try:
            ProfileImage.objects.get(id=value)
        except ProfileImage.DoesNotExist:
            raise serializers.ValidationError("Invalid image_id. ProfileImage does not exist.")
        return value

    def update(self, instance, validated_data):
        """
        사용자 정보 업데이트
        """
        image_id = validated_data.pop('image_id', None)
        if image_id:
            instance.image = ProfileImage.objects.get(id=image_id)

        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance


class TestRequestSerializer(serializers.Serializer):
    example_field = serializers.CharField(
        required=True,
        help_text="An example string field",
    )
