from django.apps import AppConfig


class MyappConfig(AppConfig):
    """
    配置应用程序的设置类。
    """

    default_auto_field = "django.db.models.BigAutoField"  # 设置默认的自动字段类型为 BigAutoField，以支持大数量的主键。
    name = "myapp"  # 应用程序的名称，Django会使用这个名称来识别和管理该应用。
