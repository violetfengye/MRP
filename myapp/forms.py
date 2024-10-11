from django import forms
from .models import MPS


# 定义 MPSForm 表单类
class MPSForm(forms.ModelForm):
    """
    用于创建或更新 MPS 记录的表单类。
    继承自 ModelForm，自动根据 MPS 模型生成表单字段。
    """

    class Meta:
        model = MPS  # 指定对应的模型为 MPS
        fields = ['material_code', 'quantity', 'date']  # 表单包含的字段


# 使用 modelformset_factory 批量创建 MPSRecord 的表单
from django.forms import modelformset_factory

# MPSRecordFormSet 用于批量创建或编辑 MPS 记录，可以一次输入 5 条记录
MPSRecordFormSet = modelformset_factory(MPS, form=MPSForm, extra=5)
