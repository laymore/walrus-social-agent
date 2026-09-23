import os
import sys
import subprocess
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TIKTOK_DIR = r"c:\Users\admin\Desktop\MK\tiktok_automation"
OUT_SLIDES_DIR = os.path.join(BASE_DIR, "demo_slides")
os.makedirs(OUT_SLIDES_DIR, exist_ok=True)

OUT_VIDEO_PATH = os.path.join(BASE_DIR, "walrus_social_agent_demo.mp4")
DESKTOP_VIDEO_PATH = r"c:\Users\admin\Desktop\walrus_social_agent_demo.mp4"
AUDIO_PATH = os.path.join(TIKTOK_DIR, "brand_audio_huyenminh.mp3")

FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
FONT_REG = "C:/Windows/Fonts/segoeui.ttf"
FONT_ARIAL_BOLD = "C:/Windows/Fonts/arialbd.ttf"

def get_font(size, bold=False):
    f_path = FONT_BOLD if bold else FONT_REG
    try:
        return ImageFont.truetype(f_path, size)
    except Exception:
        return ImageFont.load_default()

def create_base_canvas(title, subtitle=""):
    img = Image.new("RGB", (1920, 1080), color="#090d16")
    draw = ImageDraw.Draw(img)

    # Top Header Bar
    draw.rectangle([(0, 0), (1920, 110)], fill="#0f172a")
    draw.line([(0, 110), (1920, 110)], fill="#1e293b", width=3)

    # Gradient-like banner accent
    draw.rectangle([(0, 0), (8, 110)], fill="#00C4B4")

    # Brand Title
    f_head = get_font(38, bold=True)
    draw.text((40, 22), "WALRUS SOCIAL AGENT", fill="#00C4B4", font=f_head)

    f_subhead = get_font(22, bold=False)
    draw.text((40, 68), "Walrus Sessions 8 Hackathon Entry · Autonomous AI with Decentralized Memory", fill="#94a3b8", font=f_subhead)

    # Top-right Badges
    f_badge = get_font(18, bold=True)
    draw.rounded_rectangle([(1520, 32), (1880, 78)], radius=8, fill="#1e293b", outline="#38bdf8", width=2)
    draw.text((1545, 43), "SUI & WALRUS MAINNET", fill="#38bdf8", font=f_badge)

    # Slide Title in Body
    f_title = get_font(32, bold=True)
    draw.text((80, 140), title, fill="#f8fafc", font=f_title)

    if subtitle:
        f_sub = get_font(20, bold=False)
        draw.text((80, 185), subtitle, fill="#64748b", font=f_sub)

    # Bottom Footer Bar
    draw.rectangle([(0, 1020), (1920, 1080)], fill="#0a0f1d")
    draw.line([(0, 1020), (1920, 1020)], fill="#1e293b", width=2)

    f_foot = get_font(18, bold=False)
    draw.text((40, 1038), "Repository: github.com/laymore/walrus-social-agent   |   Dev Wallet: 0xfbf7...115f", fill="#64748b", font=f_foot)
    draw.text((1620, 1038), "Track: Best Chatbot ($500 WAL)", fill="#00C4B4", font=f_foot)

    return img, draw

def fit_image(src_path, max_w, max_h):
    if not os.path.exists(src_path):
        return None
    im = Image.open(src_path)
    im.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
    return im

