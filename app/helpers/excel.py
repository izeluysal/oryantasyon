"""Excel (.xlsx) dışa aktarma: tek ortak yardımcı, formül enjeksiyonuna karşı nötrleştirme."""
import io
import re
from datetime import date, datetime

from openpyxl import Workbook

CONTROL_CHARACTERS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
FORMULA_STARTERS = ("=", "+", "-", "@", "\t", "\r")
XLSX_MIMETYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def neutralize(value):
    """Metni güvenli hale getirir: kontrol karakterlerini atar, formül gibi başlayanın başına tek tırnak koyar."""
    if not isinstance(value, str):
        return value
    value = CONTROL_CHARACTERS.sub("", value)
    if value.startswith(FORMULA_STARTERS):
        return "'" + value
    return value


def excel_olustur(headers, rows, sheet_name="Sheet1"):
    """Başlık ve satırlardan .xlsx baytları üretir. Tarih ve sayılar gerçek tipte yazılır."""
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = sheet_name[:31]
    sheet.append([neutralize(header) for header in headers])
    for row in rows:
        cells = []
        for value in row:
            if isinstance(value, datetime) and value.tzinfo is not None:
                value = value.replace(tzinfo=None)
            cells.append(value if isinstance(value, (int, float, date, datetime)) else neutralize(value))
        sheet.append(cells)
    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()
