import pandas as pd
import os
from datetime import date
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_RIGHT
from reportlab.pdfgen import canvas
import re
import ctypes
from reportlab.platypus import Flowable
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import platform
import argparse
import sys
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--date", required=True, help="Date in format YYYY-MM-DD")
args = parser.parse_args()

run_date = args.date
excel_file = f"{run_date}.xlsx"

if not os.path.exists(excel_file):
    print(f" File not found: {excel_file}")
    sys.exit(1)

print(f" Using file: {excel_file}")





def create_html_report(pdf_files, success=True):
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    system = platform.system()

    links = ""
    build_url = os.environ.get("BUILD_URL", "").rstrip("/")

    for pdf in pdf_files:
        pdf_path = Path(pdf)
        filename = pdf_path.name

        # ננקה נתיב ונבטיח פורמט אינטרנט
        rel_path = pdf_path.as_posix()

        # נבנה קישור Jenkins artifact תקני
        if build_url:
            link = f"{build_url}/artifact/{rel_path}"
        else:
            link = f"artifact/{rel_path}"

        links += f'<li><a href="{link}" target="_blank" rel="noopener noreferrer">{filename}</a></li>\n'

    html_content = f"""
<!DOCTYPE html>
<html lang="he">
<head>
    <meta charset="UTF-8">
    <title>DevOps Report</title>
    <base target="_blank">

    <meta http-equiv="Content-Security-Policy"
          content="default-src * 'unsafe-inline' 'unsafe-eval' data: blob:;">
</head>
<body>
    <h1>📊 Report System - Jenkins Run</h1>
    <p><b>Status:</b> {"SUCCESS ✅" if success else "FAILED ❌"}</p>
    <p><b>Date:</b> {now}</p>
    <p><b>System:</b> {system}</p>

    <h2>Generated reports:</h2>
    <ul>
        {links}
    </ul>
</body>
</html>
"""

    with open("report.html", "w", encoding="utf-8") as f:
        f.write(html_content)


# === רישום פונט עברי ===
pdfmetrics.registerFont(TTFont('Arial', 'resources/Arial.ttf'))


# === קריאת קבצים ===
df = pd.read_excel(excel_file, dtype={"name": str}) #הקובץ היומי של חיובי הזכיינים
df["productid"] = df["productid"].astype(str).str.strip()     #המרת מספר המוצר למחרוזת
df["linename"] = df["linename"].astype(str).str.strip()



#טעינת קובץ הקווים לצורך בניית העמודים בסדר קבוע
lines_df = pd.read_excel("resources/lines.xlsx", dtype=str)
lines_df["linename"] = lines_df["linename"].astype(str).str.strip()

if "ordernum" in lines_df.columns:
    lines_df["ordernum"] = pd.to_numeric(lines_df["ordernum"], errors="coerce")
else:
    raise ValueError("עמודת 'ordernum' לא נמצאה בקובץ lines.xlsx")

suppliers_order = pd.read_excel("resources/suppliers_order.xlsx", dtype=str)
suppliers_order.columns = [c.strip().lower() for c in suppliers_order.columns]

# --- קבצי תנובה ---
tnuva_map = pd.read_excel("resources/tnuva_order.xlsx", dtype=str)
tnuva_map.columns = [c.strip().lower() for c in tnuva_map.columns]
tnuva_map["productid"] = tnuva_map["productid"].astype(str).str.strip()

tnuva_category_order = pd.read_excel("resources/tnuva_category_order.xlsx", dtype=str)
tnuva_category_order.columns = [c.strip().lower() for c in tnuva_category_order.columns]
tnuva_category_order["order"] = pd.to_numeric(tnuva_category_order["order"], errors="coerce")

product_col = "name"
category_col = "category"
category_order_col = "order"
sup_id_col = "supplierid"
sup_order_col = "order"

os.makedirs("pdf_reports", exist_ok=True)


# === עיצוב טקסט ===
hebrew_style = ParagraphStyle(
    name="Hebrew",
    fontName="Arial",
    fontSize=13,
    alignment=TA_RIGHT,
    rightIndent=10,
    allowHTML=True
)

# === קריאת תאריך מתוך K2 ===
data_date = pd.read_excel(excel_file, header=None).iloc[1, 10]
today = pd.to_datetime(data_date).strftime("%d/%m/%Y")
today_file_name = today.replace("/", "-")



daily_folder = os.path.join("pdf_reports", today_file_name)
os.makedirs(daily_folder, exist_ok=True)



def rtl(text: str) -> str:
    """היפוך טקסט עברי אך שומר מספרים"""
    words = str(text).split(" ")
    return " ".join([w[::-1] if re.search(r'[\u0590-\u05FF]', w) else w for w in words[::-1]])


