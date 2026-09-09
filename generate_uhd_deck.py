import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def build_uhd_deck(output_path="SahakarConnect_UHD_13Slide_Master_Deck.pptx"):
    prs = Presentation()
    # 16:9 Widescreen UHD standard (13.333 x 7.5 inches)
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Color Palette: Modern Official Executive Government Palette
    NAVY_PRIMARY = RGBColor(11, 30, 54)     # #0B1E36 - Deep Slate Navy
    NAVY_CARD = RGBColor(18, 44, 76)        # #122C4C
    SAFFRON = RGBColor(217, 119, 6)         # #D97706 - Warm Saffron Amber
    SAFFRON_LIGHT = RGBColor(254, 243, 199) # #FEF3C7 - Amber 100
    GREEN = RGBColor(21, 128, 61)           # #15803D - India Green
    GREEN_LIGHT = RGBColor(220, 252, 231)   # #DCFCE7 - Green 100
    ROSE = RGBColor(225, 29, 72)            # #E11D48 - Emergency Rose
    ROSE_LIGHT = RGBColor(255, 228, 230)    # #FFE4E6
    DARK_TEXT = RGBColor(30, 41, 59)        # #1E293B
    SLATE_BODY = RGBColor(71, 85, 105)      # #475569
    SLATE_LIGHT = RGBColor(248, 250, 252)   # #F8FAFC
    MUTED_TEXT = RGBColor(100, 116, 139)    # #64748B - Slate 500
    BORDER_COLOR = RGBColor(226, 232, 240)  # #E2E8F0
    BORDER_DARK = RGBColor(203, 213, 225)   # #CBD5E1
    WHITE = RGBColor(255, 255, 255)
    BLUE_ACCENT = RGBColor(37, 99, 235)     # #2563EB
    BLUE_LIGHT = RGBColor(239, 246, 255)

    def add_chrome(slide, title_text, category_pill, slide_num, total_slides=13):
        # 1. Top Tricolor Bar
        stripe_w = prs.slide_width / 3
        s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), stripe_w, Inches(0.08))
        s.fill.solid(); s.fill.fore_color.rgb = RGBColor(255, 153, 51); s.line.fill.background()
        w = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, stripe_w, Inches(0), stripe_w, Inches(0.08))
        w.fill.solid(); w.fill.fore_color.rgb = RGBColor(245, 245, 245); w.line.fill.background()
        g = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, stripe_w * 2, Inches(0), stripe_w, Inches(0.08))
        g.fill.solid(); g.fill.fore_color.rgb = RGBColor(19, 136, 8); g.line.fill.background()

        # 2. Header Area
        pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.32), Inches(3.2), Inches(0.32))
        pill.fill.solid(); pill.fill.fore_color.rgb = SAFFRON_LIGHT
        pill.line.color.rgb = SAFFRON; pill.line.width = Pt(1)
        ptf = pill.text_frame; ptf.margin_left = ptf.margin_right = ptf.margin_top = ptf.margin_bottom = 0
        pp = ptf.paragraphs[0]; pp.text = category_pill.upper(); pp.font.size = Pt(9.5); pp.font.bold = True
        pp.font.color.rgb = SAFFRON; pp.alignment = PP_ALIGN.CENTER; pp.font.name = "Arial"

        tbox = slide.shapes.add_textbox(Inches(0.8), Inches(0.68), Inches(8.5), Inches(0.75))
        ttf = tbox.text_frame; ttf.word_wrap = True; ttf.margin_left = ttf.margin_top = ttf.margin_right = ttf.margin_bottom = 0
        tp = ttf.paragraphs[0]; tp.text = title_text; tp.font.size = Pt(20); tp.font.bold = True
        tp.font.color.rgb = NAVY_PRIMARY; tp.font.name = "Arial"

        rbox = slide.shapes.add_textbox(Inches(9.5), Inches(0.35), Inches(3.033), Inches(0.9))
        rtf = rbox.text_frame; rtf.word_wrap = True; rtf.margin_right = 0
        rp = rtf.paragraphs[0]; rp.text = "SahakarConnect"; rp.font.size = Pt(13); rp.font.bold = True
        rp.font.color.rgb = NAVY_PRIMARY; rp.alignment = PP_ALIGN.RIGHT; rp.font.name = "Arial"
        rp2 = rtf.add_paragraph(); rp2.text = "Department of Cooperatives • Govt of UP"; rp2.font.size = Pt(8.5)
        rp2.font.color.rgb = MUTED_TEXT; rp2.alignment = PP_ALIGN.RIGHT; rp2.font.name = "Arial"

        fbox = slide.shapes.add_textbox(Inches(0.8), Inches(7.05), Inches(11.733), Inches(0.3))
        ftf = fbox.text_frame; ftf.word_wrap = True; ftf.margin_left = ftf.margin_top = ftf.margin_right = ftf.margin_bottom = 0
        fp = ftf.paragraphs[0]
        fp.text = f"SahakarConnect Comprehensive Project Master Deck • Ghaziabad District Federation  |  Slide {slide_num} of {total_slides}"
        fp.font.size = Pt(8.5); fp.font.color.rgb = MUTED_TEXT; fp.font.name = "Arial"

    def create_card(slide, left, top, width, height, bg_color=WHITE, border_color=BORDER_COLOR, border_width=Pt(1.2)):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid(); shape.fill.fore_color.rgb = bg_color
        shape.line.color.rgb = border_color; shape.line.width = border_width
        return shape

    # SLIDE 1
    slide1 = prs.slides.add_slide(blank_layout)
    bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), prs.slide_width, prs.slide_height)
    bg1.fill.solid(); bg1.fill.fore_color.rgb = NAVY_PRIMARY; bg1.line.fill.background()

    s_top = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), prs.slide_width, Inches(0.12))
    s_top.fill.solid(); s_top.fill.fore_color.rgb = RGBColor(255, 153, 51); s_top.line.fill.background()

    main_card = create_card(slide1, Inches(1.2), Inches(1.0), Inches(10.933), Inches(5.6), WHITE, SAFFRON, Pt(2.5))
    tb = slide1.shapes.add_textbox(Inches(1.6), Inches(1.3), Inches(10.133), Inches(5.0))
    tf = tb.text_frame; tf.word_wrap = True

    p = tf.paragraphs[0]; p.text = "SahakarConnect (सहकार कनेक्ट)"
    p.font.size = Pt(30); p.font.bold = True; p.font.color.rgb = NAVY_PRIMARY; p.alignment = PP_ALIGN.CENTER

    p = tf.add_paragraph()
    p.text = "Decentralized Cooperative Platform for Home & Artisan Services"
    p.font.size = Pt(17); p.font.bold = True; p.font.color.rgb = SAFFRON; p.alignment = PP_ALIGN.CENTER

    p = tf.add_paragraph()
    p.text = "A High-Tech Cooperative Alternative to Monopolistic Gig Aggregators in Ghaziabad District"
    p.font.size = Pt(12); p.font.color.rgb = DARK_TEXT; p.alignment = PP_ALIGN.CENTER

    p = tf.add_paragraph(); p.text = "\n"

    p = tf.add_paragraph()
    p.text = "⚡ 93% Direct Worker Payout  •  🛡️ 2% PMSBY Welfare Pool  •  📍 PostGIS GPS Dispatch  •  🌐 10+ State Languages  •  🚨 24x7 SOS"
    p.font.size = Pt(11); p.font.bold = True; p.font.color.rgb = GREEN; p.alignment = PP_ALIGN.CENTER

    p = tf.add_paragraph(); p.text = "\n"

    p = tf.add_paragraph()
    p.text = "Department of Cooperatives, Government of Uttar Pradesh\nAffiliated with Ministry of Cooperation, Government of India (cooperation.gov.in)"
    p.font.size = Pt(10); p.font.color.rgb = MUTED_TEXT; p.alignment = PP_ALIGN.CENTER

    # SLIDE 2
    slide2 = prs.slides.add_slide(blank_layout)
    add_chrome(slide2, "The Urban Gig Economy Crisis & Market Failure", "Problem Context", 2)

    col_w = Inches(2.78); col_gap = Inches(0.2); start_x = Inches(0.8); card_y = Inches(1.55); card_h = Inches(5.2)

    prob_cards = [
        ("1. Aggregator Exploitation", ROSE, ROSE_LIGHT, [
            "Predatory 30%–40% Commission cuts on every service.",
            "Workers pushed into severe debt and informal vulnerability.",
            "Zero transparency in algorithmic deductions and penalties.",
            "Arbitrary account deactivations with no appeal mechanism."
        ]),
        ("2. Zero Social Safety Net", SAFFRON, SAFFRON_LIGHT, [
            "Zero accidental insurance or hospital cash cover.",
            "No retirement pension or medical distress assistance.",
            "Artisans bear 100% of equipment, transit, and tool repair costs.",
            "Complete lack of institutional labor dignity."
        ]),
        ("3. Consumer Price Gouging", BLUE_ACCENT, BLUE_LIGHT, [
            "Unregulated 2x–3x surge pricing during rains & emergency hours.",
            "Inconsistent quality and unverified technician credentials.",
            "Absence of dedicated rapid 15-min emergency response.",
            "Impersonal corporate call centers with poor accountability."
        ]),
        ("4. The Cooperative Fix", GREEN, GREEN_LIGHT, [
            "Transition to democratic, worker-owned cooperative federations.",
            "Direct 93% revenue retention inside the local community.",
            "Institutional formalization under UP Cooperative Societies Act.",
            "Guaranteed fair pricing with zero middleman extraction."
        ])
    ]

    for i, (title, color, light_c, bullets) in enumerate(prob_cards):
        cx = start_x + (col_w + col_gap) * i
        card = create_card(slide2, cx, card_y, col_w, card_h, WHITE, color, Pt(1.5))
        
        strip = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx + Inches(0.12), card_y + Inches(0.12), col_w - Inches(0.24), Inches(0.55))
        strip.fill.solid(); strip.fill.fore_color.rgb = light_c; strip.line.fill.background()
        stf = strip.text_frame; stf.margin_left = stf.margin_right = stf.margin_top = stf.margin_bottom = 0
        sp = stf.paragraphs[0]; sp.text = title; sp.font.size = Pt(11); sp.font.bold = True; sp.font.color.rgb = color; sp.alignment = PP_ALIGN.CENTER

        tb = slide2.shapes.add_textbox(cx + Inches(0.15), card_y + Inches(0.75), col_w - Inches(0.3), card_h - Inches(0.9))
        tf = tb.text_frame; tf.word_wrap = True
        for b in bullets:
            p = tf.add_paragraph(); p.text = f"• {b}"; p.font.size = Pt(9.5); p.font.color.rgb = DARK_TEXT

    # SLIDE 3
    slide3 = prs.slides.add_slide(blank_layout)
    add_chrome(slide3, "The 93/5/2 Cooperative Revenue Split Architecture", "Economic Model & Flowchart", 3)

    top_box = create_card(slide3, Inches(3.8), Inches(1.55), Inches(5.733), Inches(0.85), NAVY_PRIMARY, SAFFRON, Pt(2))
    t_tb = slide3.shapes.add_textbox(Inches(3.9), Inches(1.6), Inches(5.533), Inches(0.75))
    t_tf = t_tb.text_frame; t_tf.word_wrap = True
    tp = t_tf.paragraphs[0]; tp.text = "Gross Citizen Service Payment (100%)"; tp.font.size = Pt(14); tp.font.bold = True; tp.font.color.rgb = WHITE; tp.alignment = PP_ALIGN.CENTER
    tp2 = t_tf.add_paragraph(); tp2.text = "Unified Digital Payment Gateway / UPI QR / Cards"; tp2.font.size = Pt(9.5); tp2.font.color.rgb = SAFFRON_LIGHT; tp2.alignment = PP_ALIGN.CENTER

    arr1 = slide3.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, Inches(2.4), Inches(2.48), Inches(0.4), Inches(0.5))
    arr1.fill.solid(); arr1.fill.fore_color.rgb = GREEN; arr1.line.fill.background()

    arr2 = slide3.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, Inches(6.46), Inches(2.48), Inches(0.4), Inches(0.5))
    arr2.fill.solid(); arr2.fill.fore_color.rgb = BLUE_ACCENT; arr2.line.fill.background()

    arr3 = slide3.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, Inches(10.5), Inches(2.48), Inches(0.4), Inches(0.5))
    arr3.fill.solid(); arr3.fill.fore_color.rgb = SAFFRON; arr3.line.fill.background()

    split_cards = [
        ("93% Direct Worker Payout", GREEN, GREEN_LIGHT, Inches(0.8), [
            "Direct UPI Settlement: Payout disbursed straight to the artisan upon service completion.",
            "35%–45% Net Income Increase: Eliminates middleman extraction, allowing workers to retain true labor value.",
            "Prompt Livelihood Security: Daily liquid earnings with zero delayed lock-ins."
        ]),
        ("5% Platform Operations", BLUE_ACCENT, BLUE_LIGHT, Inches(4.8), [
            "Cloud Infrastructure: Covers FastAPI microservices, PostgreSQL hosting, and Cloudflare tunneling.",
            "Geospatial Map APIs: Maintained PostGIS spatial database and GIS dispatch radar.",
            "Zero Private Shareholder Dividends: Platform runs purely at non-profit cost."
        ]),
        ("2% Worker Welfare & Insurance", SAFFRON, SAFFRON_LIGHT, Inches(8.8), [
            "PMSBY Accidental Insurance: Direct financing of ₹2,00,000 accidental safety net.",
            "Healthcare Distress Grants: Emergency medical assistance fund for artisans and families.",
            "Continuous Upskilling: Subsidized Skill India certification & safety tooling kits."
        ])
    ]

    for title, color, light_c, cx, bullets in split_cards:
        card = create_card(slide3, cx, Inches(3.05), Inches(3.733), Inches(3.7), WHITE, color, Pt(1.8))
        
        strip = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx + Inches(0.15), Inches(3.18), Inches(3.433), Inches(0.5))
        strip.fill.solid(); strip.fill.fore_color.rgb = light_c; strip.line.fill.background()
        stf = strip.text_frame; stf.margin_left = stf.margin_right = stf.margin_top = stf.margin_bottom = 0
        sp = stf.paragraphs[0]; sp.text = title; sp.font.size = Pt(11.5); sp.font.bold = True; sp.font.color.rgb = color; sp.alignment = PP_ALIGN.CENTER

        tb = slide3.shapes.add_textbox(cx + Inches(0.2), Inches(3.8), Inches(3.333), Inches(2.8))
        tf = tb.text_frame; tf.word_wrap = True
        for b in bullets:
            p = tf.add_paragraph(); p.text = f"• {b}"; p.font.size = Pt(9.5); p.font.color.rgb = DARK_TEXT

    # SLIDE 4
    slide4 = prs.slides.add_slide(blank_layout)
    add_chrome(slide4, "End-to-End Platform System Architecture", "Technical Architecture Flowchart", 4)

    layer_h = Inches(0.95); gap_y = Inches(0.12); start_y = Inches(1.55)
    arch_layers = [
        ("Layer 1: Presentation & Multilingual Portals", "Citizen Web Portal (/customer) • Artisan Mobile Portal (/worker) • Federation Admin (/admin) • 10+ State Languages Engine • 24x7 AI Assistant", SAFFRON, SAFFRON_LIGHT),
        ("Layer 2: API Gateway & Application Controller", "FastAPI Asynchronous Core • Starlette Session Middleware • PBKDF2-HMAC-SHA256 Auth Guard • Rate Limiting & Input Sanitizer", BLUE_ACCENT, BLUE_LIGHT),
        ("Layer 3: AI & Geospatial Intelligence Layer", "PostGIS Spatial Engine (ST_DWithin, ST_Distance) • Polynomial 7-Day Demand Forecasting • Sector Surge Multipliers • NLP Chat Engine", GREEN, GREEN_LIGHT),
        ("Layer 4: Payment, Invoice & Wage Ledger Layer", "Razorpay Unified UPI Gateway • Automated 93/5/2 Split Calculator • Itemized Digital GST Invoicing • Verifiable Official Wage Registry", NAVY_PRIMARY, RGBColor(241, 245, 249)),
        ("Layer 5: Database & Infrastructure Layer", "PostgreSQL 15 + PostGIS Extension • Cloudflare Quick Tunnels • Secure Document Store (/static/uploads) • Docker Containerization", SLATE_BODY, RGBColor(226, 232, 240))
    ]

    for i, (title, desc, color, bg_col) in enumerate(arch_layers):
        cy = start_y + (layer_h + gap_y) * i
        card = create_card(slide4, start_x, cy, Inches(11.733), layer_h, bg_col, color, Pt(1.5))
        tb = slide4.shapes.add_textbox(start_x + Inches(0.25), cy + Inches(0.12), Inches(11.233), layer_h - Inches(0.24))
        tf = tb.text_frame; tf.word_wrap = True
        p = tf.paragraphs[0]; p.text = title; p.font.size = Pt(11.5); p.font.bold = True; p.font.color.rgb = color
        p2 = tf.add_paragraph(); p2.text = desc; p2.font.size = Pt(9.5); p2.font.color.rgb = DARK_TEXT

    # SLIDE 5
    slide5 = prs.slides.add_slide(blank_layout)
    add_chrome(slide5, "Citizen & Artisan Service Lifecycle Workflow", "End-to-End Process Flowchart", 5)

    step_w = Inches(1.8); step_gap = Inches(0.18); step_y = Inches(1.6); step_h = Inches(4.9)
    steps_data = [
        ("Step 1: Booking", "Citizen selects trade & drops GPS pin on Ghaziabad sector map (Instant or Scheduled).", BLUE_ACCENT, BLUE_LIGHT),
        ("Step 2: Matching", "PostGIS ST_DWithin query discovers nearest verified artisan within 5–20 km radius.", SAFFRON, SAFFRON_LIGHT),
        ("Step 3: Dispatch", "Artisan receives mobile push payload & starts trip with live GPS tracking.", GREEN, GREEN_LIGHT),
        ("Step 4: Execution", "Artisan arrives on site (15-20 min SLA) & completes repair work.", NAVY_PRIMARY, RGBColor(241, 245, 249)),
        ("Step 5: Settlement", "Automated 93/5/2 split executed via UPI; digital GST invoice generated.", SAFFRON, SAFFRON_LIGHT),
        ("Step 6: Review", "Citizen rates service (1-5 stars) & updates verified artisan score in registry.", GREEN, GREEN_LIGHT)
    ]

    for i, (title, desc, color, bg_col) in enumerate(steps_data):
        cx = start_x + (step_w + step_gap) * i
        card = create_card(slide5, cx, step_y, step_w, step_h, WHITE, color, Pt(1.5))
        badge = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx + Inches(0.1), step_y + Inches(0.15), step_w - Inches(0.2), Inches(0.45))
        badge.fill.solid(); badge.fill.fore_color.rgb = bg_col; badge.line.fill.background()
        btf = badge.text_frame; btf.margin_left = btf.margin_right = btf.margin_top = btf.margin_bottom = 0
        bp = btf.paragraphs[0]; bp.text = title; bp.font.size = Pt(10); bp.font.bold = True; bp.font.color.rgb = color; bp.alignment = PP_ALIGN.CENTER

        tb = slide5.shapes.add_textbox(cx + Inches(0.12), step_y + Inches(0.75), step_w - Inches(0.24), step_h - Inches(0.9))
        tf = tb.text_frame; tf.word_wrap = True
        p = tf.paragraphs[0]; p.text = desc; p.font.size = Pt(9.5); p.font.color.rgb = DARK_TEXT

    # SLIDE 6
    slide6 = prs.slides.add_slide(blank_layout)
    add_chrome(slide6, "Geospatial Dispatch Engine: PostGIS & Radar Matching", "Spatial Intelligence & GIS", 6)

    half_w = Inches(5.75)
    c_left6 = create_card(slide6, start_x, card_y, half_w, card_h)
    tb = slide6.shapes.add_textbox(start_x + Inches(0.25), card_y + Inches(0.2), half_w - Inches(0.5), card_h - Inches(0.4))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = "Spatial Query Architecture"; p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = NAVY_PRIMARY

    gis_points = [
        ("Native SRID 4326 POINT Indexing", "Geographic coordinates (Latitude & Longitude) stored as native spatial point geometries for high-precision spherical distance calculations."),
        ("Sub-Second ST_DWithin Filtering", "Executes spatial radius queries (5 km to 20 km search radials) in under 15 milliseconds, filtering only verified, available workers."),
        ("Geodesic ST_Distance Sorting", "Sorts artisan candidates by accurate road/ellipsoidal distance rather than rough Euclidean approximations."),
        ("Leaflet.js Real-Time Radar", "Interactive client-side radar map displaying live sector worker pins and active dispatch routes across Ghaziabad.")
    ]
    for k, v in gis_points:
        p = tf.add_paragraph(); p.text = f"• {k}: "; p.font.size = Pt(10); p.font.bold = True; p.font.color.rgb = SAFFRON
        run = p.add_run(); run.text = v; run.font.bold = False; run.font.color.rgb = DARK_TEXT

    c_right6 = create_card(slide6, start_x + half_w + Inches(0.23), card_y, half_w, card_h)
    tb = slide6.shapes.add_textbox(start_x + half_w + Inches(0.48), card_y + Inches(0.2), half_w - Inches(0.5), card_h - Inches(0.4))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = "Ghaziabad District Sector Coverage"; p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = NAVY_PRIMARY

    sectors_list = [
        ("Indirapuram (Shipra Sun City, Ahinsa Khand)", "210+ Verified Artisans • 12-min response"),
        ("Vaishali (Sectors 1 to 9)", "160+ Verified Artisans • 14-min response"),
        ("Vasundhara (Sectors 1 to 18)", "175+ Verified Artisans • 15-min response"),
        ("Raj Nagar & Raj Nagar Extension", "330+ Verified Artisans • 12-min response"),
        ("Crossings Republik & Kaushambi", "245+ Verified Artisans • 16-min response"),
        ("Kavi Nagar, Shastri Nagar & Sahibabad", "340+ Verified Artisans • 15-min response")
    ]
    for loc, meta in sectors_list:
        p = tf.add_paragraph(); p.text = f"📍 {loc}\n   "; p.font.size = Pt(9.5); p.font.bold = True; p.font.color.rgb = NAVY_PRIMARY
        run = p.add_run(); run.text = meta; run.font.bold = False; run.font.color.rgb = GREEN

    # SLIDE 7
    slide7 = prs.slides.add_slide(blank_layout)
    add_chrome(slide7, "AI Seasonal Demand Forecasting & Labor Allocation", "Predictive Analytics Engine", 7)

    c_left7 = create_card(slide7, start_x, card_y, half_w, card_h)
    tb = slide7.shapes.add_textbox(start_x + Inches(0.25), card_y + Inches(0.2), half_w - Inches(0.5), card_h - Inches(0.4))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = "Predictive Modeling Engine (forecast.py)"; p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = NAVY_PRIMARY

    ai_points = [
        ("Polynomial Trend Estimation", "Evaluates historical booking volume patterns combined with polynomial regression models to project 7-day category-wise demand."),
        ("Weekend Surge Multipliers", "Models 35%–45% service surges on Saturdays and Sundays across Electricians, Plumbers, Carpenters, and AC technicians."),
        ("Proactive Workforce Mobilization", "Alerts artisan cooperative guilds 48 hours prior to anticipated demand peaks, preventing sector shortages."),
        ("Dynamic Proximity Dispatch Score", "Ranks candidates using a multivariable function combining spatial distance, skill certification tier, and customer ratings.")
    ]
    for k, v in ai_points:
        p = tf.add_paragraph(); p.text = f"• {k}: "; p.font.size = Pt(10); p.font.bold = True; p.font.color.rgb = SAFFRON
        run = p.add_run(); run.text = v; run.font.bold = False; run.font.color.rgb = DARK_TEXT

    c_right7 = create_card(slide7, start_x + half_w + Inches(0.23), card_y, half_w, card_h)
    tb = slide7.shapes.add_textbox(start_x + half_w + Inches(0.48), card_y + Inches(0.2), half_w - Inches(0.5), card_h - Inches(0.4))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = "Sector Demand Multiplier Breakdown"; p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = NAVY_PRIMARY

    surge_data = [
        ("Raj Nagar Extension", "1.35x Surge Index", "Dominant: Move-in Electrical & Deep Cleaning"),
        ("Crossings Republik", "1.28x Surge Index", "Dominant: RO & Appliance Servicing"),
        ("Indirapuram", "1.25x Surge Index", "Dominant: AC Jet Cleaning & Wiring"),
        ("Vasundhara", "1.20x Surge Index", "Dominant: Modular Carpentry & Locks"),
        ("Vaishali", "1.18x Surge Index", "Dominant: Sanitary Fitting & Plumbing"),
        ("Kavi Nagar", "1.15x Surge Index", "Dominant: General Home Maintenance")
    ]
    for loc, surge, dom in surge_data:
        p = tf.add_paragraph(); p.text = f"📊 {loc}: "; p.font.size = Pt(9.5); p.font.bold = True; p.font.color.rgb = NAVY_PRIMARY
        run = p.add_run(); run.text = f"{surge} ({dom})"; run.font.bold = False; run.font.color.rgb = SAFFRON

    # SLIDE 8
    slide8 = prs.slides.add_slide(blank_layout)
    add_chrome(slide8, "24x7 Emergency SOS Rapid Dispatch Engine", "Crisis Management & SLA", 8)

    col_w = Inches(3.75)
    sos_cards = [
        ("1. Emergency SOS Triggers", ROSE, ROSE_LIGHT, [
            "Severe Electrical Short Circuits: Sparking MCBs, neutral failure, and burning smell.",
            "Water Mainline Pipe Bursts: Rapid flooding, overhead tank valve rupture.",
            "Late-Night Door Lockouts: Jammed master locks, broken key extraction.",
            "HVAC / Deep Gas Faults: Inverter PCB shorting and urgent cooling failure."
        ]),
        ("2. Rapid 15-Min Response SLA", SAFFRON, SAFFRON_LIGHT, [
            "Priority Queue Bypass: Emergency requests automatically jump to the top of the dispatch stack.",
            "Automated Sector Lead Alert: Closest on-duty emergency master artisan receives high-priority buzzer.",
            "Toll-Free Hotline Fallback: 24x7 telephone backup via 1800-GZB-HELP.",
            "Direct Sector Coordinator Line: Real-time coordination with resident society RWAs."
        ]),
        ("3. Standardized Transparent Pricing", GREEN, GREEN_LIGHT, [
            "Fixed Urgent Surcharge (+₹150): Completely transparent flat fee for rapid 15-min SLA.",
            "Zero Predatory Surge Gouging: Eliminates the 300% surge pricing charged by private commercial apps.",
            "Itemized Digital Invoicing: Full breakdown of base fare + urgent fee + GST.",
            "Post-Emergency Safety Audit: Free follow-up safety verification by the cooperative."
        ])
    ]

    for i, (title, color, light_c, bullets) in enumerate(sos_cards):
        cx = start_x + (col_w + col_gap) * i
        card = create_card(slide8, cx, card_y, col_w, card_h, WHITE, color, Pt(1.5))
        strip = slide8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx + Inches(0.12), card_y + Inches(0.12), col_w - Inches(0.24), Inches(0.55))
        strip.fill.solid(); strip.fill.fore_color.rgb = light_c; strip.line.fill.background()
        stf = strip.text_frame; stf.margin_left = stf.margin_right = stf.margin_top = stf.margin_bottom = 0
        sp = stf.paragraphs[0]; sp.text = title; sp.font.size = Pt(11); sp.font.bold = True; sp.font.color.rgb = color; sp.alignment = PP_ALIGN.CENTER

        tb = slide8.shapes.add_textbox(cx + Inches(0.15), card_y + Inches(0.75), col_w - Inches(0.3), card_h - Inches(0.9))
        tf = tb.text_frame; tf.word_wrap = True
        for b in bullets:
            p = tf.add_paragraph(); p.text = f"• {b}"; p.font.size = Pt(9.5); p.font.color.rgb = DARK_TEXT

    # SLIDE 9
    slide9 = prs.slides.add_slide(blank_layout)
    add_chrome(slide9, "Multilingual Accessibility & 24x7 AI Assistant", "Citizen Inclusivity & Conversational AI", 9)

    c_left9 = create_card(slide9, start_x, card_y, half_w, card_h)
    tb = slide9.shapes.add_textbox(start_x + Inches(0.25), card_y + Inches(0.2), half_w - Inches(0.5), card_h - Inches(0.4))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = "10+ State Regional Language Engine"; p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = NAVY_PRIMARY

    lang_points = [
        ("Supported Languages", "English, हिन्दी (Hindi), भोजपुरी (Bhojpuri), ਪੰਜਾਬੀ (Punjabi), বাংলা (Bengali), ગુજરાતી (Gujarati), मराठी (Marathi), தமிழ் (Tamil), తెలుగు (Telugu), ಕನ್ನಡ (Kannada)."),
        ("100% Comprehensive Portal Coverage", "Translates all navigation, search cards, service descriptions, booking tracking steps, and administrative audit tables."),
        ("Session Persistence", "Language selection is automatically preserved across portal navigation using client-side localStorage."),
        ("Zero Digital Literacy Barrier", "Ensures migrant and vernacular-speaking artisans can operate the platform comfortably without English fluency.")
    ]
    for k, v in lang_points:
        p = tf.add_paragraph(); p.text = f"• {k}: "; p.font.size = Pt(10); p.font.bold = True; p.font.color.rgb = SAFFRON
        run = p.add_run(); run.text = v; run.font.bold = False; run.font.color.rgb = DARK_TEXT

    c_right9 = create_card(slide9, start_x + half_w + Inches(0.23), card_y, half_w, card_h)
    tb = slide9.shapes.add_textbox(start_x + half_w + Inches(0.48), card_y + Inches(0.2), half_w - Inches(0.5), card_h - Inches(0.4))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = "Sahakar AI Sahayak (सहकार मित्र)"; p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = NAVY_PRIMARY

    bot_points = [
        ("24x7 Conversational Support", "Instant natural language assistant embedded across all portals via floating widget (/api/ai/chat)."),
        ("Service & Rate Consultation", "Answers citizen queries regarding standard rates, booking processes, and emergency SOS services."),
        ("Artisan Onboarding Guide", "Guides prospective artisans through document uploading and trade guild registration steps."),
        ("Official Scheme Advisory", "Explains PMSBY accidental insurance cover and cooperative welfare fund allocations.")
    ]
    for k, v in bot_points:
        p = tf.add_paragraph(); p.text = f"• {k}: "; p.font.size = Pt(10); p.font.bold = True; p.font.color.rgb = GREEN
        run = p.add_run(); run.text = v; run.font.bold = False; run.font.color.rgb = DARK_TEXT

    # SLIDE 10
    slide10 = prs.slides.add_slide(blank_layout)
    add_chrome(slide10, "Social Security, PMSBY & Government Integration", "Institutional Linkages & Policy Alignment", 10)

    col_w = Inches(3.75)
    gov_cards = [
        ("1. Artisan Social Security", GREEN, GREEN_LIGHT, [
            "Pradhan Mantri Suraksha Bima Yojana (PMSBY): Direct integration providing ₹2,00,000 accidental death & disability insurance.",
            "Emergency Healthcare Grants: Dedicated cooperative welfare pool offering immediate hospital expense subsidies.",
            "Retirement Safety Pool: Collective long-term welfare accumulation for senior artisans.",
            "Workplace Safety Gear: Subsidized safety tooling and PPE equipment distribution."
        ]),
        ("2. Official Citizen Helpdesk", BLUE_ACCENT, BLUE_LIGHT, [
            "Toll-Free 24x7 Citizen Helpline: 1800-GZB-HELP / 1800-180-2525.",
            "Ghaziabad Federation Line: 0120-2828001 / +91-9811000001.",
            "Official Support Emails: support@sahakarghaziabad.in, helpdesk-coop@up.gov.in.",
            "Physical Headquarters: Sahakari Bhawan, Sector 10, Raj Nagar, Ghaziabad, UP - 201002."
        ]),
        ("3. Policy & Regulatory Alignment", NAVY_PRIMARY, RGBColor(241, 245, 249), [
            "Ministry of Cooperation, Govt. of India: Aligned with National Cooperative Policy & Database (cooperation.gov.in).",
            "Department of Cooperatives, Govt. of UP: Registered under the UP Cooperative Societies Act (upsdc.gov.in).",
            "Skill India & NSDC: Formal certification auditing aligned with National Skills Qualifications Framework (NSQF).",
            "District Administration Ghaziabad: Civic administrative recognition (ghaziabad.nic.in)."
        ])
    ]

    for i, (title, color, light_c, bullets) in enumerate(gov_cards):
        cx = start_x + (col_w + col_gap) * i
        card = create_card(slide10, cx, card_y, col_w, card_h, WHITE, color, Pt(1.5))
        strip = slide10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx + Inches(0.12), card_y + Inches(0.12), col_w - Inches(0.24), Inches(0.55))
        strip.fill.solid(); strip.fill.fore_color.rgb = light_c; strip.line.fill.background()
        stf = strip.text_frame; stf.margin_left = stf.margin_right = stf.margin_top = stf.margin_bottom = 0
        sp = stf.paragraphs[0]; sp.text = title; sp.font.size = Pt(11); sp.font.bold = True; sp.font.color.rgb = color; sp.alignment = PP_ALIGN.CENTER

        tb = slide10.shapes.add_textbox(cx + Inches(0.15), card_y + Inches(0.75), col_w - Inches(0.3), card_h - Inches(0.9))
        tf = tb.text_frame; tf.word_wrap = True
        for b in bullets:
            p = tf.add_paragraph(); p.text = f"• {b}"; p.font.size = Pt(9.5); p.font.color.rgb = DARK_TEXT

    # SLIDE 11
    slide11 = prs.slides.add_slide(blank_layout)
    add_chrome(slide11, "The 4 Integrated Web Portals", "User Interface & Experience", 11)

    portals_data = [
        ("1. Citizen Portal (/customer)", SAFFRON, [
            "Interactive trade picker & GPS map pin-drop.",
            "Dual booking modes: Instant on-demand or scheduled slots.",
            "Live 5-step status progression timeline tracker.",
            "Itemized digital invoice viewer & 5-star rating modal."
        ]),
        ("2. Artisan Portal (/worker)", GREEN, [
            "Online / Offline availability status toggle.",
            "Active dispatch card with En Route & Start Work buttons.",
            "Net earnings dashboard tracking daily take-home pay.",
            "Document upload modal for Skill India / ITI certificates."
        ]),
        ("3. Admin Dashboard (/admin)", BLUE_ACCENT, [
            "Live district GIS dispatch heatmap across Ghaziabad.",
            "Artisan verification queue with one-click document audit.",
            "Interactive 7-day AI demand forecasting charts.",
            "Official verifiable wage audit registry table."
        ]),
        ("4. Welcoming Homepage (/)", NAVY_PRIMARY, [
            "Official government emblem & tricolor header bar.",
            "Quick service search & locality dispatcher widget.",
            "Transparent cooperative vs corporate comparison matrix.",
            "24x7 floating AI Assistant (Sahakar Sahayak) integration."
        ])
    ]

    col_w = Inches(2.78); col_gap = Inches(0.2)
    for i, (title, color, bullets) in enumerate(portals_data):
        cx = start_x + (col_w + col_gap) * i
        card = create_card(slide11, cx, card_y, col_w, card_h, WHITE, color, Pt(1.5))
        strip = slide11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx + Inches(0.12), card_y + Inches(0.12), col_w - Inches(0.24), Inches(0.55))
        strip.fill.solid(); strip.fill.fore_color.rgb = color; strip.line.fill.background()
        stf = strip.text_frame; stf.margin_left = stf.margin_right = stf.margin_top = stf.margin_bottom = 0
        sp = stf.paragraphs[0]; sp.text = title; sp.font.size = Pt(11); sp.font.bold = True; sp.font.color.rgb = WHITE; sp.alignment = PP_ALIGN.CENTER

        tb = slide11.shapes.add_textbox(cx + Inches(0.15), card_y + Inches(0.75), col_w - Inches(0.3), card_h - Inches(0.9))
        tf = tb.text_frame; tf.word_wrap = True
        for b in bullets:
            p = tf.add_paragraph(); p.text = f"• {b}"; p.font.size = Pt(9.5); p.font.color.rgb = DARK_TEXT

    # SLIDE 12
    slide12 = prs.slides.add_slide(blank_layout)
    add_chrome(slide12, "Security Architecture & Data Privacy", "Robust Defensive Implementation", 12)

    half_w = Inches(5.75)
    c_left12 = create_card(slide12, start_x, card_y, half_w, card_h)
    tb = slide12.shapes.add_textbox(start_x + Inches(0.25), card_y + Inches(0.2), half_w - Inches(0.5), card_h - Inches(0.4))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = "Application Security Hardening"; p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = NAVY_PRIMARY

    sec_points = [
        ("SQL Injection Immunity", "Strict parameterization across all PostGIS spatial queries and SQLAlchemy ORM operations. Zero raw string concatenation."),
        ("Password Cryptography", "PBKDF2-HMAC-SHA256 password hashing with 100,000 iterations and unique 16-byte random salts. No plaintext passwords."),
        ("Secure File Upload Validation", "Strict extension whitelisting (.pdf, .jpg, .png, .webp) and UUID-based file path isolation preventing path traversal."),
        ("Cross-Site Scripting (XSS) Defense", "Jinja2 template auto-escaping and DOM-level textContent binding preventing client-side script injection.")
    ]
    for k, v in sec_points:
        p = tf.add_paragraph(); p.text = f"• {k}: "; p.font.size = Pt(10); p.font.bold = True; p.font.color.rgb = GREEN
        run = p.add_run(); run.text = v; run.font.bold = False; run.font.color.rgb = DARK_TEXT

    c_right12 = create_card(slide12, start_x + half_w + Inches(0.23), card_y, half_w, card_h)
    tb = slide12.shapes.add_textbox(start_x + half_w + Inches(0.48), card_y + Inches(0.2), half_w - Inches(0.5), card_h - Inches(0.4))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = "Verifiable Wage Audit Registry"; p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = NAVY_PRIMARY

    audit_points = [
        ("Mathematical Audit Chaining", "Every completed booking payout is chained cryptographically (prev_hash -> current_hash) to guarantee zero wage tampering."),
        ("Transparent Fund Allocation", "Guarantees mathematical proof of the 93% worker share, 5% platform operations fee, and 2% welfare contribution."),
        ("Cooperative Dispute Resolution", "Integrated citizen complaint registry with admin escalation and resolution notes."),
        ("Audited by Federation", "District Cooperative Registrar can audit the entire financial ledger with 100% data integrity.")
    ]
    for k, v in audit_points:
        p = tf.add_paragraph(); p.text = f"• {k}: "; p.font.size = Pt(10); p.font.bold = True; p.font.color.rgb = SAFFRON
        run = p.add_run(); run.text = v; run.font.bold = False; run.font.color.rgb = DARK_TEXT

    # SLIDE 13
    slide13 = prs.slides.add_slide(blank_layout)
    add_chrome(slide13, "Impact Analysis & Future Scaling Roadmap", "District Results & Strategic Vision", 13)

    col_w = Inches(3.75)
    roadmap_cards = [
        ("1. District Impact Metrics", GREEN, GREEN_LIGHT, [
            "1,250+ Verified Artisans Seeded across all major Ghaziabad residential sectors.",
            "45,000+ Completed Citizen Service Jobs modeled successfully.",
            "35%–45% Increase in Artisan Net Income under 93% direct wage retention.",
            "15–20 Min Average GPS Arrival Time for emergency and on-demand dispatches."
        ]),
        ("2. Phase 2: NCR Expansion", BLUE_ACCENT, BLUE_LIGHT, [
            "Regional Rollout: Scale across Noida, Greater Noida, Meerut, and Hapur.",
            "Block-Level Tooling Hubs: Establishing cooperative tool banks providing subsidized high-grade diagnostic tools.",
            "ONDC Network Integration: Onboarding SahakarConnect onto Open Network for Digital Commerce for interoperable booking.",
            "Women Cooperative Guilds: Specialized training for deep cleaning and home appliance maintenance."
        ]),
        ("3. Phase 3: National Blueprint", SAFFRON, SAFFRON_LIGHT, [
            "Offline Voice / IVR Booking: Accessible telephone dial-in booking for citizens without smartphones.",
            "IoT Emergency Triggers: Direct smart-meter and pipe-pressure sensor integration for automated leak/outage dispatch.",
            "State Cooperative Replicability: Open blueprint for adoption by Cooperative Departments across all Indian states.",
            "National Policy Benchmark: Setting the gold standard for platform cooperativism in India."
        ])
    ]

    for i, (title, color, light_c, bullets) in enumerate(roadmap_cards):
        cx = start_x + (col_w + col_gap) * i
        card = create_card(slide13, cx, card_y, col_w, card_h, WHITE, color, Pt(1.5))
        strip = slide13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx + Inches(0.12), card_y + Inches(0.12), col_w - Inches(0.24), Inches(0.55))
        strip.fill.solid(); strip.fill.fore_color.rgb = light_c; strip.line.fill.background()
        stf = strip.text_frame; stf.margin_left = stf.margin_right = stf.margin_top = stf.margin_bottom = 0
        sp = stf.paragraphs[0]; sp.text = title; sp.font.size = Pt(11); sp.font.bold = True; sp.font.color.rgb = color; sp.alignment = PP_ALIGN.CENTER

        tb = slide13.shapes.add_textbox(cx + Inches(0.15), card_y + Inches(0.75), col_w - Inches(0.3), card_h - Inches(0.9))
        tf = tb.text_frame; tf.word_wrap = True
        for b in bullets:
            p = tf.add_paragraph(); p.text = f"• {b}"; p.font.size = Pt(9.5); p.font.color.rgb = DARK_TEXT

    prs.save(output_path)
    print(f"✅ UHD 13-Slide Master Deck successfully generated at: {output_path}")

if __name__ == "__main__":
    build_uhd_deck()
