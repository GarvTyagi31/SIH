import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_sih_presentation(output_path="SahakarConnect_SIH2026_Idea_Presentation.pptx"):
    prs = Presentation()
    # 16:9 Widescreen standard
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Official SIH & Theme Color Palette
    NAVY = RGBColor(15, 41, 66)        # #0F2942 - Deep Navy
    SAFFRON = RGBColor(217, 119, 6)    # #D97706 - Saffron / Amber
    GREEN = RGBColor(21, 128, 61)      # #15803D - India Green
    DARK_TEXT = RGBColor(30, 41, 59)   # #1E293B - Slate 800
    MUTED_TEXT = RGBColor(100, 116, 139) # #64748B - Slate 500
    LIGHT_BG = RGBColor(248, 250, 252) # #F8FAFC - Off White Card
    BORDER_COLOR = RGBColor(203, 213, 225) # Slate 300
    WHITE = RGBColor(255, 255, 255)
    ACCENT_BLUE = RGBColor(37, 99, 235)

    def add_header(slide, title_text, subtitle_text=None, slide_num=None):
        # Top Tricolor Accent Stripe
        stripe_w = prs.slide_width / 3
        # Saffron
        s_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), stripe_w, Inches(0.08))
        s_shape.fill.solid()
        s_shape.fill.fore_color.rgb = RGBColor(255, 153, 51)
        s_shape.line.fill.background()
        # White
        w_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, stripe_w, Inches(0), stripe_w, Inches(0.08))
        w_shape.fill.solid()
        w_shape.fill.fore_color.rgb = RGBColor(240, 240, 240)
        w_shape.line.fill.background()
        # Green
        g_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, stripe_w * 2, Inches(0), stripe_w, Inches(0.08))
        g_shape.fill.solid()
        g_shape.fill.fore_color.rgb = RGBColor(19, 136, 8)
        g_shape.line.fill.background()

        # Title Box
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(8.5), Inches(1.1))
        tf = title_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p = tf.paragraphs[0]
        p.text = title_text
        p.font.size = Pt(22)
        p.font.bold = True
        p.font.color.rgb = NAVY
        p.font.name = "Arial"

        if subtitle_text:
            p2 = tf.add_paragraph()
            p2.text = subtitle_text
            p2.font.size = Pt(12)
            p2.font.color.rgb = SAFFRON
            p2.font.bold = True
            p2.font.name = "Arial"

        # SIH Header Tag in Top Right
        sih_box = slide.shapes.add_textbox(Inches(9.2), Inches(0.35), Inches(3.4), Inches(0.9))
        stf = sih_box.text_frame
        stf.word_wrap = True
        stf.margin_right = 0
        sp = stf.paragraphs[0]
        sp.text = "SMART INDIA HACKATHON 2026"
        sp.font.size = Pt(11)
        sp.font.bold = True
        sp.font.color.rgb = NAVY
        sp.alignment = PP_ALIGN.RIGHT
        sp2 = stf.add_paragraph()
        sp2.text = "Idea Submission Template • Official Format"
        sp2.font.size = Pt(9)
        sp2.font.color.rgb = MUTED_TEXT
        sp2.alignment = PP_ALIGN.RIGHT

        # Bottom Footer
        footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.0), Inches(11.8), Inches(0.35))
        ftf = footer_box.text_frame
        ftf.word_wrap = True
        ftf.margin_left = ftf.margin_top = ftf.margin_right = ftf.margin_bottom = 0
        fp = ftf.paragraphs[0]
        fp.text = f"@SIH Idea submission - Template | Team ID: [Your Team ID] | Slide {slide_num if slide_num else ''}"
        fp.font.size = Pt(9)
        fp.font.color.rgb = MUTED_TEXT

    # =========================================================================
    # SLIDE 1: TITLE PAGE (Left blank for user as requested)
    # =========================================================================
    slide1 = prs.slides.add_slide(blank_layout)
    add_header(slide1, "SMART INDIA HACKATHON 2026", "Idea Submission • Title Slide", 1)

    card1 = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(11.73), Inches(5.2))
    card1.fill.solid()
    card1.fill.fore_color.rgb = WHITE
    card1.line.color.rgb = BORDER_COLOR
    card1.line.width = Pt(1.5)

    tb1 = slide1.shapes.add_textbox(Inches(1.2), Inches(1.8), Inches(11.0), Inches(4.5))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p = tf1.paragraphs[0]
    p.text = "TITLE PAGE"
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = NAVY

    fields = [
        ("Problem Statement ID –", "[ Enter Problem Statement ID here ]"),
        ("Problem Statement Title –", "[ Enter Problem Statement Title here ]"),
        ("Theme –", "[ Enter Theme here, e.g. Smart Automation / Cooperatives / Citizen Services ]"),
        ("PS Category –", "Software / Hardware"),
        ("Team ID –", "[ Enter Team ID registered on portal ]"),
        ("Team Name –", "[ Enter Team Name registered on portal ]"),
        ("Team Leader & Members –", "[ Enter Leader & Member details here ]"),
        ("Institute Name –", "[ Enter College / Institute Name here ]")
    ]

    for label, placeholder in fields:
        p = tf1.add_paragraph()
        p.text = f"{label} "
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = DARK_TEXT
        run = p.add_run()
        run.text = placeholder
        run.font.bold = False
        run.font.color.rgb = SAFFRON

    # =========================================================================
    # SLIDE 2: IDEA TITLE & PROPOSED SOLUTION
    # =========================================================================
    slide2 = prs.slides.add_slide(blank_layout)
    add_header(slide2, "IDEA TITLE: SahakarConnect", "Proposed Solution (Describe your Idea/Solution/Prototype)", 2)

    # 3 Cards Layout: Detailed Solution, Addressing the Problem, Innovation/Uniqueness
    col_w = Inches(3.75)
    col_gap = Inches(0.24)
    start_x = Inches(0.8)
    card_y = Inches(1.5)
    card_h = Inches(5.2)

    # Card 1: Detailed Solution
    c1 = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, start_x, card_y, col_w, card_h)
    c1.fill.solid()
    c1.fill.fore_color.rgb = WHITE
    c1.line.color.rgb = BORDER_COLOR
    tb = slide2.shapes.add_textbox(start_x + Inches(0.2), card_y + Inches(0.2), col_w - Inches(0.4), card_h - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "1. Proposed Solution & Architecture"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = NAVY

    points1 = [
        "Cooperative Gig Marketplace: Open-source digital platform connecting certified blue-collar artisans (Electricians, Plumbers, Carpenters, AC Technicians) with urban households.",
        "93/5/2 Fair Wage Model: 93% direct worker payout, 5% platform maintenance, and 2% allocated to a collective Worker Welfare & Insurance Fund.",
        "Dual Booking & SOS Dispatch: Supports instant on-demand dispatch (15–20 min SLA), scheduled slots (8 AM–8 PM), and 24x7 Emergency SOS response for household crises."
    ]
    for pt in points1:
        p = tf.add_paragraph()
        p.text = f"• {pt}"
        p.font.size = Pt(10.5)
        p.font.color.rgb = DARK_TEXT

    # Card 2: Addressing the Problem
    c2 = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, start_x + col_w + col_gap, card_y, col_w, card_h)
    c2.fill.solid()
    c2.fill.fore_color.rgb = WHITE
    c2.line.color.rgb = BORDER_COLOR
    tb = slide2.shapes.add_textbox(start_x + col_w + col_gap + Inches(0.2), card_y + Inches(0.2), col_w - Inches(0.4), card_h - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "2. How It Addresses the Problem"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = NAVY

    points2 = [
        "Eliminates 30-40% Commission Gouging: Replaces predatory corporate aggregators with a community-owned cooperative model that guarantees fair livelihood.",
        "Zero Surge Pricing for Citizens: Standardized, government-approved rates with transparent itemized invoicing.",
        "Institutional Social Safety Net: Bridges unorganized artisans with Pradhan Mantri Suraksha Bima Yojana (PMSBY) accidental cover and health relief.",
        "Formal Skill Accreditation: Integrates Skill India & ITI certification validation with official police verification."
    ]
    for pt in points2:
        p = tf.add_paragraph()
        p.text = f"• {pt}"
        p.font.size = Pt(10.5)
        p.font.color.rgb = DARK_TEXT

    # Card 3: Innovation & Uniqueness
    c3 = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, start_x + (col_w + col_gap)*2, card_y, col_w, card_h)
    c3.fill.solid()
    c3.fill.fore_color.rgb = WHITE
    c3.line.color.rgb = BORDER_COLOR
    tb = slide2.shapes.add_textbox(start_x + (col_w + col_gap)*2 + Inches(0.2), card_y + Inches(0.2), col_w - Inches(0.4), card_h - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "3. Innovation & Uniqueness"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = NAVY

    points3 = [
        "Democratic Cooperative Governance: Governed by artisan federation guilds under the UP Cooperative Societies Act.",
        "Verified Cryptographic Audit Trail: Mathematical chaining of payouts and welfare fees preventing unauthorized wage tampering.",
        "10+ State Regional Languages: Live dynamic UI across Hindi, Bhojpuri, Punjabi, Bengali, Gujarati, Marathi, Tamil, Telugu, Kannada, English.",
        "24x7 AI Sahayak Assistant: Multilingual voice/text conversational bot for instant citizen support."
    ]
    for pt in points3:
        p = tf.add_paragraph()
        p.text = f"• {pt}"
        p.font.size = Pt(10.5)
        p.font.color.rgb = DARK_TEXT

    # =========================================================================
    # SLIDE 3: TECHNICAL APPROACH
    # =========================================================================
    slide3 = prs.slides.add_slide(blank_layout)
    add_header(slide3, "TECHNICAL APPROACH", "Technologies Used & Implementation Methodology / Workflow", 3)

    # 2 Column Layout: Left Column Tech Stack (40%), Right Column Process Workflow (60%)
    left_w = Inches(5.0)
    right_w = Inches(6.5)

    # Left: Tech Stack
    c_left = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, start_x, card_y, left_w, card_h)
    c_left.fill.solid()
    c_left.fill.fore_color.rgb = WHITE
    c_left.line.color.rgb = BORDER_COLOR
    tb = slide3.shapes.add_textbox(start_x + Inches(0.2), card_y + Inches(0.2), left_w - Inches(0.4), card_h - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Core Technology Stack"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = NAVY

    techs = [
        ("Backend & APIs", "Python 3.11, FastAPI (Asynchronous Microservices), SQLAlchemy ORM"),
        ("Database & GIS", "PostgreSQL + PostGIS (SRID 4326 POINT geometry, ST_DWithin spatial indexing)"),
        ("AI & Predictive Models", "Polynomial trend estimators for 7-day demand forecasting & locality surge allocation"),
        ("Security & Wage Ledger", "PBKDF2-HMAC-SHA256 password hashing, chained wage settlement auditor"),
        ("Frontend & Mapping", "Tailwind CSS, Jinja2, Leaflet.js interactive GIS radar, 10+ State Language Engine"),
        ("Payments & Cloud", "Unified digital UPI gateway, Docker containerization, Cloudflare quick tunnels")
    ]
    for k, v in techs:
        p = tf.add_paragraph()
        p.text = f"• {k}: "
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = DARK_TEXT
        run = p.add_run()
        run.text = v
        run.font.bold = False
        run.font.color.rgb = MUTED_TEXT

    # Right: Implementation Workflow
    c_right = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, start_x + left_w + Inches(0.23), card_y, right_w, card_h)
    c_right.fill.solid()
    c_right.fill.fore_color.rgb = WHITE
    c_right.line.color.rgb = BORDER_COLOR
    tb = slide3.shapes.add_textbox(start_x + left_w + Inches(0.43), card_y + Inches(0.2), right_w - Inches(0.4), card_h - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Methodology & End-to-End Workflow"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = NAVY

    workflow_steps = [
        ("Step 1: Citizen Booking / SOS Trigger", "Resident selects trade (Electrician, Plumber, Carpenter, AC) and drops a GPS location pin across Ghaziabad sectors."),
        ("Step 2: Sub-Second Geospatial Matching", "PostGIS ST_DWithin query discovers verified, available artisans within a 5–20 km radius sorted by proximity and Skill India tier."),
        ("Step 3: Real-Time Dispatch & Progression", "Artisan receives job payload on mobile web portal -> transitions status: Assigned -> En Route (GPS active) -> In Progress -> Completed."),
        ("Step 4: Automated 93/5/2 Split & Settlement", "System automatically routes 93% to artisan's UPI, 5% to platform operations, and 2% to the collective worker welfare insurance pool."),
        ("Step 5: Audit Logging & Citizen Feedback", "Generates itemized digital GST invoice and records the transaction on the verifiable cooperative audit registry.")
    ]
    for k, v in workflow_steps:
        p = tf.add_paragraph()
        p.text = f"{k}: "
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = SAFFRON
        run = p.add_run()
        run.text = v
        run.font.bold = False
        run.font.color.rgb = DARK_TEXT

    # =========================================================================
    # SLIDE 4: FEASIBILITY AND VIABILITY
    # =========================================================================
    slide4 = prs.slides.add_slide(blank_layout)
    add_header(slide4, "FEASIBILITY AND VIABILITY", "Feasibility Analysis, Potential Challenges & Strategic Mitigation", 4)

    col_w = Inches(3.75)
    c1 = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, start_x, card_y, col_w, card_h)
    c1.fill.solid()
    c1.fill.fore_color.rgb = WHITE
    c1.line.color.rgb = BORDER_COLOR
    tb = slide4.shapes.add_textbox(start_x + Inches(0.2), card_y + Inches(0.2), col_w - Inches(0.4), card_h - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "1. Feasibility Analysis"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = NAVY

    f_points = [
        "Technical Feasibility: Built entirely on open-source, robust production technologies (FastAPI, PostgreSQL, Leaflet.js). Highly scalable with zero proprietary license dependencies.",
        "Operational Feasibility: Direct federation partnership with existing registered artisan unions and primary cooperative societies in Ghaziabad district.",
        "Economic Viability: 5% platform maintenance fee achieves self-sustaining operational break-even while increasing artisan net income by 35–45%."
    ]
    for pt in f_points:
        p = tf.add_paragraph()
        p.text = f"• {pt}"
        p.font.size = Pt(10.5)
        p.font.color.rgb = DARK_TEXT

    c2 = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, start_x + col_w + col_gap, card_y, col_w, card_h)
    c2.fill.solid()
    c2.fill.fore_color.rgb = WHITE
    c2.line.color.rgb = BORDER_COLOR
    tb = slide4.shapes.add_textbox(start_x + col_w + col_gap + Inches(0.2), card_y + Inches(0.2), col_w - Inches(0.4), card_h - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "2. Potential Risks & Challenges"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = NAVY

    r_points = [
        "Digital Literacy Barrier: Informal blue-collar artisans may struggle with complex smartphone interfaces.",
        "Cold-Start Spatial Liquidity: Ensuring sufficient verified artisan density across peripheral Ghaziabad sectors during early rollout.",
        "Service Quality & Punctuality: Maintaining uniform workmanship standards and preventing platform circumvention."
    ]
    for pt in r_points:
        p = tf.add_paragraph()
        p.text = f"• {pt}"
        p.font.size = Pt(10.5)
        p.font.color.rgb = DARK_TEXT

    c3 = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, start_x + (col_w + col_gap)*2, card_y, col_w, card_h)
    c3.fill.solid()
    c3.fill.fore_color.rgb = WHITE
    c3.line.color.rgb = BORDER_COLOR
    tb = slide4.shapes.add_textbox(start_x + (col_w + col_gap)*2 + Inches(0.2), card_y + Inches(0.2), col_w - Inches(0.4), card_h - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "3. Mitigation Strategies"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = NAVY

    m_points = [
        "10+ Regional State Languages & AI Bot: Native language voice/text assistance to simplify artisan job acceptance and navigation.",
        "AI 7-Day Demand Forecasting: Proactively alerts artisan guilds to mobilize workers in high-demand residential sectors before weekend surges.",
        "Aadhaar KYC & Skill Auditing: Federation admins verify ITI/NSDC trade certificates before granting badge verification."
    ]
    for pt in m_points:
        p = tf.add_paragraph()
        p.text = f"• {pt}"
        p.font.size = Pt(10.5)
        p.font.color.rgb = DARK_TEXT

    # =========================================================================
    # SLIDE 5: IMPACT AND BENEFITS
    # =========================================================================
    slide5 = prs.slides.add_slide(blank_layout)
    add_header(slide5, "IMPACT AND BENEFITS", "Social, Economic & Citizen Benefits of SahakarConnect", 5)

    # 2 Big Cards: Audience Impact & Quadruple Bottom-Line Benefits
    half_w = Inches(5.75)
    c_left5 = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, start_x, card_y, half_w, card_h)
    c_left5.fill.solid()
    c_left5.fill.fore_color.rgb = WHITE
    c_left5.line.color.rgb = BORDER_COLOR
    tb = slide5.shapes.add_textbox(start_x + Inches(0.25), card_y + Inches(0.2), half_w - Inches(0.5), card_h - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "1. Impact on Target Stakeholders"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = NAVY

    stakeholders = [
        ("Artisans & Gig Workers", "Direct 30-45% increase in take-home wages; transition from vulnerable informal daily labor to recognized, insured, and dignified professionals."),
        ("Citizens & Households", "Access to trusted, verified ITI craftsmen at standard rates with guaranteed 15-20 min arrival and 24x7 emergency SOS assistance."),
        ("Government & Cooperative Unions", "Digital formalization of unorganized gig workforce; transparent labor data for policy design and direct social welfare disbursements.")
    ]
    for k, v in stakeholders:
        p = tf.add_paragraph()
        p.text = f"• {k}: "
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = GREEN
        run = p.add_run()
        run.text = v
        run.font.bold = False
        run.font.color.rgb = DARK_TEXT

    c_right5 = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, start_x + half_w + Inches(0.23), card_y, half_w, card_h)
    c_right5.fill.solid()
    c_right5.fill.fore_color.rgb = WHITE
    c_right5.line.color.rgb = BORDER_COLOR
    tb = slide5.shapes.add_textbox(start_x + half_w + Inches(0.48), card_y + Inches(0.2), half_w - Inches(0.5), card_h - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "2. Multi-Dimensional Societal Benefits"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = NAVY

    benefits = [
        ("Social Protection", "Dedicated 2% cooperative deduction pool financing Pradhan Mantri Suraksha Bima Yojana (PMSBY) accidental cover (₹2 Lakhs) and health subsidies."),
        ("Local Economic Multiplier", "93% of revenue circulates directly within the local Ghaziabad artisan economy instead of corporate venture capital extraction."),
        ("Environmental Sustainability", "Smart geospatial proximity matching minimizes deadhead transit miles, reducing urban travel emissions across Ghaziabad sectors.")
    ]
    for k, v in benefits:
        p = tf.add_paragraph()
        p.text = f"• {k}: "
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = SAFFRON
        run = p.add_run()
        run.text = v
        run.font.bold = False
        run.font.color.rgb = DARK_TEXT

    # =========================================================================
    # SLIDE 6: RESEARCH AND REFERENCES
    # =========================================================================
    slide6 = prs.slides.add_slide(blank_layout)
    add_header(slide6, "RESEARCH AND REFERENCES", "Policy Frameworks, Regulatory Standards & Technical References", 6)

    c_left6 = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, start_x, card_y, half_w, card_h)
    c_left6.fill.solid()
    c_left6.fill.fore_color.rgb = WHITE
    c_left6.line.color.rgb = BORDER_COLOR
    tb = slide6.shapes.add_textbox(start_x + Inches(0.25), card_y + Inches(0.2), half_w - Inches(0.5), card_h - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Government & Policy Frameworks"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = NAVY

    gov_refs = [
        ("Ministry of Cooperation, Govt. of India", "National Database on Cooperatives & National Policy Framework on Digital Cooperatives (cooperation.gov.in)"),
        ("Department of Cooperatives, Govt. of UP", "Uttar Pradesh Cooperative Societies Act, 1965 & Artisan Federation Rules (upsdc.gov.in)"),
        ("Pradhan Mantri Suraksha Bima Yojana (PMSBY)", "Ministry of Finance social security accidental insurance integration guidelines (jansuraksha.gov.in)"),
        ("Skill India Mission & NSDC", "National Skills Qualifications Framework (NSQF) for electrical, plumbing & woodwork trades (skillindia.gov.in)")
    ]
    for k, v in gov_refs:
        p = tf.add_paragraph()
        p.text = f"1. {k}\n   "
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = NAVY
        run = p.add_run()
        run.text = v
        run.font.bold = False
        run.font.color.rgb = MUTED_TEXT

    c_right6 = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, start_x + half_w + Inches(0.23), card_y, half_w, card_h)
    c_right6.fill.solid()
    c_right6.fill.fore_color.rgb = WHITE
    c_right6.line.color.rgb = BORDER_COLOR
    tb = slide6.shapes.add_textbox(start_x + half_w + Inches(0.48), card_y + Inches(0.2), half_w - Inches(0.5), card_h - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Technical & Academic Citations"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = NAVY

    tech_refs = [
        ("International Labour Organization (ILO)", "Report on Platform Cooperativism: Reclaiming Democratic Control & Decent Work in the Gig Economy (2023)."),
        ("PostgreSQL & PostGIS Reference", "Open Geospatial Consortium (OGC) Simple Features Standard for Spatial Distance & Radar Proximity Calculations."),
        ("National Informatics Centre (NIC)", "District Administration Ghaziabad Official Civic Infrastructure & GIS Boundaries Reference (ghaziabad.nic.in)."),
        ("NITI Aayog Report (2022)", "'Booming Gig and Platform Economy': Leveraging Cooperative Frameworks for Informal Social Security.")
    ]
    for k, v in tech_refs:
        p = tf.add_paragraph()
        p.text = f"1. {k}\n   "
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = NAVY
        run = p.add_run()
        run.text = v
        run.font.bold = False
        run.font.color.rgb = MUTED_TEXT

    prs.save(output_path)
    print(f"✅ Presentation successfully generated at: {output_path}")

if __name__ == "__main__":
    create_sih_presentation()
