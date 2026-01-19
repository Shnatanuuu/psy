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
    "Shanghai": "上海",
    "Beijing": "北京",
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

# Translation function using GPT-4o mini
def translate_text(text, target_language="zh"):
    """Translate text using GPT-4o mini with caching"""
    if not text or not text.strip():
        return text
    
    # Check cache first
    cache_key = f"{text}_{target_language}"
    if cache_key in st.session_state.translations_cache:
        return st.session_state.translations_cache[cache_key]
    
    # Don't translate numbers or alphanumeric codes
    if text.strip().replace('.', '').replace(',', '').replace('-', '').isdigit():
        st.session_state.translations_cache[cache_key] = text
        return text
    
    if not openai_client:
        st.session_state.translations_cache[cache_key] = text
        return text
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are a professional translator. Translate the following text to {target_language}. Only return the translation, no explanations. Preserve any numbers, dates, and special formatting."},
                {"role": "user", "content": text}
            ],
            temperature=0.1,
            max_tokens=500
        )
        
        translated_text = response.choices[0].message.content.strip()
        st.session_state.translations_cache[cache_key] = translated_text
        return translated_text
    except Exception as e:
        st.warning(f"Translation failed: {str(e)}. Using original text.")
        st.session_state.translations_cache[cache_key] = text
        return text

# Helper function to get translated text with caching
def get_text(key, fallback=None):
    """Get translated text based on current UI language"""
    lang = st.session_state.ui_language
    
    # Base English texts
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
        "version": "Version"
    }
    
    text = texts.get(key, fallback or key)
    
    # Translate if needed
    if lang == "zh" and openai_client:
        return translate_text(text, "zh")
    return text

