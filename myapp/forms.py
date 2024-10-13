from django import forms
from .models import MPSRecord


# 定义 MPSRecordForm 表单类
class MPSRecordForm(forms.ModelForm):
    """
    用于创建或更新 MPS 记录的表单类。
    继承自 ModelForm，自动根据 MPS 模型生成表单字段。
    """

    class Meta:
        model = MPSRecord  # 指定对应的模型为 MPSRecord
        fields = ['mps_id', 'material_name', 'required_quantity', 'due_date']  # 表单包含的字段
