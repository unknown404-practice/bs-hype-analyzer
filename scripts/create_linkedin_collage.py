import os
from PIL import Image, ImageDraw, ImageFont, ImageOps
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"

FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
FONT_REGULAR = "C:/Windows/Fonts/segoeui.ttf"
FONT_MONO = "C:/Windows/Fonts/consola.ttf"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

def draw_badge(draw, text, x, y, bg_color, text_color, font, pad_x=18, pad_y=8, radius=8):
    bbox = font.getbbox(text)
    w = bbox[2] - bbox[0] + pad_x * 2
    h = bbox[3] - bbox[1] + pad_y * 2
    draw.rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=bg_color, outline=None)
    draw.text((x + pad_x, y + pad_y), text, font=font, fill=text_color)
    return w

def create_portrait_collage():
    WIDTH = 2400
    HEIGHT = 2800
    
    canvas = Image.new("RGB", (WIDTH, HEIGHT), color="#080c14")
    draw = ImageDraw.Draw(canvas)
    
    # Fonts
    f_title = get_font(FONT_BOLD, 72)
    f_subtitle = get_font(FONT_REGULAR, 34)
    f_badge = get_font(FONT_BOLD, 26)
    f_card_title = get_font(FONT_BOLD, 30)
    f_card_sub = get_font(FONT_REGULAR, 22)
    f_footer_bold = get_font(FONT_BOLD, 28)
    f_footer_mono = get_font(FONT_MONO, 26)
    
    # 1. Header Banner
    header_box = [60, 50, WIDTH - 60, 310]
    draw.rounded_rectangle(header_box, radius=20, fill="#0f172a", outline="#334155", width=2)
    
    # Title & Subtitle
    draw.text((100, 75), "AI-POWERED BS & HYPE ANALYZER", font=f_title, fill="#38bdf8")
    draw.text((100, 165), "Quantifying Media Sensationalism & Mapping Circular Echo Chambers · 100% Offline", font=f_subtitle, fill="#94a3b8")
    
    # Badges Row
    badge_x = 100
    badge_y = 230
    badge_x += draw_badge(draw, "100% Local Inference", badge_x, badge_y, "#064e3b", "#34d399", f_badge) + 20
    badge_x += draw_badge(draw, "Multi-Modal (RSS + Whisper STT)", badge_x, badge_y, "#0c4a6e", "#38bdf8", f_badge) + 20
    badge_x += draw_badge(draw, "NetworkX Graph Theory", badge_x, badge_y, "#581c87", "#c084fc", f_badge) + 20
    badge_x += draw_badge(draw, "22/22 Tests Passing", badge_x, badge_y, "#881337", "#fb7185", f_badge) + 20
    draw_badge(draw, "Open Source MIT", badge_x, badge_y, "#78350f", "#fbbf24", f_badge)
    
    # 2. 2x2 Image Panels Grid
    grid_top = 340
    grid_bottom = HEIGHT - 160
    grid_w = (WIDTH - 120 - 40) // 2
    grid_h = (grid_bottom - grid_top - 40) // 2
    
    panels = [
        {
            "img_path": FIGURES_DIR / "dashboard_preview.png",
            "title": "01 · REAL-TIME EXECUTIVE DASHBOARD",
            "sub": "Interactive KPI cards, 5-factor radar diagnostics & threshold filtering",
            "tag_color": "#38bdf8",
            "row": 0, "col": 0
        },
        {
            "img_path": FIGURES_DIR / "echo_chamber_labeled.png",
            "title": "02 · NARRATIVE ECHO-CHAMBER NETWORK",
            "sub": "Cross-outlet narrative co-amplification, modularity clusters & PageRank bridges",
            "tag_color": "#c084fc",
            "row": 0, "col": 1
        },
        {
            "img_path": ASSETS_DIR / "architecture.png",
            "title": "03 · 4-TIER DECOUPLED PIPELINE",
            "sub": "Decoupled ingestion, mathematical NLP scoring, graph analytics & desktop UI",
            "tag_color": "#34d399",
            "row": 1, "col": 0
        },
        {
            "img_path": FIGURES_DIR / "outlet_comparison.png",
            "title": "04 · MEDIA SENSATIONALISM BENCHMARK",
            "sub": "10 media outlets ranked by empirical hype score vs. critical alert threshold",
            "tag_color": "#fb7185",
            "row": 1, "col": 1
        }
    ]
    
    for p in panels:
        px = 60 + p["col"] * (grid_w + 40)
        py = grid_top + p["row"] * (grid_h + 40)
        
        # Outer Card Container
        draw.rounded_rectangle([px, py, px + grid_w, py + grid_h], radius=16, fill="#0f172a", outline="#1e293b", width=2)
        
        # Card Header
        draw.text((px + 24, py + 22), p["title"], font=f_card_title, fill=p["tag_color"])
        draw.text((px + 24, py + 62), p["sub"], font=f_card_sub, fill="#64748b")
        
        # Image Area
        img_area_top = py + 105
        img_area_w = grid_w - 48
        img_area_h = grid_h - 125
        
        if p["img_path"].exists():
            im = Image.open(p["img_path"]).convert("RGBA")
            # Aspect-fit image
            im_ratio = im.width / im.height
            area_ratio = img_area_w / img_area_h
            
            if im_ratio > area_ratio:
                new_w = img_area_w
                new_h = int(img_area_w / im_ratio)
            else:
                new_h = img_area_h
                new_w = int(img_area_h * im_ratio)
                
            im_resized = im.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            # Center inside image area
            offset_x = px + 24 + (img_area_w - new_w) // 2
            offset_y = img_area_top + (img_area_h - new_h) // 2
            
            # Subtle background for letterbox
            draw.rounded_rectangle([px + 24, img_area_top, px + 24 + img_area_w, img_area_top + img_area_h],
                                   radius=10, fill="#080c14", outline="#1e293b", width=1)
            
            canvas.paste(im_resized, (offset_x, offset_y), im_resized)
            
    # 3. Footer Bar
    footer_y = HEIGHT - 130
    draw.rounded_rectangle([60, footer_y, WIDTH - 60, HEIGHT - 40], radius=16, fill="#0f172a", outline="#334155", width=2)
    draw.text((100, footer_y + 28), "Engineered by Ranadeep Saha · Member, Google Developer Group", font=f_footer_bold, fill="#f8fafc")
    draw.text((WIDTH - 760, footer_y + 30), "github.com/unknown404-practice/bs-hype-analyzer", font=f_footer_mono, fill="#38bdf8")
    
    out_file = ASSETS_DIR / "linkedin_showcase_portrait.png"
    canvas.save(out_file, quality=95)
    print(f"Saved portrait collage: {out_file} ({out_file.stat().st_size // 1024} KB)")

