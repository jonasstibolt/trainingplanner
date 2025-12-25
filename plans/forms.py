from django import forms
from .models import Plan, Tag 

DEFAULT_MARKDOWN = """# New 3-month plan

## Overview
- Goal:
- Start date:
- Notes:

## Month 1
### Week 1
- 
"""

class PlanForm(forms.ModelForm):

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.order_by("name"),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Plan
        fields = ["title", "description", "tags", "current_markdown"]
        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Only for "create" (instance doesn't exist yet)
        if not self.instance.pk and not self.initial.get("current_markdown"):
            self.initial["current_markdown"] = DEFAULT_MARKDOWN
