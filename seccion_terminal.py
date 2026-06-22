"""
seccion_terminal.py
Terminal MongoDB shell para Streamlit.
"""

import json
from datetime import datetime
import streamlit as st
from services.terminal_service import TerminalService
from terminal_estilos import TERMINAL_CSS


@st.cache_resource
def _get_terminal_svc():
    return TerminalService()


EJEMPLOS = [
    {
        "categoria": "📖 Consultas básicas",
        "items": [
            {"label": "Todos los proveedores activos",
             "codigo": "db.proveedores.find({estado_activo: true})"},
            {"label": "Un estudiante de semestre 4",
             "codigo": "db.estudiantes.findOne({semestre: 4})"},
            {"label": "Total de consumos",
             "codigo": "db.consumos.countDocuments({})"},
            {"label": "Sedes (solo nombre y capacidad)",
             "codigo": "db.sedes.find({}, {nombre_sede: 1, capacidad_maxima: 1})"},
            {"label": "Valores únicos de facultad",
             "codigo": 'db.estudiantes.distinct("facultad")'},
        ]
    },
    {
        "categoria": "📅 Filtros por fecha",
        "items": [
            {"label": "Consumos desde fecha (ISODate)",
             "codigo": 'db.consumos.find({fecha_consumo: {$gte: ISODate("2026-01-01")}})'},
            {"label": "Consumos desde fecha (Date)",
             "codigo": 'db.consumos.find({fecha_consumo: {$gte: Date("2026-01-01")}})'},
            {"label": "Consumos desde fecha (string)",
             "codigo": 'db.consumos.find({fecha_consumo: {$gte: "2026-01-01"}})'},
        ]
    },
    {
        "categoria": "🔗 Encadenados",
        "items": [
            {"label": "find + sort + limit",
             "codigo": "db.evaluaciones.find({calificacion: {$gte: 4}}).sort({calificacion: -1}).limit(10)"},
            {"label": "find + skip + limit (paginación)",
             "codigo": "db.estudiantes.find({semestre: {$gte: 5}}).skip(0).limit(20)"},
        ]
    },
    {
        "categoria": "📊 Aggregate pipeline",
        "items": [
            {"label": "$match + $group + $sort",
             "codigo": (
                 "db.evaluaciones.aggregate([\n"
                 "  {$match: {calificacion: {$gte: 3}}},\n"
                 "  {$group: {_id: \"$sede_id.nombre_sede\", promedio: {$avg: \"$calificacion\"}, total: {$sum: 1}}},\n"
                 "  {$sort: {promedio: -1}}\n"
                 "])"
             )},
            {"label": "$match + $project",
             "codigo": (
                 "db.estudiantes.aggregate([\n"
                 "  {$match: {subsidio_activo: true}},\n"
                 "  {$project: {nombre_completo: 1, facultad: 1, semestre: 1, _id: 0}}\n"
                 "])"
             )},
            {"label": "$group + $count por facultad",
             "codigo": (
                 "db.estudiantes.aggregate([\n"
                 "  {$group: {_id: \"$facultad\", total: {$sum: 1}}},\n"
                 "  {$sort: {total: -1}}\n"
                 "])"
             )},
            {"label": "$unwind + $group",
             "codigo": (
                 "db.menus.aggregate([\n"
                 "  {$unwind: \"$ingredientes\"},\n"
                 "  {$group: {_id: \"$ingredientes\", apariciones: {$sum: 1}}},\n"
                 "  {$sort: {apariciones: -1}},\n"
                 "  {$limit: 10}\n"
                 "])"
             )},
        ]
    },
    {
        "categoria": "✏️ Escritura",
        "items": [
            {"label": "updateOne",
             "codigo": (
                 "db.proveedores.updateOne(\n"
                 "  {nit: \"900123456-7\"},\n"
                 "  {$set: {estado_activo: false}}\n"
                 ")"
             )},
            {"label": "deleteOne",
             "codigo": "db.consumos.deleteOne({validacion_identidad: false})"},
        ]
    },
]

