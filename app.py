import streamlit as st
from datetime import datetime
from bson import ObjectId
from models import Proveedor, Sede, Estudiante, Consumo, Menu, Evaluacion, crear_colecciones
from connection import obtener_bd
from services import (
    ProveedorService, SedeService, EstudianteService, ConsumoService,
    MenuService, EvaluacionService
)
from estilos import aplicar_estilos, mostrar_header, render_stat_card

st.set_page_config(page_title="Subsidio de Alimentación", layout="wide")

aplicar_estilos()
mostrar_header()

REGISTROS_POR_PAGINA = 20

# ── Session state init ──
_INIT = {
    "seccion": "Proveedores",
    "modo_form": "crear",
    "id_edicion": None,
    "confirmar_eliminar": None,
    "show_form": False,
    "_prev_seccion": None,
    "db_error": None,
    "pag_proveedores": 1,
    "pag_sedes": 1,
    "pag_estudiantes": 1,
    "pag_consumos": 1,
    "pag_menus": 1,
    "pag_evaluaciones": 1,
}
for k, v in _INIT.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Servicios cacheados (solo se crean UNA VEZ) ──
@st.cache_resource
def _init_servicios():
    db = obtener_bd()
    crear_colecciones(db)
    return (
        ProveedorService(),
        SedeService(),
        EstudianteService(),
        ConsumoService(),
        MenuService(),
        EvaluacionService(),
    )

try:
    proveedor_svc, sede_svc, estudiante_svc, consumo_svc, menu_svc, evaluacion_svc = _init_servicios()
    svc_map = {
        "Proveedores": proveedor_svc,
        "Sedes": sede_svc,
        "Estudiantes": estudiante_svc,
        "Consumos": consumo_svc,
        "Menús": menu_svc,
        "Evaluaciones": evaluacion_svc,
    }
except Exception as e:
    st.session_state.db_error = str(e)
    proveedor_svc = sede_svc = estudiante_svc = consumo_svc = menu_svc = evaluacion_svc = None
    svc_map = {}

# ── Mapeo de claves de sección usadas en los links de la tabla ──
SECC_SVC = {
    "proveedores": proveedor_svc,
    "sedes": sede_svc,
    "estudiantes": estudiante_svc,
    "consumos": consumo_svc,
    "menus": menu_svc,
    "evaluaciones": evaluacion_svc,
}
SECC_NOMBRE = {
    "proveedores": "Proveedores",
    "sedes": "Sedes",
    "estudiantes": "Estudiantes",
    "consumos": "Consumos",
    "menus": "Menús",
    "evaluaciones": "Evaluaciones",
}

# ── Procesar acciones que vienen de los links Editar/Eliminar de la tabla ──
qp = st.query_params
if "accion" in qp:
    accion = qp.get("accion")
    sec = qp.get("sec")
    rid = qp.get("id")
    servicio_qp = SECC_SVC.get(sec)
    if servicio_qp and rid:
        st.session_state._seccion_pendiente = SECC_NOMBRE.get(sec)
        if accion == "editar":
            obj = servicio_qp.obtener_por_id(rid)
            if obj:
                for k, v in obj.__dict__.items():
                    if k != "_id":
                        st.session_state[f"edit_{k}"] = v
                st.session_state.id_edicion = rid
                st.session_state.modo_form = "editar"
                st.session_state.show_form = True
        elif accion == "eliminar":
            st.session_state.confirmar_eliminar = rid
    st.query_params.clear()
    st.rerun()

# ── Sidebar ──
_opciones_nav = ["Proveedores", "Sedes", "Estudiantes", "Consumos", "Menús", "Evaluaciones"]
_idx_default = 0
if "_seccion_pendiente" in st.session_state:
    pendiente = st.session_state.pop("_seccion_pendiente")
    if pendiente in _opciones_nav:
        _idx_default = _opciones_nav.index(pendiente)
        st.session_state.seccion = pendiente
        st.session_state._prev_seccion = pendiente