def build_slide_1():
    img = Image.new("RGB", (1920, 1080), color="#070a13")
    draw = ImageDraw.Draw(img)

    # Glow effect
    draw.ellipse([(660, 180), (1260, 780)], fill="#0d233a")
    draw.ellipse([(760, 280), (1160, 680)], fill="#0e344d")

    f_huge = get_font(72, bold=True)
    draw.text((960, 360), "WALRUS SOCIAL AGENT", fill="#00e5ff", font=f_huge, anchor="mm")

    f_lead = get_font(34, bold=True)
    draw.text((960, 440), "Autonomous AI Counselor with Decentralized Long-Term Memory", fill="#ffffff", font=f_lead, anchor="mm")

    f_desc = get_font(24, bold=False)
    draw.text((960, 500), "Built for Walrus Sessions 8 Hackathon · Deployed on Sui & Walrus Mainnet", fill="#94a3b8", font=f_desc, anchor="mm")

    # Feature Pills
    pills = [
        "🧠 Zero Amnesia",
        "⚡ 0.237ms Dual-Layer Cache",
        "🔐 SEAL Encryption",
        "🌐 TikTok Studio Live 24/7",
        "✨ Google Antigravity Agent"
    ]
    x_start = 220
    for p in pills:
        draw.rounded_rectangle([(x_start, 620), (x_start + 280, 680)], radius=30, fill="#0f172a", outline="#00C4B4", width=2)
        f_pill = get_font(18, bold=True)
        draw.text((x_start + 140, 650), p, fill="#f8fafc", font=f_pill, anchor="mm")
        x_start += 300

    f_cred = get_font(20, bold=False)
    draw.text((960, 780), "Live Target: @aihuyenminh (TikTok)   ·   Author: Huyen Minh Team (silver)", fill="#38bdf8", font=f_cred, anchor="mm")

    out_file = os.path.join(OUT_SLIDES_DIR, "slide_01.png")
    img.save(out_file)
    print("Saved slide 1")

def build_slide_2():
    img, draw = create_base_canvas(
        "ARCHITECTURAL BREAKTHROUGH: DUAL-LAYER RESILIENT MEMORY",
        "Combining permanent decentralized On-Chain immutability with 0.237ms ultra-fast local responsiveness"
    )

    # Left Box: Problem
    draw.rounded_rectangle([(80, 240), (920, 960)], radius=16, fill="#0f172a", outline="#ef4444", width=2)
    f_box_h = get_font(28, bold=True)
    draw.text((120, 280), "❌ The Amnesiac Social Bot Problem", fill="#f87171", font=f_box_h)

    f_b = get_font(22, bold=False)
    points_bad = [
        "• Traditional chatbots suffer from total session amnesia.",
        "• User comments on Video #1 with their birth details (BaZi/Zi Wei).",
        "• 3 days later on Video #2, the bot forgets and re-asks everything.",
        "• Centralized SQL/Firebase databases create data silos and privacy risks.",
        "• Direct on-chain writes can take ~120s during relayer throttling,",
        "  which crashes browser automation (Playwright UI timeout)."
    ]
    y = 360
    for pt in points_bad:
        draw.text((120, y), pt, fill="#cbd5e1", font=f_b)
        y += 70

    # Right Box: Solution
    draw.rounded_rectangle([(1000, 240), (1840, 960)], radius=16, fill="#0f172a", outline="#10b981", width=2)
    draw.text((1040, 280), "✅ Walrus-First Dual-Layer Solution", fill="#34d399", font=f_box_h)

    points_good = [
        "• Layer 1 (Walrus Primary): Source of Truth on Sui Mainnet.",
        "• Layer 2 (Local Cache): Instant fallback speed of 0.237 ms.",
        "• 500,000x Speedup prevents browser UI freezing & timeouts.",
        "• Async Worker Thread commits memory blobs in background.",
        "• SEAL Encrypted: Private, user-owned, cryptographically secure.",
        "• Cross-Platform: Same memory shared across TikTok, Web & Bots!"
    ]
    y = 360
    for pt in points_good:
        draw.text((1040, y), pt, fill="#e2e8f0", font=f_b)
        y += 70

    out_file = os.path.join(OUT_SLIDES_DIR, "slide_02.png")
    img.save(out_file)
    print("Saved slide 2")

