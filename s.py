import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from datetime import datetime
import io
import pytz
from openai import OpenAI
import os
from dotenv import load_dotenv
import base64
from io import BytesIO

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key:
    openai_client = OpenAI(api_key=openai_api_key)
else:
    openai_client = None
    st.warning("OpenAI API key not found. Translation features will be limited.")

# Page config
st.set_page_config(
    page_title="Physical Test Report",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Chinese cities dictionary
CHINESE_CITIES = {
    "Guangzhou": "广东",
    "Shenzhen": "深圳",
    "Dongguan": "东莞",
    "Foshan": "佛山",
    "Zhongshan": "中山",
    "Huizhou": "惠州",
    "Zhuhai": "珠海",
    "Jiangmen": "江门",
    "Zhaoqing": "肇庆",
    "Shanghai": "Shanghai",
    "Beijing": "Beijing",
    "Suzhou": "苏州",
    "Hangzhou": "杭州",
    "Ningbo": "宁波",
    "Wenzhou": "温州",
    "Wuhan": "武汉",
    "Chengdu": "成都",
    "Chongqing": "重庆",
    "Tianjin": "天津",
    "Nanjing": "南京",
    "Xi'an": "西安",
    "Qingdao": "青岛",
    "Dalian": "大连",
    "Shenyang": "沈阳",
    "Changsha": "长沙",
    "Zhengzhou": "郑州",
    "Jinan": "济南",
    "Harbin": "哈尔滨",
    "Changchun": "长春",
    "Taiyuan": "太原",
    "Shijiazhuang": "石家庄",
    "Lanzhou": "兰州",
    "Xiamen": "厦门",
    "Fuzhou": "福州",
    "Nanning": "南宁",
    "Kunming": "昆明",
    "Guiyang": "贵阳",
    "Haikou": "海口",
    "Ürümqi": "乌鲁木齐",
    "Lhasa": "拉萨"
}

# Custom icons for better UI
ICONS = {
    "title": "🧪",
    "basic_info": "📋",
    "adhesive_test": "📏",
    "components_test": "🔩",
    "flexing_test": "🔄",
    "abrasion_test": "↔️",
    "resistance_test": "🛡️",
    "hardness_test": "💎",
    "conclusion": "✅",
    "signatures": "✍️",
    "generate": "📊",
    "download": "📥",
    "settings": "⚙️",
    "language": "🌐",
    "location": "📍",
    "time": "🕐",
    "info": "ℹ️",
    "factory": "🏭",
    "brand": "🏷️",
    "po": "📄",
    "style": "👕",
    "description": "📄",
    "sales": "👔",
    "tech": "🔧",
    "qc": "👁️",
    "test": "🧪",
    "success": "✅",
    "error": "⚠️",
    "warning": "⚠️",
    "upload": "📤",
    "photo": "📷",
    "process": "🔄",
    "standard": "📊",
    "result": "📈",
    "comments": "💬",
    "pull_test": "⚡",
    "rust_test": "🛡️"
}

# Custom CSS with enhanced styling - Green theme for testing
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1.5rem;
        padding: 0.5rem;
        text-shadow: 0 2px 10px rgba(0,0,0,0.1);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .section-header {
        font-size: 1.9rem;
        font-weight: 700;
        color: #2c3e50;
        margin-top: 2.5rem;
        margin-bottom: 1.5rem;
        padding: 0.8rem 1.2rem;
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border-radius: 12px;
        border-left: 5px solid #10b981;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .section-header-icon {
        font-size: 1.8rem;
    }
    .stButton>button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        font-size: 1.3rem;
        font-weight: 600;
        padding: 1rem 2.5rem;
        border-radius: 12px;
        border: none;
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        width: 100%;
        position: relative;
        overflow: hidden;
    }
    .stButton>button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }
    .stButton>button:before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: 0.5s;
    }
    .stButton>button:hover:before {
        left: 100%;
    }
    .info-box {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        padding: 1.8rem;
        border-radius: 15px;
        color: white;
        margin: 1.5rem 0;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.1);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-right: 1px solid #dee2e6;
    }
    .stSelectbox, .stTextInput, .stTextArea, .stRadio, .stNumberInput {
        background-color: white;
        border-radius: 10px;
        padding: 0.8rem;
        box-shadow: 0 3px 6px rgba(0,0,0,0.05);
        border: 1px solid #e0e0e0;
        transition: all 0.3s;
    }
    .stSelectbox:hover, .stTextInput:hover, .stTextArea:hover, .stRadio:hover, .stNumberInput:hover {
        border-color: #10b981;
        box-shadow: 0 5px 10px rgba(16, 185, 129, 0.1);
    }
    .stExpander {
        background-color: white;
        border-radius: 12px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        margin-bottom: 1.2rem;
        border: 1px solid #e0e0e0;
        overflow: hidden;
    }
    .stExpander > div:first-child {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border-radius: 12px 12px 0 0;
    }
    div[data-baseweb="tab"] {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border-radius: 10px !important;
        padding: 0.5rem;
        margin: 0.2rem;
    }
    .metric-container {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    }
    .location-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        box-shadow: 0 3px 6px rgba(0,0,0,0.1);
    }
    .footer {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border-radius: 15px;
        margin-top: 2rem;
        border-top: 3px solid #10b981;
    }
    .test-pass {
        background-color: #d1fae5;
        color: #065f46;
        padding: 4px 12px;
        border-radius: 4px;
        font-weight: bold;
        border: 1px solid #a7f3d0;
    }
    .test-fail {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 4px 12px;
        border-radius: 4px;
        font-weight: bold;
        border: 1px solid #fecaca;
    }
    .test-accept {
        background-color: #fef3c7;
        color: #92400e;
        padding: 4px 12px;
        border-radius: 4px;
        font-weight: bold;
        border: 1px solid #fde68a;
    }
    .test-icon {
        font-size: 1.5rem;
        animation: pulse 2s infinite;
        display: inline-block;
        margin-right: 15px;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'ui_language' not in st.session_state:
    st.session_state.ui_language = "en"
if 'pdf_language' not in st.session_state:
    st.session_state.pdf_language = "en"
if 'selected_city' not in st.session_state:
    st.session_state.selected_city = "Shanghai"
if 'translations_cache' not in st.session_state:
    st.session_state.translations_cache = {}

# Fixed English texts for PDF (no translation needed)
ENGLISH_TEXTS = {
    "company": "GRAND STEP (H.K.) LTD",
    "title": "PHYSICAL TEST REPORT",
    "test_location": "Test Location:",
    "report_date": "Report Date:",
    
    # Section headers
    "basic_info": "1. BASIC INFORMATION",
    "adhesive_test": "2. ADHESIVE/PULL TEST",
    "components_test": "3. COMPONENTS PHYSICAL TEST",
    "flexing_test": "4. FLEXING TEST",
    "abrasion_test": "5. ABRASION TEST",
    "resistance_test": "6. RESISTANCE TEST",
    "hardness_test": "7. HARDNESS TEST",
    "conclusion": "8. CONCLUSION",
    "rust_test": "RUST TEST",
    
    # Labels
    "report_no": "Report No.:",
    "date_no": "Date/No.:",
    "ci_no": "CI / Order No.:",
    "order_qty": "Order QTY:",
    "brand": "Brand:",
    "produced_qty": "Produced QTY:",
    "style_no": "Style No.:",
    "factory_trader": "Factory/Trader:",
    "sales": "Sales:",
    
    # Standard note
    "standard_note": "Note: This is Grand Step Company Standard only. Any priority should follow Customer or 3rd Lab Standard",
    
    # Test headers
    "flat_shoe": "Flat Shoe",
    "high_heel": "High Heel",
    "sole_wedge": "Sole/Wedge",
    "toe": "Toe",
    "forepart": "Forepart",
    "waist": "Waist",
    "heel": "Heel",
    "heel_height": "Heel Height",
    "cm_5_8": "5CM-8CM",
    "above_8cm": "Above 8CM",
    
    # Table headers
    "item": "Item",
    "standard": "Standard",
    "result": "Result",
    "comments": "Comments",
    "remark": "Remark",
    
    # Components
    "buckle": "Buckle",
    "strap": "Strap",
    "eyelet": "Eyelet",
    "studs": "Studs",
    "diamond_bow": "Diamond/Bow",
    "top_lift": "Top lift",
    "loop": "Loop",
    "toe_post": "Toe Post Attachment",
    "zipper": "Zipper",
    "perment_set": "Perment set at 400N",
    
    # Component standards
    "buckle_std": "20 kg/200N",
    "strap_std": "20 kg/200N",
    "eyelet_std": "20 kg/200N",
    "studs_std": "20 kg/200N",
    "diamond_std": "7KG/70N",
    "top_lift_std": "15 kg/140N",
    "loop_std": "20 KG/200N",
    "toe_post_std": "EVA/Rubber: 150N, Others: 200N",
    "zipper_std": "25 kg/250N",
    "perment_set_std": "Max deformation ≤ 15%",
    
    # Rust test
    "rust_test_full": "RUST TEST",
    
    # Flexing test
    "upper": "Upper",
    "shoe_flex": "Shoe Flex",
    "foxing": "Foxing",
    "upper_std": "250,000 cycles",
    "shoe_flex_std": "100,000 cycles",
    "foxing_std": "≥ 2.0 N/mm",
    
    # Abrasion test
    "top_lift_abrasion": "Top Lift",
    "outsole_abrasion": "Outsole Abrasion",
    "outsole_abrasion_std": "Rubber & PU: 300mm³, TPR: 350mm³, EVA: 700mm³, PVC: 250mm³",
    
    # Resistance test
    "outsole_resistance": "Outsole",
    "heel_fatigue": "Heel Fatigue",
    "heel_fatigue_std": "20,000 cycles, Top lift area ≤ 1cm²",
    
    # Hardness test
    "eva_hardness": "EVA",
    "outsole_hardness": "Outsole Hardness",
    
    # Conclusion
    "pass_label": "PASS",
    "fail_label": "FAIL",
    "accept_label": "ACCEPT",
    
    # Signatures
    "verified_by": "Verified by:",
    "testing_person": "Testing Person:",
    "signature": "Signature",
    
    # Version
    "version": "Version 2024.09"
}

# Fixed Chinese texts for PDF (no translation needed)
CHINESE_TEXTS = {
    "company": "GRAND STEP (H.K.) LTD",
    "title": "物理测试报告",
    "test_location": "测试地点:",
    "report_date": "报告日期:",
    
    # Section headers
    "basic_info": "1. 基本信息",
    "adhesive_test": "2. 粘合/拉力测试",
    "components_test": "3. 配件物理测试",
    "flexing_test": "4. 弯曲测试",
    "abrasion_test": "5. 耐磨测试",
    "resistance_test": "6. 阻力测试",
    "hardness_test": "7. 硬度测试",
    "conclusion": "8. 结论",
    "rust_test": "防锈测试",
    
    # Labels
    "report_no": "报告编号:",
    "date_no": "日期/编号:",
    "ci_no": "CI/订单号:",
    "order_qty": "订单数量:",
    "brand": "品牌:",
    "produced_qty": "生产数量:",
    "style_no": "款式号:",
    "factory_trader": "工厂/贸易商:",
    "sales": "销售:",
    
    # Standard note
    "standard_note": "注：此标准仅为 Grand Step 公司标准。如有冲突，应遵循客户或第三方实验室标准",
    
    # Test headers
    "flat_shoe": "平底鞋",
    "high_heel": "高跟鞋",
    "sole_wedge": "鞋底/楔形",
    "toe": "鞋头",
    "forepart": "前掌",
    "waist": "腰窝",
    "heel": "后跟",
    "heel_height": "后跟高度",
    "cm_5_8": "5厘米-8厘米",
    "above_8cm": "8厘米以上",
    
    # Table headers
    "item": "项目",
    "standard": "标准",
    "result": "结果",
    "comments": "备注",
    "remark": "备注",
    
    # Components
    "buckle": "鞋扣",
    "strap": "饰带",
    "eyelet": "眼扣",
    "studs": "饰钉",
    "diamond_bow": "钻石/蝴蝶结",
    "top_lift": "天皮",
    "loop": "穿扣",
    "toe_post": "趾柱附件",
    "zipper": "拉链头",
    "perment_set": "400N永久变形测试",
    
    # Component standards
    "buckle_std": "20 kg/200N",
    "strap_std": "20 kg/200N",
    "eyelet_std": "20 kg/200N",
    "studs_std": "20 kg/200N",
    "diamond_std": "7KG/70N",
    "top_lift_std": "15 kg/140N",
    "loop_std": "20 KG/200N",
    "toe_post_std": "EVA/橡胶: 150N, 其他: 200N",
    "zipper_std": "25 kg/250N",
    "perment_set_std": "最大变形 ≤ 15%",
    
    # Rust test
    "rust_test_full": "防锈测试",
    
    # Flexing test
    "upper": "鞋面",
    "shoe_flex": "鞋弯曲",
    "foxing": "围条",
    "upper_std": "250,000次循环",
    "shoe_flex_std": "100,000次循环",
    "foxing_std": "≥ 2.0 N/mm",
    
    # Abrasion test
    "top_lift_abrasion": "天皮",
    "outsole_abrasion": "外底耐磨",
    "outsole_abrasion_std": "橡胶 & PU: 300mm³, TPR: 350mm³, EVA: 700mm³, PVC: 250mm³",
    
    # Resistance test
    "outsole_resistance": "外底",
    "heel_fatigue": "后跟疲劳",
    "heel_fatigue_std": "20,000次循环，天皮区域≤1cm²",
    
    # Hardness test
    "eva_hardness": "EVA",
    "outsole_hardness": "外底硬度",
    
    # Conclusion
    "pass_label": "通过",
    "fail_label": "不通过",
    "accept_label": "接受",
    
    # Signatures
    "verified_by": "审核人:",
    "testing_person": "测试人员:",
    "signature": "签名",
    
    # Version
    "version": "版本 2024.09"
}

def get_pdf_text(key, pdf_lang):
    """Get text for PDF based on language (English or Chinese)"""
    if pdf_lang == "en":
        return ENGLISH_TEXTS.get(key, key)
    else:
        return CHINESE_TEXTS.get(key, key)

def get_location_display(selected_city, pdf_lang):
    """Get location display text based on language"""
    if pdf_lang == "en":
        # For English PDF, show only English city name
        return f"{selected_city}"
    else:
        # For Chinese PDF, show Chinese city name
        chinese_name = CHINESE_CITIES[selected_city]
        # Check if the Chinese name contains Chinese characters
        if any('\u4e00' <= char <= '\u9fff' for char in chinese_name):
            return f"{selected_city} ({chinese_name})"
        else:
            return f"{selected_city}"

# Helper function to get translated text for UI with caching
def get_text(key, fallback=None):
    """Get translated text based on current UI language"""
    lang = st.session_state.ui_language
    
    # Base English texts for UI
    texts = {
        "title": "Physical Test Report",
        "basic_info": "Basic Information",
        "adhesive_test": "Adhesive/Pull Test",
        "components_test": "Components Physical Test",
        "flexing_test": "Flexing Test",
        "abrasion_test": "Abrasion Test",
        "resistance_test": "Resistance Test",
        "hardness_test": "Hardness Test",
        "conclusion": "Conclusion",
        "signatures": "Signatures & Verification",
        "generate_pdf": "Generate PDF Report",
        "download_pdf": "Download PDF Report",
        "report_no": "Report No.",
        "ci_no": "CI / Order No.",
        "order_qty": "Order Quantity",
        "produced_qty": "Produced Quantity",
        "factory": "Factory/Trader",
        "brand": "Brand/Trademark",
        "style": "Style No.",
        "sales": "Sales",
        "test_standard": "Test Standard",
        "test_result": "Test Result",
        "comments": "Comments",
        "footer_text": "Physical Test Report System",
        "generate_success": "PDF Generated Successfully!",
        "fill_required": "Please fill in at least CI No. and Style No.!",
        "creating_pdf": "Creating your professional PDF report...",
        "pdf_details": "PDF Details",
        "report_language": "Report Language",
        "generated": "Generated",
        "location": "Location",
        "error_generating": "Error generating PDF",
        "select_location": "Select Location",
        "user_interface_language": "User Interface Language",
        "pdf_report_language": "PDF Report Language",
        "test_location": "Test Location",
        "local_time": "Local Time",
        "quick_guide": "Quick Guide",
        "powered_by": "Powered by Streamlit",
        "copyright": "© 2025 - Physical Test Report Platform",
        "upload_photo": "Upload Shoe Photo",
        "standard_note": "Note: This is Grand Step Company Standard only. Any priority should follow Customer or 3rd Lab Standard",
        "flat_shoe": "Flat Shoe",
        "high_heel": "High Heel",
        "toe": "Toe",
        "forepart": "Forepart",
        "waist": "Waist",
        "heel": "Heel",
        "standard_value": "Standard",
        "remark": "Remark",
        "item": "Item",
        "pass_fail_accept": "Pass/Fail/Accept",
        "rust_test": "Rust Test",
        "outsole": "Outsole",
        "shoe_flex": "Shoe Flex",
        "upper": "Upper",
        "foxing": "Foxing",
        "top_lift": "Top Lift",
        "outsole_abrasion": "Outsole Abrasion",
        "heel_fatigue": "Heel Fatigue",
        "eva": "EVA",
        "outsole_hardness": "Outsole Hardness",
        "verified_by": "Verified by",
        "testing_person": "Testing Person",
        "version": "Version",
        "pass": "PASS",
        "fail": "FAIL",
        "accept": "ACCEPT"
    }
    
    text = texts.get(key, fallback or key)
    
    # Translate if needed for UI only (not for PDF)
    if lang == "zh" and openai_client and key not in ["pass", "fail", "accept"]:
        try:
            # Check cache
            cache_key = f"ui_{text}_{lang}"
            if cache_key in st.session_state.translations_cache:
                return st.session_state.translations_cache[cache_key]
            
            # Don't translate numbers or alphanumeric codes
            if text.strip().replace('.', '').replace(',', '').replace('-', '').isdigit():
                st.session_state.translations_cache[cache_key] = text
                return text
            
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Translate the following text to Chinese. Only return the translation, no explanations. Preserve any numbers, dates, and special formatting."},
                    {"role": "user", "content": text}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            translated_text = response.choices[0].message.content.strip()
            st.session_state.translations_cache[cache_key] = translated_text
            return translated_text
        except Exception as e:
            return text
    return text

def get_test_result_display(result):
    """Get styled test result display"""
    if result == "Pass":
        return '<span class="test-pass">Pass</span>'
    elif result == "Fail":
        return '<span class="test-fail">Fail</span>'
    else:
        return '<span class="test-accept">Accept</span>'

# Enhanced PDF Generation with Headers and Footers
class PDFWithHeaderFooter(SimpleDocTemplate):
    def __init__(self, *args, **kwargs):
        self.pdf_language = kwargs.pop('pdf_language', 'en')
        self.selected_city = kwargs.pop('selected_city', '')
        self.chinese_city = kwargs.pop('chinese_city', '')
        self.chinese_font = kwargs.pop('chinese_font', 'Helvetica')
        super().__init__(*args, **kwargs)
        
    def afterFlowable(self, flowable):
        """Add header and footer"""
        if isinstance(flowable, PageBreak):
            return
            
        # Add header on all pages except first
        if self.page > 1:
            self.canv.saveState()
            self.canv.setFillColor(colors.HexColor('#10b981'))
            self.canv.rect(0, self.pagesize[1] - 0.6*inch, self.pagesize[0], 0.6*inch, fill=1, stroke=0)
            
            font_size = 12
            if self.pdf_language == "zh":
                self.canv.setFont(self.chinese_font, font_size)
            else:
                self.canv.setFont('Helvetica-Bold', font_size)
                
            self.canv.setFillColor(colors.white)
            header_title = "GRAND STEP PHYSICAL TEST REPORT"
            self.canv.drawCentredString(
                self.pagesize[0]/2.0, 
                self.pagesize[1] - 0.4*inch, 
                header_title
            )
            self.canv.restoreState()
            
        # Footer on all pages
        self.canv.saveState()
        
        self.canv.setFillColor(colors.HexColor('#f8f9fa'))
        self.canv.rect(0, 0, self.pagesize[0], 0.7*inch, fill=1, stroke=0)
        
        self.canv.setStrokeColor(colors.HexColor('#10b981'))
        self.canv.setLineWidth(1)
        self.canv.line(0, 0.7*inch, self.pagesize[0], 0.7*inch)
        
        font_size = 8
        if self.pdf_language == "zh":
            self.canv.setFont(self.chinese_font, font_size)
        else:
            self.canv.setFont('Helvetica', font_size)
            
        self.canv.setFillColor(colors.HexColor('#666666'))
        
        china_tz = pytz.timezone('Asia/Shanghai')
        current_time = datetime.now(china_tz)
        
        # Get location display based on language
        location_display = get_location_display(self.selected_city, self.pdf_language)
        if self.pdf_language == "zh":
            location_info = f"{get_pdf_text('test_location', 'zh')} {location_display}"
        else:
            location_info = f"{get_pdf_text('test_location', 'en')} {location_display}"
        
        self.canv.drawString(0.5*inch, 0.25*inch, location_info)
        
        timestamp = f"{get_pdf_text('report_date', self.pdf_language).replace(':', '')} {current_time.strftime('%Y-%m-%d %H:%M:%S')}"
        self.canv.drawCentredString(self.pagesize[0]/2.0, 0.25*inch, timestamp)
        
        page_num = f"Page {self.page}"
        self.canv.drawRightString(self.pagesize[0] - 0.5*inch, 0.25*inch, page_num)
        
        self.canv.restoreState()

def truncate_text(text, max_length=50):
    """Truncate text if too long for PDF cells"""
    if not text:
        return ""
    if len(str(text)) > max_length:
        return str(text)[:max_length-3] + "..."
    return str(text)

def generate_pdf():
    """Generate PDF report"""
    buffer = io.BytesIO()
    
    # Get location info
    selected_city = st.session_state.selected_city
    chinese_city = CHINESE_CITIES[selected_city]
    pdf_lang = st.session_state.pdf_language
    
    # Register Chinese font if needed
    chinese_font = 'Helvetica'
    
    if pdf_lang == "zh":
        try:
            # Try to register Chinese fonts
            try:
                pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
                chinese_font = 'STSong-Light'
            except Exception as e1:
                try:
                    pdfmetrics.registerFont(TTFont('SimSun', 'simsun.ttc'))
                    chinese_font = 'SimSun'
                except Exception as e2:
                    try:
                        pdfmetrics.registerFont(TTFont('YaHei', 'msyh.ttc'))
                        chinese_font = 'YaHei'
                    except Exception as e3:
                        chinese_font = 'Helvetica'
        except Exception as e:
            chinese_font = 'Helvetica'
    
    # Create PDF with proper margins
    doc = PDFWithHeaderFooter(
        buffer, 
        pagesize=A4,
        topMargin=0.8*inch,
        bottomMargin=0.8*inch,
        leftMargin=0.5*inch,
        rightMargin=0.5*inch,
        pdf_language=pdf_lang,
        selected_city=selected_city,
        chinese_city=chinese_city,
        chinese_font=chinese_font
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Create styles
    title_font = 'Helvetica-Bold' if pdf_lang != "zh" else chinese_font
    normal_font = 'Helvetica' if pdf_lang != "zh" else chinese_font
    bold_font = 'Helvetica-Bold' if pdf_lang != "zh" else chinese_font
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#10b981'),
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName=bold_font,
        underlineWidth=1,
        underlineColor=colors.HexColor('#059669'),
        underlineOffset=-3
    )
    
    company_style = ParagraphStyle(
        'CompanyStyle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#333333'),
        spaceAfter=5,
        alignment=TA_CENTER,
        fontName=bold_font
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#059669'),
        alignment=TA_CENTER,
        spaceAfter=20,
        fontName=bold_font
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.white,
        spaceAfter=8,
        spaceBefore=12,
        fontName=bold_font,
        borderPadding=6,
        borderColor=colors.HexColor('#10b981'),
        borderWidth=1,
        borderRadius=4,
        backColor=colors.HexColor('#10b981'),
        alignment=TA_LEFT
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubheading',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=6,
        fontName=bold_font,
        alignment=TA_LEFT
    )
    
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        fontName=normal_font
    )
    
    bold_style = ParagraphStyle(
        'BoldStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        fontName=bold_font,
        textColor=colors.HexColor('#2c3e50')
    )
    
    small_style = ParagraphStyle(
        'SmallStyle',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        fontName=normal_font
    )
    
    # Helper function to create paragraphs with proper font and text wrapping
    def create_paragraph(text, bold=False, style=None, small=False):
        if style is None:
            if small:
                style = small_style
            else:
                style = bold_style if bold else normal_style
        
        # Truncate long text to prevent overflow
        clean_text = truncate_text(text)
        
        # Ensure proper font is used based on language
        if pdf_lang == "zh" and chinese_font != 'Helvetica':
            style = ParagraphStyle(
                f"CustomStyle_{bold}_{small}",
                parent=style,
                fontName=chinese_font if not bold else chinese_font,
                wordWrap='LTR'
            )
        
        return Paragraph(str(clean_text), style)
    
    # Get values from session state
    report_no = truncate_text(st.session_state.get('report_no', ''), 15)
    ci_no = truncate_text(st.session_state.get('ci_no', ''), 15)
    order_qty = truncate_text(st.session_state.get('order_qty', ''), 10)
    style_no = truncate_text(st.session_state.get('style_no', ''), 15)
    brand = truncate_text(st.session_state.get('brand', ''), 15)
    produced_qty = truncate_text(st.session_state.get('produced_qty', ''), 10)
    factory = truncate_text(st.session_state.get('factory', ''), 20)
    sales = truncate_text(st.session_state.get('sales', ''), 15)
    test_date = st.session_state.get('test_date', datetime.now())
    
    # Company Header
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(get_pdf_text("company", pdf_lang), company_style))
    
    # Title
    elements.append(Paragraph(get_pdf_text("title", pdf_lang), title_style))
    
    # Location and date
    china_tz = pytz.timezone('Asia/Shanghai')
    current_time = datetime.now(china_tz)
    
    # Get location display based on language
    location_display = get_location_display(selected_city, pdf_lang)
    location_text = f"{get_pdf_text('test_location', pdf_lang)} {location_display}"
    date_text = f"{get_pdf_text('report_date', pdf_lang)} {current_time.strftime('%Y-%m-%d')}"
    
    elements.append(Paragraph(location_text, subtitle_style))
    elements.append(Paragraph(date_text, subtitle_style))
    
    elements.append(Paragraph("<hr width='80%' color='#10b981'/>", normal_style))
    elements.append(Spacer(1, 15))
    
    # 1. Basic Information Table
    elements.append(Paragraph(get_pdf_text("basic_info", pdf_lang), heading_style))
    elements.append(Spacer(1, 5))
    
    basic_data = [
        [
            create_paragraph(get_pdf_text("report_no", pdf_lang), bold=True), 
            create_paragraph(report_no), 
            create_paragraph(get_pdf_text("date_no", pdf_lang), bold=True), 
            create_paragraph(test_date.strftime('%Y-%m-%d') if hasattr(test_date, 'strftime') else str(test_date))
        ],
        [
            create_paragraph(get_pdf_text("ci_no", pdf_lang), bold=True), 
            create_paragraph(ci_no), 
            create_paragraph(get_pdf_text("order_qty", pdf_lang), bold=True), 
            create_paragraph(str(order_qty))
        ],
        [
            create_paragraph(get_pdf_text("brand", pdf_lang), bold=True), 
            create_paragraph(brand), 
            create_paragraph(get_pdf_text("produced_qty", pdf_lang), bold=True), 
            create_paragraph(str(produced_qty))
        ],
        [
            create_paragraph(get_pdf_text("style_no", pdf_lang), bold=True), 
            create_paragraph(style_no), 
            create_paragraph(get_pdf_text("factory_trader", pdf_lang), bold=True), 
            create_paragraph(factory)
        ],
        [
            create_paragraph(get_pdf_text("sales", pdf_lang), bold=True), 
            create_paragraph(sales), 
            create_paragraph("", bold=True), 
            create_paragraph("")
        ]
    ]
    
    basic_table = Table(basic_data, colWidths=[1.5*inch, 2.0*inch, 1.5*inch, 2.0*inch])
    basic_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0fdf4')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#f0fdf4')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), bold_font),
        ('FONTNAME', (2, 0), (2, -1), bold_font),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d4d4d4')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
    ]))
    elements.append(basic_table)
    elements.append(Spacer(1, 15))
    
    # Standard note
    elements.append(Paragraph(get_pdf_text("standard_note", pdf_lang), small_style))
    elements.append(Spacer(1, 10))
    
    # 2. Adhesive/Pull Test
    elements.append(PageBreak())
    
    elements.append(Paragraph(get_pdf_text("adhesive_test", pdf_lang), heading_style))
    elements.append(Spacer(1, 5))
    
    # Get adhesive test values
    flat_shoe_toe_result = truncate_text(st.session_state.get('flat_shoe_toe_result', ''), 8)
    flat_shoe_forepart_result = truncate_text(st.session_state.get('flat_shoe_forepart_result', ''), 8)
    flat_shoe_waist_result = truncate_text(st.session_state.get('flat_shoe_waist_result', ''), 8)
    flat_shoe_heel_result = truncate_text(st.session_state.get('flat_shoe_heel_result', ''), 8)
    
    adhesive_data = [
        [
            create_paragraph(get_pdf_text("flat_shoe", pdf_lang), bold=True, small=True),
            create_paragraph(get_pdf_text("standard", pdf_lang), bold=True, small=True),
            create_paragraph(get_pdf_text("result", pdf_lang), bold=True, small=True),
            create_paragraph(get_pdf_text("high_heel", pdf_lang), bold=True, small=True),
            create_paragraph(get_pdf_text("sole_wedge", pdf_lang), bold=True, small=True),
            create_paragraph(get_pdf_text("standard", pdf_lang), bold=True, small=True),
            create_paragraph(get_pdf_text("remark", pdf_lang), bold=True, small=True)
        ],
        [
            create_paragraph(get_pdf_text("toe", pdf_lang), small=True),
            create_paragraph("12 kg / 3N", small=True),
            create_paragraph(flat_shoe_toe_result, small=True),
            create_paragraph(get_pdf_text("toe", pdf_lang), small=True),
            create_paragraph("", small=True),
            create_paragraph("12 kg / 3N", small=True),
            create_paragraph("", small=True)
        ],
        [
            create_paragraph(get_pdf_text("forepart", pdf_lang), small=True),
            create_paragraph("12 kg / 3N", small=True),
            create_paragraph(flat_shoe_forepart_result, small=True),
            create_paragraph(get_pdf_text("forepart", pdf_lang), small=True),
            create_paragraph("", small=True),
            create_paragraph("12 kg / 3N", small=True),
            create_paragraph("", small=True)
        ],
        [
            create_paragraph(get_pdf_text("waist", pdf_lang), small=True),
            create_paragraph("12 kg / 3N", small=True),
            create_paragraph(flat_shoe_waist_result, small=True),
            create_paragraph(get_pdf_text("waist", pdf_lang), small=True),
            create_paragraph("", small=True),
            create_paragraph("12 kg / 3N", small=True),
            create_paragraph("", small=True)
        ],
        [
            create_paragraph(get_pdf_text("heel", pdf_lang), small=True),
            create_paragraph("", small=True),
            create_paragraph(flat_shoe_heel_result, small=True),
            create_paragraph(get_pdf_text("heel", pdf_lang), small=True),
            create_paragraph("60 kg/500N / 80 kg/800N", small=True),
            create_paragraph(f"{get_pdf_text('heel_height', pdf_lang)} {get_pdf_text('cm_5_8', pdf_lang)} / {get_pdf_text('above_8cm', pdf_lang)}", small=True),
            create_paragraph("", small=True)
        ]
    ]
    
    adhesive_table = Table(adhesive_data, colWidths=[0.8*inch, 1.0*inch, 0.7*inch, 0.8*inch, 1.3*inch, 1.3*inch, 1.0*inch])
    adhesive_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
        ('BACKGROUND', (3, 0), (-1, 0), colors.HexColor('#059669')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), bold_font),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
    ]))
    elements.append(adhesive_table)
    elements.append(Spacer(1, 15))
    
    # 3. Components Physical Test
    elements.append(Paragraph(get_pdf_text("components_test", pdf_lang), heading_style))
    elements.append(Spacer(1, 5))
    
    # Get components test values
    components_data = [
        [
            create_paragraph(get_pdf_text("item", pdf_lang), bold=True, small=True),
            create_paragraph(get_pdf_text("standard", pdf_lang), bold=True, small=True),
            create_paragraph(get_pdf_text("result", pdf_lang), bold=True, small=True),
            create_paragraph(get_pdf_text("comments", pdf_lang), bold=True, small=True),
            create_paragraph(get_pdf_text("item", pdf_lang), bold=True, small=True),
            create_paragraph(get_pdf_text("standard", pdf_lang), bold=True, small=True),
            create_paragraph(get_pdf_text("result", pdf_lang), bold=True, small=True),
            create_paragraph(get_pdf_text("comments", pdf_lang), bold=True, small=True)
        ]
    ]
    
    # Add component test rows using fixed texts
    components_list = [
        (get_pdf_text("buckle", pdf_lang), get_pdf_text("buckle_std", pdf_lang), 
         truncate_text(st.session_state.get('buckle_result', ''), 8), 
         truncate_text(st.session_state.get('buckle_comments', ''), 12),
         get_pdf_text("top_lift", pdf_lang), get_pdf_text("top_lift_std", pdf_lang), 
         truncate_text(st.session_state.get('top_lift_result', ''), 8), 
         truncate_text(st.session_state.get('top_lift_comments', ''), 12)),
        
        (get_pdf_text("strap", pdf_lang), get_pdf_text("strap_std", pdf_lang), 
         truncate_text(st.session_state.get('strap_result', ''), 8), 
         truncate_text(st.session_state.get('strap_comments', ''), 12),
         get_pdf_text("loop", pdf_lang), get_pdf_text("loop_std", pdf_lang), 
         truncate_text(st.session_state.get('loop_result', ''), 8), 
         truncate_text(st.session_state.get('loop_comments', ''), 12)),
        
        (get_pdf_text("eyelet", pdf_lang), get_pdf_text("eyelet_std", pdf_lang), 
         truncate_text(st.session_state.get('eyelet_result', ''), 8), 
         truncate_text(st.session_state.get('eyelet_comments', ''), 12),
         get_pdf_text("toe_post", pdf_lang), get_pdf_text("toe_post_std", pdf_lang), 
         truncate_text(st.session_state.get('toe_post_result', ''), 8), 
         truncate_text(st.session_state.get('toe_post_comments', ''), 12)),
        
        (get_pdf_text("studs", pdf_lang), get_pdf_text("studs_std", pdf_lang), 
         truncate_text(st.session_state.get('studs_result', ''), 8), 
         truncate_text(st.session_state.get('studs_comments', ''), 12),
         get_pdf_text("zipper", pdf_lang), get_pdf_text("zipper_std", pdf_lang), 
         truncate_text(st.session_state.get('zipper_result', ''), 8), 
         truncate_text(st.session_state.get('zipper_comments', ''), 12)),
        
        (get_pdf_text("diamond_bow", pdf_lang), get_pdf_text("diamond_std", pdf_lang), 
         truncate_text(st.session_state.get('diamond_result', ''), 8), 
         truncate_text(st.session_state.get('diamond_comments', ''), 12),
         get_pdf_text("perment_set", pdf_lang), get_pdf_text("perment_set_std", pdf_lang), 
         truncate_text(st.session_state.get('perment_set_result', ''), 8), 
         truncate_text(st.session_state.get('perment_set_comments', ''), 12))
    ]
    
    for comp1, std1, res1, com1, comp2, std2, res2, com2 in components_list:
        components_data.append([
            create_paragraph(comp1, small=True),
            create_paragraph(std1, small=True),
            create_paragraph(res1, small=True),
            create_paragraph(com1, small=True),
            create_paragraph(comp2, small=True),
            create_paragraph(std2, small=True),
            create_paragraph(res2, small=True),
            create_paragraph(com2, small=True)
        ])
    
    components_table = Table(components_data, colWidths=[0.8*inch, 0.9*inch, 0.6*inch, 0.9*inch, 0.8*inch, 0.9*inch, 0.6*inch, 0.9*inch])
    components_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), bold_font),
        ('FONTSIZE', (0, 0), (-1, -1), 6.5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
    ]))
    elements.append(components_table)
    
    # Rust Test
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(get_pdf_text("rust_test_full", pdf_lang), subheading_style))
    
    rust_data = [
        [
            create_paragraph(get_pdf_text("buckle", pdf_lang)),
            create_paragraph(truncate_text(st.session_state.get('rust_buckle_result', ''), 10)),
            create_paragraph(get_pdf_text("eyelet", pdf_lang)),
            create_paragraph(truncate_text(st.session_state.get('rust_eyelet_result', ''), 10))
        ],
        [
            create_paragraph(get_pdf_text("strap", pdf_lang)),
            create_paragraph(truncate_text(st.session_state.get('rust_strap_result', ''), 10)),
            create_paragraph(get_pdf_text("studs", pdf_lang)),
            create_paragraph(truncate_text(st.session_state.get('rust_studs_result', ''), 10))
        ]
    ]
    
    rust_table = Table(rust_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    rust_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
    ]))
    elements.append(rust_table)
    
    elements.append(PageBreak())
    
    # 4. Flexing Test
    elements.append(Paragraph(get_pdf_text("flexing_test", pdf_lang), heading_style))
    elements.append(Spacer(1, 5))
    
    # Get flexing test values
    flexing_data = [
        [
            create_paragraph(get_pdf_text("item", pdf_lang), bold=True),
            create_paragraph(get_pdf_text("standard", pdf_lang), bold=True),
            create_paragraph(get_pdf_text("result", pdf_lang), bold=True),
            create_paragraph(get_pdf_text("comments", pdf_lang), bold=True)
        ],
        [
            create_paragraph(get_pdf_text("upper", pdf_lang)),
            create_paragraph(get_pdf_text("upper_std", pdf_lang)),
            create_paragraph(truncate_text(st.session_state.get('upper_flex_result', ''), 10)),
            create_paragraph(truncate_text(st.session_state.get('upper_flex_comments', ''), 30))
        ],
        [
            create_paragraph(get_pdf_text("shoe_flex", pdf_lang)),
            create_paragraph(get_pdf_text("shoe_flex_std", pdf_lang)),
            create_paragraph(truncate_text(st.session_state.get('shoe_flex_result', ''), 10)),
            create_paragraph(truncate_text(st.session_state.get('shoe_flex_comments', ''), 30))
        ],
        [
            create_paragraph(get_pdf_text("foxing", pdf_lang)),
            create_paragraph(get_pdf_text("foxing_std", pdf_lang)),
            create_paragraph(truncate_text(st.session_state.get('foxing_result', ''), 10)),
            create_paragraph(truncate_text(st.session_state.get('foxing_comments', ''), 30))
        ]
    ]
    
    flexing_table = Table(flexing_data, colWidths=[1.8*inch, 2.0*inch, 1.2*inch, 2.2*inch])
    flexing_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), bold_font),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
    ]))
    elements.append(flexing_table)
    
    # 5. Abrasion Test
    elements.append(Spacer(1, 15))
    elements.append(Paragraph(get_pdf_text("abrasion_test", pdf_lang), heading_style))
    elements.append(Spacer(1, 5))
    
    abrasion_data = [
        [
            create_paragraph(get_pdf_text("item", pdf_lang), bold=True),
            create_paragraph(get_pdf_text("standard", pdf_lang), bold=True),
            create_paragraph(get_pdf_text("result", pdf_lang), bold=True),
            create_paragraph(get_pdf_text("comments", pdf_lang), bold=True)
        ],
        [
            create_paragraph(get_pdf_text("top_lift_abrasion", pdf_lang)),
            create_paragraph(""),
            create_paragraph(truncate_text(st.session_state.get('top_lift_abrasion_result', ''), 10)),
            create_paragraph(truncate_text(st.session_state.get('top_lift_abrasion_comments', ''), 30))
        ],
        [
            create_paragraph(get_pdf_text("outsole_abrasion", pdf_lang)),
            create_paragraph(get_pdf_text("outsole_abrasion_std", pdf_lang), small=True),
            create_paragraph(truncate_text(st.session_state.get('outsole_abrasion_result', ''), 10)),
            create_paragraph(truncate_text(st.session_state.get('outsole_abrasion_comments', ''), 30))
        ]
    ]
    
    abrasion_table = Table(abrasion_data, colWidths=[1.8*inch, 3.0*inch, 1.2*inch, 2.2*inch])
    abrasion_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), bold_font),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
    ]))
    elements.append(abrasion_table)
    
    # 6. Resistance Test
    elements.append(Spacer(1, 15))
    elements.append(Paragraph(get_pdf_text("resistance_test", pdf_lang), heading_style))
    elements.append(Spacer(1, 5))
    
    resistance_data = [
        [
            create_paragraph(get_pdf_text("item", pdf_lang), bold=True),
            create_paragraph(get_pdf_text("standard", pdf_lang), bold=True),
            create_paragraph(get_pdf_text("result", pdf_lang), bold=True),
            create_paragraph(get_pdf_text("comments", pdf_lang), bold=True)
        ],
        [
            create_paragraph(get_pdf_text("outsole_resistance", pdf_lang)),
            create_paragraph(""),
            create_paragraph(truncate_text(st.session_state.get('outsole_resistance_result', ''), 10)),
            create_paragraph(truncate_text(st.session_state.get('outsole_resistance_comments', ''), 30))
        ],
        [
            create_paragraph(get_pdf_text("heel_fatigue", pdf_lang)),
            create_paragraph(get_pdf_text("heel_fatigue_std", pdf_lang), small=True),
            create_paragraph(truncate_text(st.session_state.get('heel_fatigue_result', ''), 10)),
            create_paragraph(truncate_text(st.session_state.get('heel_fatigue_comments', ''), 30))
        ]
    ]
    
    resistance_table = Table(resistance_data, colWidths=[1.8*inch, 3.0*inch, 1.2*inch, 2.2*inch])
    resistance_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), bold_font),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
    ]))
    elements.append(resistance_table)
    
    # 7. Hardness Test
    elements.append(Spacer(1, 15))
    elements.append(Paragraph(get_pdf_text("hardness_test", pdf_lang), heading_style))
    elements.append(Spacer(1, 5))
    
    hardness_data = [
        [
            create_paragraph(get_pdf_text("item", pdf_lang), bold=True),
            create_paragraph(get_pdf_text("standard", pdf_lang), bold=True),
            create_paragraph(get_pdf_text("result", pdf_lang), bold=True),
            create_paragraph(get_pdf_text("comments", pdf_lang), bold=True)
        ],
        [
            create_paragraph(get_pdf_text("eva_hardness", pdf_lang)),
            create_paragraph(""),
            create_paragraph(truncate_text(st.session_state.get('eva_hardness_result', ''), 10)),
            create_paragraph(truncate_text(st.session_state.get('eva_hardness_comments', ''), 30))
        ],
        [
            create_paragraph(get_pdf_text("outsole_hardness", pdf_lang)),
            create_paragraph(""),
            create_paragraph(truncate_text(st.session_state.get('outsole_hardness_result', ''), 10)),
            create_paragraph(truncate_text(st.session_state.get('outsole_hardness_comments', ''), 30))
        ]
    ]
    
    hardness_table = Table(hardness_data, colWidths=[1.8*inch, 3.0*inch, 1.2*inch, 2.2*inch])
    hardness_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), bold_font),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
    ]))
    elements.append(hardness_table)
    
    # 8. Conclusion - FIXED TO FIT WITHIN PAGE
    elements.append(Spacer(1, 15))  # Reduced spacing
    elements.append(Paragraph(get_pdf_text("conclusion", pdf_lang), heading_style))
    elements.append(Spacer(1, 5))
    
    # Get conclusion values
    pass_result = truncate_text(st.session_state.get('pass_result', ''), 35)  # Reduced from 50
    fail_result = truncate_text(st.session_state.get('fail_result', ''), 35)  # Reduced from 50
    accept_result = truncate_text(st.session_state.get('accept_result', ''), 35)  # Reduced from 50
    
    conclusion_data = [
        [
            create_paragraph(get_pdf_text("pass_label", pdf_lang), bold=True),
            create_paragraph(pass_result, small=True),  # Use small font
            create_paragraph(get_pdf_text("fail_label", pdf_lang), bold=True),
            create_paragraph(fail_result, small=True),  # Use small font
            create_paragraph(get_pdf_text("accept_label", pdf_lang), bold=True),
            create_paragraph(accept_result, small=True)  # Use small font
        ]
    ]
    
    # Adjusted column widths to fit within page
    conclusion_table = Table(conclusion_data, colWidths=[0.8*inch, 1.6*inch, 0.8*inch, 1.6*inch, 0.8*inch, 1.6*inch])
    conclusion_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (0, -1), bold_font),
        ('FONTNAME', (2, 0), (2, -1), bold_font),
        ('FONTNAME', (4, 0), (4, -1), bold_font),
        ('FONTSIZE', (0, 0), (-1, -1), 8),  # Reduced font size
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white])
    ]))
    elements.append(conclusion_table)
    
    # Signatures - Moved to new page if needed
    elements.append(Spacer(1, 10))
    
    # Get signature values
    verified_by = truncate_text(st.session_state.get('verified_by', ''), 20)
    testing_person = truncate_text(st.session_state.get('testing_person', ''), 20)
    
    signature_data = [
        [
            create_paragraph(get_pdf_text("verified_by", pdf_lang), bold=True),
            create_paragraph(verified_by),
            create_paragraph(""),
            create_paragraph(get_pdf_text("testing_person", pdf_lang), bold=True),
            create_paragraph(testing_person)
        ],
        [
            create_paragraph(""),
            create_paragraph("_________________________"),
            create_paragraph(""),
            create_paragraph(""),
            create_paragraph("_________________________")
        ],
        [
            create_paragraph(""),
            create_paragraph(get_pdf_text("signature", pdf_lang)),
            create_paragraph(""),
            create_paragraph(""),
            create_paragraph(get_pdf_text("signature", pdf_lang))
        ]
    ]
    
    signature_table = Table(signature_data, colWidths=[1.2*inch, 2.3*inch, 0.5*inch, 1.2*inch, 2.3*inch])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), bold_font),
        ('FONTNAME', (3, 0), (3, -1), bold_font),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(signature_table)
    
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(get_pdf_text("version", pdf_lang), normal_style))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

