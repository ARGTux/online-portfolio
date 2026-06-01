"""
Portfolio Showcase — Public Viewer
===================================
The public-facing side of the portfolio. No login required.
Visitors can browse projects, filter by tags/status,
view details, and download attachments.
"""

import streamlit as st
import json
import os
import base64
from pathlib import Path
from datetime import datetime

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Portfolio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Paths ───────────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent
DATA_FILE   = BASE_DIR / "data" / "projects.json"
CONFIG_FILE = BASE_DIR / "data" / "config.json"
UPLOADS_DIR = BASE_DIR / "data" / "uploads"


# ─── Data Helpers ─────────────────────────────────────────────────────────────
def load_projects() -> list[dict]:
    if DATA_FILE.exists():
        with open(DATA_FILE, encoding="utf-8") as f:
            data = json.load(f)
        return sorted(data, key=lambda x: x.get("order", 999))
    return []


def load_config() -> dict:
    defaults = {
        "name": "Your Name",
        "tagline": "Developer & builder. Passionate about great software.",
        "availability_badge": "Open to Opportunities",
        "social_links": [],
    }
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, encoding="utf-8") as f:
            loaded = json.load(f)
        defaults.update(loaded)
    return defaults


def get_project(projects: list[dict], pid: str) -> dict | None:
    return next((p for p in projects if p["id"] == pid), None)


def img_to_b64(path: str | Path) -> str | None:
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return None


