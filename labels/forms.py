from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Batch, Product


from django.utils.translation import gettext_lazy as _

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "oil_batch_number"]
        widgets = {
            "name": forms.TextInput(attrs={"autocomplete": "off"}),
            "oil_batch_number": forms.TextInput(attrs={"dir": "ltr", "autocomplete": "off"}),
        }

    def clean_name(self):
        return self.cleaned_data["name"].strip().upper()
    
    def clean_oil_batch_number(self):
        return self.cleaned_data["oil_batch_number"].strip().upper()

class BatchForm(forms.ModelForm):
    """Used to add a new batch (and optionally make it active)."""

    class Meta:
        model = Batch
        fields = ["batch_number", "is_active"]

    def clean_batch_number(self):
        return self.cleaned_data["batch_number"].strip().upper()


class IngredientsForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["ingredients_text"]
        widgets = {
            "ingredients_text": forms.Textarea(
                attrs={"dir": "ltr", "rows": 6,
                       "placeholder": "ALCOHOL DENAT., PARFUM, AQUA, ..."}
            ),
        }


class PrintTrackingForm(forms.Form):
    product_id = forms.IntegerField()
    quantity = forms.IntegerField(min_value=1, max_value=100, initial=1)


class PrintIngredientsForm(forms.Form):
    product_id = forms.IntegerField()
    quantity = forms.IntegerField(min_value=1, max_value=100, initial=1)
    note = forms.CharField(required=False, max_length=300)


class ClearRecordsForm(forms.Form):
    start_date = forms.DateField()
    end_date = forms.DateField()

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("start_date")
        end = cleaned.get("end_date")
        if start and end and start > end:
            cleaned["start_date"], cleaned["end_date"] = end, start
        return cleaned