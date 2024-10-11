from django import forms
from .models import MPS


class MPSForm(forms.ModelForm):
    class Meta:
        model = MPS
        fields = ['material_code', 'quantity', 'date']


from django.forms import modelformset_factory

MPSRecordFormSet = modelformset_factory(MPS, form=MPSForm, extra=5)  # 可以一次输入5条记录