BADGE_FECHA = {
    "ISODate": ("ISODate", "#79C0FF"),
    "Date":    ("Date()",  "#D2A8FF"),
    "string":  ("string",  "#FFA657"),
}


def _render_tabla(docs: list):
    if not docs:
        st.markdown('<div class="term-scalar">— sin resultados —</div>', unsafe_allow_html=True)
        return

    cols = []
    seen = set()
    for doc in docs:
        if isinstance(doc, dict):
            for k in doc.keys():
                if k not in seen:
                    cols.append(k)
                    seen.add(k)

    if not cols:
        st.markdown(f'<div class="term-scalar">{json.dumps(docs, ensure_ascii=False, indent=2)}</div>',
                    unsafe_allow_html=True)
        return

    headers = "".join(f"<th>{c}</th>" for c in cols)
    rows_html = ""
    for doc in docs:
        if not isinstance(doc, dict):
            rows_html += f'<tr><td colspan="{len(cols)}">{doc}</td></tr>'
            continue
        cells = ""
        for c in cols:
            val = doc.get(c, "")
            if val is None or val == "":
                cells += '<td class="td-null">null</td>'
            elif isinstance(val, bool):
                cls = "td-bool-true" if val else "td-bool-false"
                cells += f'<td class="{cls}">{"true" if val else "false"}</td>'
            elif isinstance(val, (int, float)):
                cells += f'<td class="td-num">{val}</td>'
            elif isinstance(val, dict):
                txt = json.dumps(val, ensure_ascii=False)
                display = txt[:60] + "…" if len(txt) > 60 else txt
                cells += f'<td title="{txt}">{display}</td>'
            elif isinstance(val, list):
                txt = ", ".join(str(i) for i in val[:3])
                if len(val) > 3:
                    txt += f" +{len(val)-3}"
                cells += f"<td>{txt}</td>"
            else:
                txt = str(val)
                display = txt if len(txt) <= 60 else txt[:57] + "…"
                cells += f'<td title="{txt}">{display}</td>'
        rows_html += f"<tr>{cells}</tr>"

    st.markdown(
        f'<div style="overflow-x:auto;">'
        f'<table class="term-table"><thead><tr>{headers}</tr></thead>'
        f'<tbody>{rows_html}</tbody></table></div>',
        unsafe_allow_html=True,
    )


def _render_lista(datos: list):
    items_html = "".join(
        f'<div class="term-list-item">'
        f'<span class="td-num">[{i}]</span>&nbsp;&nbsp;{v}'
        f'</div>'
        for i, v in enumerate(datos)
    )
    st.markdown(f'<div class="term-list-wrap">{items_html}</div>', unsafe_allow_html=True)


FILAS_POR_PAGINA = 25


