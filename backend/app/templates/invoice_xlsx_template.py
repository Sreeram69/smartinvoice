import io
import os
from typing import Dict, Any, List
import openpyxl
from openpyxl.styles import Alignment, Font
from app.templates.invoice_template import amount_to_words


def get_template_xlsx_path() -> str:
    """Finds the template file in assets or fallback path."""
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    asset_path = os.path.join(curr_dir, "assets", "INVOICE format.xlsx")
    if os.path.exists(asset_path):
        return asset_path
    
    desktop_fallback = r"C:\Users\cheek\OneDrive\Desktop\New folder\INVOICE format.xlsx"
    if os.path.exists(desktop_fallback):
        return desktop_fallback

    raise FileNotFoundError("Could not find 'INVOICE format.xlsx' template asset.")


def generate_invoice_xlsx(data: Dict[str, Any]) -> io.BytesIO:
    """
    Populates 'INVOICE format.xlsx' with dynamic invoice and customer data,
    keeping all original formatting, borders, formulas, and 2-column side-by-side printing layout.
    """
    template_path = get_template_xlsx_path()
    wb = openpyxl.load_workbook(template_path)
    ws = wb.active

    # Remove duplicate floating SENDER at row 1
    ws['A1'].value = None
    ws['K1'].value = None

    sender = data.get('sender', {})
    customer = data.get('customer', {})
    doc_number = str(data.get('doc_number', '123'))
    date_str = str(data.get('date', '22-10-2026'))
    weight_str = str(data.get('weight') or '').strip()
    items = data.get('items', [])
    total_val = str(data.get('total', '0'))

    # Calculate numeric total
    items_sum = 0.0
    for it in items:
        try:
            cnt = float(str(it.get('count', 1)).replace(',', ''))
            prc = float(str(it.get('price', 0)).replace(',', ''))
            items_sum += cnt * prc
        except Exception:
            pass

    if items_sum > 0:
        num_total = items_sum
    else:
        try:
            num_total = float(total_val.replace(',', '').strip())
        except Exception:
            num_total = 0.0

    words_text = amount_to_words(num_total)
    destination = str(customer.get('country') or customer.get('state') or customer.get('city') or 'U.A.E').strip().upper()
    origin_country = str(sender.get('country') or sender.get('state') or 'INDIA').strip().upper()
    loading_port = str(sender.get('city') or 'INDIA').strip().upper()

    # --- Populate Column A to I (First Invoice Copy) ---
    ws['A3'] = sender.get('name', '').upper()
    ws['A4'] = sender.get('address_line_1', '').upper()
    ws['A5'] = sender.get('city', '').upper()
    ws['B7'] = sender.get('phone', '')

    ws['F2'] = f" Date:{date_str}"
    ws['H2'] = f"INVOICE NO : {doc_number}"
    ws['F4'] = None
    ws['F7'] = "SEND FOR PERSONAL USE ONLY"

    ws['A9'] = customer.get('name', '').upper()
    ws['A10'] = customer.get('address_line_1', '').upper()
    ws['A11'] = customer.get('address_line_2', '').upper() if customer.get('address_line_2') else customer.get('city', '').upper()
    ws['A12'] = f"{customer.get('city', '')}, {customer.get('country', destination)}".strip(', ').upper()
    ws['B13'] = customer.get('phone', '')

    pcs_weight = f"1PCS / {weight_str}" if weight_str else "1PCS"

    # Unmerge any old merges in rows 14-19
    for m in list(ws.merged_cells.ranges):
        if m.min_row >= 14 and m.max_row <= 19 and m.min_col <= 9:
            try:
                ws.unmerge_cells(str(m))
            except Exception:
                pass

    # Clear rows 14-19
    for r in range(14, 20):
        for c in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']:
            cell = ws[f'{c}{r}']
            if not isinstance(cell, openpyxl.cell.cell.MergedCell):
                cell.value = None

    header_font = Font(name='Calibri', size=10, bold=True)
    body_font = Font(name='Calibri', size=10, bold=False)
    bold_body_font = Font(name='Calibri', size=10, bold=True)

    center_align = Alignment(horizontal='center', vertical='center', wrap_text=False)
    left_align = Alignment(horizontal='left', vertical='center', wrap_text=False)
    right_align = Alignment(horizontal='right', vertical='center', wrap_text=False)

    # Realigned Route & Destination Block (Rows 14 to 19):
    # Left A14:E16 -> Port of loading
    # Right F14:I16 -> Country of origin of goods
    ws.merge_cells('A14:E16')
    ws['A14'].value = f"Port of loading:  {loading_port}"
    ws['A14'].font = bold_body_font
    ws['A14'].alignment = Alignment(horizontal='left', vertical='center', indent=1)

    ws.merge_cells('F14:I16')
    ws['F14'].value = f"Country of origin of goods:  {origin_country}"
    ws['F14'].font = bold_body_font
    ws['F14'].alignment = center_align

    # Left A17:E19 -> Final Destination
    # Right F17:I19 -> 1PCS / 14KG
    ws.merge_cells('A17:E19')
    ws['A17'].value = f"Final Destination:  {destination}"
    ws['A17'].font = bold_body_font
    ws['A17'].alignment = Alignment(horizontal='left', vertical='center', indent=1)

    ws.merge_cells('F17:I19')
    ws['F17'].value = pcs_weight
    ws['F17'].font = Font(name='Calibri', size=11, bold=True)
    ws['F17'].alignment = center_align

    # Clean borders for rows 14-19
    from openpyxl.styles import Border, Side
    thin_border = Side(style='thin', color='000000')
    for r in range(14, 20):
        for c in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']:
            t = thin_border if r in [14, 17] else None
            b = thin_border if r in [16, 19] else None
            l = thin_border if c in ['A', 'F'] else None
            ri = thin_border if c in ['E', 'I'] else None
            ws[f'{c}{r}'].border = Border(top=t, bottom=b, left=l, right=ri)

    # Column widths for single invoice copy (Columns A to I)
    for col_letter, width in [('A', 12.5), ('B', 14.0), ('G', 12.0), ('H', 15.0), ('I', 16.0)]:
        ws.column_dimensions[col_letter].width = width

    # Row 20 Headers (Single Copy)
    headers_first_copy = {
        'A20': 'S.NO',
        'B20': 'ITEM DETAILS',
        'G20': 'COUNT',
        'H20': 'RATE\nINR',
        'I20': 'AMOUNT\nINR'
    }

    for cell_ref, text in headers_first_copy.items():
        ws[cell_ref].value = text
        ws[cell_ref].alignment = Alignment(
            horizontal='center',
            vertical='center',
            wrap_text=True
        )
        ws[cell_ref].font = header_font


    # Items rows 21 to 35
    for r in range(21, 36):
        idx = r - 21
        if idx < len(items):
            it = items[idx]
            ws[f'A{r}'] = idx + 1
            ws[f'A{r}'].alignment = center_align
            ws[f'A{r}'].font = body_font

            ws[f'B{r}'] = str(it.get('name', '')).upper()
            ws[f'B{r}'].alignment = left_align
            ws[f'B{r}'].font = body_font

            try:
                cnt = float(it.get('count', 1))
            except Exception:
                cnt = 1.0
            ws[f'G{r}'] = cnt
            ws[f'G{r}'].alignment = center_align
            ws[f'G{r}'].font = body_font
            ws[f'G{r}'].number_format = '0'

            try:
                prc = float(it.get('price', 0))
            except Exception:
                prc = 0.0
            ws[f'H{r}'] = prc
            ws[f'H{r}'].alignment = right_align
            ws[f'H{r}'].font = body_font
            ws[f'H{r}'].number_format = '0.00'

            ws[f'I{r}'] = f'=G{r}*H{r}'
            ws[f'I{r}'].alignment = right_align
            ws[f'I{r}'].font = body_font
            ws[f'I{r}'].number_format = '0.00'
        else:
            ws[f'A{r}'] = None
            ws[f'B{r}'] = None
            ws[f'G{r}'] = None
            ws[f'H{r}'] = None
            ws[f'I{r}'] = None

    ws['E36'].value = 'TOTAL AMOUNT'
    ws['E36'].alignment = right_align
    ws['E36'].font = header_font

    ws['I36'] = '=SUM(I21:I35)'
    ws['I36'].alignment = right_align
    ws['I36'].font = header_font
    ws['I36'].number_format = '0.00'

    ws['A37'] = f"IN WORDS - {words_text}"
    ws['A37'].alignment = left_align
    ws['A37'].font = bold_body_font

    # --- 7 Points Declaration & Signature (Rows 38 to 45) ---
    decl_text = (
        "DECLARATION\n"
        "1. We hereby declare that the goods described in this invoice are of Indian origin, and the prices stated represent the actual value of the goods.\n"
        "2. We certify that all particulars and information provided in this invoice are true, correct, and complete to the best of our knowledge.\n"
        "3. The description, quantity, and value of the goods have been accurately stated in this invoice.\n"
        "4. The goods are intended for personal use only and are not intended for commercial resale, where applicable.\n"
        "5. The shipment details and other particulars stated in this invoice are provided for customs clearance and shipping purposes.\n"
        "6. We accept responsibility for the accuracy of the information and documents provided in connection with this shipment.\n"
        "7. This invoice has been issued in good faith for the purpose of shipment, customs assessment, and related documentation."
    )

    # Unmerge any old merges in rows 38-46 first
    for m in list(ws.merged_cells.ranges):
        if m.min_row >= 38 and m.min_col <= 9:
            try:
                ws.unmerge_cells(str(m))
            except Exception:
                pass

    # Clear old text in rows 38-46
    for r in range(38, 47):
        for c in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']:
            cell = ws[f'{c}{r}']
            if not isinstance(cell, openpyxl.cell.cell.MergedCell):
                cell.value = None

    ws.merge_cells('A38:F45')
    ws['A38'].value = decl_text
    ws['A38'].font = Font(name='Calibri', size=7.2, bold=False)
    ws['A38'].alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)

    for r in range(38, 46):
        ws.row_dimensions[r].height = 14.5

    ws.merge_cells('G42:I42')
    ws['G42'].value = 'SENDER SIGNATURE'
    ws['G42'].font = Font(name='Calibri', size=9, bold=True)
    ws['G42'].alignment = Alignment(horizontal='center', vertical='center')

    ws.merge_cells('G45:I45')
    ws['G45'].value = '(Authorized signatory)'
    ws['G45'].font = Font(name='Calibri', size=8, bold=False)
    ws['G45'].alignment = Alignment(horizontal='center', vertical='center')

    # Set explicit print area and single-page fit to export only single invoice copy (Columns A to I)
    ws.print_area = 'A1:I45'
    ws.page_setup.orientation = ws.ORIENTATION_PORTRAIT
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 1

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer
