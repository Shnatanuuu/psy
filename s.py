import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from datetime import datetime
import io
import pytz
from openai import OpenAI
import os
from dotenv import load_dotenv
import re

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=openai_api_key) if openai_api_key else None

# ─── Register Chinese font ──────────────────────────────────────────────────
try:
    pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
    CHINESE_FONT = 'STSong-Light'
except Exception:
    CHINESE_FONT = 'Helvetica'

st.set_page_config(
    page_title="Physical Test Report",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Chinese cities ─────────────────────────────────────────────────────────
CHINESE_CITIES = {
    "Guangzhou": "广州", "Shenzhen": "深圳", "Dongguan": "东莞",
    "Foshan": "佛山", "Zhongshan": "中山", "Huizhou": "惠州",
    "Zhuhai": "珠海", "Jiangmen": "江门", "Zhaoqing": "肇庆",
    "Shanghai": "上海", "Beijing": "北京", "Suzhou": "苏州",
    "Hangzhou": "杭州", "Ningbo": "宁波", "Wenzhou": "温州",
    "Wuhan": "武汉", "Chengdu": "成都", "Chongqing": "重庆",
    "Tianjin": "天津", "Nanjing": "南京", "Xi'an": "西安",
    "Qingdao": "青岛", "Dalian": "大连", "Shenyang": "沈阳",
    "Changsha": "长沙", "Zhengzhou": "郑州", "Jinan": "济南",
    "Harbin": "哈尔滨", "Changchun": "长春", "Taiyuan": "太原",
    "Shijiazhuang": "石家庄", "Lanzhou": "兰州", "Xiamen": "厦门",
    "Fuzhou": "福州", "Nanning": "南宁", "Kunming": "昆明",
    "Guiyang": "贵阳", "Haikou": "海口", "Ürümqi": "乌鲁木齐",
    "Lhasa": "拉萨",
}

# ─── Text dictionaries ────────────────────────────────────────────────────
ENGLISH_TEXTS = {
    "title": "Physical Test Report",
    "company": "GRAND STEP (H.K.) LTD",
    "report_title": "PHYSICAL TEST REPORT",
    "basic_info": "1. BASIC INFORMATION",
    "adhesive_test": "2. ADHESIVE / PULL TEST",
    "components_test": "3. COMPONENTS PHYSICAL TEST",
    "flexing_test": "4. FLEXING TEST",
    "abrasion_test": "5. ABRASION TEST",
    "resistance_test": "6. RESISTANCE TEST",
    "hardness_test": "7. HARDNESS TEST",
    "conclusion_sec": "8. CONCLUSION",
    "rust_test": "RUST TEST",
    "report_no": "Report No.", "date_no": "Date/No.",
    "ci_no": "CI / Order No.", "order_qty": "Order QTY",
    "brand": "Brand", "produced_qty": "Produced QTY",
    "style_no": "Style No.", "factory_trader": "Factory/Trader",
    "sales": "Sales",
    "standard_note": "Note: This is Grand Step Company Standard only. Any priority should follow Customer or 3rd Lab Standard",
    "flat_shoe": "Flat Shoe", "high_heel": "High Heel",
    "sole_wedge": "Sole/Wedge",
    "toe": "Toe", "forepart": "Forepart", "waist": "Waist", "heel": "Heel",
    "heel_height": "Heel Height", "cm_5_8": "5CM-8CM", "above_8cm": "Above 8CM",
    "item": "Item", "standard": "Standard", "result": "Result",
    "comments": "Comments", "remark": "Remark",
    "buckle": "Buckle", "strap": "Strap", "eyelet": "Eyelet",
    "studs": "Studs", "diamond_bow": "Diamond/Bow", "top_lift": "Top Lift",
    "loop": "Loop", "toe_post": "Toe Post Attachment",
    "zipper": "Zipper", "perment_set": "Perment Set at 400N",
    "buckle_std": "20 kg/200N", "strap_std": "20 kg/200N",
    "eyelet_std": "20 kg/200N", "studs_std": "20 kg/200N",
    "diamond_std": "7KG/70N", "top_lift_std": "15 kg/140N",
    "loop_std": "20 KG/200N",
    "toe_post_std": "EVA/Rubber: 150N, Others: 200N",
    "zipper_std": "25 kg/250N", "perment_set_std": "Max deformation ≤ 15%",
    "upper": "Upper", "shoe_flex": "Shoe Flex", "foxing": "Foxing",
    "upper_std": "250,000 cycles", "shoe_flex_std": "100,000 cycles",
    "foxing_std": "≥ 2.0 N/mm",
    "top_lift_abrasion": "Top Lift",
    "outsole_abrasion": "Outsole Abrasion",
    "outsole_abrasion_std": "Rubber & PU: 300mm³, TPR: 350mm³, EVA: 700mm³, PVC: 250mm³",
    "outsole_resistance": "Outsole",
    "heel_fatigue": "Heel Fatigue",
    "heel_fatigue_std": "20,000 cycles, Top lift area ≤ 1cm²",
    "eva_hardness": "EVA", "outsole_hardness": "Outsole Hardness",
    "pass_label": "PASS", "fail_label": "FAIL", "accept_label": "ACCEPT",
    "verified_by": "Verified by", "testing_person": "Testing Person",
    "signature": "Signature", "version": "Version 2024.09",
    "test_location": "Test Location:", "report_date": "Report Date:",
    "generate_pdf": "🎯 Generate PDF Report",
    "download_pdf": "📥 Download PDF Report",
    "fill_required": "Please fill in CI No. and Style No.!",
    "creating_pdf": "Creating PDF report...",
    "generate_success": "PDF Generated Successfully!",
    "pdf_details": "PDF Details",
    "report_language": "Report Language",
    "generated": "Generated",
    "location": "Location",
    "error_generating": "Error generating PDF",
    "footer_text": "Physical Test Report System",
    "powered_by": "Powered by Streamlit",
    "copyright": "© 2025 - Physical Test Report Platform",
    "translation_active": "Translation API: Active",
    "translation_off": "Translation API: Not Configured",
    "tab_basic": "📋 Basic Info",
    "tab_adhesive": "📏 Adhesive",
    "tab_components": "🔩 Components",
    "tab_flexing": "🔄 Flexing",
    "tab_abrasion": "↔️ Abrasion",
    "tab_resistance": "🛡️ Resistance",
    "tab_hardness": "💎 Hardness",
    "tab_conclusion": "✅ Conclusion",
}

CHINESE_TEXTS = {
    "title": "物理测试报告",
    "company": "GRAND STEP (H.K.) LTD",
    "report_title": "物理测试报告",
    "basic_info": "1. 基本信息",
    "adhesive_test": "2. 粘合/拉力测试",
    "components_test": "3. 配件物理测试",
    "flexing_test": "4. 弯曲测试",
    "abrasion_test": "5. 耐磨测试",
    "resistance_test": "6. 阻力测试",
    "hardness_test": "7. 硬度测试",
    "conclusion_sec": "8. 结论",
    "rust_test": "防锈测试",
    "report_no": "报告编号", "date_no": "日期/编号",
    "ci_no": "CI/订单号", "order_qty": "订单数量",
    "brand": "品牌", "produced_qty": "生产数量",
    "style_no": "款式号", "factory_trader": "工厂/贸易商",
    "sales": "销售",
    "standard_note": "注：此标准仅为 Grand Step 公司标准。如有冲突，应遵循客户或第三方实验室标准",
    "flat_shoe": "平底鞋", "high_heel": "高跟鞋",
    "sole_wedge": "鞋底/楔形",
    "toe": "鞋头", "forepart": "前掌", "waist": "腰窝", "heel": "后跟",
    "heel_height": "后跟高度", "cm_5_8": "5CM-8CM", "above_8cm": "8CM以上",
    "item": "项目", "standard": "标准", "result": "结果",
    "comments": "备注", "remark": "备注",
    "buckle": "鞋扣", "strap": "饰带", "eyelet": "眼扣",
    "studs": "饰钉", "diamond_bow": "钻石/蝴蝶结", "top_lift": "天皮",
    "loop": "穿扣", "toe_post": "趾柱附件",
    "zipper": "拉链头", "perment_set": "400N永久变形测试",
    "buckle_std": "20 kg/200N", "strap_std": "20 kg/200N",
    "eyelet_std": "20 kg/200N", "studs_std": "20 kg/200N",
    "diamond_std": "7KG/70N", "top_lift_std": "15 kg/140N",
    "loop_std": "20 KG/200N",
    "toe_post_std": "EVA/橡胶: 150N, 其他: 200N",
    "zipper_std": "25 kg/250N", "perment_set_std": "最大变形 ≤ 15%",
    "upper": "鞋面", "shoe_flex": "鞋弯曲", "foxing": "围条",
    "upper_std": "250,000次循环", "shoe_flex_std": "100,000次循环",
    "foxing_std": "≥ 2.0 N/mm",
    "top_lift_abrasion": "天皮",
    "outsole_abrasion": "外底耐磨",
    "outsole_abrasion_std": "橡胶 & PU: 300mm³, TPR: 350mm³, EVA: 700mm³, PVC: 250mm³",
    "outsole_resistance": "外底",
    "heel_fatigue": "后跟疲劳",
    "heel_fatigue_std": "20,000次循环，天皮区域≤1cm²",
    "eva_hardness": "EVA", "outsole_hardness": "外底硬度",
    "pass_label": "通过", "fail_label": "不通过", "accept_label": "接受",
    "verified_by": "审核人", "testing_person": "测试人员",
    "signature": "签名", "version": "版本 2024.09",
    "test_location": "测试地点:", "report_date": "报告日期:",
    "generate_pdf": "🎯 生成PDF报告",
    "download_pdf": "📥 下载PDF报告",
    "fill_required": "请填写CI号和款式号！",
    "creating_pdf": "正在创建PDF报告...",
    "generate_success": "PDF生成成功！",
    "pdf_details": "PDF详情",
    "report_language": "报告语言",
    "generated": "生成时间",
    "location": "地点",
    "error_generating": "生成PDF错误",
    "footer_text": "物理测试报告系统",
    "powered_by": "由Streamlit驱动",
    "copyright": "© 2025 - 物理测试报告平台",
    "translation_active": "翻译API: 已启用",
    "translation_off": "翻译API: 未配置",
    "tab_basic": "📋 基本信息",
    "tab_adhesive": "📏 粘合测试",
    "tab_components": "🔩 配件测试",
    "tab_flexing": "🔄 弯曲测试",
    "tab_abrasion": "↔️ 耐磨测试",
    "tab_resistance": "🛡️ 阻力测试",
    "tab_hardness": "💎 硬度测试",
    "tab_conclusion": "✅ 结论",
}

def t(key):
    lang = st.session_state.get('ui_language', 'en')
    d = CHINESE_TEXTS if lang == 'zh' else ENGLISH_TEXTS
    return d.get(key, ENGLISH_TEXTS.get(key, key))

def pt(key, pdf_lang):
    d = CHINESE_TEXTS if pdf_lang == 'zh' else ENGLISH_TEXTS
    return d.get(key, ENGLISH_TEXTS.get(key, key))

# ─── Session state ────────────────────────────────────────────────────────
for key, val in [
    ('ui_language', 'en'), ('pdf_language', 'en'),
    ('selected_city', 'Shanghai'), ('translations_cache', {}),
]:
    if key not in st.session_state:
        st.session_state[key] = val

# ══════════════════════════════════════════════════════════════════════════
#  PDF DESIGN TOKENS
# ══════════════════════════════════════════════════════════════════════════
C_PRIMARY   = colors.HexColor('#1a1a2e')
C_ACCENT    = colors.HexColor('#e94560')
C_ACCENT2   = colors.HexColor('#0f3460')
C_LIGHT     = colors.HexColor('#f0f4ff')
C_WHITE     = colors.white
C_GREY_TEXT = colors.HexColor('#555555')
C_GREY_LINE = colors.HexColor('#dddddd')
C_GREEN     = colors.HexColor('#27ae60')
C_RED       = colors.HexColor('#e74c3c')
C_ORANGE    = colors.HexColor('#f39c12')

PAGE_W, PAGE_H = A4
HEADER_H  = 60
FOOTER_H  = 36
MARGIN_L  = 40
MARGIN_R  = 40
CONTENT_W = PAGE_W - MARGIN_L - MARGIN_R


def _font(pdf_lang, bold=False):
    if pdf_lang == "zh":
        return CHINESE_FONT
    return 'Helvetica-Bold' if bold else 'Helvetica'


def _char_width(ch, font_size):
    cp = ord(ch)
    if (0x4E00 <= cp <= 0x9FFF or 0x3400 <= cp <= 0x4DBF or
            0x3000 <= cp <= 0x303F or 0xFF00 <= cp <= 0xFFEF or
            0x3040 <= cp <= 0x309F or 0x30A0 <= cp <= 0x30FF):
        return font_size * 1.0
    return font_size * 0.52


def _text_width(text, font_size):
    return sum(_char_width(ch, font_size) for ch in str(text))


def _wrap_text(text, max_width, font_size):
    if not text or not str(text).strip():
        return ["—"]
    text = str(text)
    lines = []
    for paragraph in text.replace('\r\n', '\n').replace('\r', '\n').split('\n'):
        if not paragraph.strip():
            lines.append("")
            continue
        words = paragraph.split()
        current, current_w = "", 0.0
        for word in words:
            word_w = _text_width(word, font_size)
            space_w = _text_width(" ", font_size)
            if current == "":
                if word_w > max_width:
                    for ch in word:
                        ch_w = _char_width(ch, font_size)
                        if current_w + ch_w > max_width and current:
                            lines.append(current); current = ch; current_w = ch_w
                        else:
                            current += ch; current_w += ch_w
                else:
                    current, current_w = word, word_w
            else:
                test_w = current_w + space_w + word_w
                if test_w <= max_width:
                    current += " " + word; current_w = test_w
                else:
                    lines.append(current)
                    if word_w > max_width:
                        current, current_w = "", 0.0
                        for ch in word:
                            ch_w = _char_width(ch, font_size)
                            if current_w + ch_w > max_width and current:
                                lines.append(current); current = ch; current_w = ch_w
                            else:
                                current += ch; current_w += ch_w
                    else:
                        current, current_w = word, word_w
        if current:
            lines.append(current)
    return lines if lines else ["—"]


# ─── Drawing primitives ───────────────────────────────────────────────────
def draw_page_frame(c, page_num, total_pages, pdf_lang, city, city_zh, gen_time):
    w, h = PAGE_W, PAGE_H
    c.setFillColor(C_PRIMARY)
    c.rect(0, h - HEADER_H, w, HEADER_H, fill=1, stroke=0)
    c.setFillColor(C_ACCENT)
    c.rect(0, h - HEADER_H, 6, HEADER_H, fill=1, stroke=0)
    c.setFillColor(C_WHITE); c.setFont(_font(pdf_lang, bold=True), 13)
    c.drawString(MARGIN_L, h - HEADER_H + 22, "Grand Step (H.K.) Ltd")
    c.setFont(_font(pdf_lang), 9)
    c.drawRightString(w - MARGIN_R, h - HEADER_H + 22,
                      "物理测试报告" if pdf_lang == "zh" else "PHYSICAL TEST REPORT")
    # Footer
    c.setFillColor(C_PRIMARY)
    c.rect(0, 0, w, FOOTER_H, fill=1, stroke=0)
    c.setFillColor(C_ACCENT)
    c.rect(0, FOOTER_H - 3, w, 3, fill=1, stroke=0)
    c.setFillColor(C_WHITE); c.setFont(_font(pdf_lang), 7.5)
    loc_str  = f"地点: {city} ({city_zh})" if pdf_lang == "zh" else f"Location: {city}"
    pg_str   = f"第 {page_num} 页 / 共 {total_pages} 页" if pdf_lang == "zh" else f"Page {page_num} of {total_pages}"
    time_str = f"生成时间: {gen_time}" if pdf_lang == "zh" else f"Generated: {gen_time}"
    c.drawString(MARGIN_L, 13, loc_str)
    c.drawCentredString(w / 2, 13, time_str)
    c.drawRightString(w - MARGIN_R, 13, pg_str)


def draw_section_header(c, y, label, pdf_lang):
    bar_h = 22
    c.setFillColor(C_ACCENT2)
    c.roundRect(MARGIN_L, y - bar_h, CONTENT_W, bar_h, 4, fill=1, stroke=0)
    c.setFillColor(C_WHITE); c.setFont(_font(pdf_lang, bold=True), 10)
    c.drawString(MARGIN_L + 10, y - bar_h + 7, label)
    return y - bar_h - 8


def draw_kv_row(c, x, y, w, label, value, pdf_lang, shade=False):
    ROW_H = 18
    if shade:
        c.setFillColor(C_LIGHT)
        c.rect(x, y - ROW_H, w, ROW_H, fill=1, stroke=0)
    c.setStrokeColor(C_GREY_LINE); c.setLineWidth(0.4)
    c.line(x, y - ROW_H, x + w, y - ROW_H)
    lw = w * 0.38
    c.setFillColor(C_ACCENT2); c.setFont(_font(pdf_lang, bold=True), 8)
    c.drawString(x + 6, y - ROW_H + 6, str(label))
    c.setFillColor(C_PRIMARY); c.setFont(_font(pdf_lang), 8)
    c.drawString(x + lw + 6, y - ROW_H + 6, str(value)[:80])
    return y - ROW_H


def draw_two_col_kv(c, y, pairs, pdf_lang):
    col_w = (CONTENT_W - 10) / 2
    for i, (l1, v1, l2, v2) in enumerate(pairs):
        shade = (i % 2 == 0)
        draw_kv_row(c, MARGIN_L,              y, col_w, l1, v1, pdf_lang, shade)
        draw_kv_row(c, MARGIN_L + col_w + 10, y, col_w, l2, v2, pdf_lang, shade)
        y -= 18
    return y


def draw_text_block(c, y, label, text, pdf_lang, accent_color=None):
    if not text or not str(text).strip():
        text = "—"
    if accent_color is None:
        accent_color = C_ACCENT2
    FONT_SIZE = 8; LINE_H = 14; PADDING = 8; LABEL_H = 18
    lines = _wrap_text(text, CONTENT_W - 20, FONT_SIZE)
    block_h = LABEL_H + len(lines) * LINE_H + PADDING * 2
    c.setFillColor(C_LIGHT)
    c.rect(MARGIN_L, y - block_h, CONTENT_W, block_h, fill=1, stroke=0)
    c.setFillColor(accent_color)
    c.rect(MARGIN_L, y - LABEL_H, CONTENT_W, LABEL_H, fill=1, stroke=0)
    c.setStrokeColor(C_GREY_LINE); c.setLineWidth(0.4)
    c.rect(MARGIN_L, y - block_h, CONTENT_W, block_h, fill=0, stroke=1)
    c.setFillColor(C_WHITE); c.setFont(_font(pdf_lang, bold=True), 8)
    c.drawString(MARGIN_L + 8, y - LABEL_H + 6, str(label))
    ty = y - LABEL_H - PADDING - LINE_H + 4
    c.setFillColor(C_PRIMARY); c.setFont(_font(pdf_lang), FONT_SIZE)
    for line in lines:
        if line:
            c.drawString(MARGIN_L + 10, ty, line)
        ty -= LINE_H
    return y - block_h - 6


def draw_generic_table(c, y, rows, col_widths, pdf_lang, header=True):
    HDR_H = 22; ROW_PAD = 6; FS = 8; LH = 13
    abs_widths = [CONTENT_W * f for f in col_widths]
    col_inner  = [cw - 10 for cw in abs_widths]
    fn_b = _font(pdf_lang, bold=True); fn_r = _font(pdf_lang)

    start_row = 0
    if header:
        c.setFillColor(C_ACCENT)
        c.rect(MARGIN_L, y - HDR_H, CONTENT_W, HDR_H, fill=1, stroke=0)
        c.setFillColor(C_WHITE); c.setFont(fn_b, 8.5)
        cx = MARGIN_L + 5
        for i, cell in enumerate(rows[0]):
            c.drawString(cx, y - HDR_H + 8, str(cell))
            cx += abs_widths[i]
        y -= HDR_H
        start_row = 1

    table_top = y
    for ri, row in enumerate(rows[start_row:]):
        wrapped = [_wrap_text(str(cell), col_inner[ci], FS) for ci, cell in enumerate(row)]
        max_lines = max(len(w) for w in wrapped)
        row_h = max_lines * LH + ROW_PAD * 2

        if ri % 2 == 0:
            c.setFillColor(C_LIGHT)
            c.rect(MARGIN_L, y - row_h, CONTENT_W, row_h, fill=1, stroke=0)

        c.setStrokeColor(C_GREY_LINE); c.setLineWidth(0.3)
        c.line(MARGIN_L, y - row_h, MARGIN_L + CONTENT_W, y - row_h)

        cx_sep = MARGIN_L
        for cw in abs_widths[:-1]:
            cx_sep += cw
            c.line(cx_sep, y, cx_sep, y - row_h)

        cx = MARGIN_L
        for ci, (wlines, cw) in enumerate(zip(wrapped, abs_widths)):
            ty = y - ROW_PAD - LH + 3
            if ci == 0:
                c.setFillColor(C_ACCENT2); c.setFont(fn_b, FS)
            else:
                c.setFillColor(C_PRIMARY); c.setFont(fn_r, FS)
            for ln in wlines:
                if ln:
                    c.drawString(cx + 5, ty, ln)
                ty -= LH
            cx += cw
        y -= row_h

    c.setStrokeColor(C_GREY_LINE); c.setLineWidth(0.5)
    c.rect(MARGIN_L, y, CONTENT_W, table_top - y, fill=0, stroke=1)
    return y - 6


def draw_result_badge(c, x, y, result, pdf_lang):
    r = str(result).strip().upper()
    if r in ("PASS", "通过"):
        bg, fg = C_GREEN, C_WHITE
        label = pt("pass_label", pdf_lang)
    elif r in ("FAIL", "不通过"):
        bg, fg = C_RED, C_WHITE
        label = pt("fail_label", pdf_lang)
    else:
        bg, fg = C_ORANGE, C_WHITE
        label = pt("accept_label", pdf_lang)
    w = _text_width(label, 7) + 10
    c.setFillColor(bg)
    c.roundRect(x - w / 2, y - 4, w, 12, 3, fill=1, stroke=0)
    c.setFillColor(fg); c.setFont(_font(pdf_lang, bold=True), 7)
    c.drawCentredString(x, y + 2, label)


# ══════════════════════════════════════════════════════════════════════════
#  PDF GENERATION
# ══════════════════════════════════════════════════════════════════════════
def generate_pdf():
    pdf_lang = st.session_state.pdf_language
    city     = st.session_state.selected_city
    city_zh  = CHINESE_CITIES.get(city, city)
    china_tz = pytz.timezone('Asia/Shanghai')
    now      = datetime.now(china_tz)
    gen_time = now.strftime('%Y-%m-%d %H:%M')

    def gs(key, default=''):
        v = st.session_state.get(key, default)
        return str(v) if v is not None else ''

    def fmt_date(d):
        if d is None: return ''
        try:
            return d.strftime('%Y年%m月%d日') if pdf_lang == "zh" else d.strftime('%Y-%m-%d')
        except: return str(d)

    def res(key):
        v = gs(key)
        if not v: return '—'
        v_up = v.upper()
        if pdf_lang == "zh":
            if v_up == "PASS": return pt("pass_label", pdf_lang)
            if v_up == "FAIL": return pt("fail_label", pdf_lang)
            return pt("accept_label", pdf_lang)
        return v

    def com(key):
        v = gs(key)
        return v if v else '—'

    def _build(buf_out, total_pages_known):
        c = rl_canvas.Canvas(buf_out, pagesize=A4)
        fn_b = _font(pdf_lang, bold=True); fn_r = _font(pdf_lang)
        page_counter = [1]

        def new_page():
            c.showPage(); page_counter[0] += 1
            draw_page_frame(c, page_counter[0], total_pages_known, pdf_lang, city, city_zh, gen_time)
            return PAGE_H - HEADER_H - 20

        def check_space(y, needed=120):
            if y < FOOTER_H + needed:
                return new_page()
            return y

        # ── PAGE 1 ──────────────────────────────────────────────────────
        draw_page_frame(c, 1, total_pages_known, pdf_lang, city, city_zh, gen_time)
        y = PAGE_H - HEADER_H - 20

        # Cover banner
        c.setFillColor(C_PRIMARY)
        c.rect(MARGIN_L, y - 120, CONTENT_W, 120, fill=1, stroke=0)
        c.setFillColor(C_ACCENT)
        c.rect(MARGIN_L, y - 120, 8, 120, fill=1, stroke=0)
        c.setFillColor(C_ACCENT)
        c.rect(MARGIN_L, y - 6, CONTENT_W, 6, fill=1, stroke=0)
        c.setFillColor(C_WHITE); c.setFont(fn_b, 20)
        c.drawString(MARGIN_L + 24, y - 40, "Grand Step (H.K.) Ltd")
        c.setFont(fn_r, 11)
        c.setFillColor(colors.HexColor('#aab8ff'))
        c.drawString(MARGIN_L + 24, y - 60, pt("report_title", pdf_lang))
        pill_items = [
            ("日期" if pdf_lang == "zh" else "Date",     fmt_date(gs('test_date') and st.session_state.get('test_date') or now.date())),
            ("地点" if pdf_lang == "zh" else "Location", f"{city} {city_zh}" if pdf_lang == "zh" else city),
            ("语言" if pdf_lang == "zh" else "Language", "中文" if pdf_lang == "zh" else "English"),
        ]
        px = MARGIN_L + 24
        for lbl, val in pill_items:
            c.setFillColor(colors.HexColor('#0d2244'))
            pill_w = _text_width(f"{lbl}: {val}", 7) + 16
            c.roundRect(px, y - 108, pill_w, 16, 4, fill=1, stroke=0)
            c.setFillColor(colors.HexColor('#aab8ff')); c.setFont(fn_b, 7)
            c.drawString(px + 8, y - 100, f"{lbl}:")
            lbl_w = _text_width(lbl, 7) + 8
            c.setFillColor(C_WHITE); c.setFont(fn_r, 7)
            c.drawString(px + 8 + lbl_w, y - 100, val)
            px += pill_w + 8
        y -= 136

        # ── 1. BASIC INFORMATION ─────────────────────────────────────────
        y = draw_section_header(c, y, pt("basic_info", pdf_lang), pdf_lang)
        test_date_val = st.session_state.get('test_date', now.date())
        pairs = [
            (pt("report_no", pdf_lang), gs('report_no') or '—',
             pt("date_no",   pdf_lang), fmt_date(test_date_val)),
            (pt("ci_no",     pdf_lang), gs('ci_no') or '—',
             pt("order_qty", pdf_lang), gs('order_qty') or '—'),
            (pt("brand",     pdf_lang), gs('brand') or '—',
             pt("produced_qty", pdf_lang), gs('produced_qty') or '—'),
            (pt("style_no",  pdf_lang), gs('style_no') or '—',
             pt("factory_trader", pdf_lang), gs('factory') or '—'),
            (pt("sales",     pdf_lang), gs('sales') or '—', '', ''),
        ]
        y = draw_two_col_kv(c, y, pairs, pdf_lang)
        y -= 6
        y = draw_text_block(c, y, pt("standard_note", pdf_lang), pt("standard_note", pdf_lang), pdf_lang, C_ACCENT)
        y -= 10

        # ── 2. ADHESIVE / PULL TEST ──────────────────────────────────────
        y = check_space(y, 200)
        y = draw_section_header(c, y, pt("adhesive_test", pdf_lang), pdf_lang)

        # --- Flat Shoe sub-header ---
        c.setFillColor(C_ACCENT2)
        c.roundRect(MARGIN_L, y - 18, CONTENT_W, 18, 3, fill=1, stroke=0)
        c.setFillColor(C_WHITE); c.setFont(_font(pdf_lang, bold=True), 9)
        c.drawString(MARGIN_L + 8, y - 18 + 5, pt("flat_shoe", pdf_lang))
        y -= 26

        flat_rows = [
            [pt("item", pdf_lang), pt("standard", pdf_lang), pt("result", pdf_lang), pt("remark", pdf_lang)],
            [pt("toe",      pdf_lang), "12 kg/3N", res('flat_shoe_toe_result'),      com('flat_shoe_toe_remark')],
            [pt("forepart", pdf_lang), "12 kg/3N", res('flat_shoe_forepart_result'), com('flat_shoe_forepart_remark')],
            [pt("waist",    pdf_lang), "12 kg/3N", res('flat_shoe_waist_result'),    com('flat_shoe_waist_remark')],
            [pt("heel",     pdf_lang), "—",        res('flat_shoe_heel_result'),     com('flat_shoe_heel_remark')],
        ]
        y = draw_generic_table(c, y, flat_rows, [0.22, 0.28, 0.20, 0.30], pdf_lang)
        y -= 10

        # --- High Heel sub-header ---
        y = check_space(y, 160)
        c.setFillColor(C_ACCENT2)
        c.roundRect(MARGIN_L, y - 18, CONTENT_W, 18, 3, fill=1, stroke=0)
        c.setFillColor(C_WHITE); c.setFont(_font(pdf_lang, bold=True), 9)
        hh_label = pt("high_heel", pdf_lang) + " / " + pt("sole_wedge", pdf_lang)
        c.drawString(MARGIN_L + 8, y - 18 + 5, hh_label)
        y -= 26

        hh_rows = [
            [pt("item", pdf_lang), pt("standard", pdf_lang), pt("result", pdf_lang), pt("remark", pdf_lang)],
            [pt("toe",      pdf_lang), "12 kg/3N", res('high_heel_toe_result'),      com('high_heel_toe_remark')],
            [pt("forepart", pdf_lang), "12 kg/3N", res('high_heel_forepart_result'), com('high_heel_forepart_remark')],
            [pt("waist",    pdf_lang), "12 kg/3N", res('high_heel_waist_result'),    com('high_heel_waist_remark')],
            [pt("heel",     pdf_lang),
             f"60kg/500N ({pt('cm_5_8', pdf_lang)}) / 80kg/800N ({pt('above_8cm', pdf_lang)})",
             res('high_heel_heel_result'), com('high_heel_heel_remark')],
        ]
        y = draw_generic_table(c, y, hh_rows, [0.15, 0.35, 0.20, 0.30], pdf_lang)
        y -= 10

        # ── 3. COMPONENTS PHYSICAL TEST ──────────────────────────────────
        y = check_space(y, 160)
        y = draw_section_header(c, y, pt("components_test", pdf_lang), pdf_lang)

        comp_hdr = [
            pt("item", pdf_lang), pt("standard", pdf_lang), pt("result", pdf_lang), pt("comments", pdf_lang),
            pt("item", pdf_lang), pt("standard", pdf_lang), pt("result", pdf_lang), pt("comments", pdf_lang),
        ]
        comp_rows = [
            comp_hdr,
            [pt("buckle", pdf_lang),      pt("buckle_std", pdf_lang),      res('buckle_result'),      com('buckle_comments'),
             pt("top_lift", pdf_lang),    pt("top_lift_std", pdf_lang),    res('top_lift_result'),    com('top_lift_comments')],
            [pt("strap", pdf_lang),       pt("strap_std", pdf_lang),       res('strap_result'),       com('strap_comments'),
             pt("loop", pdf_lang),        pt("loop_std", pdf_lang),        res('loop_result'),        com('loop_comments')],
            [pt("eyelet", pdf_lang),      pt("eyelet_std", pdf_lang),      res('eyelet_result'),      com('eyelet_comments'),
             pt("toe_post", pdf_lang),    pt("toe_post_std", pdf_lang),    res('toe_post_result'),    com('toe_post_comments')],
            [pt("studs", pdf_lang),       pt("studs_std", pdf_lang),       res('studs_result'),       com('studs_comments'),
             pt("zipper", pdf_lang),      pt("zipper_std", pdf_lang),      res('zipper_result'),      com('zipper_comments')],
            [pt("diamond_bow", pdf_lang), pt("diamond_std", pdf_lang),     res('diamond_result'),     com('diamond_comments'),
             pt("perment_set", pdf_lang), pt("perment_set_std", pdf_lang), res('perment_set_result'), com('perment_set_comments')],
        ]
        y = draw_generic_table(c, y, comp_rows,
                               [0.12, 0.13, 0.10, 0.15, 0.12, 0.13, 0.10, 0.15], pdf_lang)
        y -= 6

        # Rust Test sub-section
        y = check_space(y, 80)
        rust_label = pt("rust_test", pdf_lang)
        c.setFillColor(C_ACCENT2)
        c.roundRect(MARGIN_L, y - 18, CONTENT_W, 18, 3, fill=1, stroke=0)
        c.setFillColor(C_WHITE); c.setFont(fn_b, 9)
        c.drawString(MARGIN_L + 8, y - 18 + 5, rust_label)
        y -= 26

        rust_rows = [
            [pt("buckle",  pdf_lang), pt("eyelet", pdf_lang), pt("strap", pdf_lang), pt("studs", pdf_lang)],
            [res('rust_buckle_result'), res('rust_eyelet_result'), res('rust_strap_result'), res('rust_studs_result')],
        ]
        y = draw_generic_table(c, y, rust_rows, [0.25, 0.25, 0.25, 0.25], pdf_lang, header=False)
        y -= 10

        # ── PAGE BREAK before remaining tests ───────────────────────────
        y = new_page()

        # ── 4. FLEXING TEST ──────────────────────────────────────────────
        y = draw_section_header(c, y, pt("flexing_test", pdf_lang), pdf_lang)
        flex_rows = [
            [pt("item", pdf_lang), pt("standard", pdf_lang), pt("result", pdf_lang), pt("comments", pdf_lang)],
            [pt("upper",    pdf_lang), pt("upper_std",     pdf_lang), res('upper_flex_result'), com('upper_flex_comments')],
            [pt("shoe_flex",pdf_lang), pt("shoe_flex_std", pdf_lang), res('shoe_flex_result'),  com('shoe_flex_comments')],
            [pt("foxing",   pdf_lang), pt("foxing_std",    pdf_lang), res('foxing_result'),     com('foxing_comments')],
        ]
        y = draw_generic_table(c, y, flex_rows, [0.22, 0.30, 0.18, 0.30], pdf_lang)
        y -= 10

        # ── 5. ABRASION TEST ─────────────────────────────────────────────
        y = check_space(y, 100)
        y = draw_section_header(c, y, pt("abrasion_test", pdf_lang), pdf_lang)
        abr_rows = [
            [pt("item", pdf_lang), pt("standard", pdf_lang), pt("result", pdf_lang), pt("comments", pdf_lang)],
            [pt("top_lift_abrasion", pdf_lang), "", res('top_lift_abrasion_result'), com('top_lift_abrasion_comments')],
            [pt("outsole_abrasion",  pdf_lang), pt("outsole_abrasion_std", pdf_lang), res('outsole_abrasion_result'), com('outsole_abrasion_comments')],
        ]
        y = draw_generic_table(c, y, abr_rows, [0.22, 0.30, 0.18, 0.30], pdf_lang)
        y -= 10

        # ── 6. RESISTANCE TEST ───────────────────────────────────────────
        y = check_space(y, 100)
        y = draw_section_header(c, y, pt("resistance_test", pdf_lang), pdf_lang)
        res_rows = [
            [pt("item", pdf_lang), pt("standard", pdf_lang), pt("result", pdf_lang), pt("comments", pdf_lang)],
            [pt("outsole_resistance", pdf_lang), "", res('outsole_resistance_result'), com('outsole_resistance_comments')],
            [pt("heel_fatigue",       pdf_lang), pt("heel_fatigue_std", pdf_lang), res('heel_fatigue_result'), com('heel_fatigue_comments')],
        ]
        y = draw_generic_table(c, y, res_rows, [0.22, 0.30, 0.18, 0.30], pdf_lang)
        y -= 10

        # ── 7. HARDNESS TEST ─────────────────────────────────────────────
        y = check_space(y, 100)
        y = draw_section_header(c, y, pt("hardness_test", pdf_lang), pdf_lang)
        hrd_rows = [
            [pt("item", pdf_lang), pt("standard", pdf_lang), pt("result", pdf_lang), pt("comments", pdf_lang)],
            [pt("eva_hardness",     pdf_lang), "", res('eva_hardness_result'),     com('eva_hardness_comments')],
            [pt("outsole_hardness", pdf_lang), "", res('outsole_hardness_result'), com('outsole_hardness_comments')],
        ]
        y = draw_generic_table(c, y, hrd_rows, [0.22, 0.30, 0.18, 0.30], pdf_lang)
        y -= 10

        # ── 8. CONCLUSION ────────────────────────────────────────────────
        y = check_space(y, 120)
        y = draw_section_header(c, y, pt("conclusion_sec", pdf_lang), pdf_lang)

        col_w3 = CONTENT_W / 3
        labels = [pt("pass_label", pdf_lang), pt("fail_label", pdf_lang), pt("accept_label", pdf_lang)]
        values = [gs('pass_result'), gs('fail_result'), gs('accept_result')]
        label_colors = [C_GREEN, C_RED, C_ORANGE]
        BOX_HDR = 20; BOX_PAD = 8; FS_C = 8; LH_C = 13

        max_lines = 1
        for v in values:
            max_lines = max(max_lines, len(_wrap_text(v or '—', col_w3 - 16, FS_C)))
        box_h = BOX_HDR + max_lines * LH_C + BOX_PAD * 2

        for ci, (lbl, val, lc) in enumerate(zip(labels, values, label_colors)):
            bx = MARGIN_L + ci * col_w3
            c.setFillColor(C_LIGHT)
            c.rect(bx, y - box_h, col_w3, box_h, fill=1, stroke=0)
            c.setFillColor(lc)
            c.rect(bx, y - BOX_HDR, col_w3, BOX_HDR, fill=1, stroke=0)
            c.setFillColor(C_WHITE); c.setFont(fn_b, 9)
            c.drawCentredString(bx + col_w3 / 2, y - BOX_HDR + 7, lbl)
            c.setFillColor(C_PRIMARY); c.setFont(fn_r, FS_C)
            wlines = _wrap_text(val or '—', col_w3 - 16, FS_C)
            ty = y - BOX_HDR - BOX_PAD - LH_C + 3
            for ln in wlines:
                if ln:
                    c.drawString(bx + 8, ty, ln)
                ty -= LH_C
            c.setStrokeColor(C_GREY_LINE); c.setLineWidth(0.4)
            c.rect(bx, y - box_h, col_w3, box_h, fill=0, stroke=1)
        y -= box_h + 12

        # ── SIGNATURES ───────────────────────────────────────────────────
        y = check_space(y, 100)
        col_w2 = (CONTENT_W - 10) / 2
        sig_pairs = [
            (pt("verified_by",    pdf_lang), gs('verified_by')    or ''),
            (pt("testing_person", pdf_lang), gs('testing_person') or ''),
        ]
        c.setFillColor(C_LIGHT)
        c.roundRect(MARGIN_L, y - 70, CONTENT_W, 70, 4, fill=1, stroke=0)
        c.setStrokeColor(C_GREY_LINE); c.setLineWidth(0.5)
        c.roundRect(MARGIN_L, y - 70, CONTENT_W, 70, 4, fill=0, stroke=1)
        for i, (lbl, val) in enumerate(sig_pairs):
            bx = MARGIN_L + i * (col_w2 + 10)
            c.setFillColor(C_ACCENT2); c.setFont(fn_b, 8)
            c.drawString(bx + 8, y - 18, lbl)
            c.setFillColor(C_PRIMARY); c.setFont(fn_r, 8)
            c.drawString(bx + 8, y - 32, val or "_________________")
            c.setStrokeColor(C_PRIMARY); c.setLineWidth(1)
            c.line(bx + 8, y - 44, bx + col_w2 - 8, y - 44)
            c.setFillColor(C_GREY_TEXT); c.setFont(fn_r, 7)
            c.drawCentredString(bx + col_w2 / 2, y - 56, pt("signature", pdf_lang))
        y -= 80

        # Version & disclaimer
        y = check_space(y, 40)
        c.setFillColor(C_GREY_TEXT); c.setFont(fn_r, 7.5)
        c.drawRightString(MARGIN_L + CONTENT_W, y, pt("version", pdf_lang))
        y -= 12
        disc = pt("standard_note", pdf_lang)
        disc_lines = _wrap_text(disc, CONTENT_W - 20, 7.5)
        for ln in disc_lines:
            if ln: c.drawString(MARGIN_L, y, ln)
            y -= 11

        c.save()
        return page_counter[0]

    count_buf = io.BytesIO()
    actual_total = _build(count_buf, 99)
    buf = io.BytesIO()
    _build(buf, actual_total)
    buf.seek(0)
    return buf


# ══════════════════════════════════════════════════════════════════════════
#  STREAMLIT UI
# ══════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
  .main-header{font-size:2.6rem;font-weight:800;text-align:center;
    color:#4299E1;margin-bottom:1.5rem;padding:0.5rem;}
  .section-header{font-size:1.4rem;font-weight:700;color:#1a1a2e;
    margin:2rem 0 1rem;padding:0.7rem 1.2rem;
    background:linear-gradient(135deg,#f0f4ff 0%,#dde4ff 100%);
    border-radius:10px;border-left:5px solid #e94560;}
  .stButton>button{background:linear-gradient(135deg,#1a1a2e 0%,#e94560 100%);
    color:white;font-size:1.1rem;font-weight:600;padding:0.9rem 2rem;
    border-radius:10px;border:none;width:100%;transition:all .3s;}
  .stButton>button:hover{transform:translateY(-2px);box-shadow:0 8px 16px rgba(233,69,96,.35);}
  .footer{text-align:center;padding:1.5rem;
    background:linear-gradient(135deg,#f0f4ff 0%,#dde4ff 100%);
    border-radius:12px;margin-top:2rem;border-top:3px solid #e94560;}
  .location-badge{display:inline-flex;align-items:center;gap:6px;
    background:linear-gradient(135deg,#1a1a2e 0%,#0f3460 100%);
    color:white;padding:.4rem .9rem;border-radius:20px;font-weight:600;font-size:.85rem;}
  .remark-label{font-size:.78rem;font-weight:600;color:#0f3460;
    margin-bottom:2px;margin-top:6px;}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")

    st.markdown("#### 🌐 Interface Language")
    ui_choice = st.selectbox("UI Lang", ["English", "中文 (Mandarin)"],
                             index=0 if st.session_state.ui_language == "en" else 1,
                             key="ui_lang_select", label_visibility="collapsed")
    new_ui = "en" if ui_choice == "English" else "zh"
    if new_ui != st.session_state.ui_language:
        st.session_state.ui_language = new_ui
        st.session_state.translations_cache = {}
        st.rerun()

    st.markdown("#### 📄 PDF Language")
    pdf_choice = st.selectbox("PDF Lang", ["English", "中文 (Mandarin)"],
                              index=0 if st.session_state.pdf_language == "en" else 1,
                              key="pdf_lang_select", label_visibility="collapsed")
    st.session_state.pdf_language = "en" if pdf_choice == "English" else "zh"

    st.markdown("#### 📍 Location")
    city_keys = list(CHINESE_CITIES.keys())
    city_idx  = city_keys.index(st.session_state.selected_city) if st.session_state.selected_city in city_keys else 0
    sel_city  = st.selectbox("Location", city_keys, index=city_idx,
                             key="city_select", label_visibility="collapsed")
    st.session_state.selected_city = sel_city
    st.markdown(f'<div class="location-badge">📍 {sel_city} ({CHINESE_CITIES.get(sel_city,"")})</div>',
                unsafe_allow_html=True)

    st.markdown("#### 🕐 Local Time")
    china_tz = pytz.timezone('Asia/Shanghai')
    now_cn = datetime.now(china_tz)
    st.metric("Local Time", now_cn.strftime('%H:%M:%S'), now_cn.strftime('%Y-%m-%d'))

    if openai_client:
        st.success(f"✅ {t('translation_active')}")
    else:
        st.warning(f"⚠️ {t('translation_off')}")

    st.markdown("---")
    st.markdown("### ⚠️ Test Standards Note")
    st.info("This is Grand Step Company Standard only. Any priority should follow Customer or 3rd Lab Standard.")

    st.markdown("---")
    st.markdown("### ℹ️ Quick Guide")
    for step in ["1. Fill Basic Info", "2. Complete all test tabs",
                 "3. Enter results & comments", "4. Add conclusion & signatures",
                 "5. Generate PDF"]:
        st.write(step)

# ── Main header ────────────────────────────────────────────────────────────
st.markdown(f'<div class="main-header">🧪 {t("title")}</div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    t("tab_basic"), t("tab_adhesive"), t("tab_components"),
    t("tab_flexing"), t("tab_abrasion"), t("tab_resistance"),
    t("tab_hardness"), t("tab_conclusion"),
])

RESULT_OPTS = ["Pass", "Fail", "Accept"]
RUST_OPTS   = ["Pass", "Fail"]

# ══════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown(f'<div class="section-header">📋 {t("basic_info")}</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.text_input(f"📄 {t('report_no')}", placeholder="PTR-2024-001", key="report_no")
        st.text_input(f"📄 {t('ci_no')}",     placeholder="CI-2024-001",  key="ci_no")
        st.text_input(f"👕 {t('style_no')}",  placeholder="XYZ-2024",     key="style_no")
        st.text_input(f"🏭 {t('factory_trader')}", placeholder="ABC Co.",  key="factory")
    with c2:
        st.date_input(f"📅 Test Date", datetime.now().date(), key="test_date")
        st.number_input(f"🔢 {t('order_qty')}",    min_value=0, value=1000, key="order_qty")
        st.text_input(f"🏷️ {t('brand')}",          placeholder="Brand Name", key="brand")
        st.number_input(f"🔢 {t('produced_qty')}", min_value=0, value=1000, key="produced_qty")
        st.text_input(f"👔 {t('sales')}",           placeholder="Sales Rep",  key="sales")
    st.info(f"⚠️ {t('standard_note')}")

# ══════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown(f'<div class="section-header">📏 {t("adhesive_test")}</div>', unsafe_allow_html=True)

    # ── Flat Shoe ──────────────────────────────────────────────────────────
    st.markdown("### 👟 Flat Shoe")
    st.caption("Standard: 12 kg/3N for Toe, Forepart, Waist")

    for part_key, part_label in [("toe", "Toe"), ("forepart", "Forepart"),
                                  ("waist", "Waist"), ("heel", "Heel")]:
        col_res, col_rem = st.columns([1, 2])
        with col_res:
            st.selectbox(
                f"Flat Shoe – {part_label}",
                RESULT_OPTS,
                key=f"flat_shoe_{part_key}_result"
            )
        with col_rem:
            st.markdown(f'<div class="remark-label">📝 {part_label} Remark</div>', unsafe_allow_html=True)
            st.text_input(
                f"flat_shoe_{part_key}_remark_label",
                placeholder=f"Remark for Flat Shoe {part_label}...",
                key=f"flat_shoe_{part_key}_remark",
                label_visibility="collapsed"
            )

    st.divider()

    # ── High Heel ──────────────────────────────────────────────────────────
    st.markdown("### 👠 High Heel / Sole / Wedge")
    st.caption("Standard: Heel 5CM–8CM: 60kg/500N | Above 8CM: 80kg/800N")

    for part_key, part_label in [("toe", "Toe"), ("forepart", "Forepart"),
                                  ("waist", "Waist"), ("heel", "Heel")]:
        col_res, col_rem = st.columns([1, 2])
        with col_res:
            st.selectbox(
                f"High Heel – {part_label}",
                RESULT_OPTS,
                key=f"high_heel_{part_key}_result"
            )
        with col_rem:
            st.markdown(f'<div class="remark-label">📝 {part_label} Remark</div>', unsafe_allow_html=True)
            st.text_input(
                f"high_heel_{part_key}_remark_label",
                placeholder=f"Remark for High Heel {part_label}...",
                key=f"high_heel_{part_key}_remark",
                label_visibility="collapsed"
            )

# ══════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown(f'<div class="section-header">🔩 {t("components_test")}</div>', unsafe_allow_html=True)

    comp_fields = [
        ("buckle", "Buckle"), ("strap", "Strap"), ("eyelet", "Eyelet"),
        ("studs",  "Studs"),  ("diamond_bow", "Diamond/Bow"),
        ("top_lift", "Top Lift"), ("loop", "Loop"), ("toe_post", "Toe Post"),
        ("zipper", "Zipper"), ("perment_set", "Perment Set 400N"),
    ]
    c1, c2, c3 = st.columns(3)
    for i, (k, lbl) in enumerate(comp_fields):
        col = [c1, c2, c3][i % 3]
        with col:
            st.selectbox(lbl, RESULT_OPTS, key=f"{k}_result")
            st.text_input(f"{lbl} Comments", placeholder="Comments...",
                          key=f"{k}_comments", label_visibility="collapsed")

    st.markdown(f"### 🛡️ {t('rust_test')}")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.selectbox("Rust Buckle",  RUST_OPTS, key="rust_buckle_result")
    with c2: st.selectbox("Rust Eyelet",  RUST_OPTS, key="rust_eyelet_result")
    with c3: st.selectbox("Rust Strap",   RUST_OPTS, key="rust_strap_result")
    with c4: st.selectbox("Rust Studs",   RUST_OPTS, key="rust_studs_result")

# ══════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown(f'<div class="section-header">🔄 {t("flexing_test")}</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.selectbox("Upper",     RESULT_OPTS, key="upper_flex_result")
        st.text_input("Upper Comments", placeholder="Comments...", key="upper_flex_comments", label_visibility="collapsed")
    with c2:
        st.selectbox("Shoe Flex", RESULT_OPTS, key="shoe_flex_result")
        st.text_input("Shoe Flex Comments", placeholder="Comments...", key="shoe_flex_comments", label_visibility="collapsed")
    with c3:
        st.selectbox("Foxing",    RESULT_OPTS, key="foxing_result")
        st.text_input("Foxing Comments", placeholder="Comments...", key="foxing_comments", label_visibility="collapsed")

# ══════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown(f'<div class="section-header">↔️ {t("abrasion_test")}</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.selectbox("Top Lift Abrasion", RESULT_OPTS, key="top_lift_abrasion_result")
        st.text_input("Top Lift Comments", placeholder="Comments...", key="top_lift_abrasion_comments", label_visibility="collapsed")
    with c2:
        st.selectbox("Outsole Abrasion",  RESULT_OPTS, key="outsole_abrasion_result")
        st.text_input("Outsole Abrasion Comments", placeholder="Comments...", key="outsole_abrasion_comments", label_visibility="collapsed")

# ══════════════════════════════════════════════════════════════════════════
with tab6:
    st.markdown(f'<div class="section-header">🛡️ {t("resistance_test")}</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.selectbox("Outsole Resistance", RESULT_OPTS, key="outsole_resistance_result")
        st.text_input("Outsole Resistance Comments", placeholder="Comments...", key="outsole_resistance_comments", label_visibility="collapsed")
    with c2:
        st.selectbox("Heel Fatigue",       RESULT_OPTS, key="heel_fatigue_result")
        st.text_input("Heel Fatigue Comments", placeholder="Comments...", key="heel_fatigue_comments", label_visibility="collapsed")

# ══════════════════════════════════════════════════════════════════════════
with tab7:
    st.markdown(f'<div class="section-header">💎 {t("hardness_test")}</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.selectbox("EVA Hardness",     RESULT_OPTS, key="eva_hardness_result")
        st.text_input("EVA Comments",    placeholder="Comments...", key="eva_hardness_comments", label_visibility="collapsed")
    with c2:
        st.selectbox("Outsole Hardness", RESULT_OPTS, key="outsole_hardness_result")
        st.text_input("Outsole Hardness Comments", placeholder="Comments...", key="outsole_hardness_comments", label_visibility="collapsed")

# ══════════════════════════════════════════════════════════════════════════
with tab8:
    st.markdown(f'<div class="section-header">✅ {t("conclusion_sec")}</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**✅ PASS**")
        st.text_area("Pass items", placeholder="List items that passed...", height=120, key="pass_result", label_visibility="collapsed")
    with c2:
        st.markdown("**❌ FAIL**")
        st.text_area("Fail items", placeholder="List items that failed...", height=120, key="fail_result", label_visibility="collapsed")
    with c3:
        st.markdown("**⚠️ ACCEPT**")
        st.text_area("Accept items", placeholder="Accepted with conditions...", height=120, key="accept_result", label_visibility="collapsed")

    st.markdown(f'<div class="section-header">✍️ Signatures</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.text_input(f"👁️ {t('verified_by')}",    placeholder="Quality Manager", key="verified_by")
    with c2:
        st.text_input(f"🧪 {t('testing_person')}", placeholder="Tester Name",     key="testing_person")

# ── Generate button ─────────────────────────────────────────────────────────
st.markdown("---")
_, center_col, _ = st.columns([1, 2, 1])
with center_col:
    if st.button(t('generate_pdf'), use_container_width=True):
        if not st.session_state.get('ci_no') or not st.session_state.get('style_no'):
            st.error(f"⚠️ {t('fill_required')}")
        else:
            with st.spinner(f"⏳ {t('creating_pdf')}"):
                try:
                    pdf_buf = generate_pdf()
                    st.success(f"✅ {t('generate_success')}")
                    with st.expander(f"ℹ️ {t('pdf_details')}"):
                        mc1, mc2 = st.columns(2)
                        with mc1:
                            st.metric(t('location'),
                                      f"{st.session_state.selected_city} ({CHINESE_CITIES.get(st.session_state.selected_city,'')})")
                            st.metric(t('report_language'),
                                      "中文" if st.session_state.pdf_language == "zh" else "English")
                        with mc2:
                            st.metric(t('generated'),
                                      datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%H:%M:%S'))
                    fname = (f"Physical_Test_{st.session_state.get('ci_no','report')}_"
                             f"{st.session_state.selected_city}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
                    st.download_button(label=t('download_pdf'), data=pdf_buf,
                                       file_name=fname, mime="application/pdf",
                                       use_container_width=True)
                except Exception as e:
                    st.error(f"❌ {t('error_generating')}: {str(e)}")
                    with st.expander("Debug"):
                        import traceback; st.code(traceback.format_exc())

# ── Footer ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="footer">
  <p style="font-size:1.1rem;font-weight:700;color:#1a1a2e;margin-bottom:.4rem;">
    🧪 {t('footer_text')}
  </p>
  <p style="font-size:.85rem;color:#555;">
    📍 {st.session_state.selected_city} ({CHINESE_CITIES.get(st.session_state.selected_city,'')}) &nbsp;|&nbsp;
    🌐 {"中文" if st.session_state.pdf_language=="zh" else "English"}
  </p>
  <p style="font-size:.75rem;color:#999;margin-top:.8rem;">
    {t('powered_by')} &nbsp;|&nbsp; {t('copyright')}
  </p>
</div>
""", unsafe_allow_html=True)