def _render_paginacion_terminal(total_docs: int, pagina_actual: int) -> int:
    """Renderiza controles de paginación y devuelve la página activa."""
    total_pags = max(1, -(-total_docs // FILAS_POR_PAGINA))   # ceil division
    if total_pags <= 1:
        return pagina_actual

    nueva_pagina = pagina_actual
    c1, c2, c3, c4, c5 = st.columns([1, 1, 3, 1, 1])

    with c1:
        if st.button("⟪", key="term_primera", disabled=pagina_actual <= 1,
                     help="Primera página", use_container_width=True):
            nueva_pagina = 1
    with c2:
        if st.button("‹", key="term_prev", disabled=pagina_actual <= 1,
                     help="Página anterior", use_container_width=True):
            nueva_pagina = pagina_actual - 1
    with c3:
        st.markdown(
            f'<div class="term-pag-info">'
            f'Página <strong>{pagina_actual}</strong> de <strong>{total_pags}</strong>'
            f'&nbsp;·&nbsp; {total_docs} documentos'
            f'</div>',
            unsafe_allow_html=True,
        )
    with c4:
        if st.button("›", key="term_next", disabled=pagina_actual >= total_pags,
                     help="Página siguiente", use_container_width=True):
            nueva_pagina = pagina_actual + 1
    with c5:
        if st.button("⟫", key="term_ultima", disabled=pagina_actual >= total_pags,
                     help="Última página", use_container_width=True):
            nueva_pagina = total_pags

    return nueva_pagina


def _render_resultado(resultado: dict):
    tipo           = resultado.get("tipo")
    metodo         = resultado.get("metodo", "")
    sintaxis_fecha = resultado.get("sintaxis_fecha")

    # ── Badges de cabecera ──
    if tipo == "error":
        badge_estado = '<span class="term-badge-error">ERROR</span>'
    elif tipo in ("tabla", "lista"):
        n = resultado.get("total", 0)
        total_bd = resultado.get("total_bd")
        truncado = resultado.get("truncado", False)
        if total_bd and total_bd > n:
            badge_estado = (
                f'<span class="term-badge-warn">'
                f'{n} cargados · {total_bd:,} en BD</span>'
            )
        else:
            badge_estado = (
                f'<span class="term-badge-{"warn" if truncado else "ok"}">'
                f'{n} resultado{"s" if n != 1 else ""}</span>'
            )
    else:
        badge_estado = '<span class="term-badge-ok">OK</span>'

    badge_metodo = f'<span class="term-badge-method">{metodo}</span>' if metodo else ""

    badge_fecha = ""
    if sintaxis_fecha and sintaxis_fecha in BADGE_FECHA:
        label, color = BADGE_FECHA[sintaxis_fecha]
        badge_fecha = (
            f'<span class="term-badge-fecha" style="border-color:{color};color:{color};">'
            f'📅 {label}</span>'
        )

    st.markdown(
        f'<div class="term-output">'
        f'<div class="term-output-header">'
        f'<div style="display:flex;gap:8px;align-items:center;">'
        f'{badge_metodo}{badge_fecha}'
        f'</div>'
        f'<div>{badge_estado}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    if tipo == "error":
        st.markdown(f'<div class="term-error">{resultado["mensaje"]}</div>', unsafe_allow_html=True)

    elif tipo == "escalar":
        val = resultado.get("valor", "")
        val_str = (
            json.dumps(val, indent=2, ensure_ascii=False)
            if isinstance(val, dict) else str(val)
        )
        st.markdown(f'<div class="term-scalar">{val_str}</div>', unsafe_allow_html=True)

    elif tipo == "lista":
        _render_lista(resultado.get("datos", []))

    elif tipo == "tabla":
        todos = resultado.get("datos", [])
        total_docs = len(todos)

        # ── Paginación: calcular slice ──
        pagina_actual = st.session_state.get("terminal_pagina", 1)
        inicio = (pagina_actual - 1) * FILAS_POR_PAGINA
        fin    = inicio + FILAS_POR_PAGINA
        pagina_docs = todos[inicio:fin]

        _render_tabla(pagina_docs)

        if resultado.get("truncado"):
            st.markdown(
                '<div class="term-truncated-notice">'
                f'⚠ Se cargaron los primeros 500 documentos de la BD. '
                'Usa .limit(N) para acotar la consulta.'
                '</div>',
                unsafe_allow_html=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Controles de página FUERA del div (Streamlit no mezcla bien widgets dentro de HTML) ──
    if tipo == "tabla":
        todos = resultado.get("datos", [])
        if len(todos) > FILAS_POR_PAGINA:
            nueva_pagina = _render_paginacion_terminal(len(todos), st.session_state.terminal_pagina)
            if nueva_pagina != st.session_state.terminal_pagina:
                st.session_state.terminal_pagina = nueva_pagina
                st.rerun()


def seccion_terminal():
    st.markdown(TERMINAL_CSS, unsafe_allow_html=True)
    svc = _get_terminal_svc()

    # ── Session state ──
    if "terminal_historial" not in st.session_state:
        st.session_state.terminal_historial = []
    if "terminal_consulta" not in st.session_state:
        st.session_state.terminal_consulta = "db.consumos.countDocuments({})"
    if "terminal_resultado" not in st.session_state:
        st.session_state.terminal_resultado = None
    if "terminal_pagina" not in st.session_state:
        st.session_state.terminal_pagina = 1

    st.markdown('<h2 style="margin-bottom:4px;">Terminal MongoDB</h2>', unsafe_allow_html=True)
    st.markdown(
        '<p style="color:#5C6470;font-size:14px;margin-bottom:20px;">'
        'Sintaxis nativa del shell de MongoDB. Claves sin comillas, '
        '<code>true</code>/<code>false</code>, <code>ISODate()</code>, '
        '<code>$match</code>, <code>$group</code>… exactamente como en Compass o mongosh.'
        '</p>',
        unsafe_allow_html=True,
    )

    col_main, col_side = st.columns([3, 1])

    with col_main:
        st.markdown(
            '<div class="term-shell">'
            '<div class="term-titlebar">'
            '<div class="term-dots">'
            '<div class="term-dot term-dot-red"></div>'
            '<div class="term-dot term-dot-yellow"></div>'
            '<div class="term-dot term-dot-green"></div>'
            '</div>'
            '<span class="term-title-label">comedor_universitario — mongosh</span>'
            '</div>'
            '<div class="term-body">',
            unsafe_allow_html=True,
        )

        consulta = st.text_area(
            label="consulta",
            value=st.session_state.terminal_consulta,
            height=120,
            placeholder="db.estudiantes.findOne({semestre: 4})",
            label_visibility="collapsed",
            key="terminal_input",
        )

        st.markdown("</div></div>", unsafe_allow_html=True)

        col_run, col_clear, _ = st.columns([1, 1, 4])
        with col_run:
            ejecutar = st.button("▶  Ejecutar", type="primary", use_container_width=True)
        with col_clear:
            limpiar = st.button("✕  Limpiar", use_container_width=True)

        if limpiar:
            st.session_state.terminal_consulta = ""
            st.session_state.terminal_resultado = None
            st.session_state.terminal_pagina = 1
            st.rerun()

        if ejecutar and consulta.strip():
            st.session_state.terminal_consulta = consulta
            st.session_state.terminal_pagina = 1   # reset página al ejecutar
            with st.spinner("Ejecutando…"):
                resultado = svc.ejecutar(consulta)
            st.session_state.terminal_resultado = resultado
            st.session_state.terminal_historial.insert(0, {
                "consulta": consulta,
                "resultado": resultado,
                "ts": datetime.now().strftime("%H:%M:%S"),
            })
            st.session_state.terminal_historial = st.session_state.terminal_historial[:20]
            st.rerun()

        if st.session_state.terminal_resultado is not None:
            _render_resultado(st.session_state.terminal_resultado)

    with col_side:
        for grupo in EJEMPLOS:
            with st.expander(grupo["categoria"], expanded=False):
                for ej in grupo["items"]:
                    st.markdown(
                        f'<div class="term-example-label">{ej["label"]}</div>'
                        f'<div class="term-example">{ej["codigo"]}</div>',
                        unsafe_allow_html=True,
                    )
                    if st.button("Usar", key=f"ej_{ej['label']}", use_container_width=True):
                        st.session_state.terminal_consulta = ej["codigo"]
                        st.session_state.terminal_resultado = None
                        st.rerun()

        if st.session_state.terminal_historial:
            with st.expander("🕑 Historial", expanded=False):
                for i, entrada in enumerate(st.session_state.terminal_historial):
                    tipo  = entrada["resultado"].get("tipo", "")
                    icono = "✓" if tipo != "error" else "✗"
                    color = "#27C93F" if tipo != "error" else "#FF5F56"
                    corta = entrada["consulta"].replace("\n", " ")
                    corta = corta if len(corta) <= 45 else corta[:42] + "…"
                    st.markdown(
                        f'<div class="term-history-item">'
                        f'<span style="color:{color};font-weight:700;">{icono}</span>'
                        f'<span class="term-history-code">{corta}</span>'
                        f'<span class="term-history-time">{entrada["ts"]}</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    if st.button("↩", key=f"hist_{i}", use_container_width=True):
                        st.session_state.terminal_consulta = entrada["consulta"]
                        st.session_state.terminal_resultado = None
                        st.rerun()