def build_slide_3():
    img, draw = create_base_canvas(
        "LIVE PRODUCTION PROOF: TIKTOK STUDIO AUTOMATION",
        "Real-time comment crawler & counselor (@aihuyenminh) operating 24/7 with 100% reply success rate"
    )

    shot_path = os.path.join(TIKTOK_DIR, "all_comments_crawled.png")
    im = fit_image(shot_path, 1150, 720)
    if im:
        draw.rounded_rectangle([(70, 230), (70 + im.width + 20, 230 + im.height + 20)], radius=12, fill="#1e293b", outline="#38bdf8", width=2)
        img.paste(im, (80, 240))

    # Right Side Callout Card
    draw.rounded_rectangle([(1280, 230), (1840, 950)], radius=16, fill="#0f172a", outline="#00C4B4", width=2)
    f_card_h = get_font(26, bold=True)
    draw.text((1310, 270), "📊 Live Channel Metrics", fill="#00C4B4", font=f_card_h)

    f_card_b = get_font(20, bold=False)
    metrics = [
        ("Monitored Users:", "25 Customers"),
        ("Walrus Synced:", "24 / 25 Blobs On-Chain"),
        ("Bot Reply Rate:", "100% Automated"),
        ("Active Days:", "> 10 Days in Prod"),
        ("MCP Handshake:", "0.145 seconds"),
        ("Local Fallback:", "0.237 ms (0.0002s)"),
        ("Agent Engine:", "Google Antigravity Agent")
    ]
    y = 340
    for label, val in metrics:
        draw.text((1310, y), label, fill="#94a3b8", font=f_card_b)
        f_val = get_font(22, bold=True)
        draw.text((1310, y + 28), val, fill="#f8fafc", font=f_val)
        y += 80

    out_file = os.path.join(OUT_SLIDES_DIR, "slide_03.png")
    img.save(out_file)
    print("Saved slide 3")

def build_slide_4():
    img, draw = create_base_canvas(
        "CASE STUDIES: VERIFIABLE BEFORE & AFTER CONVERSATIONS",
        "Demonstrating deep contextual continuity across separate video posts without repeating questions"
    )

    im1 = fit_image(os.path.join(TIKTOK_DIR, "expanded_reply.png"), 840, 520)
    im2 = fit_image(os.path.join(TIKTOK_DIR, "after_successful_reply.png"), 840, 520)

    if im1:
        draw.rounded_rectangle([(80, 240), (80 + im1.width + 10, 240 + im1.height + 10)], radius=8, fill="#1e293b", outline="#38bdf8", width=2)
        img.paste(im1, (85, 245))
        f_cap = get_font(20, bold=True)
        draw.text((90, 780), "Case #1: User @quangnguyen0301 (Born 1995 Ất Hợi) — Multi-turn recall", fill="#38bdf8", font=f_cap)

    if im2:
        draw.rounded_rectangle([(980, 240), (980 + im2.width + 10, 240 + im2.height + 10)], radius=8, fill="#1e293b", outline="#10b981", width=2)
        img.paste(im2, (985, 245))
        draw.text((990, 780), "Case #2: User @tiniluong & @cuongid111 (1999 Kỷ Mão) — Marriage & Fortune advice", fill="#34d399", font=f_cap)

    # Bottom summary box
    draw.rounded_rectangle([(80, 830), (1840, 960)], radius=12, fill="#0f172a", outline="#64748b", width=1)
    f_sum = get_font(22, bold=False)
    draw.text((110, 860), "💡 The Difference: When @cuongid111 returns, the AI recalls their 1999 birth year & 2027 Marriage luck instantly.", fill="#f1f5f9", font=f_sum)
    draw.text((110, 905), "Zero repetition. Zero cognitive friction. Pure decentralized empathy powered by Walrus Memory!", fill="#00C4B4", font=f_sum)

    out_file = os.path.join(OUT_SLIDES_DIR, "slide_04.png")
    img.save(out_file)
    print("Saved slide 4")

def build_slide_5():
    img, draw = create_base_canvas(
        "ON-CHAIN VERIFICATION: WALRUSCAN & SUI MAINNET",
        "Cryptographically certified blobs stored on Walrus decentralized storage (Namespace: huyenminh_social_crm)"
    )

    shot_path = os.path.join(TIKTOK_DIR, "demo_screenshots", "walruscan_verified_blob.png")
    im = fit_image(shot_path, 1150, 720)
    if im:
        draw.rounded_rectangle([(70, 230), (70 + im.width + 20, 230 + im.height + 20)], radius=12, fill="#1e293b", outline="#00C4B4", width=2)
        img.paste(im, (80, 240))

    # Right Side Callout Card
    draw.rounded_rectangle([(1280, 230), (1840, 950)], radius=16, fill="#0f172a", outline="#38bdf8", width=2)
    f_card_h = get_font(26, bold=True)
    draw.text((1310, 270), "🔍 On-Chain Proofs", fill="#38bdf8", font=f_card_h)

    f_card_b = get_font(20, bold=False)
    proofs = [
        ("Blob ID:", "PEzXmHsOMC9vyL7..."),
        ("SEAL Encryption:", "seal_encrypt_fence"),
        ("Blob Status:", "certify_blob (Verified)"),
        ("Network:", "Walrus Mainnet"),
        ("Account Object:", "0xb893...c4e6"),
        ("Package ID:", "0xcee7...24c6"),
        ("Total Verified Blobs:", "10+ On-Chain Blobs")
    ]
    y = 340
    for label, val in proofs:
        draw.text((1310, y), label, fill="#94a3b8", font=f_card_b)
        f_val = get_font(22, bold=True)
        draw.text((1310, y + 28), val, fill="#f8fafc", font=f_val)
        y += 80

    out_file = os.path.join(OUT_SLIDES_DIR, "slide_05.png")
    img.save(out_file)
    print("Saved slide 5")