def translate_pdf_content(text, pdf_lang):
    """Translate text for PDF based on selected language"""
    if pdf_lang == "en" or not openai_client:
        return text
    return translate_text(text, "zh")

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
        self.header_text = kwargs.pop('header_text', '')
        self.location = kwargs.pop('location', '')
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
        
        if self.pdf_language == "zh" and self.chinese_city:
            location_info = f"测试地点: {self.selected_city} ({self.chinese_city})"
        else:
            location_info = f"Test Location: {self.selected_city}"
        
        self.canv.drawString(0.5*inch, 0.25*inch, location_info)
        
        timestamp = f"Generated: {current_time.strftime('%Y-%m-%d %H:%M:%S')}"
        self.canv.drawCentredString(self.pagesize[0]/2.0, 0.25*inch, timestamp)
        
        page_num = f"Page {self.page}"
        self.canv.drawRightString(self.pagesize[0] - 0.5*inch, 0.25*inch, page_num)
        
        self.canv.restoreState()

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
    
    # Create PDF
    doc = PDFWithHeaderFooter(
        buffer, 
        pagesize=A4,
        topMargin=0.8*inch,
        bottomMargin=0.8*inch,
        header_text="GRAND STEP PHYSICAL TEST REPORT",
        location=f"{selected_city}",
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
    
    # Helper function
    def create_paragraph(text, style=normal_style, bold=False):
        if bold:
            font_name = bold_font
        else:
            font_name = normal_font
        
        custom_style = ParagraphStyle(
            f"CustomStyle_{bold}",
            parent=style,
            fontName=font_name
        )
        
        return Paragraph(text, custom_style)
    
    # Get values from session state
    report_no = st.session_state.get('report_no', '')
    ci_no = st.session_state.get('ci_no', '')
    order_qty = st.session_state.get('order_qty', '')
    style_no = st.session_state.get('style_no', '')
    brand = st.session_state.get('brand', '')
    produced_qty = st.session_state.get('produced_qty', '')
    factory = st.session_state.get('factory', '')
    sales = st.session_state.get('sales', '')
    test_date = st.session_state.get('test_date', datetime.now())
    
    # Company Header
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("GRAND STEP (H.K.) LTD", company_style))
    
    # Title
    report_title = translate_pdf_content("PHYSICAL TEST REPORT", pdf_lang)
    elements.append(Paragraph(report_title, title_style))
    
    # Location and date
    china_tz = pytz.timezone('Asia/Shanghai')
    current_time = datetime.now(china_tz)
    
    if pdf_lang == "zh":
        location_text = translate_pdf_content(f"测试地点: {selected_city} ({chinese_city})", pdf_lang)
    else:
        location_text = f"Test Location: {selected_city}"
    
    date_text = translate_pdf_content(f"Report Date: {current_time.strftime('%Y-%m-%d')}", pdf_lang)
    
    elements.append(Paragraph(location_text, subtitle_style))
    elements.append(Paragraph(date_text, subtitle_style))
    
    elements.append(Paragraph("<hr width='80%' color='#10b981'/>", normal_style))
    elements.append(Spacer(1, 15))
    
    # 1. Basic Information Table
    basic_title = translate_pdf_content("1. BASIC INFORMATION", pdf_lang)
    elements.append(Paragraph(basic_title, heading_style))
    elements.append(Spacer(1, 5))
    
    basic_data = [
        [
            create_paragraph(translate_pdf_content("Report No.:", pdf_lang), bold=True), 
            create_paragraph(report_no), 
            create_paragraph(translate_pdf_content("Date/No.", pdf_lang), bold=True), 
            create_paragraph(test_date.strftime('%Y-%m-%d') if hasattr(test_date, 'strftime') else str(test_date))
        ],
        [
            create_paragraph(translate_pdf_content("CI / Order No.:", pdf_lang), bold=True), 
            create_paragraph(ci_no), 
            create_paragraph(translate_pdf_content("Order QTY:", pdf_lang), bold=True), 
            create_paragraph(str(order_qty))
        ],
        [
            create_paragraph(translate_pdf_content("Brand:", pdf_lang), bold=True), 
            create_paragraph(brand), 
            create_paragraph(translate_pdf_content("Produced QTY:", pdf_lang), bold=True), 
            create_paragraph(str(produced_qty))
        ],
        [
            create_paragraph(translate_pdf_content("Style No.:", pdf_lang), bold=True), 
            create_paragraph(style_no), 
            create_paragraph(translate_pdf_content("Factory/Trader:", pdf_lang), bold=True), 
            create_paragraph(factory)
        ],
        [
            create_paragraph(translate_pdf_content("Sales:", pdf_lang), bold=True), 
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
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'LEFT'),
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
    standard_note = translate_pdf_content(
        "Note: This is Grand Step Company Standard only. Any priority should follow Customer or 3rd Lab Standard",
        pdf_lang
    )
    elements.append(Paragraph(standard_note, normal_style))
    elements.append(Spacer(1, 10))
    
    # 2. Adhesive/Pull Test
    elements.append(PageBreak())
    
    adhesive_title = translate_pdf_content("2. ADHESIVE/PULL TEST", pdf_lang)
    elements.append(Paragraph(adhesive_title, heading_style))
    elements.append(Spacer(1, 5))
    
    # Get adhesive test values
    flat_shoe_toe_result = st.session_state.get('flat_shoe_toe_result', '')
    flat_shoe_forepart_result = st.session_state.get('flat_shoe_forepart_result', '')
    flat_shoe_waist_result = st.session_state.get('flat_shoe_waist_result', '')
    flat_shoe_heel_result = st.session_state.get('flat_shoe_heel_result', '')
    
    high_heel_toe_result = st.session_state.get('high_heel_toe_result', '')
    high_heel_forepart_result = st.session_state.get('high_heel_forepart_result', '')
    high_heel_waist_result = st.session_state.get('high_heel_waist_result', '')
    high_heel_heel_result = st.session_state.get('high_heel_heel_result', '')
    
    adhesive_data = [
        [
            create_paragraph(translate_pdf_content("Flat Shoe", pdf_lang), bold=True),
            create_paragraph(translate_pdf_content("Standard", pdf_lang), bold=True),
            create_paragraph(translate_pdf_content("Result", pdf_lang), bold=True),
            create_paragraph(translate_pdf_content("High Heel", pdf_lang), bold=True),
            create_paragraph(translate_pdf_content("Sole/Wedge", pdf_lang), bold=True),
            create_paragraph(translate_pdf_content("Standard", pdf_lang), bold=True),
            create_paragraph(translate_pdf_content("Remark", pdf_lang), bold=True)
        ],
        [
            create_paragraph(translate_pdf_content("Toe", pdf_lang)),
            create_paragraph("12 kg / 3N"),
            create_paragraph(flat_shoe_toe_result),
            create_paragraph(translate_pdf_content("Toe", pdf_lang)),
            create_paragraph(""),
            create_paragraph("12 kg / 3N"),
            create_paragraph("")
        ],
        [
            create_paragraph(translate_pdf_content("Forepart", pdf_lang)),
            create_paragraph("12 kg / 3N"),
            create_paragraph(flat_shoe_forepart_result),
            create_paragraph(translate_pdf_content("Forepart", pdf_lang)),
            create_paragraph(""),
            create_paragraph("12 kg / 3N"),
            create_paragraph("")
        ],
        [
            create_paragraph(translate_pdf_content("Waist", pdf_lang)),
            create_paragraph("12 kg / 3N"),
            create_paragraph(flat_shoe_waist_result),
            create_paragraph(translate_pdf_content("Waist", pdf_lang)),
            create_paragraph(""),
            create_paragraph("12 kg / 3N"),
            create_paragraph("")
        ],
        [
            create_paragraph(translate_pdf_content("Heel", pdf_lang)),
            create_paragraph(""),
            create_paragraph(flat_shoe_heel_result),
            create_paragraph(translate_pdf_content("Heel", pdf_lang)),
            create_paragraph("60 kg/500N / 80 kg/800N"),
            create_paragraph("Heel Height 5CM-8CM / Above 8CM"),
            create_paragraph("")
        ]
    ]
    
    adhesive_table = Table(adhesive_data, colWidths=[0.9*inch, 1.2*inch, 0.9*inch, 0.9*inch, 1.5*inch, 1.5*inch, 1.1*inch])
    adhesive_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
        ('BACKGROUND', (3, 0), (-1, 0), colors.HexColor('#059669')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), bold_font),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
    ]))
    elements.append(adhesive_table)
    elements.append(Spacer(1, 15))
    
    # 3. Components Physical Test
    components_title = translate_pdf_content("3. COMPONENTS PHYSICAL TEST", pdf_lang)
    elements.append(Paragraph(components_title, heading_style))
    elements.append(Spacer(1, 5))
    
    # Get components test values
    components_data = [
        [
            create_paragraph(translate_pdf_content("Item", pdf_lang), bold=True),
            create_paragraph(translate_pdf_content("Standard", pdf_lang), bold=True),
            create_paragraph(translate_pdf_content("Result", pdf_lang), bold=True),
            create_paragraph(translate_pdf_content("Comments", pdf_lang), bold=True),
            create_paragraph(translate_pdf_content("Item", pdf_lang), bold=True),
            create_paragraph(translate_pdf_content("Standard", pdf_lang), bold=True),
            create_paragraph(translate_pdf_content("Result", pdf_lang), bold=True),
            create_paragraph(translate_pdf_content("Comments", pdf_lang), bold=True)
        ]
    ]
    
    # Add component test rows
    components_list = [
        ("Buckle 鞋扣", "20 kg/200N", st.session_state.get('buckle_result', ''), st.session_state.get('buckle_comments', ''),
         "Top lift天皮", "15 kg/140N", st.session_state.get('top_lift_result', ''), st.session_state.get('top_lift_comments', '')),
        ("Strap 饰带", "20 kg/200N", st.session_state.get('strap_result', ''), st.session_state.get('strap_comments', ''),
         "Loop 穿扣", "20 KG/200N", st.session_state.get('loop_result', ''), st.session_state.get('loop_comments', '')),
        ("Eyelet 眼扣", "20 kg/200N", st.session_state.get('eyelet_result', ''), st.session_state.get('eyelet_comments', ''),
         "Toe Post Attachment", "EVA/Rubber: 150N, Others: 200N", st.session_state.get('toe_post_result', ''), st.session_state.get('toe_post_comments', '')),
        ("Studs 饰钉", "20 kg/200N", st.session_state.get('studs_result', ''), st.session_state.get('studs_comments', ''),
         "Zipper拉链头", "25 kg/250N", st.session_state.get('zipper_result', ''), st.session_state.get('zipper_comments', '')),
        ("Diamond/Bow", "7KG/70N", st.session_state.get('diamond_result', ''), st.session_state.get('diamond_comments', ''),
         "Perment set at 400N", "Max deformation ≤ 15%", st.session_state.get('perment_set_result', ''), st.session_state.get('perment_set_comments', ''))
    ]
    
    for comp1, std1, res1, com1, comp2, std2, res2, com2 in components_list:
        components_data.append([
            create_paragraph(translate_pdf_content(comp1, pdf_lang)),
            create_paragraph(std1),
            create_paragraph(res1),
            create_paragraph(com1),
            create_paragraph(translate_pdf_content(comp2, pdf_lang)),
            create_paragraph(std2),
            create_paragraph(res2),
            create_paragraph(com2)
        ])
    
    components_table = Table(components_data, colWidths=[1.0*inch, 1.0*inch, 0.8*inch, 1.0*inch, 1.0*inch, 1.0*inch, 0.8*inch, 1.0*inch])
    components_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), bold_font),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
    ]))
    elements.append(components_table)
    
    # Rust Test
    elements.append(Spacer(1, 10))
    rust_title = translate_pdf_content("RUST TEST", pdf_lang)
    elements.append(Paragraph(rust_title, subheading_style))
    
    rust_data = [
        [
            create_paragraph(translate_pdf_content("Buckle", pdf_lang)),
            create_paragraph(st.session_state.get('rust_buckle_result', '')),
            create_paragraph(translate_pdf_content("Eyelet", pdf_lang)),
            create_paragraph(st.session_state.get('rust_eyelet_result', ''))
        ],
        [
            create_paragraph(translate_pdf_content("Strap", pdf_lang)),
            create_paragraph(st.session_state.get('rust_strap_result', '')),
            create_paragraph(translate_pdf_content("Studs", pdf_lang)),
            create_paragraph(st.session_state.get('rust_studs_result', ''))
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
    flexing_title = translate_pdf_content("4. FLEXING TEST", pdf_lang)
    elements.append(Paragraph(flexing_title, heading_style))
    elements.append(Spacer(1, 5))
    
    # Get flexing test values
    flexing_data = [
        [
            create_paragraph(translate_pdf_content("Item", pdf_lang), bold=True),
            create_paragraph(translate_pdf_content("Standard", pdf_lang), bold=True),
            create_paragraph(translate_pdf_content("Result", pdf_lang), bold=True),
            create_paragraph(translate_pdf_content("Comments", pdf_lang), bold=True)
        ],
        [
            create_paragraph(translate_pdf_content("Upper", pdf_lang)),
            create_paragraph("250,000 cycles"),
            create_paragraph(st.session_state.get('upper_flex_result', '')),
            create_paragraph(st.session_state.get('upper_flex_comments', ''))
        ],
        [
            create_paragraph(translate_pdf_content("Shoe Flex", pdf_lang)),
            create_paragraph("100,000 cycles"),
            create_paragraph(st.session_state.get('shoe_flex_result', '')),
            create_paragraph(st.session_state.get('shoe_flex_comments', ''))
        ],
        [
            create_paragraph(translate_pdf_content("Foxing", pdf_lang)),
            create_paragraph("≥ 2.0 N/mm"),
            create_paragraph(st.session_state.get('foxing_result', '')),
            create_paragraph(st.session_state.get('foxing_comments', ''))
        ]
    ]
    
    flexing_table = Table(flexing_data, colWidths=[2.0*inch, 2.0*inch, 1.5*inch, 2.5*inch])
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
    abrasion_title = translate_pdf_content("5. ABRASION TEST", pdf_lang)
    elements.append(Paragraph(abrasion_title, heading_style))
    elements.append(Spacer(1, 5))
    
    abrasion_data = [
        [
            create_paragraph(translate_pdf_content("Item", pdf_lang), bold=True),
            create_paragraph(translate_pdf_content("Standard", pdf_lang), bold=True),
            create_paragraph(translate_pdf_content("Result", pdf_lang), bold=True),
            create_paragraph(translate_pdf_content("Comments", pdf_lang), bold=True)
        ],
        [
            create_paragraph(translate_pdf_content("Top Lift", pdf_lang)),
            create_paragraph(""),
            create_paragraph(st.session_state.get('top_lift_abrasion_result', '')),
            create_paragraph(st.session_state.get('top_lift_abrasion_comments', ''))
        ],
        [
            create_paragraph(translate_pdf_content("Outsole Abrasion", pdf_lang)),
            create_paragraph("Rubber & PU: 300mm³, TPR: 350mm³, EVA: 700mm³, PVC: 250mm³"),
            create_paragraph(st.session_state.get('outsole_abrasion_result', '')),
            create_paragraph(st.session_state.get('outsole_abrasion_comments', ''))
        ]
    ]
    
    abrasion_table = Table(abrasion_data, colWidths=[2.0*inch, 3.0*inch, 1.5*inch, 2.5*inch])
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
    resistance_title = translate_pdf_content("6. RESISTANCE TEST", pdf_lang)
    elements.append(Paragraph(resistance_title, heading_style))
    elements.append(Spacer(1, 5))
    
    resistance_data = [
        [
            create_paragraph(translate_pdf_content("Item", pdf_lang), bold=True),
            create_paragraph(translate_pdf_content("Standard", pdf_lang), bold=True),
            create_paragraph(translate_pdf_content("Result", pdf_lang), bold=True),
            create_paragraph(translate_pdf_content("Comments", pdf_lang), bold=True)
        ],
        [
            create_paragraph(translate_pdf_content("Outsole", pdf_lang)),
            create_paragraph(""),
            create_paragraph(st.session_state.get('outsole_resistance_result', '')),
            create_paragraph(st.session_state.get('outsole_resistance_comments', ''))
        ],
        [
            create_paragraph(translate_pdf_content("Heel Fatigue", pdf_lang)),
            create_paragraph("20,000 cycles, Top lift area ≤ 1cm²"),
            create_paragraph(st.session_state.get('heel_fatigue_result', '')),
            create_paragraph(st.session_state.get('heel_fatigue_comments', ''))
        ]
    ]
    
    resistance_table = Table(resistance_data, colWidths=[2.0*inch, 3.0*inch, 1.5*inch, 2.5*inch])
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
    hardness_title = translate_pdf_content("7. HARDNESS TEST", pdf_lang)
    elements.append(Paragraph(hardness_title, heading_style))
    elements.append(Spacer(1, 5))
    
    hardness_data = [
        [
            create_paragraph(translate_pdf_content("Item", pdf_lang), bold=True),
            create_paragraph(translate_pdf_content("Standard", pdf_lang), bold=True),
            create_paragraph(translate_pdf_content("Result", pdf_lang), bold=True),
            create_paragraph(translate_pdf_content("Comments", pdf_lang), bold=True)
        ],
        [
            create_paragraph(translate_pdf_content("EVA", pdf_lang)),
            create_paragraph(""),
            create_paragraph(st.session_state.get('eva_hardness_result', '')),
            create_paragraph(st.session_state.get('eva_hardness_comments', ''))
        ],
        [
            create_paragraph(translate_pdf_content("Outsole Hardness", pdf_lang)),
            create_paragraph(""),
            create_paragraph(st.session_state.get('outsole_hardness_result', '')),
            create_paragraph(st.session_state.get('outsole_hardness_comments', ''))
        ]
    ]
    
    hardness_table = Table(hardness_data, colWidths=[2.0*inch, 3.0*inch, 1.5*inch, 2.5*inch])
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
    
    # 8. Conclusion
    elements.append(Spacer(1, 20))
    conclusion_title = translate_pdf_content("8. CONCLUSION", pdf_lang)
    elements.append(Paragraph(conclusion_title, heading_style))
    elements.append(Spacer(1, 10))
    
    # Get conclusion values
    pass_result = st.session_state.get('pass_result', '')
    fail_result = st.session_state.get('fail_result', '')
    accept_result = st.session_state.get('accept_result', '')
    
    conclusion_data = [
        [
            create_paragraph(translate_pdf_content("PASS", pdf_lang), bold=True),
            create_paragraph(pass_result),
            create_paragraph(translate_pdf_content("FAIL", pdf_lang), bold=True),
            create_paragraph(fail_result),
            create_paragraph(translate_pdf_content("ACCEPT", pdf_lang), bold=True),
            create_paragraph(accept_result)
        ]
    ]
    
    conclusion_table = Table(conclusion_data, colWidths=[1.0*inch, 2.0*inch, 1.0*inch, 2.0*inch, 1.0*inch, 2.0*inch])
    conclusion_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (0, -1), bold_font),
        ('FONTNAME', (2, 0), (2, -1), bold_font),
        ('FONTNAME', (4, 0), (4, -1), bold_font),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(conclusion_table)
    
    # Signatures
    elements.append(Spacer(1, 20))
    
    # Get signature values
    verified_by = st.session_state.get('verified_by', '')
    testing_person = st.session_state.get('testing_person', '')
    
    signature_data = [
        [
            create_paragraph(translate_pdf_content("Verified by:", pdf_lang), bold=True),
            create_paragraph(verified_by),
            create_paragraph(""),
            create_paragraph(translate_pdf_content("Testing Person:", pdf_lang), bold=True),
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
            create_paragraph("Signature"),
            create_paragraph(""),
            create_paragraph(""),
            create_paragraph("Signature")
        ]
    ]
    
    signature_table = Table(signature_data, colWidths=[1.5*inch, 2.5*inch, 0.5*inch, 1.5*inch, 2.5*inch])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), bold_font),
        ('FONTNAME', (3, 0), (3, -1), bold_font),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(signature_table)
    
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("Version 2024.09", normal_style))
    
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