# === איתור עמודות ספק ===
supplier_id_col = None
supplier_name_col = None

for col in df.columns:
    cname = str(col).lower()
    if "id" in cname and "sup" in cname:
        supplier_id_col = col
    elif "sup" in cname and ("name" in cname or "שם" in cname):
        supplier_name_col = col

if supplier_id_col is None:
    supplier_id_col = df.columns[-2]
if supplier_name_col is None:
    supplier_name_col = df.columns[-1]


# === עיצוב כותרות טבלה ===
styles = getSampleStyleSheet()
header_style = styles["Normal"]
header_style.fontName = 'Arial'
header_style.fontSize = 9.5
header_style.alignment = TA_RIGHT
header_style.wordWrap = 'CJK'


# ✅ איחוד קבוצות 5 ו־6
#לביטול האיחוד של 5 ו 6 למחוק את השורה הבאה
#df["groupprint"] = df["groupprint"].astype(str).replace({"5": "5-6", "6": "5-6"})

page_map = []

# === מעבר על קבוצות חניון ===
for group_id, group_df in df.groupby("groupprint"):

    filename = f"קבוצת_חניון_{group_id} - {today_file_name}.pdf"  # שמות נקיים בלי תאריך
    pdf_path = os.path.join(daily_folder, filename)

    #pdf_path = f"pdf_reports/קבוצת_חניון_{group_id} - {today_file_name}.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    page_width = A4[0] - doc.leftMargin - doc.rightMargin

    # --- קווי חלוקה ---
    lines_df.columns = [c.strip().lower() for c in lines_df.columns]
    if "linename" not in lines_df.columns:
        lines_df["linename"] = lines_df["linenum"].apply(lambda x: f"קו {x}")

    subset_cols = ["linenum", "linename"]
    if "ordernum" in lines_df.columns:
        subset_cols.append("ordernum")

    all_lines = (
        lines_df.loc[
            lines_df["groupprint"].isin(["5", "6"])
            if group_id == "5-6" else
            lines_df["groupprint"] == str(group_id),
            subset_cols
        ]
        .assign(
            linenum=lambda d: pd.to_numeric(d["linenum"], errors="coerce"),
            ordernum=lambda d: pd.to_numeric(d.get("ordernum"), errors="coerce")
        )
        .sort_values(by=[c for c in ["ordernum", "linenum"] if c in subset_cols])
        .drop_duplicates(subset=["linename"])
        .reset_index(drop=True)
    )

    # --- סדר ספקים ---
    group_df[supplier_id_col] = group_df[supplier_id_col].astype(str)
    suppliers_order[sup_id_col] = suppliers_order[sup_id_col].astype(str)

    group_df = group_df.merge(
        suppliers_order[[sup_id_col, sup_order_col]],
        how="left",
        left_on=supplier_id_col,
        right_on=sup_id_col
    ).assign(order=lambda d: pd.to_numeric(d[sup_order_col], errors="coerce").fillna(9999))


    # === לולאה על ספקים ===
    for supplier_id in group_df.drop_duplicates(subset=[supplier_id_col]).sort_values("order")[supplier_id_col]:

        supplier_df = group_df[group_df[supplier_id_col] == supplier_id]
        supplier_name = str(supplier_df.iloc[0][supplier_name_col])

        pivot = supplier_df.pivot_table(
            index="linename",
            columns="name",
            values="mount",
            fill_value=0,
            aggfunc="sum"
        )

        # הוספת קווים חסרים
        for _, row in all_lines.iterrows():
            if row["linename"] not in pivot.index:
                pivot.loc[row["linename"]] = 0

        # ✅ סדר נכון של הקווים לפי ordernum ואז linenum
        pivot = (
            pivot.reset_index()
            .merge(all_lines[["linename", "linenum", "ordernum"]], on="linename", how="left")
            .sort_values(by=["ordernum", "linenum"], na_position="last")
            .set_index("linename")
        )

        # ✅ חשוב: להסיר את העמודות שנוספו רק למיון (כדי שלא יופיעו במקום שמות המוצרים)
        pivot = pivot.drop(columns=["ordernum", "linenum"], errors="ignore")

        chunks = []
        max_products_per_page = 6


        # ✅ טיפול בתנובה לפי productid → קטגוריות → סדר קטגוריות
        if supplier_id == "1":

            # productid → name מתוך data.xlsx
            id_to_name = (
                supplier_df[["productid", "name"]]
                .dropna()
                .drop_duplicates(subset=["productid"])
                .set_index("productid")["name"]
                .to_dict()
            )

            # בניית סדר קטגוריות
            category_order = (
                tnuva_category_order.sort_values(category_order_col)[category_col]
                .tolist()
            )

            desired_cols = []
            # מעבר על קטגוריות → בתוך קטגוריה על productid
            for cat in category_order:
                cat_pids = tnuva_map.loc[
                    tnuva_map[category_col] == cat, "productid"
                ].tolist()

                # productid → שם עמודה ב־pivot
                cols = [
                    id_to_name[pid]
                    for pid in cat_pids
                    if pid in id_to_name and id_to_name[pid] in pivot.columns
                ]
                desired_cols.extend(cols)

                if cols:
                    total_pages = (len(cols) + max_products_per_page - 1) // max_products_per_page
                    for i in range(0, len(cols), max_products_per_page):
                        chunks.append({
                            "category": cat,
                            "page_products": cols[i:i + max_products_per_page],
                            "page_num": (i // max_products_per_page) + 1,
                            "total_pages": total_pages
                        })

            # מוצרים שלא נמצאים בקטגוריה
            leftover = [c for c in pivot.columns if c not in desired_cols]
            if leftover:
                total_pages = (len(leftover) + max_products_per_page - 1) // max_products_per_page
                for i in range(0, len(leftover), max_products_per_page):
                    chunks.append({
                        "category": None,
                        "page_products": leftover[i:i + max_products_per_page],
                        "page_num": (i // max_products_per_page) + 1,
                        "total_pages": total_pages
                    })

        else:
            product_columns = list(pivot.columns)
            total_pages = (len(product_columns) + max_products_per_page - 1) // max_products_per_page
            for i in range(0, len(product_columns), max_products_per_page):
                chunks.append({
                    "category": None,
                    "page_products": product_columns[i:i + max_products_per_page],
                    "page_num": (i // max_products_per_page) + 1,
                    "total_pages": total_pages
                })


        # === יצירת PDF על בסיס chunks ===
        for chunk in chunks:
            sub_pivot = pivot.loc[:, [c for c in chunk["page_products"] if c in pivot.columns]]

            title = f"ריכוז מוצרים יומי – קבוצת חניון {group_id} / ספק: {supplier_name}"
            if chunk["category"]:
                title += f" / קטגוריה: {chunk['category']}"
            title += f"  עמוד {chunk['page_num']} מתוך {chunk['total_pages']}  {today}"

            elements.append(Paragraph(rtl(title), hebrew_style))
            elements.append(Spacer(1, 10))

            headers = [Paragraph(rtl(str(c)), header_style) for c in sub_pivot.columns] + [Paragraph(rtl("שם קו"), header_style)]
            data = [headers]

            for line_name, row_values in zip(sub_pivot.index, sub_pivot.itertuples(index=False, name=None)):
                line_row = all_lines.loc[all_lines["linename"] == line_name]
                line_num = int(line_row["linenum"].values[0]) if not line_row.empty else "-"
                row = list(map(str, row_values)) + [Paragraph(rtl(f"  {line_name}"), header_style)]
                #row = list(map(str, row_values)) + [Paragraph(rtl(f"קו {line_num}  {line_name}"), header_style)]
                data.append(row)

            col_widths = [(page_width / (len(sub_pivot.columns)+1))] * (len(sub_pivot.columns)+1)

            table = Table(data, repeatRows=1, hAlign="RIGHT", colWidths=col_widths)
            table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Arial'),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER')
            ]))
            elements.append(table)

            # שורת סה"כ — התא האחרון עם טקסט RTL כ-Paragraph כדי שלא יופיעו ריבועים
            total_values = [sub_pivot[c].sum() for c in sub_pivot.columns]
            total_row = total_values + [Paragraph(rtl("סה״כ"), header_style)]

            total_table = Table([total_row], hAlign="RIGHT", colWidths=col_widths)
            total_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Arial'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BACKGROUND', (0, 0), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER')
            ]))

            elements.append(total_table)


            class SupplierMarker(Flowable):
                def __init__(self, supplier_id):
                    super().__init__()
                    self.supplier_id = supplier_id

                def wrap(self, availWidth, availHeight):
                    return (0, 0)

                def draw(self):
                    # הערך נרשם בתוך ה־canvas state של העמוד הזה בלבד
                    self.canv._supplier_id = str(self.supplier_id).strip()



            elements.append(SupplierMarker(supplier_id))
            page_map.append({
                'group': str(group_id),
                'supplier': str(supplier_id),
                'category': chunk['category'],  # יכול להיות None או שם הקטגוריה
                'page_in_doc': len([e for e in elements if isinstance(e, PageBreak)])
            })
            elements.append(PageBreak())


    # === מספור עמודים ===
    # class NumberedCanvas(canvas.Canvas):
    #     def __init__(self, *args, **kwargs):
    #         super().__init__(*args, **kwargs)
    #         self._saved_page_states = []
    #     def showPage(self):
    #         self._saved_page_states.append(dict(self.__dict__))
    #         self._startPage()
    #     def save(self):
    #         num_pages = len(self._saved_page_states)
    #         for state in self._saved_page_states:
    #             self.__dict__.update(state)
    #             page_num = self._pageNumber
    #             self.setFont("Arial", 9)
    #             self.drawRightString(A4[0]-80, 20, f"{num_pages} {rtl('מתוך')} {page_num} {rtl('עמוד')}")
    #             super().showPage()
    #         super().save()

    class NumberedCanvas(canvas.Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._saved_page_states = []

        def showPage(self):
            # שמירת כל מצב הדף כולל _supplier_id
            self._saved_page_states.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            num_pages = len(self._saved_page_states)

            for state in self._saved_page_states:
                self.__dict__.update(state)

                # קבלת מזהה הספק
                supplier_id = state.get("_supplier_id", "")
                supplier_id = str(supplier_id).strip()

                # קביעת טקסט תחתון
                footer_text = rtl("חלב - קלסר סגול") if supplier_id in ["1","60","50","65","69"] else rtl("לחם - ערימה כללית")

                self.setFont("Arial", 10)

                # מספור עמודים
                self.drawRightString(
                    A4[0] - 80, 20,
                    f"{num_pages} {rtl('מתוך')} {self._pageNumber} {rtl('עמוד')}"
                )

                # הטקסט ליד המספור
                self.drawString(40, 20, footer_text)

                super().showPage()

            super().save()


    doc.build(elements, canvasmaker=NumberedCanvas)


master_writer = PdfWriter()
#פונקצייה להוספת העמודים לקובץ מאסטר
def add_pages_to_master(filter_fn):
    for i, info in enumerate(page_map):
        if filter_fn(info):
            # מוצאים את הקובץ המתאים
            filename = f"קבוצת_חניון_{info['group']} - {today_file_name}.pdf"
            path = os.path.join(daily_folder, filename)
            reader = PdfReader(path)
            # מוסיפים את העמוד הספציפי (info['page_in_doc'] הוא האינדקס)
            master_writer.add_page(reader.pages[info['page_in_doc']])

# --- ביצוע ההרכבה לפי הסדר שביקשת ---

# 1. כל קבוצת חניון 1
add_pages_to_master(lambda x: x['group'] == "1")

# 2. העתק נוסף של ספקים: סלטי משני, תנובה ראשון, רמת הגולן, טרה
suppliers_to_duplicate = ["60", "50", "65", "69"]
add_pages_to_master(lambda x: x['group'] == "1" and x['supplier'] in suppliers_to_duplicate)

# 3. קטגוריות ספציפיות של תנובה (ספק 1)
cats_to_extra = ["חלב", "משקאות ושוקו"]
add_pages_to_master(lambda x: x['group'] == "1" and x['supplier'] == "1" and x['category'] in cats_to_extra)

# 4. כל שאר קבוצות החניונים (מלבד 1 | 8)
add_pages_to_master(lambda x: x['group'] != "1" and x['group'] != "8")

#הוספת העתקים נוספים של קבוצות חלב מחניונים 5 ו 6
add_pages_to_master(lambda x: x['group'] == "5" and x['supplier'] in ["1","60","50","65","69"] )
add_pages_to_master(lambda x: x['group'] == "6" and x['supplier'] in ["1","60","50","65","69"] )

#הוספת העמוד של השוקו מרמת החייל
cats_to_extra = ["משקאות ושוקו"] # קטגוריות של תנובה להוספה מרמת החייל
add_pages_to_master(lambda x: x['group'] == "4" and x['supplier'] == "1" and x['category'] in cats_to_extra)




# שמירה סופית
master_final_path = os.path.join(daily_folder, f"מאסטר_הפצה_{today_file_name}.pdf")
with open(master_final_path, "wb") as f:
    master_writer.write(f)


pdf_files = []
pdf_files = sorted(pdf_files)


if os.path.exists(daily_folder):
    for file in os.listdir(daily_folder):
        if file.lower().endswith(".pdf"):
            pdf_files.append(os.path.join(daily_folder, file))

create_html_report(pdf_files, success=True)


# ✅ פתיחת התיקייה
#os.startfile(daily_folder)
