def build_slide_6():
    img, draw = create_base_canvas(
        "DECENTRALIZED TECHNICAL ARTICLE PUBLISHED ON INKRAY",
        "Official technical writeup & Before/After case study published directly via Inkray MCP on Sui Mainnet"
    )

    shot_path = os.path.join(TIKTOK_DIR, "demo_screenshots", "inkray_published_article.png")
    im = fit_image(shot_path, 1150, 720)
    if im:
        draw.rounded_rectangle([(70, 230), (70 + im.width + 20, 230 + im.height + 20)], radius=12, fill="#1e293b", outline="#a855f7", width=2)
        img.paste(im, (80, 240))

    # Right Side Callout Card
    draw.rounded_rectangle([(1280, 230), (1840, 950)], radius=16, fill="#0f172a", outline="#a855f7", width=2)
    f_card_h = get_font(26, bold=True)
    draw.text((1310, 270), "📰 Inkray Publication", fill="#c084fc", font=f_card_h)

    f_card_b = get_font(20, bold=False)
    article_info = [
        ("Platform:", "Inkray (Sui Web3 Media)"),
        ("Author Publication:", "silver (@chats.sui)"),
        ("Sui Mainnet Tx:", "8i6NKcsvh6Uwi..."),
        ("Article Object ID:", "0x98cf55c49e..."),
        ("Target Track:", "Best Article ($100 WAL)"),
        ("Bug Bounty Track:", "5 Bugs Reported ($500)"),
        ("Submission Form:", "DeepSurge (deepsurge.xyz)")
    ]
    y = 340
    for label, val in article_info:
        draw.text((1310, y), label, fill="#94a3b8", font=f_card_b)
        f_val = get_font(22, bold=True)
        draw.text((1310, y + 28), val, fill="#f8fafc", font=f_val)
        y += 80

    out_file = os.path.join(OUT_SLIDES_DIR, "slide_06.png")
    img.save(out_file)
    print("Saved slide 6")

def main():
    print("🚀 Bắt đầu tạo 6 Slides Full HD 1080p...")
    build_slide_1()
    build_slide_2()
    build_slide_3()
    build_slide_4()
    build_slide_5()
    build_slide_6()
    print("✅ Đã hoàn tất tạo 6 Slide ảnh!")

    # Tạo tệp input list cho ffmpeg concat
    list_file = os.path.join(OUT_SLIDES_DIR, "slides.txt")
    with open(list_file, "w", encoding="utf-8") as f:
        for i in range(1, 7):
            slide_name = f"slide_{i:02d}.png"
            f.write(f"file '{slide_name}'\n")
            f.write("duration 6\n")
        f.write(f"file 'slide_06.png'\n")

    print("🎬 Đang render video MP4 bằng FFmpeg...")
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", list_file,
        "-stream_loop", "-1", "-i", AUDIO_PATH,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
        "-c:a", "aac", "-b:a", "192k",
        "-t", "36",
        "-af", "afade=t=out:st=33:d=3",
        OUT_VIDEO_PATH
    ]

    subprocess.run(cmd, check=True)
    print(f"🎉 Đã xuất video tại: {OUT_VIDEO_PATH}")

    # Copy ra Desktop
    import shutil
    shutil.copy(OUT_VIDEO_PATH, DESKTOP_VIDEO_PATH)
    print(f"🎉 Đã sao chép video ra Desktop: {DESKTOP_VIDEO_PATH}")

if __name__ == "__main__":
    main()