# Sidebar with enhanced filters
with st.sidebar:
    st.markdown(f'### {ICONS["settings"]} Settings & Filters')
    
    # Language filters with icons
    st.markdown(f'#### {ICONS["language"]} Language Settings')
    ui_language = st.selectbox(
        "User Interface Language",
        ["English", "Mandarin"],
        index=0 if st.session_state.ui_language == "en" else 1,
        key="ui_lang_select"
    )
    st.session_state.ui_language = "en" if ui_language == "English" else "zh"
    
    pdf_language = st.selectbox(
        "PDF Report Language",
        ["English", "Mandarin"],
        index=0 if st.session_state.pdf_language == "en" else 1,
        key="pdf_lang_select"
    )
    st.session_state.pdf_language = "en" if pdf_language == "English" else "zh"
    
    # Location filter with enhanced UI
    st.markdown(f'#### {ICONS["location"]} Location Settings')
    selected_city = st.selectbox(
        "Select Test Location",
        list(CHINESE_CITIES.keys()),
        index=list(CHINESE_CITIES.keys()).index(st.session_state.selected_city) 
        if st.session_state.selected_city in CHINESE_CITIES else 0,
        key="city_select"
    )
    st.session_state.selected_city = selected_city
    
    # Display selected location in a badge
    st.markdown(f"""
    <div class="location-badge">
        {ICONS["location"]} {selected_city} ({CHINESE_CITIES[selected_city]})
    </div>
    """, unsafe_allow_html=True)
    
    # Timezone information
    st.markdown(f'#### {ICONS["time"]} Timezone Info')
    china_tz = pytz.timezone('Asia/Shanghai')
    current_time = datetime.now(china_tz)
    st.metric(
        "Local Time", 
        current_time.strftime('%H:%M:%S'),
        current_time.strftime('%Y-%m-%d')
    )
    
    # Translation status
    if openai_client:
        st.success(f"{ICONS['success']} Translation API: Active")
    else:
        st.warning(f"{ICONS['warning']} Translation API: Not Configured")
    
    st.markdown("---")
    
    # Test Standards Info
    st.markdown(f'#### {ICONS["standard"]} Test Standards')
    st.info(f"""
    {ICONS["info"]} **Important Note:**
    This is Grand Step Company Standard only.
    Any priority should follow Customer or 3rd Lab Standard
    """)
    
    st.markdown("---")
    st.markdown(f'### {ICONS["info"]} Instructions')
    st.info(f"""
    {ICONS["info"]} **Quick Guide:**
    1. {ICONS["basic_info"]} Fill basic information
    2. {ICONS["test"]} Complete all test sections
    3. {ICONS["language"]} Select preferred languages
    4. {ICONS["location"]} Choose test location
    5. {ICONS["generate"]} Generate PDF report
    """)

