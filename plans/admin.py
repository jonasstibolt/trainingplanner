from django.contrib import admin
from .models import Plan, Block, Workout, WorkoutItem, Exercise, Tag


class BlockInline(admin.TabularInline):
    model = Block
    extra = 0


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("title", "start_date", "duration_days")
    search_fields = ("title", "goal")
    filter_horizontal = ("targets",)
    inlines = [BlockInline]


class WorkoutInline(admin.TabularInline):
    model = Workout
    extra = 0


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ("title", "plan", "start_offset_days", "duration_days", "repeat")
    search_fields = ("title", "plan__title")
    list_filter = ("plan",)
    filter_horizontal = ("foci",)
    inlines = [WorkoutInline]


class WorkoutItemInline(admin.TabularInline):
    model = WorkoutItem
    extra = 0
    autocomplete_fields = ("exercise", "alternatives",)
    filter_horizontal = ("tags", "alternatives",)


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ("title", "block", "offset_days", "type")
    search_fields = ("title", "block__title", "block__plan__title")
    list_filter = ("block__plan", "type")
    inlines = [WorkoutItemInline]


@admin.register(WorkoutItem)
class WorkoutItemAdmin(admin.ModelAdmin):
    list_display = ("workout", "order", "exercise", "sets", "reps", "distance", "intensity")
    list_filter = ("workout__block__plan",)
    search_fields = ("workout__title", "exercise__name")


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("name", "is_unsorted")
    list_filter = ("is_unsorted",)
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("scope", "name")
    list_filter = ("scope",)
    search_fields = ("name",)
