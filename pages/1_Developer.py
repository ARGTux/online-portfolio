"""
Portfolio Showcase — Developer Dashboard
=========================================
Password-protected admin panel for managing portfolio projects.
Supports: add / edit / delete projects, upload images & attachments,
live preview, profile editing, and JSON backup/restore.
"""

import streamlit as st
import json
import uuid
import shutil
import os
import base64
from pathlib import Path
from datetime import datetime

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dev Dashboard · Portfolio",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Paths ───────────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent.parent
DATA_FILE   = BASE_DIR / "data" / "projects.json"
CONFIG_FILE = BASE_DIR / "data" / "config.json"
UPLOADS_DIR = BASE_DIR / "data" / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


# ─── Data helpers ─────────────────────────────────────────────────────────────
def load_projects() -> list[dict]:
    if DATA_FILE.exists():
        with open(DATA_FILE, encoding="utf-8") as f:
            return json.load(f)
    return []


def save_projects(projects: list[dict]):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(projects, f, indent=2, ensure_ascii=False)


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


def save_config(cfg: dict):
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def img_to_b64(path: Path) -> str | None:
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return None


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def get_project(projects: list[dict], pid: str) -> dict | None:
    return next((p for p in projects if p["id"] == pid), None)


# ─── CSS ─────────────────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
    #MainMenu, footer { visibility: hidden; }

    /* ── Login gate ── */
    .login-wrap {
        max-width: 420px;
        margin: 80px auto;
        background: #111119;
        border: 1px solid rgba(124,58,237,0.25);
        border-radius: 20px;
        padding: 48px 40px;
        box-shadow: 0 32px 80px rgba(0,0,0,0.6), 0 0 0 1px rgba(124,58,237,0.1);
    }
    .login-icon { font-size: 2.8rem; margin-bottom: 12px; }
    .login-title {
        font-size: 1.5rem;
        font-weight: 800;
        color: #f1f5f9;
        margin-bottom: 6px;
    }
    .login-sub { font-size: 0.85rem; color: #475569; margin-bottom: 28px; }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: #0d0d16 !important;
        border-right: 1px solid rgba(255,255,255,0.05) !important;
    }
    .sidebar-logo {
        font-size: 1.2rem;
        font-weight: 800;
        color: #c4b5fd;
        padding: 8px 0 24px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .sidebar-section {
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #334155;
        margin: 20px 0 8px;
    }
    .proj-item {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 9px 12px;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.18s;
        margin-bottom: 4px;
        border: 1px solid transparent;
    }
    .proj-item:hover {
        background: rgba(124,58,237,0.1);
        border-color: rgba(124,58,237,0.2);
    }
    .proj-item-active {
        background: rgba(124,58,237,0.15) !important;
        border-color: rgba(124,58,237,0.3) !important;
    }
    .proj-item-name { font-size: 0.83rem; color: #cbd5e1; font-weight: 500; flex: 1; }
    .proj-item-status {
        font-size: 0.62rem;
        font-weight: 700;
        padding: 2px 7px;
        border-radius: 99px;
    }

    /* ── Page header ── */
    .page-header {
        padding: 36px 40px 0;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        margin-bottom: 32px;
    }
    .page-badge {
        display: inline-block;
        background: rgba(124,58,237,0.12);
        border: 1px solid rgba(124,58,237,0.3);
        color: #a78bfa;
        padding: 3px 12px;
        border-radius: 99px;
        font-size: 0.68rem;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 10px;
    }
    .page-title {
        font-size: 1.7rem;
        font-weight: 800;
        color: #f1f5f9;
        margin-bottom: 24px;
    }

    /* ── Cards in dashboard ── */
    .dash-card {
        background: #111119;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 16px;
        transition: all 0.2s;
    }
    .dash-card:hover {
        border-color: rgba(124,58,237,0.25);
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    }
    .proj-card-title { font-size: 1rem; font-weight: 700; color: #f1f5f9; margin-bottom: 6px; }
    .proj-card-tags { display: flex; gap: 5px; flex-wrap: wrap; }
    .mini-tag {
        background: rgba(124,58,237,0.1);
        border: 1px solid rgba(124,58,237,0.22);
        color: #a78bfa;
        padding: 2px 8px;
        border-radius: 99px;
        font-size: 0.66rem;
        font-weight: 500;
    }

    /* ── Form section labels ── */
    .form-section {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #4b5563;
        margin: 28px 0 12px;
        padding-bottom: 6px;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }

    /* ── Preview frame ── */
    .preview-card {
        background: linear-gradient(145deg, #141420, #111118);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 18px;
        overflow: hidden;
    }
    .preview-img-placeholder {
        height: 160px;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 3rem;
    }
    .preview-body { padding: 20px; }
    .preview-title { font-size: 1rem; font-weight: 700; color: #f1f5f9; margin-bottom: 8px; }
    .preview-desc {
        font-size: 0.8rem;
        color: #94a3b8;
        line-height: 1.6;
        margin-bottom: 14px;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    .preview-tags { display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 14px; }
    .preview-tag {
        background: rgba(124,58,237,0.12);
        border: 1px solid rgba(124,58,237,0.25);
        color: #c4b5fd;
        padding: 3px 9px;
        border-radius: 99px;
        font-size: 0.68rem;
        font-weight: 500;
    }

    /* ── Status badges ── */
    .status-live     { background: rgba(16,185,129,0.12); border: 1px solid rgba(16,185,129,0.3);  color: #34d399; }
    .status-wip      { background: rgba(245,158,11,0.12); border: 1px solid rgba(245,158,11,0.3);  color: #fbbf24; }
    .status-archived { background: rgba(100,116,139,0.12);border: 1px solid rgba(100,116,139,0.3); color: #94a3b8; }
    .status-pill-sm {
        display: inline-block;
        padding: 3px 9px;
        border-radius: 99px;
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* ── Info box ── */
    .info-box {
        background: rgba(59,130,246,0.08);
        border: 1px solid rgba(59,130,246,0.2);
        border-radius: 10px;
        padding: 14px 16px;
        font-size: 0.82rem;
        color: #93c5fd;
        margin-bottom: 16px;
    }
    .warn-box {
        background: rgba(239,68,68,0.08);
        border: 1px solid rgba(239,68,68,0.2);
        border-radius: 10px;
        padding: 14px 16px;
        font-size: 0.82rem;
        color: #fca5a5;
        margin-bottom: 16px;
    }

    /* ── Streamlit overrides ── */
    div[data-testid="stTextInput"] input,
    div[data-testid="stTextArea"] textarea,
    div[data-testid="stSelectbox"] > div > div,
    div[data-testid="stNumberInput"] input {
        background: #0f0f1a !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
    }
    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stTextArea"] textarea:focus {
        border-color: rgba(124,58,237,0.5) !important;
        box-shadow: 0 0 0 2px rgba(124,58,237,0.15) !important;
    }
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.2s !important;
    }
    section[data-testid="stSidebarNav"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)


# ─── Auth ─────────────────────────────────────────────────────────────────────
def check_auth() -> bool:
    return st.session_state.get("dev_authenticated", False)


def login_gate():
    st.markdown('<div class="login-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="login-icon">🛠️</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-title">Developer Access</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-sub">Enter your developer password to manage the portfolio.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)  # close for styling context

    # Render actual inputs outside the HTML div (Streamlit limitation)
    with st.container():
        col_c, col_f, col_c2 = st.columns([1, 2, 1])
        with col_f:
            st.markdown("### 🔐 Developer Login")
            pwd = st.text_input("Password", type="password", placeholder="Enter password…", key="login_pwd")
            if st.button("Sign In →", use_container_width=True, type="primary"):
                correct = st.secrets.get("DEV_PASSWORD", "portfolio2024")
                if pwd == correct:
                    st.session_state["dev_authenticated"] = True
                    st.rerun()
                else:
                    st.error("Incorrect password. Try again.")
            st.caption("💡 Default password is `portfolio2024` — change it in `.streamlit/secrets.toml`")


# ─── Sidebar ──────────────────────────────────────────────────────────────────
def render_sidebar(projects: list[dict]) -> str:
    """Returns the current active view: 'dashboard', 'add', 'profile', 'backup', or a project ID."""
    with st.sidebar:
        st.markdown('<div class="sidebar-logo">⚡ Dev Dashboard</div>', unsafe_allow_html=True)

        view = st.session_state.get("current_view", "dashboard")

        if st.button("🏠  Overview", use_container_width=True):
            st.session_state["current_view"] = "dashboard"
            st.session_state.pop("editing_project", None)
            st.session_state.pop("profile_links", None)
            st.rerun()

        if st.button("➕  Add New Project", use_container_width=True, type="primary"):
            st.session_state["current_view"] = "add"
            st.session_state.pop("editing_project", None)
            st.session_state.pop("profile_links", None)
            st.rerun()

        st.markdown('<div class="sidebar-section">Projects</div>', unsafe_allow_html=True)

        status_icons = {"live": "🟢", "wip": "🟡", "archived": "⚫"}
        sorted_projects = sorted(projects, key=lambda x: x.get("order", 999))
        for proj in sorted_projects:
            pid    = proj["id"]
            icon   = status_icons.get(proj.get("status", "wip"), "⚪")
            is_sel = st.session_state.get("editing_project") == pid
            label  = f"{icon}  {proj.get('title', 'Untitled')}"
            if st.button(label, key=f"sb_{pid}", use_container_width=True):
                st.session_state["current_view"] = "edit"
                st.session_state["editing_project"] = pid
                st.session_state.pop("profile_links", None)
                st.rerun()

        st.divider()
        st.markdown('<div class="sidebar-section">Settings</div>', unsafe_allow_html=True)

        if st.button("👤  Edit Profile", use_container_width=True):
            st.session_state["current_view"] = "profile"
            st.rerun()

        if st.button("💾  Backup & Restore", use_container_width=True):
            st.session_state["current_view"] = "backup"
            st.session_state.pop("profile_links", None)
            st.rerun()

        st.divider()
        if st.button("🚪  Sign Out", use_container_width=True):
            st.session_state["dev_authenticated"] = False
            st.session_state.pop("profile_links", None)
            st.rerun()

    return st.session_state.get("current_view", "dashboard")


# ─── Dashboard Overview ───────────────────────────────────────────────────────
def render_dashboard(projects: list[dict]):
    st.markdown('<div class="page-header">', unsafe_allow_html=True)
    st.markdown('<div class="page-badge">🛠️ Developer</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">Portfolio Overview</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    with st.container():
        # Stats
        live  = sum(1 for p in projects if p.get("status") == "live")
        wip   = sum(1 for p in projects if p.get("status") == "wip")
        arch  = sum(1 for p in projects if p.get("status") == "archived")
        techs = {t for p in projects for t in p.get("tags", [])}

        mc1, mc2, mc3, mc4 = st.columns(4)
        mc1.metric("Total Projects", len(projects))
        mc2.metric("🟢 Live",        live)
        mc3.metric("🟡 WIP",         wip)
        mc4.metric("Tags",           len(techs))

        st.divider()
        st.subheader("All Projects")
        if st.button("➕ Add New Project", type="primary"):
            st.session_state["current_view"] = "add"
            st.rerun()

        st.write("")

        sorted_projects = sorted(projects, key=lambda x: x.get("order", 999))
        for proj in sorted_projects:
            pid    = proj["id"]
            status = proj.get("status", "wip")
            tags   = proj.get("tags", [])
            tags_html = "".join(f'<span class="mini-tag">{t}</span>' for t in tags[:5])
            status_icon = {"live": "🟢", "wip": "🟡", "archived": "⚫"}.get(status, "⚪")

            with st.container():
                col_info, col_actions = st.columns([4, 1])
                with col_info:
                    st.markdown(f"""
                    <div class="dash-card">
                        <div class="proj-card-title">{status_icon} {proj.get('title', 'Untitled')}</div>
                        <div class="proj-card-tags">{tags_html}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_actions:
                    st.write("")
                    st.write("")
                    if st.button("✏️ Edit", key=f"edit_{pid}", use_container_width=True):
                        st.session_state["current_view"] = "edit"
                        st.session_state["editing_project"] = pid
                        st.rerun()
                    if st.button("🗑️ Delete", key=f"del_{pid}", use_container_width=True):
                        st.session_state[f"confirm_delete_{pid}"] = True
                        st.rerun()
                    if st.session_state.get(f"confirm_delete_{pid}"):
                        st.warning("Delete this project?")
                        if st.button("Yes, delete", key=f"yes_del_{pid}", use_container_width=True):
                            projects[:] = [p for p in projects if p["id"] != pid]
                            # Remove uploads
                            proj_dir = UPLOADS_DIR / pid
                            if proj_dir.exists():
                                shutil.rmtree(proj_dir)
                            save_projects(projects)
                            st.session_state.pop(f"confirm_delete_{pid}", None)
                            st.success("Project deleted.")
                            st.rerun()
                        if st.button("Cancel", key=f"cancel_del_{pid}", use_container_width=True):
                            st.session_state.pop(f"confirm_delete_{pid}", None)
                            st.rerun()


# ─── Project Form ─────────────────────────────────────────────────────────────
def render_project_form(projects: list[dict], edit_pid: str | None = None):
    is_edit = edit_pid is not None
    proj    = get_project(projects, edit_pid) if is_edit else {}

    action_label = "Edit Project" if is_edit else "Add New Project"
    st.markdown('<div class="page-header">', unsafe_allow_html=True)
    st.markdown('<div class="page-badge">🛠️ Developer</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-title">{action_label}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Determine project dir
    pid = proj.get("id", str(uuid.uuid4()))
    proj_dir   = UPLOADS_DIR / pid
    img_dir    = proj_dir / "images"
    att_dir    = proj_dir / "attachments"
    img_dir.mkdir(parents=True, exist_ok=True)
    att_dir.mkdir(parents=True, exist_ok=True)

    form_col, preview_col = st.columns([3, 2], gap="large")

    with form_col:
        # ── Basic Info ──
        st.markdown('<div class="form-section">📋 Basic Information</div>', unsafe_allow_html=True)
        title = st.text_input("Project Title *", value=proj.get("title", ""), placeholder="My Awesome Project")

        status_opts = ["live", "wip", "archived"]
        cur_status  = proj.get("status", "wip")
        status = st.selectbox(
            "Status",
            status_opts,
            index=status_opts.index(cur_status) if cur_status in status_opts else 1,
            format_func=lambda s: {"live": "🟢 Live", "wip": "🟡 Work In Progress", "archived": "⚫ Archived"}[s],
        )

        order = st.number_input("Display Order", min_value=1, max_value=999,
                                value=proj.get("order", len(projects) + 1))

        # ── Description ──
        st.markdown('<div class="form-section">📝 Description (Markdown supported)</div>', unsafe_allow_html=True)
        desc = st.text_area(
            "Description",
            value=proj.get("description", ""),
            height=240,
            placeholder="## Overview\nDescribe your project here. **Markdown** is fully supported.",
            label_visibility="collapsed",
        )

        # ── Tags ──
        st.markdown('<div class="form-section">🏷️ Tags</div>', unsafe_allow_html=True)
        tags_str = st.text_input(
            "Tags (comma-separated)",
            value=", ".join(proj.get("tags", [])),
            placeholder="Python, FastAPI, React, PostgreSQL",
            label_visibility="collapsed",
        )
        tags = [t.strip() for t in tags_str.split(",") if t.strip()]

        # ── Links ──
        st.markdown('<div class="form-section">🔗 Links</div>', unsafe_allow_html=True)
        lc1, lc2 = st.columns(2)
        with lc1:
            demo_url = st.text_input("Live Demo URL", value=proj.get("demo_url", ""), placeholder="https://...")
        with lc2:
            repo_url = st.text_input("Repository URL", value=proj.get("repo_url", ""), placeholder="https://github.com/...")

        # ── Images ──
        st.markdown('<div class="form-section">📸 Screenshots / Images</div>', unsafe_allow_html=True)

        # Show existing images
        existing_images: list[str] = proj.get("images", [])
        valid_existing = [i for i in existing_images if (BASE_DIR / i).exists()]

        if valid_existing:
            st.caption(f"{len(valid_existing)} existing image(s):")
            img_cols = st.columns(min(len(valid_existing), 4))
            to_remove = []
            for idx, img_rel in enumerate(valid_existing):
                with img_cols[idx % 4]:
                    st.image(str(BASE_DIR / img_rel), use_container_width=True)
                    if st.button("🗑️", key=f"rm_img_{pid}_{idx}", help="Remove this image"):
                        to_remove.append(img_rel)
            for img_rel in to_remove:
                img_path = BASE_DIR / img_rel
                if img_path.exists():
                    img_path.unlink()
                valid_existing.remove(img_rel)

        uploaded_imgs = st.file_uploader(
            "Upload images (PNG, JPG, WebP)",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=True,
            key=f"img_up_{pid}",
        )
        new_img_paths: list[str] = list(valid_existing)
        if uploaded_imgs:
            for uf in uploaded_imgs:
                safe_name = uf.name.replace(" ", "_")
                dest      = img_dir / safe_name
                dest.write_bytes(uf.read())
                rel = str(dest.relative_to(BASE_DIR))
                if rel not in new_img_paths:
                    new_img_paths.append(rel)
            st.success(f"✅ {len(uploaded_imgs)} image(s) uploaded.")

        # ── Attachments ──
        st.markdown('<div class="form-section">📎 File Attachments</div>', unsafe_allow_html=True)

        existing_atts: list[dict] = proj.get("attachments", [])
        valid_atts = [a for a in existing_atts if (BASE_DIR / a.get("path", "")).exists()]

        if valid_atts:
            st.caption(f"{len(valid_atts)} existing attachment(s):")
            to_remove_att = []
            for att in valid_atts:
                ac1, ac2 = st.columns([4, 1])
                with ac1:
                    st.markdown(f"📄 `{att['name']}`")
                with ac2:
                    if st.button("🗑️", key=f"rm_att_{pid}_{att['name']}", help="Remove"):
                        to_remove_att.append(att)
            for att in to_remove_att:
                att_path = BASE_DIR / att["path"]
                if att_path.exists():
                    att_path.unlink()
                valid_atts.remove(att)

        uploaded_files = st.file_uploader(
            "Upload attachments (PDF, ZIP, DOCX, etc.)",
            accept_multiple_files=True,
            key=f"att_up_{pid}",
        )
        new_atts: list[dict] = list(valid_atts)
        if uploaded_files:
            for uf in uploaded_files:
                safe_name = uf.name.replace(" ", "_")
                dest      = att_dir / safe_name
                dest.write_bytes(uf.read())
                rel = str(dest.relative_to(BASE_DIR))
                entry = {"name": uf.name, "path": rel}
                if not any(a["name"] == uf.name for a in new_atts):
                    new_atts.append(entry)
            st.success(f"✅ {len(uploaded_files)} file(s) uploaded.")

        # ── Save ──
        st.write("")
        save_col, cancel_col = st.columns([2, 1])
        with save_col:
            save_btn = st.button("💾 Save Project", type="primary", use_container_width=True)
        with cancel_col:
            if st.button("Cancel", use_container_width=True):
                st.session_state["current_view"] = "dashboard"
                st.session_state.pop("editing_project", None)
                st.rerun()

        if save_btn:
            if not title.strip():
                st.error("Project title is required.")
            else:
                new_proj = {
                    "id":          pid,
                    "title":       title.strip(),
                    "description": desc,
                    "tags":        tags,
                    "status":      status,
                    "demo_url":    demo_url.strip(),
                    "repo_url":    repo_url.strip(),
                    "images":      new_img_paths,
                    "attachments": new_atts,
                    "order":       int(order),
                    "created_at":  proj.get("created_at", now_iso()),
                    "updated_at":  now_iso(),
                }
                if is_edit:
                    idx = next((i for i, p in enumerate(projects) if p["id"] == pid), None)
                    if idx is not None:
                        projects[idx] = new_proj
                    else:
                        projects.append(new_proj)
                else:
                    projects.append(new_proj)

                save_projects(projects)
                st.success("✅ Project saved successfully!")
                st.session_state["current_view"] = "dashboard"
                st.session_state.pop("editing_project", None)
                st.rerun()

    # ── Live Preview ──────────────────────────────────────────────────────────
    with preview_col:
        st.markdown("#### 👁️ Live Preview")
        st.caption("Updates as you type")

        first_line_desc = ""
        for line in desc.splitlines():
            clean = line.strip().lstrip("#").strip()
            if clean:
                first_line_desc = clean
                break

        # Find a preview image
        preview_img_path = None
        for img_rel in new_img_paths:
            p = BASE_DIR / img_rel
            if p.exists():
                preview_img_path = p
                break

        tag_html_preview = "".join(
            f'<span class="preview-tag">{t}</span>' for t in tags[:6]
        )
        status_colours = {
            "live":     ("rgba(16,185,129,0.12)", "rgba(16,185,129,0.3)", "#34d399", "● Live"),
            "wip":      ("rgba(245,158,11,0.12)", "rgba(245,158,11,0.3)", "#fbbf24", "◐ WIP"),
            "archived": ("rgba(100,116,139,0.12)","rgba(100,116,139,0.3)","#94a3b8","○ Archived"),
        }
        sc = status_colours.get(status, status_colours["wip"])

        st.markdown(f"""
        <div class="preview-card">
        """, unsafe_allow_html=True)

        if preview_img_path:
            st.image(str(preview_img_path), use_container_width=True)
        else:
            st.markdown('<div class="preview-img-placeholder">🖼️</div>', unsafe_allow_html=True)

        st.markdown(f"""
            <div class="preview-body">
                <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:8px;">
                    <div class="preview-title">{title or "Project Title"}</div>
                    <span style="background:{sc[0]};border:1px solid {sc[1]};color:{sc[2]};
                                 padding:3px 9px;border-radius:99px;font-size:0.65rem;
                                 font-weight:700;text-transform:uppercase;white-space:nowrap;">
                        {sc[3]}
                    </span>
                </div>
                <p class="preview-desc">{first_line_desc or "Your description will appear here…"}</p>
                <div class="preview-tags">{tag_html_preview or '<span style="color:#334155;font-size:0.75rem;">No tags yet</span>'}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Markdown preview
        if desc.strip():
            st.divider()
            st.caption("📄 Description Preview")
            st.markdown(desc)


# ─── Profile Editor ───────────────────────────────────────────────────────────
def render_profile_editor():
    st.markdown('<div class="page-header">', unsafe_allow_html=True)
    st.markdown('<div class="page-badge">🛠️ Developer</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">Edit Profile</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    cfg = load_config()

    st.markdown('<div class="form-section">👤 Basic Info</div>', unsafe_allow_html=True)
    name   = st.text_input("Your Name", value=cfg.get("name", ""))
    badge  = st.text_input("Availability Badge", value=cfg.get("availability_badge", "Open to Opportunities"),
                           help="Short status shown in the hero (e.g. 'Open to Opportunities')")
    tagline = st.text_area("Tagline / Bio", value=cfg.get("tagline", ""), height=100,
                           help="Shown under your name on the public side")

    st.markdown('<div class="form-section">🔗 Social & Contact Links</div>', unsafe_allow_html=True)
    st.caption("Add or remove contact links shown in the hero section.")

    if "profile_links" not in st.session_state:
        st.session_state["profile_links"] = list(cfg.get("social_links", []))

    links = st.session_state["profile_links"]

    to_delete = None
    for i, lnk in enumerate(links):
        lc1, lc2, lc3, lc4 = st.columns([1, 2, 4, 1])
        with lc1:
            icon = st.text_input("Icon", value=lnk.get("icon", "🔗"), placeholder="🔗", key=f"lnk_icon_{i}", label_visibility="collapsed")
        with lc2:
            label = st.text_input("Label", value=lnk.get("label", ""), placeholder="GitHub", key=f"lnk_lbl_{i}", label_visibility="collapsed")
        with lc3:
            url = st.text_input("URL", value=lnk.get("url", ""), placeholder="https://github.com/...", key=f"lnk_url_{i}", label_visibility="collapsed")
        with lc4:
            st.write("") # spacing alignment
            if st.button("🗑️", key=f"rm_lnk_{i}", help="Delete this link"):
                to_delete = i

        # Update values in state
        lnk["icon"] = icon
        lnk["label"] = label
        lnk["url"] = url

    if to_delete is not None:
        st.session_state["profile_links"].pop(to_delete)
        st.rerun()

    if st.button("➕ Add Link"):
        st.session_state["profile_links"].append({"label": "", "url": "", "icon": "🔗"})
        st.rerun()

    st.write("")
    if st.button("💾 Save Profile", type="primary", use_container_width=False):
        final_links = [
            lnk for lnk in st.session_state["profile_links"]
            if lnk.get("label", "").strip() or lnk.get("url", "").strip()
        ]
        cfg["name"]               = name.strip()
        cfg["tagline"]            = tagline.strip()
        cfg["availability_badge"] = badge.strip()
        cfg["social_links"]       = final_links
        save_config(cfg)
        st.session_state["profile_links"] = list(final_links)
        st.success("✅ Profile saved! The public page will reflect your changes immediately.")


# ─── Backup & Restore ─────────────────────────────────────────────────────────
def render_backup(projects: list[dict]):
    st.markdown('<div class="page-header">', unsafe_allow_html=True)
    st.markdown('<div class="page-badge">🛠️ Developer</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">Backup & Restore</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="form-section">📤 Export</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Download your entire projects database as a JSON file for safekeeping.</div>', unsafe_allow_html=True)

    json_bytes = json.dumps(projects, indent=2, ensure_ascii=False).encode("utf-8")
    st.download_button(
        label="⬇️  Download projects.json",
        data=json_bytes,
        file_name=f"projects_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
    )

    st.markdown('<div class="form-section">📥 Import</div>', unsafe_allow_html=True)
    st.markdown('<div class="warn-box">⚠️ Importing will <strong>replace</strong> all current projects. This cannot be undone. Make sure you export a backup first.</div>', unsafe_allow_html=True)

    uploaded_json = st.file_uploader("Upload a projects.json backup", type=["json"])
    if uploaded_json:
        try:
            imported = json.loads(uploaded_json.read())
            if not isinstance(imported, list):
                st.error("Invalid format: expected a JSON array.")
            else:
                st.success(f"Found {len(imported)} project(s) in the file.")
                if st.button("✅ Confirm Import (replaces all current projects)", type="primary"):
                    save_projects(imported)
                    st.success("Import complete! Reloading…")
                    st.rerun()
        except json.JSONDecodeError:
            st.error("Invalid JSON file.")


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    inject_css()

    if not check_auth():
        login_gate()
        return

    projects = load_projects()
    view     = render_sidebar(projects)

    if view == "dashboard":
        render_dashboard(projects)

    elif view == "add":
        render_project_form(projects, edit_pid=None)

    elif view == "edit":
        pid = st.session_state.get("editing_project")
        if pid:
            render_project_form(projects, edit_pid=pid)
        else:
            st.session_state["current_view"] = "dashboard"
            st.rerun()

    elif view == "profile":
        render_profile_editor()

    elif view == "backup":
        render_backup(projects)


if __name__ == "__main__":
    main()
