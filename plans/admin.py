from django.contrib import admin
from .models import Plan, Tag, PlanVersion

# Register your models here.
admin.site.register(PlanVersion)
admin.site.register(Tag)
admin.site.register(Plan)