# from django.db import models
# from django.contrib.auth.models import User
# from groups.models import Group
#
#
# class Refrigerator(models.Model):
#     name = models.CharField(max_length=100)
#     owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_refrigerators")
#     groups = models.ManyToManyField(Group, related_name="refrigerators", blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return self.name
#
#
# class Item(models.Model):
#     refrigerator = models.ForeignKey(Refrigerator, on_delete=models.CASCADE, related_name="items")
#     name = models.CharField(max_length=100)
#     quantity = models.PositiveIntegerField(default=1)
#     category = models.CharField(max_length=50, choices=[
#         ("Vegetable", "Vegetable"),
#         ("Meat", "Meat"),
#         ("Dairy", "Dairy"),
#         ("Other", "Other")
#     ])
#     expiry_date = models.DateField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return self.name