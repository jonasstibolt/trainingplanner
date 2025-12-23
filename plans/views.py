from django.shortcuts import render, get_object_or_404, redirect
from .models import Plan, PlanVersion
from .forms import PlanForm
from django.views.decorators.http import require_POST



def plan_list(request):
    plans = Plan.objects.all()
    return render(request, "plans/plan_list.html", {"plans": plans})

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
            form.save_m2m()  # harmless now, crucial later when we add tags editing
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
