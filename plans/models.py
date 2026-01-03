from django.db import models
from django.utils import timezone

# Create your models here.

class Tag(models.Model):
    class Scope(models.TextChoices):
        TARGET = "TARGET", "Target"
        FOCUS = "FOCUS", "Focus"
        WORKOUT = "WORKOUT", "Workout"

    name = models.CharField(max_length=50)
    scope = models.CharField(max_length=15, choices=Scope.choices)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["scope", "name"], name="uniq_tag_scope_name")
        ]
        ordering = ["scope", "name"]

    def __str__(self):
        return f"{self.scope}: {self.name}"


class Plan(models.Model):
    title = models.CharField(max_length=200)
    goal = models.TextField(blank=True)  # manually typed each time
    start_date = models.DateField()
    duration_days = models.PositiveIntegerField(default=84)

    is_active = models.BooleanField(default=False)

    targets = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="plans_as_target",
        limit_choices_to={"scope": Tag.Scope.TARGET},
    )

    current_markdown = models.TextField(blank=True, default="")

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


class Block(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name="blocks")

    title = models.CharField(max_length=200)
    start_offset_days = models.PositiveIntegerField()
    duration_days = models.PositiveIntegerField()
    repeat = models.PositiveIntegerField(default=1)
    note = models.TextField(blank=True)

    foci = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="blocks_as_focus",
        limit_choices_to={"scope": Tag.Scope.FOCUS},
    )

    class Meta:
        ordering = ["start_offset_days", "id"]

    def __str__(self):
        return f"{self.plan.title} / {self.title}"


class Workout(models.Model):
    block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name="workouts")

    title = models.CharField(max_length=200)
    offset_days = models.PositiveIntegerField()  # relative to plan start_date
    type = models.CharField(max_length=30, blank=True)
    note = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def mark_complete(self):
        self.completed_at = timezone.now()
    
    def mark_incomplete(self):
        self.completed_at = None


    class Meta:
        ordering = ["offset_days", "id"]

    @property
    def is_completed(self):
        return self.completed_at is not None

    def __str__(self):
        return f"{self.block.title} / D+{self.offset_days} / {self.title}"

class Exercise(models.Model):
    name = models.CharField(max_length=200, unique=True)
    is_unsorted = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class WorkoutItem(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name="items")
    exercise = models.ForeignKey(Exercise, on_delete=models.PROTECT, related_name="workout_items")

    order = models.PositiveIntegerField(default=0)

    sets = models.PositiveIntegerField(null=True, blank=True)
    reps = models.CharField(max_length=50, blank=True)  # "5" or "8-12"
    distance = models.CharField(max_length=50, blank=True)  # "10km" / "400m"
    duration_min = models.PositiveIntegerField(null=True, blank=True)
    intensity = models.CharField(max_length=50, blank=True)  # "Z2" / "RPE7" / "75%1RM"
    rest_sec = models.PositiveIntegerField(null=True, blank=True)

    note = models.TextField(blank=True)

    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="workout_items_as_tag",
        limit_choices_to={"scope": Tag.Scope.WORKOUT},
    )

    alternatives = models.ManyToManyField(
        Exercise,
        blank=True,
        related_name="alternative_for_items",
    )

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.workout.title} - {self.exercise.name}"


class WorkoutItemSession(models.Model):
    workout_item = models.ForeignKey(
        WorkoutItem,
        on_delete=models.CASCADE,
        related_name="sessions",
    )
    performed_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)

    class Meta:
        ordering = ["-performed_at"]

    def __str__(self):
        return f"{self.workout_item.exercise.name} session @ {self.performed_at:%Y-%m-%d}"


class WorkoutSet(models.Model):
    session = models.ForeignKey(
        WorkoutItemSession,
        on_delete=models.CASCADE,
        related_name="sets",
    )
    order = models.PositiveIntegerField()

    # Works for strength sets and cardio intervals
    reps = models.PositiveIntegerField(null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    distance_m = models.PositiveIntegerField(null=True, blank=True)   # e.g. 400
    duration_sec = models.PositiveIntegerField(null=True, blank=True) # e.g. 95
    rest_sec = models.PositiveIntegerField(null=True, blank=True)
    rir_or_rpe = models.PositiveIntegerField(null=True, blank=True)

    note = models.TextField(blank=True)

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(fields=["session", "order"], name="uniq_set_order_per_session")
        ]

    def __str__(self):
        return f"Set {self.order}"
