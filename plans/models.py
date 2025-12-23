from django.db import models

# Create your models here.
class Tag(models.Model):

    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Plan(models.Model):

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name="plans")
    current_markdown = models.TextField()

    def __str__(self):
        return self.title

class PlanVersion(models.Model):

    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name="versions")
    markdown = models.TextField()
    note = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.plan.title} @ {self.created_at:%Y-%m-%d %H:%M}"