# Title with enhanced styling
st.markdown(f"""
<div class="main-header">
    <span class="test-icon">🧪</span> Physical Test Report
</div>
""", unsafe_allow_html=True)

# Create tabs for better organization
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    f"{ICONS['basic_info']} Basic Info",
    f"{ICONS['adhesive_test']} Adhesive",
    f"{ICONS['components_test']} Components",
    f"{ICONS['flexing_test']} Flexing",
    f"{ICONS['abrasion_test']} Abrasion",
    f"{ICONS['resistance_test']} Resistance",
    f"{ICONS['hardness_test']} Hardness",
    f"{ICONS['conclusion']} Conclusion"
])

with tab1:
    # Basic Information Section
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["basic_info"]}</span>
        {get_text("basic_info")}
    </div>
    """, unsafe_allow_html=True)
    
    # Main basic info in columns
    col1, col2 = st.columns(2)
    
    with col1:
        report_no = st.text_input(
            f"{ICONS['po']} {get_text('report_no')}", 
            placeholder="PTR-2024-001",
            key="report_no"
        )
        
        ci_no = st.text_input(
            f"{ICONS['po']} {get_text('ci_no')}", 
            placeholder="CI-2024-001",
            key="ci_no"
        )
        
        style_no = st.text_input(
            f"{ICONS['style']} {get_text('style')}", 
            placeholder="XYZ-2024",
            key="style_no"
        )
        
        factory = st.text_input(
            f"{ICONS['factory']} {get_text('factory')}", 
            placeholder="ABC Manufacturing Co., Ltd.",
            key="factory"
        )
    
    with col2:
        test_date = st.date_input(
            f"{ICONS['time']} Test Date", 
            datetime.now(),
            key="test_date"
        )
        
        order_qty = st.number_input(
            f"{ICONS['description']} {get_text('order_qty')}", 
            min_value=0,
            value=1000,
            key="order_qty"
        )
        
        brand = st.text_input(
            f"{ICONS['brand']} {get_text('brand')}", 
            placeholder="Brand Name",
            key="brand"
        )
        
        produced_qty = st.number_input(
            f"{ICONS['description']} {get_text('produced_qty')}", 
            min_value=0,
            value=1000,
            key="produced_qty"
        )
        
        sales = st.text_input(
            f"{ICONS['sales']} {get_text('sales')}", 
            placeholder="Sales Representative",
            key="sales"
        )
    
    # Standard note
    st.info(f"""
    {ICONS['warning']} **{get_text('standard_note')}**
    """)

with tab2:
    # Adhesive/Pull Test Section
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["adhesive_test"]}</span>
        {get_text("adhesive_test")}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"### {ICONS['pull_test']} Flat Shoe Tests")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"**{get_text('toe')}**")
        flat_shoe_toe_result = st.selectbox(
            "Toe Result",
            ["Pass", "Fail", "Accept"],
            key="flat_shoe_toe_result",
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown(f"**{get_text('forepart')}**")
        flat_shoe_forepart_result = st.selectbox(
            "Forepart Result",
            ["Pass", "Fail", "Accept"],
            key="flat_shoe_forepart_result",
            label_visibility="collapsed"
        )
    
    with col3:
        st.markdown(f"**{get_text('waist')}**")
        flat_shoe_waist_result = st.selectbox(
            "Waist Result",
            ["Pass", "Fail", "Accept"],
            key="flat_shoe_waist_result",
            label_visibility="collapsed"
        )
    
    st.markdown(f"**{get_text('heel')}**")
    flat_shoe_heel_result = st.selectbox(
        "Heel Result",
        ["Pass", "Fail", "Accept"],
        key="flat_shoe_heel_result",
        label_visibility="collapsed"
    )
    
    st.markdown(f"### {ICONS['pull_test']} High Heel Tests")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"**{get_text('toe')}**")
        high_heel_toe_result = st.selectbox(
            "High Heel Toe Result",
            ["Pass", "Fail", "Accept"],
            key="high_heel_toe_result",
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown(f"**{get_text('forepart')}**")
        high_heel_forepart_result = st.selectbox(
            "High Heel Forepart Result",
            ["Pass", "Fail", "Accept"],
            key="high_heel_forepart_result",
            label_visibility="collapsed"
        )
    
    with col3:
        st.markdown(f"**{get_text('waist')}**")
        high_heel_waist_result = st.selectbox(
            "High Heel Waist Result",
            ["Pass", "Fail", "Accept"],
            key="high_heel_waist_result",
            label_visibility="collapsed"
        )
    
    st.markdown(f"**{get_text('heel')}**")
    high_heel_heel_result = st.selectbox(
        "High Heel Heel Result",
        ["Pass", "Fail", "Accept"],
        key="high_heel_heel_result",
        label_visibility="collapsed"
    )

with tab3:
    # Components Physical Test Section
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["components_test"]}</span>
        {get_text("components_test")}
    </div>
    """, unsafe_allow_html=True)
    
    # Components Test Grid
    st.markdown("#### Component Tests - Left Side")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        buckle_result = st.selectbox("Buckle", ["Pass", "Fail", "Accept"], key="buckle_result")
        strap_result = st.selectbox("Strap", ["Pass", "Fail", "Accept"], key="strap_result")
        eyelet_result = st.selectbox("Eyelet", ["Pass", "Fail", "Accept"], key="eyelet_result")
        studs_result = st.selectbox("Studs", ["Pass", "Fail", "Accept"], key="studs_result")
        diamond_result = st.selectbox("Diamond/Bow", ["Pass", "Fail", "Accept"], key="diamond_result")
    
    with col2:
        buckle_comments = st.text_input("Buckle Comments", key="buckle_comments", placeholder="Comments...")
        strap_comments = st.text_input("Strap Comments", key="strap_comments", placeholder="Comments...")
        eyelet_comments = st.text_input("Eyelet Comments", key="eyelet_comments", placeholder="Comments...")
        studs_comments = st.text_input("Studs Comments", key="studs_comments", placeholder="Comments...")
        diamond_comments = st.text_input("Diamond Comments", key="diamond_comments", placeholder="Comments...")
    
    st.markdown("#### Component Tests - Right Side")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        top_lift_result = st.selectbox("Top Lift", ["Pass", "Fail", "Accept"], key="top_lift_result")
        loop_result = st.selectbox("Loop", ["Pass", "Fail", "Accept"], key="loop_result")
        toe_post_result = st.selectbox("Toe Post", ["Pass", "Fail", "Accept"], key="toe_post_result")
        zipper_result = st.selectbox("Zipper", ["Pass", "Fail", "Accept"], key="zipper_result")
        perment_set_result = st.selectbox("Perment Set", ["Pass", "Fail", "Accept"], key="perment_set_result")
    
    with col2:
        top_lift_comments = st.text_input("Top Lift Comments", key="top_lift_comments", placeholder="Comments...")
        loop_comments = st.text_input("Loop Comments", key="loop_comments", placeholder="Comments...")
        toe_post_comments = st.text_input("Toe Post Comments", key="toe_post_comments", placeholder="Comments...")
        zipper_comments = st.text_input("Zipper Comments", key="zipper_comments", placeholder="Comments...")
        perment_set_comments = st.text_input("Perment Set Comments", key="perment_set_comments", placeholder="Comments...")
    
    # Rust Test
    st.markdown(f"### {ICONS['rust_test']} {get_text('rust_test')}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        rust_buckle_result = st.selectbox("Rust Buckle", ["Pass", "Fail"], key="rust_buckle_result")
        rust_strap_result = st.selectbox("Rust Strap", ["Pass", "Fail"], key="rust_strap_result")
    
    with col2:
        rust_eyelet_result = st.selectbox("Rust Eyelet", ["Pass", "Fail"], key="rust_eyelet_result")
        rust_studs_result = st.selectbox("Rust Studs", ["Pass", "Fail"], key="rust_studs_result")

with tab4:
    # Flexing Test Section
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["flexing_test"]}</span>
        {get_text("flexing_test")}
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"**{get_text('upper')}**")
        upper_flex_result = st.selectbox(
            "Upper Flex Result",
            ["Pass", "Fail", "Accept"],
            key="upper_flex_result",
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown(f"**{get_text('shoe_flex')}**")
        shoe_flex_result = st.selectbox(
            "Shoe Flex Result",
            ["Pass", "Fail", "Accept"],
            key="shoe_flex_result",
            label_visibility="collapsed"
        )
    
    with col3:
        st.markdown(f"**{get_text('foxing')}**")
        foxing_result = st.selectbox(
            "Foxing Result",
            ["Pass", "Fail", "Accept"],
            key="foxing_result",
            label_visibility="collapsed"
        )
    
    # Comments
    col1, col2, col3 = st.columns(3)
    
    with col1:
        upper_flex_comments = st.text_input(
            "Upper Flex Comments",
            key="upper_flex_comments",
            placeholder="Comments..."
        )
    
    with col2:
        shoe_flex_comments = st.text_input(
            "Shoe Flex Comments",
            key="shoe_flex_comments",
            placeholder="Comments..."
        )
    
    with col3:
        foxing_comments = st.text_input(
            "Foxing Comments",
            key="foxing_comments",
            placeholder="Comments..."
        )

with tab5:
    # Abrasion Test Section
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["abrasion_test"]}</span>
        {get_text("abrasion_test")}
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**{get_text('top_lift')}**")
        top_lift_abrasion_result = st.selectbox(
            "Top Lift Abrasion Result",
            ["Pass", "Fail", "Accept"],
            key="top_lift_abrasion_result",
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown(f"**{get_text('outsole_abrasion')}**")
        outsole_abrasion_result = st.selectbox(
            "Outsole Abrasion Result",
            ["Pass", "Fail", "Accept"],
            key="outsole_abrasion_result",
            label_visibility="collapsed"
        )
    
    # Comments
    col1, col2 = st.columns(2)
    
    with col1:
        top_lift_abrasion_comments = st.text_input(
            "Top Lift Abrasion Comments",
            key="top_lift_abrasion_comments",
            placeholder="Comments..."
        )
    
    with col2:
        outsole_abrasion_comments = st.text_input(
            "Outsole Abrasion Comments",
            key="outsole_abrasion_comments",
            placeholder="Comments..."
        )

with tab6:
    # Resistance Test Section
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["resistance_test"]}</span>
        {get_text("resistance_test")}
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**{get_text('outsole')}**")
        outsole_resistance_result = st.selectbox(
            "Outsole Resistance Result",
            ["Pass", "Fail", "Accept"],
            key="outsole_resistance_result",
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown(f"**{get_text('heel_fatigue')}**")
        heel_fatigue_result = st.selectbox(
            "Heel Fatigue Result",
            ["Pass", "Fail", "Accept"],
            key="heel_fatigue_result",
            label_visibility="collapsed"
        )
    
    # Comments
    col1, col2 = st.columns(2)
    
    with col1:
        outsole_resistance_comments = st.text_input(
            "Outsole Resistance Comments",
            key="outsole_resistance_comments",
            placeholder="Comments..."
        )
    
    with col2:
        heel_fatigue_comments = st.text_input(
            "Heel Fatigue Comments",
            key="heel_fatigue_comments",
            placeholder="Comments..."
        )

with tab7:
    # Hardness Test Section
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["hardness_test"]}</span>
        {get_text("hardness_test")}
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**{get_text('eva')}**")
        eva_hardness_result = st.selectbox(
            "EVA Hardness Result",
            ["Pass", "Fail", "Accept"],
            key="eva_hardness_result",
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown(f"**{get_text('outsole_hardness')}**")
        outsole_hardness_result = st.selectbox(
            "Outsole Hardness Result",
            ["Pass", "Fail", "Accept"],
            key="outsole_hardness_result",
            label_visibility="collapsed"
        )
    
    # Comments
    col1, col2 = st.columns(2)
    
    with col1:
        eva_hardness_comments = st.text_input(
            "EVA Hardness Comments",
            key="eva_hardness_comments",
            placeholder="Comments..."
        )
    
    with col2:
        outsole_hardness_comments = st.text_input(
            "Outsole Hardness Comments",
            key="outsole_hardness_comments",
            placeholder="Comments..."
        )

with tab8:
    # Conclusion and Signatures
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["conclusion"]}</span>
        {get_text("conclusion")}
    </div>
    """, unsafe_allow_html=True)
    
    # Overall Conclusion
    st.markdown("### Overall Test Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"**{get_text('pass')}**")
        pass_result = st.text_area(
            "Pass Results",
            placeholder="List items that passed...",
            height=100,
            key="pass_result"
        )
    
    with col2:
        st.markdown(f"**{get_text('fail')}**")
        fail_result = st.text_area(
            "Fail Results",
            placeholder="List items that failed...",
            height=100,
            key="fail_result"
        )
    
    with col3:
        st.markdown(f"**{get_text('accept')}**")
        accept_result = st.text_area(
            "Accept Results",
            placeholder="List items accepted with conditions...",
            height=100,
            key="accept_result"
        )
    
    # Signatures
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["signatures"]}</span>
        {get_text("signatures")}
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        verified_by = st.text_input(
            f"{ICONS['qc']} {get_text('verified_by')}", 
            placeholder="Quality Manager Name",
            key="verified_by"
        )
    
    with col2:
        testing_person = st.text_input(
            f"{ICONS['test']} {get_text('testing_person')}", 
            placeholder="Tester Name",
            key="testing_person"
        )

# Generate PDF Button
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button(f"{ICONS['generate']} {get_text('generate_pdf')}", use_container_width=True):
        if not st.session_state.get('ci_no') or not st.session_state.get('style_no'):
            st.error(f"{ICONS['error']} {get_text('fill_required')}")
        else:
            with st.spinner(f"{ICONS['time']} {get_text('creating_pdf')}"):
                try:
                    pdf_buffer = generate_pdf()
                    st.success(f"{ICONS['success']} {get_text('generate_success')}")
                    
                    # Display PDF preview info
                    with st.expander(f"{ICONS['info']} {get_text('pdf_details')}"):
                        col_info1, col_info2 = st.columns(2)
                        with col_info1:
                            st.metric(get_text("location"), f"{selected_city} ({CHINESE_CITIES[selected_city]})")
                            st.metric(get_text("report_language"), "Mandarin" if st.session_state.pdf_language == "zh" else "English")
                        with col_info2:
                            china_tz = pytz.timezone('Asia/Shanghai')
                            current_time = datetime.now(china_tz)
                            st.metric(get_text("generated"), current_time.strftime('%H:%M:%S'))
                    
                    # Download button
                    filename = f"Physical_Test_Report_{st.session_state.get('ci_no', '')}_{selected_city}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    st.download_button(
                        label=f"{ICONS['download']} {get_text('download_pdf')}",
                        data=pdf_buffer,
                        file_name=filename,
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                except Exception as e:
                    st.error(f"{ICONS['error']} {get_text('error_generating')}: {str(e)}")

# Footer
st.markdown("---")
st.markdown(f"""
<div class="footer">
    <p style='font-size: 1.2rem; font-weight: 600; color: #10b981; margin-bottom: 0.5rem;'>
        {ICONS['title']} {get_text('footer_text')}
    </p>
    <p style='font-size: 0.9rem; color: #666666;'>
        {ICONS['location']} {get_text('location')}: {selected_city} ({CHINESE_CITIES[selected_city]}) | 
        {ICONS['language']} {get_text('report_language')}: {'Mandarin' if st.session_state.pdf_language == 'zh' else 'English'}
    </p>
    <p style='font-size: 0.8rem; color: #999999; margin-top: 1rem;'>
        {get_text('powered_by')} | {get_text('copyright')}
    </p>
</div>
""", unsafe_allow_html=True)

# Create .env file instructions in sidebar
with st.sidebar:
    with st.expander(f"{ICONS['info']} API Setup"):
        st.code("""
# Create .env file in your project folder
OPENAI_API_KEY=your-api-key-here
""")
        st.info("Restart the app after adding your API key to enable translations.")
