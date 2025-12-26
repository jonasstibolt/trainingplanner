from django.urls import path
from . import views

app_name="plans"

urlpatterns = [
    path("", views.plan_list, name="plan_list"),
    path("new/", views.plan_create, name="plan_create"),
    path("<int:pk>/", views.plan_detail, name="plan_detail"),
    path("<int:pk>/edit/", views.plan_edit, name="plan_edit"),
    path("<int:pk>/versions/<int:version_id>/restore/", views.plan_restore_version, name="plan_restore_version"),
    path("<int:pk>/overview/", views.plan_overview, name="plan_overview"),

]
