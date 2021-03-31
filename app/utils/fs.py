import xlwt
from uuid import uuid4
from config.settings import TEMP_PATH


def generate_excel(cols, rows, filename):
    wb = xlwt.Workbook(encoding='utf-8')  # 实例化，有encoding和style_compression参数
    sheet1 = wb.add_sheet("sheet1", cell_overwrite_ok=True)  # Workbook的方法，生成名为111.xls文件

    for i in range(0, len(cols)):  # 添加EXCEL头
        sheet1.write(0, i, cols[i]['value'])
    num = 0 # 从第二行开始
    for item in rows:
        for i in range(0, len(cols)):  # 添加EXCEL头
            sheet1.write(num+1, i, item[cols[i]['key']])
            print(num+1, i, item[cols[i]['key']])
        num += 1  # 自增1
    excel_name = str(uuid4()) + '.xls'
    url = TEMP_PATH + '/' + excel_name
    wb.save(url)
    return '/media/temp/' + excel_name