# ─── CSS ─────────────────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ── Reset & base ── */
    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container {
        padding: 48px 32px !important;
        max-width: 1250px !important;
        margin: 0 auto !important;
    }

    /* ── Hero ── */
    .hero-wrap {
        background: linear-gradient(145deg, #07070f 0%, #0f0f1e 45%, #0a0a14 100%);
        padding: 64px 48px 52px;
        border: 1px solid rgba(124,58,237,0.18);
        border-radius: 24px;
        position: relative;
        overflow: hidden;
    }
    .hero-wrap::before {
        content: '';
        position: absolute;
        top: -120px; right: -80px;
        width: 560px; height: 560px;
        background: radial-gradient(circle, rgba(124,58,237,0.12) 0%, transparent 65%);
        border-radius: 50%;
        pointer-events: none;
    }
    .hero-wrap::after {
        content: '';
        position: absolute;
        bottom: -60px; left: 200px;
        width: 300px; height: 300px;
        background: radial-gradient(circle, rgba(59,130,246,0.07) 0%, transparent 65%);
        border-radius: 50%;
        pointer-events: none;
    }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(124,58,237,0.12);
        border: 1px solid rgba(124,58,237,0.35);
        color: #c4b5fd;
        padding: 5px 14px;
        border-radius: 99px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        margin-bottom: 22px;
    }
    .hero-badge::before { content: '◉'; color: #a78bfa; font-size: 0.6rem; }
    .hero-title {
        font-size: clamp(2.4rem, 5vw, 3.8rem);
        font-weight: 900;
        line-height: 1.08;
        margin: 0 0 18px;
        background: linear-gradient(135deg, #fff 0%, #c4b5fd 55%, #93c5fd 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .hero-sub {
        font-size: 1.05rem;
        color: #94a3b8;
        max-width: 580px;
        line-height: 1.75;
        margin-bottom: 36px;
        font-weight: 400;
    }
    .social-row { display: flex; gap: 10px; flex-wrap: wrap; }
    .social-btn {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.1);
        color: #cbd5e1 !important;
        padding: 9px 18px;
        border-radius: 10px;
        text-decoration: none !important;
        font-size: 0.83rem;
        font-weight: 500;
        transition: all 0.22s ease;
    }
    .social-btn:hover {
        background: rgba(124,58,237,0.18);
        border-color: rgba(124,58,237,0.45);
        color: #c4b5fd !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(124,58,237,0.2);
    }

    /* ── Stats strip ── */
    .stats-strip {
        display: flex;
        align-items: center;
        gap: 0;
        background: #111119;
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 18px;
        padding: 0 40px;
        margin-top: 24px;
        margin-bottom: 24px;
    }
    .stat-cell {
        padding: 20px 40px 20px 0;
        border-right: 1px solid rgba(255,255,255,0.06);
        margin-right: 40px;
    }
    .stat-cell:last-child { border-right: none; }
    .stat-val {
        font-size: 1.9rem;
        font-weight: 800;
        background: linear-gradient(135deg, #a78bfa, #60a5fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1;
    }
    .stat-lbl {
        font-size: 0.68rem;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-top: 4px;
        font-weight: 500;
    }

    /* ── Filter bar ── */
    .filter-bar {
        padding: 24px 0 12px;
        background: transparent;
    }
    .section-heading {
        font-size: 1.6rem;
        font-weight: 800;
        color: #f1f5f9;
        margin-bottom: 4px;
    }
    .section-sub {
        font-size: 0.85rem;
        color: #4b5563;
        margin-bottom: 24px;
    }

    /* ── Project Grid ── */
    .grid-wrap { padding: 16px 0 80px; background: transparent; }

    /* ── Card ── */
    .pcard {
        background: linear-gradient(145deg, #141420, #111118);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 18px;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 24px;
    }
    .pcard:hover {
        border-color: rgba(124,58,237,0.38);
        transform: translateY(-5px);
        box-shadow: 0 24px 50px rgba(0,0,0,0.5), 0 0 0 1px rgba(124,58,237,0.18), 0 0 40px rgba(124,58,237,0.06);
    }
    .pcard-img {
        width: 100%;
        height: 190px;
        object-fit: cover;
        display: block;
    }
    .pcard-placeholder {
        width: 100%;
        height: 190px;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 3.5rem;
    }
    .pcard-body { padding: 22px; }
    .pcard-top {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        margin-bottom: 10px;
    }
    .pcard-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #f1f5f9;
        line-height: 1.3;
        flex: 1;
        margin-right: 10px;
    }
    .pcard-desc {
        font-size: 0.82rem;
        color: #94a3b8;
        line-height: 1.65;
        margin-bottom: 16px;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    .tag-row { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 18px; }
    .tag {
        padding: 3px 10px;
        border-radius: 99px;
        font-size: 0.69rem;
        font-weight: 600;
        letter-spacing: 0.3px;
    }
    .tag-purple { background: rgba(124,58,237,0.12); border: 1px solid rgba(124,58,237,0.28); color: #c4b5fd; }
    .tag-blue   { background: rgba(59,130,246,0.12); border: 1px solid rgba(59,130,246,0.28); color: #93c5fd; }
    .tag-teal   { background: rgba(20,184,166,0.12); border: 1px solid rgba(20,184,166,0.28); color: #5eead4; }
    .tag-rose   { background: rgba(244,63,94,0.12);  border: 1px solid rgba(244,63,94,0.28);  color: #fda4af; }
    .tag-amber  { background: rgba(245,158,11,0.12); border: 1px solid rgba(245,158,11,0.28); color: #fcd34d; }

    .status-pill {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 99px;
        font-size: 0.67rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        white-space: nowrap;
    }
    .status-live     { background: rgba(16,185,129,0.12); border: 1px solid rgba(16,185,129,0.3);  color: #34d399; }
    .status-wip      { background: rgba(245,158,11,0.12); border: 1px solid rgba(245,158,11,0.3);  color: #fbbf24; }
    .status-archived { background: rgba(100,116,139,0.12);border: 1px solid rgba(100,116,139,0.3); color: #94a3b8; }

    .link-row { display: flex; gap: 8px; }
    .plink {
        flex: 1;
        text-align: center;
        padding: 8px 14px;
        border-radius: 9px;
        text-decoration: none !important;
        font-size: 0.78rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .plink-demo {
        background: rgba(124,58,237,0.14);
        border: 1px solid rgba(124,58,237,0.32);
        color: #c4b5fd !important;
    }
    .plink-demo:hover { background: rgba(124,58,237,0.28); transform: translateY(-1px); }
    .plink-repo {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.09);
        color: #94a3b8 !important;
    }
    .plink-repo:hover { background: rgba(255,255,255,0.09); color: #e2e8f0 !important; }

    /* ── Detail Page ── */
    .detail-page-header {
        margin-top: 16px;
        margin-bottom: 32px;
        padding-bottom: 24px;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        flex-wrap: wrap;
    }
    .detail-page-title {
        font-size: 2.2rem;
        font-weight: 900;
        background: linear-gradient(135deg, #fff 0%, #c4b5fd 70%, #93c5fd 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(145deg, #111119, #151522) !important;
        border: 1px solid rgba(124,58,237,0.18) !important;
        border-radius: 20px !important;
        box-shadow: 0 16px 40px rgba(0,0,0,0.4) !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        padding: 24px !important;
    }
    .detail-section-label {
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #4b5563;
        margin-bottom: 10px;
        margin-top: 20px;
    }
    .att-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        padding: 8px 14px;
        border-radius: 10px;
        margin-right: 8px;
        margin-bottom: 8px;
        font-size: 0.82rem;
        color: #cbd5e1;
    }
    .meta-row {
        display: flex;
        gap: 24px;
        flex-wrap: wrap;
        margin-top: 16px;
        padding-top: 16px;
        border-top: 1px solid rgba(255,255,255,0.05);
    }
    .meta-item { font-size: 0.75rem; color: #4b5563; }
    .meta-item span { color: #64748b; }

    /* ── Empty state ── */
    .empty-state {
        text-align: center;
        padding: 80px 40px;
        color: #334155;
    }
    .empty-state-icon { font-size: 3.5rem; margin-bottom: 16px; }
    .empty-state-text { font-size: 1rem; }

    /* ── Divider ── */
    .fancy-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, rgba(124,58,237,0.35) 40%, rgba(59,130,246,0.25) 60%, transparent 100%);
        margin: 0;
    }

    /* ── Footer ── */
    .custom-footer {
        text-align: center;
        padding: 36px;
        color: #1e293b;
        font-size: 0.75rem;
        border-top: 1px solid rgba(255,255,255,0.04);
    }

    /* ── Streamlit widget overrides ── */
    div[data-testid="stMultiSelect"] > div,
    div[data-testid="stSelectbox"] > div > div {
        background: #13131f !important;
        border-color: rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
    }
    div[data-testid="stExpander"] {
        background: transparent !important;
        border: none !important;
    }
    div[data-testid="stExpander"] > details {
        background: transparent !important;
        border: none !important;
    }
    /* hide default streamlit sidebar nav label */
    section[data-testid="stSidebarNav"] { display: none; }
    </style>
    """, unsafe_allow_html=True)


# ─── Tag colour cycling ───────────────────────────────────────────────────────
TAG_COLOURS = ["tag-purple", "tag-blue", "tag-teal", "tag-rose", "tag-amber"]
_tag_colour_cache: dict[str, str] = {}

def tag_colour(tag: str) -> str:
    if tag not in _tag_colour_cache:
        idx = len(_tag_colour_cache) % len(TAG_COLOURS)
        _tag_colour_cache[tag] = TAG_COLOURS[idx]
    return _tag_colour_cache[tag]


def status_pill(status: str) -> str:
    icons = {"live": "● Live", "wip": "◐ WIP", "archived": "○ Archived"}
    label = icons.get(status.lower(), status)
    cls   = f"status-{status.lower()}"
    return f'<span class="status-pill {cls}">{label}</span>'


def tags_html(tags: list[str]) -> str:
    return "".join(
        f'<span class="tag {tag_colour(t)}">{t}</span>' for t in tags
    )


def first_line(text: str) -> str:
    """Return first non-empty, non-heading line of markdown."""
    for line in text.splitlines():
        clean = line.strip().lstrip("#").strip()
        if clean:
            return clean
    return ""


# ─── Hero ────────────────────────────────────────────────────────────────────
def render_hero(cfg: dict):
    badge = cfg.get("availability_badge", "")
    name  = cfg.get("name", "Your Name")
    sub   = cfg.get("tagline", "")

    links_html = ""
    for lnk in cfg.get("social_links", []):
        icon  = lnk.get("icon", "")
        label = lnk.get("label", "")
        url   = lnk.get("url", "#")
        links_html += f'<a class="social-btn" href="{url}" target="_blank">{icon} {label}</a>'

    st.markdown(f"""
    <div class="hero-wrap">
        <div class="hero-badge">{badge}</div>
        <h1 class="hero-title">Hi, I'm {name} 👋</h1>
        <p class="hero-sub">{sub}</p>
        <div class="social-row">{links_html}</div>
    </div>
    """, unsafe_allow_html=True)


# ─── Stats strip ─────────────────────────────────────────────────────────────
def render_stats(projects: list[dict]):
    live  = sum(1 for p in projects if p.get("status") == "live")
    techs = {t for p in projects for t in p.get("tags", [])}
    st.markdown(f"""
    <div class="stats-strip">
        <div class="stat-cell">
            <div class="stat-val">{len(projects)}</div>
            <div class="stat-lbl">Projects</div>
        </div>
        <div class="stat-cell">
            <div class="stat-val">{live}</div>
            <div class="stat-lbl">Live</div>
        </div>
        <div class="stat-cell">
            <div class="stat-val">{len(techs)}</div>
            <div class="stat-lbl">Tags</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─── Card ────────────────────────────────────────────────────────────────────
def render_card(project: dict, idx: int):
    pid   = project["id"]
    title = project.get("title", "Untitled")
    desc  = project.get("description", "")
    tags  = project.get("tags", [])
    status = project.get("status", "wip")
    demo  = project.get("demo_url", "")
    repo  = project.get("repo_url", "")
    images = project.get("images", [])

    # ── Card image ──
    img_html = ""
    for img_rel in images:
        img_path = BASE_DIR / img_rel
        b64 = img_to_b64(img_path)
        if b64:
            ext = Path(img_rel).suffix.lstrip(".")
            mime = "jpeg" if ext in ("jpg", "jpeg") else ext
            img_html = f'<img class="pcard-img" src="data:image/{mime};base64,{b64}" alt="{title}">'
            break
    if not img_html:
        img_html = '<div class="pcard-placeholder">🖼️</div>'

    # ── Links ──
    links_html = ""
    if demo:
        links_html += f'<a class="plink plink-demo" href="{demo}" target="_blank">🚀 Live Demo</a>'
    if repo:
        links_html += f'<a class="plink plink-repo" href="{repo}" target="_blank">📂 Repository</a>'

    # ── Short description (first non-empty line) ──
    short = first_line(desc) or "No description provided."

    st.markdown(f"""
    <div class="pcard">
        {img_html}
        <div class="pcard-body">
            <div class="pcard-top">
                <div class="pcard-title">{title}</div>
                {status_pill(status)}
            </div>
            <p class="pcard-desc">{short}</p>
            <div class="tag-row">{tags_html(tags)}</div>
            <div class="link-row">{links_html if links_html else '<span style="color:#334155;font-size:0.78rem;">No links yet</span>'}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔎  View Case Study", key=f"view_{pid}_{idx}", width="stretch"):
        st.session_state["selected_project_id"] = pid
        st.rerun()


# ─── Full Project View ────────────────────────────────────────────────────────
def render_full_project_view(project: dict):
    pid         = project["id"]
    title       = project.get("title", "Untitled")
    desc        = project.get("description", "")
    tags        = project.get("tags", [])
    status      = project.get("status", "wip")
    demo        = project.get("demo_url", "")
    repo        = project.get("repo_url", "")
    images      = project.get("images", [])
    attachments = project.get("attachments", [])
    updated     = project.get("updated_at", "")

    # Back button
    st.write("")
    if st.button("← Back to Projects", type="secondary"):
        st.session_state.pop("selected_project_id", None)
        st.rerun()

    # Title & Status Header
    st.markdown(f"""
    <div class="detail-page-header">
        <h1 class="detail-page-title">{title}</h1>
        {status_pill(status)}
    </div>
    """, unsafe_allow_html=True)

    # 2-Column details
    left_col, right_col = st.columns([7, 4], gap="large")

    with left_col:
        # Gallery
        valid_images = []
        for img_rel in images:
            img_path = BASE_DIR / img_rel
            if img_path.exists():
                valid_images.append(img_path)

        if valid_images:
            st.markdown('<div class="detail-section-label" style="margin-top:0;">📸 Project Gallery</div>', unsafe_allow_html=True)
            if len(valid_images) == 1:
                st.image(str(valid_images[0]), width="stretch")
            else:
                st.image(str(valid_images[0]), width="stretch")
                cols = st.columns(min(len(valid_images) - 1, 4))
                for i, img_path in enumerate(valid_images[1:]):
                    with cols[i % len(cols)]:
                        st.image(str(img_path), width="stretch")
            st.write("")

        # Markdown Description
        st.markdown('<div class="detail-section-label">📝 Project Case Study & Details</div>', unsafe_allow_html=True)
        st.markdown(desc)

    with right_col:
        with st.container(border=True):
            st.markdown('<div class="detail-section-label" style="margin-top:0; color:#c4b5fd;">🏷️ Tags</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="tag-row" style="margin-bottom:20px;">{tags_html(tags)}</div>', unsafe_allow_html=True)

            if demo or repo:
                st.markdown('<div class="detail-section-label" style="color:#c4b5fd;">🔗 Links & Resources</div>', unsafe_allow_html=True)
                if demo:
                    st.link_button("🚀 Live Demo", demo, width="stretch", type="primary")
                    st.write("")
                if repo:
                    st.link_button("📂 View Code Repository", repo, width="stretch")
                    st.write("")

            if attachments:
                st.markdown('<div class="detail-section-label" style="color:#c4b5fd;">📎 Downloadable Files</div>', unsafe_allow_html=True)
                for att in attachments:
                    att_name = att.get("name", "File")
                    att_path = BASE_DIR / att.get("path", "")
                    if att_path.exists():
                        with open(att_path, "rb") as f:
                            file_bytes = f.read()
                        st.download_button(
                            label=f"⬇️  {att_name}",
                            data=file_bytes,
                            file_name=att_name,
                            key=f"dl_full_{pid}_{att_name}",
                            width="stretch",
                        )
                        st.write("")

            if updated:
                try:
                    dt = datetime.fromisoformat(updated)
                    updated_fmt = dt.strftime("%B %d, %Y")
                except Exception:
                    updated_fmt = updated
                st.markdown(f"""
                <div style="font-size:0.75rem; color:#475569; margin-top:28px; padding-top:16px; border-top:1px solid rgba(255,255,255,0.05);">
                    Last updated: <span style="color:#64748b;">{updated_fmt}</span>
                </div>
                """, unsafe_allow_html=True)

    st.write("")
    st.write("")


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    inject_css()
    cfg      = load_config()
    projects = load_projects()

    # Show single-project view if selected
    selected_id = st.session_state.get("selected_project_id")
    if selected_id:
        proj = get_project(projects, selected_id)
        if proj:
            render_full_project_view(proj)
            
            # Simple Footer inside the full page view
            st.markdown('<div class="fancy-divider" style="margin-top:40px;"></div>', unsafe_allow_html=True)
            year = datetime.now().year
            name = cfg.get("name", "Developer")
            st.markdown(
                f'<div class="custom-footer">© {year} {name} · Built with Streamlit ⚡</div>',
                unsafe_allow_html=True,
            )
            return

    # Default grid view
    # Compact profile card (no hero)
    avatar_src = 'https://via.placeholder.com/120'
    avatar_path = cfg.get('avatar_path')
    if avatar_path and Path(avatar_path).exists():
        avatar_b64 = img_to_b64(avatar_path)
        if avatar_b64:
            avatar_src = f"data:image/png;base64,{avatar_b64}"
    
    st.markdown(f"""
    <div style='display:flex; align-items:center; gap:24px; margin-bottom:2rem;'>
        <img src='{avatar_src}' alt='Avatar' style='border-radius:50%; width:120px; height:120px;'>
        <div>
            <h1 style='margin:0; font-size:2.4rem; color:#e2e8f0;'>{cfg.get('name', 'Your Name')}</h1>
            <p style='margin:4px 0 0; color:#94a3b8;'>{cfg.get('tagline', '')}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats strip follows the profile
    render_stats(projects)

    # ── Filter bar ──────────────────────────────────────────────────────────
    st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Projects</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Click "View Case Study" on any card to read more, see screenshots & download attachments.</div>', unsafe_allow_html=True)

    all_tags = sorted({t for p in projects for t in p.get("tags", [])})
    fc1, fc2, fc3 = st.columns([3, 1, 1])
    with fc1:
        sel_tags = st.multiselect("Filter by tag", all_tags, placeholder="All tags", label_visibility="collapsed")
    with fc2:
        sel_status = st.selectbox("Status", ["All", "Live", "WIP", "Archived"], label_visibility="collapsed")
    with fc3:
        search = st.text_input("Search", placeholder="🔍  Search…", label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Apply filters ────────────────────────────────────────────────────────
    filtered = projects
    if sel_tags:
        filtered = [p for p in filtered if any(t in p.get("tags", []) for t in sel_tags)]
    if sel_status != "All":
        filtered = [p for p in filtered if p.get("status", "").lower() == sel_status.lower()]
    if search:
        q = search.lower()
        filtered = [
            p for p in filtered
            if q in p.get("title", "").lower()
            or q in p.get("description", "").lower()
            or any(q in t.lower() for t in p.get("tags", []))
        ]

    # ── Project grid ────────────────────────────────────────────────────────
    st.markdown('<div class="grid-wrap">', unsafe_allow_html=True)

    if not filtered:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">🔭</div>
            <div class="empty-state-text">No projects match your filters.<br>Try adjusting the search or filter options.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        cols = st.columns(3, gap="large")
        for i, proj in enumerate(filtered):
            with cols[i % 3]:
                render_card(proj, i)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Divider + Footer ────────────────────────────────────────────────────
    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
    year = datetime.now().year
    name = cfg.get("name", "Developer")
    st.markdown(
        f'<div class="custom-footer">© {year} {name} · Built with Streamlit ⚡</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
