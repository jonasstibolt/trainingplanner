from django.urls import path
from . import views

app_name="plans"

urlpatterns = [
    path("", views.plan_list, name="plan_list"),
    path("home/", views.home, name="home"),
    path("new/", views.plan_create, name="plan_create"),
    path("how-to/", views.how_to_create_plan, name="how_to_create_plan"),
    path("<int:pk>/edit/", views.plan_edit, name="plan_edit"),
    path("<int:pk>/set-active/", views.plan_set_active, name="plan_set_active"),
    path("<int:pk>/versions/<int:version_id>/restore/", views.plan_restore_version, name="plan_restore_version"),
    path("<int:pk>/overview/", views.plan_overview, name="plan_overview"),
    path("workouts/<int:pk>/toggle-complete/", views.workout_toggle_complete, name="workout_toggle_complete"),
    path("workouts/<int:pk>/", views.workout_detail, name="workout_detail"),
    path("blocks/<int:pk>/", views.training_block_detail, name="block_detail"),
    path("items/<int:item_id>/sessions/start/", views.start_item_session, name="start_item_session"),
    path("sessions/<int:session_id>/", views.item_session_detail, name="item_session_detail"),
    path("sessions/<int:session_id>/add-set/", views.add_set_to_session, name="add_set_to_session"),
    path("<int:pk>/", views.plan_detail, name="plan_detail"),
    path("sets/<int:set_id>/delete/", views.delete_set, name="delete_set"),
    path("sessions/<int:session_id>/delete/", views.delete_session, name="delete_session"),
    path("exercises/<int:pk>/", views.exercise_detail, name="exercise_detail"),
    path("exercises/", views.exercise_list, name="exercise_list"),
    path("exercises/<int:source_id>/merge/",views.merge_exercises_from_form, name="merge_exercises_from_form"),
    
]
