TERMINAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&display=swap');

/* ── SHELL (input) ── */
.term-shell {
    background: #0D1117;
    border: 1px solid #30363D;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(0,0,0,0.35);
    margin-bottom: 16px;
}
.term-titlebar {
    background: #161B22;
    border-bottom: 1px solid #30363D;
    padding: 10px 16px;
    display: flex;
    align-items: center;
    gap: 12px;
}
.term-dots { display: flex; gap: 6px; }
.term-dot  { width: 12px; height: 12px; border-radius: 50%; }
.term-dot-red    { background: #FF5F56; }
.term-dot-yellow { background: #FFBD2E; }
.term-dot-green  { background: #27C93F; }
.term-title-label {
    color: #8B949E;
    font-size: 12px;
    font-family: 'JetBrains Mono', monospace;
    margin-left: 8px;
    letter-spacing: 0.03em;
}
.term-body { padding: 14px 18px 10px 18px; background: #0D1117; }

div.term-shell textarea {
    background: #0D1117 !important;
    color: #E6EDF3 !important;
    border: none !important;
    border-radius: 0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
    line-height: 1.7 !important;
    box-shadow: none !important;
    caret-color: #27C93F;
}
div.term-shell textarea:focus {
    box-shadow: none !important;
    border: none !important;
    outline: none !important;
}

/* ── OUTPUT CONTAINER ── */
.term-output {
    background: #1A1F2E;
    border: 1px solid #2D3448;
    border-radius: 10px;
    overflow: hidden;
    margin-top: 12px;
}
.term-output-header {
    background: #0F1320;
    border-bottom: 1px solid #2D3448;
    padding: 8px 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

/* ── BADGES ── */
.term-badge-ok {
    background: rgba(39,201,63,0.15);
    color: #3DD68C;
    font-size: 11px;
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    padding: 2px 10px;
    border-radius: 20px;
    border: 1px solid rgba(39,201,63,0.35);
}
.term-badge-warn {
    background: rgba(255,189,46,0.15);
    color: #FFBD2E;
    font-size: 11px;
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    padding: 2px 10px;
    border-radius: 20px;
    border: 1px solid rgba(255,189,46,0.35);
}
.term-badge-error {
    background: rgba(255,95,86,0.15);
    color: #FF6B6B;
    font-size: 11px;
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    padding: 2px 10px;
    border-radius: 20px;
    border: 1px solid rgba(255,95,86,0.35);
}
.term-badge-method {
    background: rgba(88,166,255,0.12);
    color: #79B8FF;
    font-size: 11px;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    padding: 2px 10px;
    border-radius: 20px;
    border: 1px solid rgba(88,166,255,0.3);
}
.term-badge-fecha {
    font-size: 11px;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    padding: 2px 10px;
    border-radius: 20px;
    border: 1px solid;
    background: transparent;
}

/* ── TABLA DE RESULTADOS ── */
/* Wrapper con overflow para scroll horizontal */
div.term-output div[style*="overflow-x"] {
    background: #1A1F2E !important;
}

table.term-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12.5px;
    background: #1A1F2E !important;
}

/* Cabecera */
table.term-table thead tr {
    background: #0F1320 !important;
}
table.term-table thead th {
    background: #0F1320 !important;
    color: #79B8FF !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
    padding: 10px 16px !important;
    text-align: left !important;
    border-bottom: 2px solid #2D3448 !important;
    border-right: 1px solid #2D3448 !important;
    white-space: nowrap !important;
}
table.term-table thead th:last-child {
    border-right: none !important;
}

/* Filas pares — fondo ligeramente más claro */
table.term-table tbody tr {
    background: #1A1F2E !important;
}
table.term-table tbody tr:nth-child(even) {
    background: #1F2535 !important;
}
table.term-table tbody tr:hover td {
    background: #263049 !important;
}

/* Celdas — color forzado con !important para ganarle a Streamlit */
table.term-table tbody td {
    padding: 8px 16px !important;
    color: #CDD9E5 !important;
    background: inherit !important;
    border-bottom: 1px solid #252B3B !important;
    border-right: 1px solid #252B3B !important;
    max-width: 280px !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    white-space: nowrap !important;
    font-size: 12.5px !important;
}
table.term-table tbody td:last-child {
    border-right: none !important;
}

/* Tipos de valores con color semántico */
.td-num        { color: #79C0FF !important; font-weight: 600 !important; }
.td-bool-true  { color: #3DD68C !important; font-weight: 600 !important; }
.td-bool-false { color: #FF6B6B !important; font-weight: 600 !important; }
.td-null       { color: #586069 !important; font-style: italic !important; }

/* Primera columna (_id) más tenue */
table.term-table tbody td:first-child {
    color: #586069 !important;
    font-size: 11px !important;
}

/* ── ESCALAR ── */
.term-scalar {
    padding: 18px 22px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 15px;
    color: #79C0FF;
    white-space: pre-wrap;
    word-break: break-all;
    background: #1A1F2E;
}

/* ── LISTA (distinct) ── */
.term-list-wrap { padding: 10px 16px; background: #1A1F2E; }
.term-list-item {
    padding: 5px 2px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    color: #CDD9E5;
    border-bottom: 1px solid #252B3B;
}

/* ── ERROR ── */
.term-error {
    padding: 16px 20px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    color: #FF6B6B;
    white-space: pre-wrap;
    background: #1A1F2E;
}
.term-error::before { content: "✗  "; font-weight: 700; }

/* ── AVISO TRUNCADO ── */
.term-truncated-notice {
    padding: 8px 16px;
    background: rgba(255,189,46,0.07);
    border-top: 1px solid rgba(255,189,46,0.25);
    color: #FFBD2E;
    font-size: 11px;
    font-family: 'Inter', sans-serif;
    text-align: center;
}

/* ── HISTORIAL ── */
.term-history-item {
    background: #161B22;
    border: 1px solid #2D3448;
    border-radius: 6px;
    padding: 7px 10px;
    margin-bottom: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #8B949E;
    display: flex;
    align-items: center;
    gap: 8px;
}
.term-history-code {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    color: #CDD9E5;
}
.term-history-time { color: #484F58; font-size: 10px; flex-shrink: 0; }

/* ── EJEMPLOS ── */
.term-example-label {
    font-family: 'Inter', sans-serif;
    font-size: 10px;
    color: #8B949E;
    margin-top: 10px;
    margin-bottom: 3px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.term-example {
    background: #0D1117;
    border-left: 3px solid #58A6FF;
    border-radius: 0 6px 6px 0;
    padding: 7px 10px;
    margin-bottom: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #CDD9E5;
    white-space: pre-wrap;
    word-break: break-all;
}
/* ── PAGINACIÓN DE RESULTADOS ── */
.term-pag-info {
    text-align: center;
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    color: #8B949E;
    padding: 6px 0;
    line-height: 1.6;
}
.term-pag-info strong {
    color: #CDD9E5;
}
</style>
"""