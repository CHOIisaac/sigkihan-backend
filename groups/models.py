# from django.db import models
# from django.contrib.auth.models import User
#
#
# class Group(models.Model):
#     name = models.CharField(max_length=100)
#     owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_groups")
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return self.name
#
#
# class GroupMember(models.Model):
#     group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="members")
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="group_memberships")
#     role = models.CharField(max_length=20, choices=[("admin", "Admin"), ("member", "Member")], default="member")
#     joined_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return f"{self.user.username} in {self.group.name}"