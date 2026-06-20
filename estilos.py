import streamlit as st
import os, base64


def aplicar_estilos():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,wght@0,400;0,600;0,700;1,400&family=Inter:wght@400;500;600&display=swap');
        @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css');

        /* ───────────────────────── BASE ───────────────────────── */
        html, body, .stApp, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #F1F5F9;
        }
        h1, h2, h3, h4 {
            font-family: 'Source Serif 4', serif !important;
            font-weight: 700 !important;
            color: #0B2545;
        }

        /* ───────────────────────── SIDEBAR ───────────────────────── */
        [data-testid="stSidebar"] {
            background-color: #0B2545 !important;
        }
        [data-testid="stSidebar"] * { color: #FFFFFF !important; }

        /* Sidebar radio (Streamlit 1.35+) */
        [data-testid="stSidebar"] [role="radiogroup"] {
            display: flex !important;
            flex-direction: column !important;
            gap: 28px !important;
            padding: 0 !important;
        }
        [data-testid="stSidebar"] [role="radio"] {
            background: transparent !important;
            padding: 14px 18px !important;
            border-radius: 0 !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 500 !important;
            font-size: 15px !important;
            border: none !important;
            border-left: 4px solid transparent !important;
            transition: border-color 0.2s, background-color 0.2s !important;
            color: #FFFFFF !important;
            margin: 0 !important;
            cursor: pointer !important;
            display: flex !important;
            align-items: center !important;
        }
        [data-testid="stSidebar"] [role="radio"]:hover {
            background: rgba(255,255,255,0.06) !important;
        }
        [data-testid="stSidebar"] [role="radio"][aria-checked="true"] {
            background: transparent !important;
            border-left: 4px solid #C9A227 !important;
        }
        [data-testid="stSidebar"] [role="radio"] * {
            color: #FFFFFF !important;
            fill: #FFFFFF !important;
        }

        /* Fallback para `.stRadio label` en versiones <1.35 */
        div[data-testid="stSidebar"] .stRadio > div { gap: 0; }
        div[data-testid="stSidebar"] .stRadio label {
            background: transparent !important;
            padding: 14px 18px !important;
            border-radius: 0 !important;
            font-family: 'Inter', sans-serif;
            font-weight: 500;
            font-size: 15px;
            border-left: 4px solid transparent;
            transition: border-color 0.2s, background-color 0.2s;
            color: #FFFFFF;
        }
        div[data-testid="stSidebar"] .stRadio label:hover {
            background: rgba(255,255,255,0.06) !important;
        }
        div[data-testid="stSidebar"] .stRadio label:has(input:checked) {
            background: transparent !important;
            border-left: 4px solid #C9A227 !important;
        }

        /* ───────────────────────── STAT CARDS ───────────────────────── */
        .stat-card {
            background: #FFFFFF;
            border: 1px solid #E5E0D3;
            border-radius: 12px;
            padding: 20px 22px;
            display: flex;
            align-items: center;
            gap: 18px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
            transition: box-shadow 0.2s;
        }
        .stat-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.06); }
        .stat-card .stat-icon {
            width: 50px;
            height: 50px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            color: #FFFFFF;
            flex-shrink: 0;
        }
        .stat-card .stat-value {
            font-size: 28px;
            font-weight: 700;
            color: #0B2545;
            line-height: 1.15;
            font-family: 'Source Serif 4', serif;
        }
        .stat-card .stat-label {
            font-size: 13px;
            color: #5C6470;
            font-weight: 500;
            margin-top: 2px;
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }

        /* ───────────────────────── TABLE ───────────────────────── */
        .table-wrap {
            background: #FFFFFF;
            border: 1px solid #D0D5DD;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }
        table.real-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }
        table.real-table thead th {
            background: #0B2545;
            color: #FFFFFF;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            padding: 10px 14px;
            text-align: left;
        }
        table.real-table tbody td {
            padding: 10px 14px;
            color: #1C2434;
            border-bottom: 1px solid #F0EDE6;
        }
        table.real-table tbody tr:hover { background: #EEF2F8; }

        .badge {
            display: inline-block;
            padding: 3px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            line-height: 1.4;
        }
        .badge-active { background: #DCFCE7; color: #166534; }
        .badge-inactive { background: #FEE2E2; color: #991B1B; }

        /* Iconos de acción (Editar / Eliminar) dentro de la tabla */
        td.cell-icon { text-align: center; width: 1%; }

        a.row-icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 30px;
            height: 30px;
            border-radius: 7px;
            text-decoration: none !important;
            font-size: 13px;
            transition: all 0.15s;
        }
        a.icon-edit {
            color: #1B4079 !important;
            background: rgba(27,64,121,0.08);
        }
        a.icon-edit:hover {
            background: #1B4079;
            color: #FFFFFF !important;
        }
        a.icon-delete {
            color: #9B2226 !important;
            background: rgba(155,34,38,0.08);
        }
        a.icon-delete:hover {
            background: #9B2226;
            color: #FFFFFF !important;
        }

        /* ───────────────────────── FORM ───────────────────────── */
        [data-testid="stForm"] {
            background: #FFFFFF;
            border: 1px solid #E5E0D3;
            border-radius: 12px;
            padding: 24px 28px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        }

        /* ───────────────────────── BUTTONS ───────────────────────── */
        .stButton button {
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            font-size: 14px;
            border-radius: 7px;
            transition: all 0.15s;
            padding: 7px 20px;
        }
        .stButton button[kind="primary"] {
            background: #1B4079 !important;
            color: #FFFFFF !important;
            border: none !important;
        }
        .stButton button[kind="primary"]:hover { background: #0B2545 !important; }
        .stButton button[kind="secondary"] {
            background: transparent !important;
            color: #5C6470 !important;
            border: 1px solid #D0D5DD !important;
        }
        .stButton button[kind="secondary"]:hover {
            border-color: #9B2226 !important;
            color: #9B2226 !important;
        }

        /* ───────────────────────── MISC ───────────────────────── */
        .stAlert { border-radius: 8px; font-family: 'Inter', sans-serif; }
        [data-testid="stSelectbox"] div[data-baseweb="select"] > div { border-radius: 7px; }
        [data-testid="stCheckbox"] label { font-family: 'Inter', sans-serif; }
        [data-testid="stPopover"] {
            border-radius: 12px;
            border: 1px solid #E5E0D3;
            box-shadow: 0 8px 24px rgba(0,0,0,0.08);
        }
        [data-testid="stDialog"] {
            border-radius: 12px;
        }
    </style>
    """, unsafe_allow_html=True)


def mostrar_header():
    import os, base64
    b64 = ""
    mime = ""
    for path in ["icons/comedor_hero.jpg", "icons/comedor_hero.jpeg", "icons/comedor_banner.jpg", "icons/comedor.png", "icons/comedor.jpg"]:
        if os.path.exists(path):
            with open(path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            ext = path.rsplit(".", 1)[-1]
            mime = "svg+xml" if ext == "svg" else ext
            break
    img_url = f"data:image/{mime};base64,{b64}" if b64 else ""
    st.markdown(f"""
    <div style="
        position:relative;
        margin:-1rem -1rem 24px -1rem;
        height:260px;
        overflow:hidden;
        border-radius:0 0 24px 24px;
    ">
        <img src="{img_url}" alt="" style="
            position:absolute;
            inset:0;
            width:100%;
            height:100%;
            object-fit:cover;
        ">
        <div style="
            position:absolute;
            inset:0;
            background:linear-gradient(rgba(11,37,69,0.35), rgba(11,37,69,0.25));
        "></div>
        <div style="
            position:absolute;
            left:40px;
            bottom:36px;
            color:white;
            z-index:10;
        ">
            <div style="font-family:'Inter',sans-serif;font-weight:600;letter-spacing:0.03em;font-size:0.95rem;margin-bottom:8px;">
                Sistema de Subsidio de Alimentación
            </div>
            <div style="width:420px;height:3px;background:#C9A227;border-radius:10px;margin-bottom:14px;"></div>
            <div style="font-size:3rem;font-weight:700;color:white;font-family:'Source Serif 4', serif;">
                Bienestar Universitario
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_stat_card(icon, value, label, bg_color):
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-icon" style="background:{bg_color};">
            <i class="fas fa-{icon}"></i>
        </div>
        <div>
            <div class="stat-value">{value}</div>
            <div class="stat-label">{label}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)