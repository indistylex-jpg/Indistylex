# Indistylex Launch Promo Videos

Professional **Coming Soon** and **Launch Date** videos for **July 10, 2026 (Friday)**.

Brand colors: Black `#1A1A1A` · Gold `#C9A94E` · White  
Fonts: Playfair Display + Inter (matching website)

---

## Generated Videos

All files are in `output/`:

| File | Format | Use for |
|------|--------|---------|
| `coming-soon-reel.mp4` | 1080×1920 (9:16) | Instagram Reels, Stories, WhatsApp Status |
| `coming-soon-square.mp4` | 1080×1080 (1:1) | Instagram/Facebook feed post |
| `coming-soon-landscape.mp4` | 1920×1080 (16:9) | YouTube, website banner, Facebook cover |
| `launch-date-reel.mp4` | 1080×1920 (9:16) | Launch countdown Reels & Stories |
| `launch-date-square.mp4` | 1080×1080 (1:1) | Launch announcement feed post |
| `launch-date-landscape.mp4` | 1920×1080 (16:9) | Website hero, YouTube, ads |

- **Duration:** 8 seconds each
- **Style:** AI-generated gold/black backgrounds + animated brand text, zoom, shimmer

---

## Suggested Posting Schedule

| When | Video | Caption idea |
|------|-------|--------------|
| **Now → July 9** | `coming-soon-reel.mp4` | "Something beautiful is on the way… 👶✨ Premium kids fashion drops soon. #Indistylex #ComingSoon" |
| **July 1** | `launch-date-square.mp4` | "Mark your calendar! 📅 We launch **July 10, 2026**. Style that speaks, quality that lasts. #Indistylex" |
| **July 7–9** | `launch-date-reel.mp4` | "3 days to go! 🚀 July 10 — indistylex.com goes live. Turn on post notifications!" |
| **July 10 (launch day)** | `launch-date-reel.mp4` + `launch-date-square.mp4` | "We're LIVE! 🎉 Shop premium kids fashion at indistylex.com" |

---

## Regenerate Videos

```bash
cd /home/shivam/work/Indistylex
python3 -m venv .video-venv          # first time only
.video-venv/bin/pip install imageio imageio-ffmpeg pillow numpy
.video-venv/bin/python digital-marketing-assets/videos/generate_launch_videos.py
```

To change the launch date, edit `render_launch_frame()` in `generate_launch_videos.py`.

---

## Source Assets

- AI backgrounds: `coming-soon-bg-*.png`, `launch-date-bg-*.png`
- Fonts: `fonts/PlayfairDisplay.ttf`, `fonts/Inter.ttf`
- Generator script: `generate_launch_videos.py`