with st.sidebar:
    import os, base64
    logo_img = ""
    for ext in ["png", "svg", "jpg", "jpeg"]:
        p = f"icons/logo.{ext}"
        if os.path.exists(p):
            with open(p, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            mime = "svg+xml" if ext == "svg" else ext
            logo_img = f'data:image/{mime};base64,{b64}'
            break
    if logo_img:
        st.markdown(
            f'<div style="text-align:center;padding:16px 0 0px 0;margin-bottom:20px;">'
            f'<img src="{logo_img}" style="max-width:80%;height:auto;"></div>',
            unsafe_allow_html=True
        )

    seccion = st.radio(
        "Ir a",
        _opciones_nav,
        index=_idx_default,
        label_visibility="collapsed",
        key="nav_radio"
    )

# ── Section change → reset form y páginas ──
if st.session_state._prev_seccion is not None and st.session_state._prev_seccion != seccion:
    st.session_state.show_form = False
    st.session_state.modo_form = "crear"
    st.session_state.id_edicion = None
    st.session_state.confirmar_eliminar = None
    st.session_state.pag_proveedores = 1
    st.session_state.pag_sedes = 1
    st.session_state.pag_estudiantes = 1
    st.session_state.pag_consumos = 1
    st.session_state.pag_menus = 1
    st.session_state.pag_evaluaciones = 1
    for k in list(st.session_state.keys()):
        if k.startswith("edit_"):
            del st.session_state[k]

st.session_state.seccion = seccion
st.session_state._prev_seccion = seccion


# ── Helpers ──
def limpiar_edit():
    for k in list(st.session_state.keys()):
        if k.startswith("edit_"):
            del st.session_state[k]


def cancelar_form():
    st.session_state.show_form = False
    st.session_state.modo_form = "crear"
    st.session_state.id_edicion = None
    limpiar_edit()
    st.rerun()


# ────────── PAGINACIÓN ──────────
def render_paginacion(total, pagina_actual, key):
    total_paginas = max(1, -(-total // REGISTROS_POR_PAGINA))  # ceil division
    if total_paginas <= 1:
        if total > 0:
            st.markdown(
                f'<p style="color:#5C6470;font-size:13px;margin-top:8px;">'
                f'{total} registro{"s" if total != 1 else ""} en total</p>',
                unsafe_allow_html=True
            )
        return pagina_actual

    nueva_pagina = pagina_actual
    cols = st.columns([1, 3, 1])
    with cols[0]:
        if st.button("← Anterior", key=f"prev_{key}", disabled=pagina_actual <= 1):
            nueva_pagina = pagina_actual - 1
    with cols[1]:
        st.markdown(
            f'<p style="text-align:center;color:#5C6470;font-size:13px;margin-top:8px;">'
            f'Página <strong>{pagina_actual}</strong> de <strong>{total_paginas}</strong>'
            f'&nbsp;·&nbsp; {total} registros en total</p>',
            unsafe_allow_html=True
        )
    with cols[2]:
        if st.button("Siguiente →", key=f"next_{key}", disabled=pagina_actual >= total_paginas):
            nueva_pagina = pagina_actual + 1
    return nueva_pagina


# ────────── TABLA ──────────
def render_tabla(items, cols_def, id_field, servicio, lookup=None, seccion_key="", display_map=None):
    if not items:
        st.markdown('<p style="color:#5C6470;font-size:14px;">No hay registros.</p>', unsafe_allow_html=True)
        return

    if display_map is None:
        display_map = {}

    def fmt(item, attr):
        val = getattr(item, attr, "")
        # Si es dict y hay display_map, extraer subcampo
        if isinstance(val, dict) and attr in display_map:
            val = val.get(display_map[attr], "")
        # Si hay lookup, mapear el valor (si es ObjectId o string)
        if lookup and attr in lookup:
            val = lookup[attr].get(str(val), str(val))
        # Formatear tipos
        if isinstance(val, datetime):
            val = val.strftime("%Y-%m-%d")
        elif isinstance(val, bool):
            val = "Sí" if val else "No"
        elif isinstance(val, ObjectId):
            val = str(val)[:8] + "…"
        elif val is None:
            val = ""
        else:
            val = str(val)
        # Si es booleano para badge
        if isinstance(val, bool):
            bc = "badge-active" if val else "badge-inactive"
            return f'<span class="badge {bc}">{val}</span>'
        # Si el valor original era bool y lo convertimos, no lo tratamos como badge
        # pero en este punto val ya es string, así que no se puede saber.
        # Mejor manejamos el badge para "Sí"/"No" en el lookup o con un campo especial.
        return val

    headers = "".join(f"<th>{c[0]}</th>" for c in cols_def) + "<th>Editar</th><th>Eliminar</th>"

    rows_html = ""
    for item in items:
        cid = str(getattr(item, id_field))
        cells = "".join(f"<td>{fmt(item, c[2])}</td>" for c in cols_def)
        edit_link = (
            f'<a class="row-icon icon-edit" href="?accion=editar&sec={seccion_key}&id={cid}" '
            f'title="Editar"><i class="fas fa-pen"></i></a>'
        )
        del_link = (
            f'<a class="row-icon icon-delete" href="?accion=eliminar&sec={seccion_key}&id={cid}" '
            f'title="Eliminar"><i class="fas fa-trash"></i></a>'
        )
        rows_html += f'<tr>{cells}<td class="cell-icon">{edit_link}</td><td class="cell-icon">{del_link}</td></tr>'

    st.markdown(f"""
    <div class="table-wrap">
        <table class="real-table">
            <thead><tr>{headers}</tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)


# ────────── FORMULARIOS ──────────
def form_proveedor():
    tit = "Editar proveedor" if st.session_state.modo_form == "editar" else "Nuevo proveedor"
    with st.form("form_proveedor"):
        st.markdown(
            f'<h3 style="color:#0B2545;font-family:\'Source Serif 4\',serif;'
            f'font-size:1.1rem;font-weight:600;margin-bottom:12px;">{tit}</h3>',
            unsafe_allow_html=True
        )
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre empresa", value=st.session_state.get("edit_nombre_empresa", ""))
            nit_val = st.text_input("NIT", value=st.session_state.get("edit_nit", ""))
            contacto = st.text_input("Contacto", value=st.session_state.get("edit_contacto_nombre", ""))
            telefono = st.text_input("Teléfono", value=st.session_state.get("edit_telefono", ""))
        with c2:
            correo = st.text_input("Correo", value=st.session_state.get("edit_correo", ""))
            frecuencia = st.text_input("Frecuencia entrega", value=st.session_state.get("edit_frecuencia_entrega", ""))
            activo = st.checkbox("Activo", value=st.session_state.get("edit_estado_activo", True))
        cols = st.columns(2)
        if cols[0].form_submit_button(
            "Guardar" if st.session_state.modo_form == "crear" else "Actualizar", type="primary"
        ):
            if st.session_state.modo_form == "editar":
                proveedor_svc.actualizar(st.session_state.id_edicion, {
                    "nombre_empresa": nombre, "nit": nit_val, "contacto_nombre": contacto,
                    "telefono": telefono, "correo": correo, "frecuencia_entrega": frecuencia,
                    "estado_activo": activo
                })
                st.success("Proveedor actualizado")
            else:
                p = Proveedor(nombre, nit_val, telefono, correo, activo,
                              contacto_nombre=contacto, frecuencia_entrega=frecuencia)
                proveedor_svc.insertar(p)
                st.success("Proveedor guardado")
            limpiar_edit()
            st.session_state.show_form = False
            st.rerun()
        if cols[1].form_submit_button("Cancelar"):
            cancelar_form()


def form_sede(proveedores_lista):
    tit = "Editar sede" if st.session_state.modo_form == "editar" else "Nueva sede"
    prov_opts = {str(p._id): p.nombre_empresa for p in proveedores_lista}
    edit_prov_str = str(st.session_state.get("edit_proveedor_id", ""))
    prov_keys = list(prov_opts.keys())
    default_idx = prov_keys.index(edit_prov_str) if edit_prov_str in prov_keys else 0

    with st.form("form_sede"):
        st.markdown(
            f'<h3 style="color:#0B2545;font-family:\'Source Serif 4\',serif;'
            f'font-size:1.1rem;font-weight:600;margin-bottom:12px;">{tit}</h3>',
            unsafe_allow_html=True
        )
        c1, c2 = st.columns(2)
        with c1:
            nombre_sede = st.text_input("Nombre sede", value=st.session_state.get("edit_nombre_sede", ""))
            ubicacion = st.text_input("Ubicación", value=st.session_state.get("edit_ubicacion", ""))
            capacidad = st.number_input("Capacidad máxima", min_value=1, step=1,
                                        value=st.session_state.get("edit_capacidad_maxima", 100))
            cupos = st.number_input("Cupos disponibles", min_value=0, step=1,
                                    value=st.session_state.get("edit_cupos_disponibles", 0))
        with c2:
            horario = st.text_input("Horario atención", value=st.session_state.get("edit_horario_atencion", ""))
            activo_sede = st.checkbox("Activa", value=st.session_state.get("edit_estado_activo", True))
            prov_id = st.selectbox(
                "Proveedor", options=prov_keys,
                format_func=lambda x: prov_opts[x],
                index=default_idx
            ) if prov_opts else None
        cols = st.columns(2)
        if cols[0].form_submit_button(
            "Guardar" if st.session_state.modo_form == "crear" else "Actualizar", type="primary"
        ):
            if prov_id:
                if st.session_state.modo_form == "editar":
                    sede_svc.actualizar(st.session_state.id_edicion, {
                        "nombre_sede": nombre_sede, "ubicacion": ubicacion,
                        "capacidad_maxima": int(capacidad), "cupos_disponibles": int(cupos),
                        "horario_atencion": horario, "estado_activo": activo_sede,
                        "proveedor_id": ObjectId(prov_id)
                    })
                    st.success("Sede actualizada")
                else:
                    s = Sede(nombre_sede, ubicacion, int(capacidad), activo_sede,
                             ObjectId(prov_id), cupos_disponibles=int(cupos), horario_atencion=horario)
                    sede_svc.insertar(s)
                    st.success("Sede guardada")
                limpiar_edit()
                st.session_state.show_form = False
                st.rerun()
        if cols[1].form_submit_button("Cancelar"):
            cancelar_form()


def form_estudiante():
    tit = "Editar estudiante" if st.session_state.modo_form == "editar" else "Nuevo estudiante"
    with st.form("form_estudiante"):
        st.markdown(
            f'<h3 style="color:#0B2545;font-family:\'Source Serif 4\',serif;'
            f'font-size:1.1rem;font-weight:600;margin-bottom:12px;">{tit}</h3>',
            unsafe_allow_html=True
        )
        c1, c2 = st.columns(2)
        with c1:
            codigo = st.text_input("Código", value=st.session_state.get("edit_codigo_estudiante", ""))
            nombre_completo = st.text_input("Nombre completo", value=st.session_state.get("edit_nombre_completo", ""))
            correo_est = st.text_input("Correo", value=st.session_state.get("edit_correo", ""))
            telefono_est = st.text_input("Teléfono", value=st.session_state.get("edit_telefono", ""))
            facultad = st.text_input("Facultad", value=st.session_state.get("edit_facultad", ""))
            programa = st.text_input("Programa", value=st.session_state.get("edit_programa", ""))
        with c2:
            semestre = st.number_input("Semestre", min_value=1, step=1,
                                       value=st.session_state.get("edit_semestre", 1))
            estrato_val = st.number_input("Estrato", min_value=1, max_value=6, step=1,
                                          value=st.session_state.get("edit_estrato", 1))
            inicio = st.date_input("Inicio subsidio")
            fin = st.date_input("Fin subsidio")
            tipo = st.selectbox(
                "Tipo almuerzo", ["Carnívoro", "Vegetariano"],
                index=["Carnívoro", "Vegetariano"].index(
                    st.session_state.get("edit_tipo_almuerzo", "Carnívoro")
                )
            )
            activo_est = st.checkbox("Subsidio activo", value=st.session_state.get("edit_subsidio_activo", True))
        cols = st.columns(2)
        if cols[0].form_submit_button(
            "Guardar" if st.session_state.modo_form == "crear" else "Actualizar", type="primary"
        ):
            if st.session_state.modo_form == "editar":
                estudiante_svc.actualizar(st.session_state.id_edicion, {
                    "codigo_estudiante": codigo, "nombre_completo": nombre_completo,
                    "correo": correo_est, "telefono": telefono_est, "facultad": facultad,
                    "programa": programa, "semestre": int(semestre), "estrato": int(estrato_val),
                    "tipo_almuerzo": tipo, "subsidio_activo": activo_est
                })
                st.success("Estudiante actualizado")
            else:
                e = Estudiante(
                    codigo, nombre_completo, correo_est, activo_est,
                    telefono=telefono_est, facultad=facultad, programa=programa,
                    semestre=int(semestre), estrato=int(estrato_val),
                    fecha_inicio_subsidio=datetime.combine(inicio, datetime.min.time()),
                    fecha_fin_subsidio=datetime.combine(fin, datetime.min.time()),
                    tipo_almuerzo=tipo
                )
                estudiante_svc.insertar(e)
                st.success("Estudiante guardado")
            limpiar_edit()
            st.session_state.show_form = False
            st.rerun()
        if cols[1].form_submit_button("Cancelar"):
            cancelar_form()


def form_consumo(estudiantes_lista, sedes_lista):
    tit = "Editar consumo" if st.session_state.modo_form == "editar" else "Nuevo consumo"
    opts_est = {str(e._id): f"{e.nombre_completo} ({e.codigo_estudiante})" for e in estudiantes_lista}
    opts_sede = {str(s._id): s.nombre_sede for s in sedes_lista}

    with st.form("form_consumo"):
        st.markdown(
            f'<h3 style="color:#0B2545;font-family:\'Source Serif 4\',serif;'
            f'font-size:1.1rem;font-weight:600;margin-bottom:12px;">{tit}</h3>',
            unsafe_allow_html=True
        )
        c1, c2 = st.columns(2)
        with c1:
            est_id_key = st.selectbox(
                "Estudiante", options=list(opts_est.keys()),
                format_func=lambda x: opts_est[x]
            ) if opts_est else None
            sede_id_key = st.selectbox(
                "Sede", options=list(opts_sede.keys()),
                format_func=lambda x: opts_sede[x]
            ) if opts_sede else None
        with c2:
            fecha = st.date_input("Fecha consumo", datetime.now())
            hora = st.text_input("Hora ingreso", "12:00")
            validado = st.checkbox("Identidad validada", True)
        cols = st.columns(2)
        if cols[0].form_submit_button(
            "Guardar" if st.session_state.modo_form == "crear" else "Actualizar", type="primary"
        ):
            if est_id_key and sede_id_key:
                if st.session_state.modo_form == "editar":
                    consumo_svc.actualizar(st.session_state.id_edicion, {
                        "estudiante_id": ObjectId(est_id_key),
                        "sede_id": ObjectId(sede_id_key),
                        "fecha_consumo": datetime.combine(fecha, datetime.min.time()),
                        "hora_ingreso": hora, "validacion_identidad": validado
                    })
                    st.success("Consumo actualizado")
                else:
                    c = Consumo(
                        ObjectId(est_id_key), ObjectId(sede_id_key),
                        datetime.combine(fecha, datetime.min.time()),
                        validado, hora_ingreso=hora
                    )
                    consumo_svc.insertar(c)
                    st.success("Consumo guardado")
                limpiar_edit()
                st.session_state.show_form = False
                st.rerun()
        if cols[1].form_submit_button("Cancelar"):
            cancelar_form()


# ── Nuevos formularios ──
def form_menu():
    tit = "Editar menú" if st.session_state.modo_form == "editar" else "Nuevo menú"
    sedes_lista = sede_svc.obtener_todos()
    opts_sede = {str(s._id): s.nombre_sede for s in sedes_lista}
    edit_sede = st.session_state.get("edit_sede_id", "")
    default_sede_idx = list(opts_sede.keys()).index(edit_sede) if edit_sede in opts_sede else 0

    with st.form("form_menu"):
        st.markdown(
            f'<h3 style="color:#0B2545;font-family:\'Source Serif 4\',serif;'
            f'font-size:1.1rem;font-weight:600;margin-bottom:12px;">{tit}</h3>',
            unsafe_allow_html=True
        )
        c1, c2 = st.columns(2)
        with c1:
            sede_key = st.selectbox(
                "Sede", options=list(opts_sede.keys()),
                format_func=lambda x: opts_sede[x],
                index=default_sede_idx
            ) if opts_sede else None
            fecha = st.date_input("Fecha", value=st.session_state.get("edit_fecha", datetime.now().date()))
            tipo = st.selectbox(
                "Tipo comida",
                ["carnivoro", "vegetariano"],
                index=0 if st.session_state.get("edit_tipo_comida", "carnivoro") == "carnivoro" else 1
            )
        with c2:
            plato = st.text_area("Plato (sopa / seco)", value=st.session_state.get("edit_plato", ""))
            info_nutri = st.text_area("Info nutricional (JSON)", value=st.session_state.get("edit_info_nutricional", ""))
            ingredientes = st.text_input("Ingredientes (separados por coma)", value=st.session_state.get("edit_ingredientes", ""))
            alergias = st.text_input("Alergias (separadas por coma)", value=st.session_state.get("edit_advertencia_alergias", ""))

        cols = st.columns(2)
        if cols[0].form_submit_button(
            "Guardar" if st.session_state.modo_form == "crear" else "Actualizar", type="primary"
        ):
            if sede_key:
                data = {
                    "sede_id": {"nombre_sede": opts_sede[sede_key], "ubicacion": ""},
                    "fecha": datetime.combine(fecha, datetime.min.time()),
                    "tipo_comida": tipo,
                    "plato": plato,
                }
                if info_nutri:
                    data["info_nutricional"] = info_nutri
                if ingredientes:
                    data["ingredientes"] = [i.strip() for i in ingredientes.split(",") if i.strip()]
                if alergias:
                    data["advertencia_alergias"] = [a.strip() for a in alergias.split(",") if a.strip()]

                sede_doc = sede_svc.obtener_por_id(sede_key)
                if sede_doc:
                    data["sede_id"]["ubicacion"] = sede_doc.ubicacion

                if st.session_state.modo_form == "editar":
                    menu_svc.actualizar(st.session_state.id_edicion, data)
                    st.success("Menú actualizado")
                else:
                    menu = Menu(**data)
                    menu_svc.insertar(menu)
                    st.success("Menú guardado")
                limpiar_edit()
                st.session_state.show_form = False
                st.rerun()
        if cols[1].form_submit_button("Cancelar"):
            cancelar_form()


def form_evaluacion():
    tit = "Editar evaluación" if st.session_state.modo_form == "editar" else "Nueva evaluación"

    estudiantes_lista = estudiante_svc.obtener_todos()
    sedes_lista = sede_svc.obtener_todos()
    menus_lista = menu_svc.obtener_todos()

    opts_est = {str(e._id): f"{e.nombre_completo} ({e.codigo_estudiante})" for e in estudiantes_lista}
    opts_sede = {str(s._id): s.nombre_sede for s in sedes_lista}
    opts_menu = {str(m._id): f"{m.plato[:40]} - {m.fecha.strftime('%Y-%m-%d')}" for m in menus_lista}

    with st.form("form_evaluacion"):
        st.markdown(
            f'<h3 style="color:#0B2545;font-family:\'Source Serif 4\',serif;'
            f'font-size:1.1rem;font-weight:600;margin-bottom:12px;">{tit}</h3>',
            unsafe_allow_html=True
        )
        c1, c2 = st.columns(2)
        with c1:
            est_key = st.selectbox(
                "Estudiante", options=list(opts_est.keys()),
                format_func=lambda x: opts_est[x],
                index=0 if not st.session_state.get("edit_estudiante_id") else list(opts_est.keys()).index(st.session_state["edit_estudiante_id"])
            ) if opts_est else None
            sede_key = st.selectbox(
                "Sede", options=list(opts_sede.keys()),
                format_func=lambda x: opts_sede[x],
                index=0 if not st.session_state.get("edit_sede_id") else list(opts_sede.keys()).index(st.session_state["edit_sede_id"])
            ) if opts_sede else None
            menu_key = st.selectbox(
                "Menú", options=list(opts_menu.keys()),
                format_func=lambda x: opts_menu[x],
                index=0 if not st.session_state.get("edit_menu_id") else list(opts_menu.keys()).index(st.session_state["edit_menu_id"])
            ) if opts_menu else None
        with c2:
            fecha_eval = st.date_input("Fecha evaluación", value=st.session_state.get("edit_fecha_evaluacion", datetime.now().date()))
            calificacion = st.selectbox("Calificación", list(range(1, 6)), index=st.session_state.get("edit_calificacion", 3)-1)
            comentario = st.text_area("Comentario", value=st.session_state.get("edit_comentario", ""))
            sugerencias = st.text_area("Sugerencias", value=st.session_state.get("edit_sugerencias", ""))

        cols = st.columns(2)
        if cols[0].form_submit_button(
            "Guardar" if st.session_state.modo_form == "crear" else "Actualizar", type="primary"
        ):
            if est_key and sede_key and menu_key:
                est_doc = estudiantes_lista[[e for e in estudiantes_lista if str(e._id)==est_key][0]]
                sede_doc = sedes_lista[[s for s in sedes_lista if str(s._id)==sede_key][0]]
                menu_doc = menus_lista[[m for m in menus_lista if str(m._id)==menu_key][0]]

                data = {
                    "estudiante_id": {
                        "nombre_completo": est_doc.nombre_completo,
                        "codigo_estudiante": est_doc.codigo_estudiante,
                        "semestre": est_doc.semestre,
                        "fecha_inicio_subsidio": est_doc.fecha_inicio_subsidio,
                        "fecha_fin_subsidio": est_doc.fecha_fin_subsidio,
                    },
                    "sede_id": {
                        "nombre_sede": sede_doc.nombre_sede,
                        "ubicacion": sede_doc.ubicacion,
                    },
                    "menu_id": {
                        "plato": menu_doc.plato,
                        "tipo_comida": menu_doc.tipo_comida,
                    },
                    "fecha_evaluacion": datetime.combine(fecha_eval, datetime.min.time()),
                    "calificacion": calificacion,
                    "comentario": comentario if comentario else None,
                    "sugerencias": sugerencias if sugerencias else None,
                }
                if st.session_state.modo_form == "editar":
                    evaluacion_svc.actualizar(st.session_state.id_edicion, data)
                    st.success("Evaluación actualizada")
                else:
                    evaluacion = Evaluacion(**data)
                    evaluacion_svc.insertar(evaluacion)
                    st.success("Evaluación guardada")
                limpiar_edit()
                st.session_state.show_form = False
                st.rerun()
        if cols[1].form_submit_button("Cancelar"):
            cancelar_form()


# ────────── SECCIONES ──────────
def seccion_proveedores():
    total = proveedor_svc.contar()
    pagina = st.session_state.pag_proveedores
    todos = proveedor_svc.obtener_pagina(pagina, REGISTROS_POR_PAGINA)

    st.markdown('<h2 style="margin-bottom:4px;">Proveedores</h2>', unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    with m1:
        render_stat_card("truck", total, "Total proveedores", "#1B4079")
    with m2:
        render_stat_card(
            "check-circle",
            proveedor_svc.coleccion.count_documents({"estado_activo": True}),
            "Activos", "#C9A227"
        )
    with m3:
        render_stat_card(
            "ban",
            proveedor_svc.coleccion.count_documents({"estado_activo": False}),
            "Inactivos", "#5C6470"
        )

    if st.session_state.show_form:
        form_proveedor()
    else:
        if st.button("+ Agregar proveedor", key="btn_agregar_proveedor", type="primary"):
            limpiar_edit()
            st.session_state.modo_form = "crear"
            st.session_state.show_form = True
            st.rerun()

    render_tabla(
        todos,
        [("Empresa", 2, "nombre_empresa"), ("NIT", 1, "nit"), ("Contacto", 1, "contacto_nombre"),
         ("Teléfono", 1, "telefono"), ("Correo", 2, "correo"), ("Activo", 1, "estado_activo")],
        "_id", proveedor_svc, seccion_key="proveedores"
    )

    nueva_pagina = render_paginacion(total, pagina, "proveedores")
    if nueva_pagina != pagina:
        st.session_state.pag_proveedores = nueva_pagina
        st.rerun()


def seccion_sedes():
    total = sede_svc.contar()
    pagina = st.session_state.pag_sedes
    todos = sede_svc.obtener_pagina(pagina, REGISTROS_POR_PAGINA)

    proveedores_lista = proveedor_svc.obtener_todos()

    st.markdown('<h2 style="margin-bottom:4px;">Sedes</h2>', unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    with m1:
        render_stat_card("building", total, "Total sedes", "#1B4079")
    with m2:
        pipeline = [{"$group": {"_id": None, "total": {"$sum": "$capacidad_maxima"}}}]
        res = list(sede_svc.coleccion.aggregate(pipeline))
        cap_total = res[0]["total"] if res else 0
        render_stat_card("users", cap_total, "Capacidad total", "#C9A227")

    prov_lookup = {str(p._id): p.nombre_empresa for p in proveedores_lista}
    render_tabla(
        todos,
        [("Sede", 2, "nombre_sede"), ("Ubicación", 1, "ubicacion"),
         ("Capacidad", 1, "capacidad_maxima"), ("Activa", 1, "estado_activo")],
        "_id", sede_svc, seccion_key="sedes"
    )

    nueva_pagina = render_paginacion(total, pagina, "sedes")
    if nueva_pagina != pagina:
        st.session_state.pag_sedes = nueva_pagina
        st.rerun()


def seccion_estudiantes():
    st.markdown('<h2 style="margin-bottom:4px;">Estudiantes</h2>', unsafe_allow_html=True)

    total_sin_filtro = estudiante_svc.contar()
    m1, m2, m3 = st.columns(3)
    with m1:
        render_stat_card("user-graduate", total_sin_filtro, "Total estudiantes", "#1B4079")
    with m2:
        render_stat_card(
            "check-circle",
            estudiante_svc.coleccion.count_documents({"subsidio_activo": True}),
            "Subsidio activo", "#C9A227"
        )
    with m3:
        render_stat_card(
            "ban",
            estudiante_svc.coleccion.count_documents({"subsidio_activo": False}),
            "Inactivos", "#5C6470"
        )

    # ── Filtros ──
    st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        codigo_filtro = st.text_input("Buscar por código", placeholder="Ej: 2024101001", label_visibility="collapsed")
    with col_f2:
        semestre_opts = ["Todos"] + [str(i) for i in range(1, 13)]
        semestre_filtro = st.selectbox("Semestre", semestre_opts, index=0, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Construir filtro ──
    filtro = {}
    if codigo_filtro:
        filtro["codigo_estudiante"] = {"$regex": codigo_filtro, "$options": "i"}
    if semestre_filtro != "Todos":
        filtro["semestre"] = int(semestre_filtro)

    if filtro:
        total = estudiante_svc.contar_con_filtro(filtro)
        pagina = 1
        st.session_state.pag_estudiantes = 1
        todos = estudiante_svc.buscar_con_filtro(filtro, pagina, REGISTROS_POR_PAGINA)
    else:
        total = estudiante_svc.contar()
        pagina = st.session_state.pag_estudiantes
        todos = estudiante_svc.buscar_con_filtro({}, pagina, REGISTROS_POR_PAGINA)

    if st.session_state.show_form:
        form_estudiante()
    else:
        if st.button("+ Agregar estudiante", key="btn_agregar_estudiante", type="primary"):
            limpiar_edit()
            st.session_state.modo_form = "crear"
            st.session_state.show_form = True
            st.rerun()

    render_tabla(
        todos,
        [("Código", 1, "codigo_estudiante"), ("Nombre", 2, "nombre_completo"),
         ("Correo", 2, "correo"), ("Facultad", 1, "facultad"), ("Programa", 1, "programa"),
         ("Semestre", 1, "semestre"), ("Activo", 1, "subsidio_activo")],
        "_id", estudiante_svc, seccion_key="estudiantes"
    )

    nueva_pagina = render_paginacion(total, pagina, "estudiantes")
    if nueva_pagina != pagina:
        st.session_state.pag_estudiantes = nueva_pagina
        st.rerun()


def seccion_consumos():
    total = consumo_svc.contar()
    pagina = st.session_state.pag_consumos
    todos = consumo_svc.obtener_pagina(pagina, REGISTROS_POR_PAGINA)

    hoy = datetime.now().date()

    st.markdown('<h2 style="margin-bottom:4px;">Consumos</h2>', unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    with m1:
        render_stat_card("utensils", total, "Total consumos", "#1B4079")
    with m2:
        render_stat_card(
            "check-circle",
            consumo_svc.coleccion.count_documents({"validacion_identidad": True}),
            "Validados", "#C9A227"
        )
    with m3:
        inicio_hoy = datetime.combine(hoy, datetime.min.time())
        fin_hoy = datetime.combine(hoy, datetime.max.time())
        render_stat_card(
            "calendar-day",
            consumo_svc.coleccion.count_documents({
                "fecha_consumo": {"$gte": inicio_hoy, "$lte": fin_hoy}
            }),
            "Hoy", "#5C6470"
        )

    if st.session_state.show_form:
        estudiantes_lista = estudiante_svc.obtener_todos()
        sedes_lista = sede_svc.obtener_todos()
        form_consumo(estudiantes_lista, sedes_lista)
    else:
        if st.button("+ Agregar consumo", key="btn_agregar_consumo", type="primary"):
            limpiar_edit()
            st.session_state.modo_form = "crear"
            st.session_state.show_form = True
            st.rerun()

    render_tabla(
        todos,
        [("Estudiante", 2, "estudiante_id"), ("Sede", 2, "sede_id"),
         ("Fecha", 1, "fecha_consumo"), ("Hora", 1, "hora_ingreso"), ("Validado", 1, "validacion_identidad")],
        "_id", consumo_svc,
        display_map={"estudiante_id": "nombre_completo", "sede_id": "nombre_sede"},
        seccion_key="consumos"
    )

    nueva_pagina = render_paginacion(total, pagina, "consumos")
    if nueva_pagina != pagina:
        st.session_state.pag_consumos = nueva_pagina
        st.rerun()


# ── Nuevas secciones ──
def seccion_menus():
    total = menu_svc.contar()
    pagina = st.session_state.pag_menus
    todos = menu_svc.obtener_pagina(pagina, REGISTROS_POR_PAGINA)

    st.markdown('<h2 style="margin-bottom:4px;">Menús</h2>', unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    with m1:
        render_stat_card("utensils", total, "Total menús", "#1B4079")
    with m2:
        carn = menu_svc.coleccion.count_documents({"tipo_comida": "carnivoro"})
        render_stat_card("drumstick-bite", carn, "Carnívoros", "#C9A227")
    with m3:
        veg = menu_svc.coleccion.count_documents({"tipo_comida": "vegetariano"})
        render_stat_card("leaf", veg, "Vegetarianos", "#5C6470")

    if st.session_state.show_form:
        form_menu()
    else:
        if st.button("+ Agregar menú", key="btn_agregar_menu", type="primary"):
            limpiar_edit()
            st.session_state.modo_form = "crear"
            st.session_state.show_form = True
            st.rerun()

    sedes_lista = sede_svc.obtener_todos()
    sede_lookup = {str(s._id): s.nombre_sede for s in sedes_lista}
    render_tabla(
        todos,
        [("Fecha", 1, "fecha"), ("Sede", 2, "sede_id"), ("Tipo", 1, "tipo_comida"),
         ("Plato", 3, "plato")],
        "_id", menu_svc,
        lookup={"sede_id": sede_lookup},
        display_map={"sede_id": "nombre_sede"},
        seccion_key="menus"
    )

    nueva_pagina = render_paginacion(total, pagina, "menus")
    if nueva_pagina != pagina:
        st.session_state.pag_menus = nueva_pagina
        st.rerun()


def seccion_evaluaciones():
    total = evaluacion_svc.contar()
    pagina = st.session_state.pag_evaluaciones
    todos = evaluacion_svc.obtener_pagina(pagina, REGISTROS_POR_PAGINA)

    st.markdown('<h2 style="margin-bottom:4px;">Evaluaciones</h2>', unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    with m1:
        render_stat_card("star", total, "Total evaluaciones", "#1B4079")
    with m2:
        pipeline = [{"$group": {"_id": None, "prom": {"$avg": "$calificacion"}}}]
        res = list(evaluacion_svc.coleccion.aggregate(pipeline))
        prom = res[0]["prom"] if res else 0
        render_stat_card("chart-line", f"{prom:.1f}", "Promedio", "#C9A227")
    with m3:
        with_comment = evaluacion_svc.coleccion.count_documents({"comentario": {"$exists": True, "$ne": ""}})
        render_stat_card("comment", with_comment, "Con comentario", "#5C6470")

    if st.session_state.show_form:
        form_evaluacion()
    else:
        if st.button("+ Agregar evaluación", key="btn_agregar_evaluacion", type="primary"):
            limpiar_edit()
            st.session_state.modo_form = "crear"
            st.session_state.show_form = True
            st.rerun()

    render_tabla(
        todos,
        [("Estudiante", 2, "estudiante_id"), ("Sede", 1, "sede_id"),
         ("Fecha", 1, "fecha_evaluacion"), ("Calif.", 1, "calificacion"),
         ("Comentario", 2, "comentario")],
        "_id", evaluacion_svc,
        display_map={"estudiante_id": "nombre_completo", "sede_id": "nombre_sede"},
        seccion_key="evaluaciones"
    )

    nueva_pagina = render_paginacion(total, pagina, "evaluaciones")
    if nueva_pagina != pagina:
        st.session_state.pag_evaluaciones = nueva_pagina
        st.rerun()


# ────────── ELIMINACIÓN (modal real) ──────────
@st.dialog("Confirmar eliminación")
def confirmar_eliminacion_dialog(cid):
    st.warning("¿Estás seguro de eliminar este registro? Esta acción no se puede deshacer.")
    c1, c2 = st.columns(2)
    if c1.button("Sí, eliminar", type="primary", use_container_width=True):
        servicio = svc_map.get(st.session_state.seccion)
        if servicio:
            servicio.eliminar(cid)
        st.session_state.confirmar_eliminar = None
        st.success("Registro eliminado")
        st.rerun()
    if c2.button("Cancelar", use_container_width=True):
        st.session_state.confirmar_eliminar = None
        st.rerun()


if st.session_state.confirmar_eliminar:
    confirmar_eliminacion_dialog(st.session_state.confirmar_eliminar)


# ────────── RENDER ──────────
if st.session_state.db_error:
    st.error(f"No se pudo conectar a la base de datos: {st.session_state.db_error}")
    st.info("Verifica que MongoDB esté en ejecución y las credenciales en .env sean correctas.")
elif proveedor_svc is None:
    st.error("La aplicación no está disponible porque no hay conexión a la base de datos.")
    st.info("Verifica la conexión MongoDB en el archivo .env y reinicia la aplicación.")
else:
    secciones = {
        "Proveedores": seccion_proveedores,
        "Sedes": seccion_sedes,
        "Estudiantes": seccion_estudiantes,
        "Consumos": seccion_consumos,
        "Menús": seccion_menus,
        "Evaluaciones": seccion_evaluaciones,
    }
    if st.session_state.seccion in secciones:
        secciones[st.session_state.seccion]()