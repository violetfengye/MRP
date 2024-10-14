# scripts/insert_bs.py

import os
import django

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myapp.models import BalanceSheet


# 批量插入资产负债表的数据
def insert_bs():
    balancesheets = [
        {'bs_id': 2, 'bs_toid': 16, 'bs_var': 'a1'},
        {'bs_id': 3, 'bs_toid': 16, 'bs_var': 'a3'},
        {'bs_id': 4, 'bs_toid': 16, 'bs_var': 'a5'},
        {'bs_id': 5, 'bs_toid': 7, 'bs_var': 'a7'},
        {'bs_id': 6, 'bs_toid': 7, 'bs_var': 'a9'},
        {'bs_id': 7, 'bs_toid': 16, 'bs_var': 'b1'},
        {'bs_id': 8, 'bs_toid': 16, 'bs_var': 'a12'},
        {'bs_id': 9, 'bs_toid': 16, 'bs_var': 'a14'},
        {'bs_id': 10, 'bs_toid': 16, 'bs_var': 'a16'},
        {'bs_id': 11, 'bs_toid': 16, 'bs_var': 'a18'},
        {'bs_id': 12, 'bs_toid': 16, 'bs_var': 'a20'},
        {'bs_id': 13, 'bs_toid': 16, 'bs_var': 'a22'},
        {'bs_id': 14, 'bs_toid': 16, 'bs_var': 'a24'},
        {'bs_id': 15, 'bs_toid': 16, 'bs_var': 'a26'},
        {'bs_id': 16, 'bs_toid': 16, 'bs_var': 'b3'},
    ]

    # 将物料数据插入 Material 表中
    for item in balancesheets:
        BalanceSheet.objects.create(
            bs_id=item['bs_id'],
            bs_toid=item['bs_toid'],
            bs_var=item['bs_var']
        )

    print("资产负债表数据插入成功！")  # 输出插入成功消息


# 执行插入操作
if __name__ == '__main__':
    insert_bs()  # 运行插入函数
