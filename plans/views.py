from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import Plan, PlanVersion, Tag, Workout, Block, WorkoutItem, WorkoutItemSession, WorkoutSet, Exercise
from .forms import PlanForm
from django.views.decorators.http import require_POST
from django.db import models, transaction



def plan_list(request):
    q = request.GET.get("q", "").strip()
    selected_tags = request.GET.getlist("tags")

    plans = Plan.objects.all()

    if q:
        plans = plans.filter(
            Q(title__icontains=q)
            | Q(goal__icontains=q)
            | Q(current_markdown__icontains=q)
        )

    if selected_tags:
        plans = plans.distinct().filter(tags__name__in=selected_tags)

    tags = Tag.objects.order_by("name")

    return render(request, "plans/plan_list.html", {
        "plans": plans,
        "tags": tags,
        "q": q,
        "selected_tags": selected_tags,
    })



def plan_detail(request, pk):
    plan = get_object_or_404(Plan, pk=pk)
    versions = plan.versions.all()
    return render(request, "plans/plan_detail.html", {"plan": plan, "versions": versions})

def plan_edit(request, pk):
    plan = get_object_or_404(Plan, pk=pk)

    if request.method == "POST":
        old_markdown = plan.current_markdown  # snapshot before binding/saving
        form = PlanForm(request.POST, instance=plan)

        if form.is_valid():
            updated_plan = form.save(commit=False)

            # Only version if markdown changed
            if updated_plan.current_markdown != old_markdown:
                PlanVersion.objects.create(
                    plan=plan,
                    markdown=old_markdown,
                    note="Edited via UI",
                )

            updated_plan.save()
            form.save_m2m()
            return redirect("plans:plan_detail", pk=plan.pk)
    else:
        form = PlanForm(instance=plan)

    return render(request, "plans/plan_edit.html", {
        "plan": plan,
        "form": form,
    })

def plan_create(request):
    if request.method == "POST":
        form = PlanForm(request.POST)
        if form.is_valid():
            plan = form.save()
            return redirect("plans:plan_detail", pk=plan.pk)
    else:
        form = PlanForm()

    return render(request, "plans/plan_create.html", {"form": form})

@require_POST
def plan_restore_version(request, pk, version_id):
    plan = get_object_or_404(Plan, pk=pk)
    version = get_object_or_404(PlanVersion, pk=version_id, plan=plan)

    # Make restore reversible: snapshot current state first
    PlanVersion.objects.create(
        plan=plan,
        markdown=plan.current_markdown,
        note=f"Auto-save before restoring {version.created_at:%Y-%m-%d %H:%M}",
    )

    plan.current_markdown = version.markdown
    plan.save(update_fields=["current_markdown"])

    return redirect("plans:plan_detail", pk=plan.pk)

def plan_overview(request, pk):
    plan = get_object_or_404(Plan, pk=pk)
    return render(request, "plans/plan_overview.html", {"plan": plan})

@require_POST
def workout_toggle_complete(request, pk):
    workout = get_object_or_404(Workout, pk=pk)

    if workout.is_completed:    
        workout.mark_incomplete()
    else:
        workout.mark_complete()

    workout.save()
    return redirect("plans:workout_detail", pk=workout.pk)

def workout_detail(request, pk):
    workout = get_object_or_404(Workout, pk=pk)
    return render(request, "plans/workout_detail.html", {"workout": workout})


def training_block_detail(request, pk):
    training_block = get_object_or_404(Block, pk=pk)
    return render(request, "plans/block_detail.html", {"training_block": training_block, "DEBUG": "HIT_BLOCK_DETAIL"})


@require_POST
def start_item_session(request, item_id):
    item = get_object_or_404(WorkoutItem, pk=item_id)
    session = WorkoutItemSession.objects.create(workout_item=item)
    return redirect("plans:item_session_detail", session_id=session.pk)

def item_session_detail(request, session_id):
    session = get_object_or_404(WorkoutItemSession, pk=session_id)
    return render(request, "plans/item_session_detail.html", {"session": session})

@require_POST
def add_set_to_session(request, session_id):
    session = get_object_or_404(WorkoutItemSession, pk=session_id)

    # auto-increment order
    next_order = (session.sets.aggregate(models.Max("order"))["order__max"] or 0) + 1

    reps = request.POST.get("reps") or None
    weight_kg = request.POST.get("weight_kg") or None
    distance_m = request.POST.get("distance_m") or None
    duration_sec = request.POST.get("duration_sec") or None
    rest_sec = request.POST.get("rest_sec") or None
    note = request.POST.get("note", "").strip()

    WorkoutSet.objects.create(
        session=session,
        order=next_order,
        reps=int(reps) if reps else None,
        weight_kg=weight_kg if weight_kg else None,
        distance_m=int(distance_m) if distance_m else None,
        duration_sec=int(duration_sec) if duration_sec else None,
        rest_sec=int(rest_sec) if rest_sec else None,
        note=note,
    )

    return redirect("plans:item_session_detail", session_id=session.pk)

@require_POST
def delete_set(request, set_id):
    s = get_object_or_404(WorkoutSet, pk=set_id)
    session_id = s.session_id
    s.delete()
    return redirect("plans:item_session_detail", session_id=session_id)

@require_POST
def delete_session(request, session_id):
    session = get_object_or_404(WorkoutItemSession, pk=session_id)
    workout_id = session.workout_item.workout_id
    session.delete()
    return redirect("plans:workout_detail", pk=workout_id)

def exercise_detail(request, pk):
    exercise = get_object_or_404(Exercise, pk=pk)

    if request.method == "POST" and exercise.is_unsorted:
        target_id = request.POST.get("target_id")
        return redirect("plans:merge_exercises", source_id=exercise.pk, target_id=target_id)

    sessions = (
        WorkoutItemSession.objects
        .filter(workout_item__exercise=exercise)
        .select_related("workout_item__workout")
        .prefetch_related("sets")
    )

    return render(request, "plans/exercise_detail.html", {
        "exercise": exercise,
        "sessions": sessions,
    })


def exercise_list(request):
    q = request.GET.get("q", "").strip()
    exercises = Exercise.objects.all()

    if q:
        exercises = exercises.filter(name__icontains=q)

    exercises = exercises.order_by("name")

    return render(request, "plans/exercise_list.html", {
        "exercises": exercises,
        "q": q,
    })

@require_POST
def merge_exercises(request, source_id, target_id):
    if source_id == target_id:
        return redirect("plans:exercise_detail", pk=target_id)

    source = get_object_or_404(Exercise, pk=source_id)
    target = get_object_or_404(Exercise, pk=target_id)

    with transaction.atomic():
        # move all workout items
        WorkoutItem.objects.filter(exercise=source).update(exercise=target)

        # optional: keep canonical flags clean
        if source.is_unsorted and not target.is_unsorted:
            pass

        source.delete()

    return redirect("plans:exercise_detail", pk=target.pk)

@require_POST
def merge_exercises_from_form(request, source_id):
    target_id = int(request.POST["target_id"])
    return merge_exercises(request, source_id=source_id, target_id=target_id)