def create_landscape_collage():
    WIDTH = 2560
    HEIGHT = 1440
    
    canvas = Image.new("RGB", (WIDTH, HEIGHT), color="#080c14")
    draw = ImageDraw.Draw(canvas)
    
    f_title = get_font(FONT_BOLD, 54)
    f_subtitle = get_font(FONT_REGULAR, 26)
    f_badge = get_font(FONT_BOLD, 20)
    f_card_title = get_font(FONT_BOLD, 22)
    f_footer_bold = get_font(FONT_BOLD, 22)
    f_footer_mono = get_font(FONT_MONO, 20)
    
    # Top Header
    draw.rounded_rectangle([50, 40, WIDTH - 50, 200], radius=16, fill="#0f172a", outline="#334155", width=2)
    draw.text((80, 58), "AI-POWERED BS & HYPE ANALYZER", font=f_title, fill="#38bdf8")
    draw.text((80, 130), "Quantifying Media Sensationalism & Mapping Narrative Echo Chambers · 100% Local Inference", font=f_subtitle, fill="#94a3b8")
    
    bx = WIDTH - 1280
    by = 75
    bx += draw_badge(draw, "100% Offline", bx, by, "#064e3b", "#34d399", f_badge, pad_x=14, pad_y=6) + 15
    bx += draw_badge(draw, "Multi-Modal NLP", bx, by, "#0c4a6e", "#38bdf8", f_badge, pad_x=14, pad_y=6) + 15
    bx += draw_badge(draw, "Graph Theory", bx, by, "#581c87", "#c084fc", f_badge, pad_x=14, pad_y=6) + 15
    draw_badge(draw, "22/22 Tests Pass", bx, by, "#881337", "#fb7185", f_badge, pad_x=14, pad_y=6)
    
    # 4 Columns Grid
    grid_top = 230
    grid_bottom = HEIGHT - 100
    col_w = (WIDTH - 100 - 3 * 30) // 4
    col_h = grid_bottom - grid_top
    
    panels = [
        (FIGURES_DIR / "dashboard_preview.png", "01 · EXECUTIVE DASHBOARD", "#38bdf8"),
        (FIGURES_DIR / "echo_chamber_labeled.png", "02 · ECHO CHAMBER GRAPH", "#c084fc"),
        (ASSETS_DIR / "architecture.png", "03 · SYSTEM ARCHITECTURE", "#34d399"),
        (FIGURES_DIR / "outlet_comparison.png", "04 · OUTLET HYPE RANKING", "#fb7185"),
    ]
    
    for idx, (path, title, color) in enumerate(panels):
        px = 50 + idx * (col_w + 30)
        py = grid_top
        
        draw.rounded_rectangle([px, py, px + col_w, py + col_h], radius=14, fill="#0f172a", outline="#1e293b", width=2)
        draw.text((px + 18, py + 16), title, font=f_card_title, fill=color)
        
        img_top = py + 60
        img_w = col_w - 36
        img_h = col_h - 78
        
        if path.exists():
            im = Image.open(path).convert("RGBA")
            im_ratio = im.width / im.height
            area_ratio = img_w / img_h
            
            if im_ratio > area_ratio:
                nw = img_w
                nh = int(img_w / im_ratio)
            else:
                nh = img_h
                nw = int(img_h * im_ratio)
                
            im_resized = im.resize((nw, nh), Image.Resampling.LANCZOS)
            ox = px + 18 + (img_w - nw) // 2
            oy = img_top + (img_h - nh) // 2
            
            draw.rounded_rectangle([px + 18, img_top, px + 18 + img_w, img_top + img_h],
                                   radius=8, fill="#080c14", outline="#1e293b", width=1)
            canvas.paste(im_resized, (ox, oy), im_resized)
            
    # Footer
    footer_y = HEIGHT - 80
    draw.rounded_rectangle([50, footer_y, WIDTH - 50, HEIGHT - 20], radius=12, fill="#0f172a", outline="#334155", width=1)
    draw.text((80, footer_y + 16), "Ranadeep Saha · Google Developer Group Member", font=f_footer_bold, fill="#f8fafc")
    draw.text((WIDTH - 640, footer_y + 18), "github.com/unknown404-practice/bs-hype-analyzer", font=f_footer_mono, fill="#38bdf8")
    
    out_file = ASSETS_DIR / "linkedin_showcase_landscape.png"
    canvas.save(out_file, quality=95)
    print(f"Saved landscape collage: {out_file} ({out_file.stat().st_size // 1024} KB)")

if __name__ == "__main__":
    create_portrait_collage()
    create_landscape_collage()
