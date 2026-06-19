# ============================================================
# SIR ACP - M06 Gestión Documental y Expedientes
# Versión v2 funcional en Streamlit
# Interfaz y navegación homologadas con M01
# Contexto: Reasentamiento Panamá - ACP - IFC PS5
# ============================================================
# Incluye:
# - Interfaz responsive y corporativa compatible con tema claro/oscuro.
# - Memoria local JSON para conservar registros capturados.
# - 10 hogares simulados.
# - Relación 1:N entre hogares y predios.
# - Predios con polígonos irregulares de diferente número de vértices.
# - Gestión de documentos, catálogo documental, expedientes, checklist y revisiones.
# - Formularios reactivos con IDs secuenciales automáticos.
# - Fichas completas por registro seleccionado.
# - Filtros multiselección por zona, hogar, persona, predio, expediente, estado y categoría.
# - Mapa general con polígonos irregulares de predios.
# - Descarga CSV de tabla filtrada visible.
# ============================================================

import json
import re
from pathlib import Path
from datetime import date, datetime
from html import escape

import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium


# ============================================================
# 1. CONFIGURACIÓN GENERAL
# ============================================================

st.set_page_config(
    page_title="SIR ACP | M06 Gestión Documental",
    page_icon="📁",
    layout="wide",
    initial_sidebar_state="expanded",
)

COLOR_PRIMARIO_SOCIONAUT = "#073B5A"
COLOR_SECUNDARIO_SOCIONAUT = "#00A6A6"
COLOR_CORAL = "#F05A43"
COLOR_GRIS_CLARO = "#F4F7F9"
COLOR_BORDE = "#D6DEE6"

ARCHIVO_MEMORIA = Path("memoria_m06_gestion_documental_v2.json")
USUARIO_PROTOTIPO = "usuario_prototipo"


# ============================================================
# 2. ESQUEMA DE TABLAS, CATÁLOGOS Y RELACIONES
# ============================================================

ESQUEMA_M06 = {
    "lugares_poblados": {
        "titulo": "Lugares poblados",
        "llave": "id_lugar_poblado",
        "campos_principales": [
            "id_lugar_poblado", "nombre_lugar_poblado", "corregimiento", "distrito", "provincia", "zona", "prioridad"
        ],
        "campos": {
            "id_lugar_poblado": "Texto/UUID",
            "nombre_lugar_poblado": "Texto",
            "corregimiento": "Texto",
            "distrito": "Texto",
            "provincia": "Texto",
            "zona": "Catálogo",
            "prioridad": "Catálogo",
            "lat": "Decimal",
            "lon": "Decimal",
        },
    },
    "hogares": {
        "titulo": "Hogares",
        "llave": "id_hogar",
        "campos_principales": [
            "id_hogar", "codigo_hogar_campo", "nombre_referencia_hogar", "id_lugar_poblado", "zona", "tipo_afectacion", "estado_residencia"
        ],
        "campos": {
            "id_hogar": "Texto/UUID",
            "codigo_hogar_campo": "Texto",
            "nombre_referencia_hogar": "Texto",
            "id_lugar_poblado": "Catálogo relacional",
            "zona": "Catálogo",
            "tipo_afectacion": "Catálogo",
            "estado_residencia": "Catálogo",
            "observaciones_generales": "Texto largo",
        },
    },
    "personas": {
        "titulo": "Personas",
        "llave": "id_persona",
        "campos_principales": [
            "id_persona", "id_hogar", "nombres", "apellidos", "documento_identidad", "parentesco", "jefe_hogar"
        ],
        "campos": {
            "id_persona": "Texto/UUID",
            "id_hogar": "Catálogo relacional",
            "nombres": "Texto",
            "apellidos": "Texto",
            "documento_identidad": "Texto protegido",
            "telefono": "Texto",
            "parentesco": "Catálogo",
            "jefe_hogar": "Booleano",
            "observaciones": "Texto largo",
        },
    },
    "predios": {
        "titulo": "Predios",
        "llave": "id_predio",
        "campos_principales": [
            "id_predio", "id_hogar", "id_lugar_poblado", "uso_principal", "tipo_tenencia", "area_total_m2",
            "area_afectada_m2", "porcentaje_afectacion", "numero_vertices"
        ],
        "campos": {
            "id_predio": "Texto/UUID",
            "id_hogar": "Catálogo relacional opcional",
            "id_lugar_poblado": "Catálogo relacional",
            "cedula_catastral": "Texto",
            "uso_principal": "Catálogo",
            "tipo_tenencia": "Catálogo",
            "area_total_m2": "Decimal",
            "area_afectada_m2": "Decimal",
            "porcentaje_afectacion": "Número calculado",
            "numero_vertices": "Número calculado",
            "vertices_poligono": "Texto largo",
            "estado_liberacion": "Catálogo",
            "observaciones": "Texto largo",
        },
    },
    "catalogo_documental": {
        "titulo": "Catálogo documental",
        "llave": "id_tipo_documento",
        "campos_principales": [
            "id_tipo_documento", "categoria_documental", "tipo_documento", "aplica_a_hogar", "aplica_a_persona",
            "aplica_a_predio", "obligatorio", "estado_catalogo"
        ],
        "campos": {
            "id_tipo_documento": "Texto/UUID",
            "categoria_documental": "Catálogo",
            "tipo_documento": "Texto",
            "descripcion": "Texto largo",
            "aplica_a_hogar": "Booleano",
            "aplica_a_persona": "Booleano",
            "aplica_a_predio": "Booleano",
            "obligatorio": "Booleano",
            "vigencia_requerida": "Catálogo",
            "estado_catalogo": "Catálogo",
        },
    },
    "documentos": {
        "titulo": "Documentos",
        "llave": "id_documento",
        "campos_principales": [
            "id_documento", "tipo_entidad_asociada", "id_hogar", "id_persona", "id_predio", "id_tipo_documento",
            "categoria_documental", "nombre_documento", "estado_documento", "fecha_carga"
        ],
        "campos": {
            "id_documento": "Texto/UUID",
            "tipo_entidad_asociada": "Catálogo",
            "id_hogar": "Catálogo relacional opcional",
            "id_persona": "Catálogo relacional opcional",
            "id_predio": "Catálogo relacional opcional",
            "id_lugar_poblado": "Catálogo relacional opcional",
            "id_tipo_documento": "Catálogo relacional",
            "categoria_documental": "Texto autollenado",
            "nombre_documento": "Texto",
            "fecha_documento": "Fecha",
            "fecha_carga": "Fecha",
            "estado_documento": "Catálogo",
            "responsable_carga": "Texto",
            "ruta_archivo": "Texto",
            "observaciones": "Texto largo",
        },
    },
    "expedientes": {
        "titulo": "Expedientes",
        "llave": "id_expediente",
        "campos_principales": [
            "id_expediente", "tipo_expediente", "id_hogar", "id_persona", "id_predio", "estado_expediente",
            "porcentaje_completitud", "responsable_expediente"
        ],
        "campos": {
            "id_expediente": "Texto/UUID",
            "tipo_expediente": "Catálogo",
            "id_hogar": "Catálogo relacional opcional",
            "id_persona": "Catálogo relacional opcional",
            "id_predio": "Catálogo relacional opcional",
            "id_lugar_poblado": "Catálogo relacional opcional",
            "estado_expediente": "Catálogo",
            "porcentaje_completitud": "Número calculado",
            "fecha_apertura": "Fecha",
            "fecha_actualizacion": "Fecha",
            "responsable_expediente": "Texto",
            "observaciones": "Texto largo",
        },
    },
    "checklist_documental": {
        "titulo": "Checklist documental",
        "llave": "id_checklist",
        "campos_principales": [
            "id_checklist", "id_expediente", "id_tipo_documento", "documento_requerido", "id_documento_asociado",
            "cumple", "estado_revision", "fecha_revision"
        ],
        "campos": {
            "id_checklist": "Texto/UUID",
            "id_expediente": "Catálogo relacional",
            "id_tipo_documento": "Catálogo relacional",
            "documento_requerido": "Texto autollenado",
            "id_documento_asociado": "Catálogo relacional opcional",
            "cumple": "Booleano",
            "estado_revision": "Catálogo",
            "fecha_revision": "Fecha",
            "responsable_revision": "Texto",
            "observaciones": "Texto largo",
        },
    },
    "revisiones_documentales": {
        "titulo": "Revisiones documentales",
        "llave": "id_revision_documental",
        "campos_principales": [
            "id_revision_documental", "id_documento", "estado_revision", "resultado_revision", "requiere_subsanacion",
            "fecha_revision", "responsable_revision"
        ],
        "campos": {
            "id_revision_documental": "Texto/UUID",
            "id_documento": "Catálogo relacional",
            "estado_revision": "Catálogo",
            "fecha_revision": "Fecha",
            "rol_revisor": "Catálogo",
            "responsable_revision": "Texto",
            "resultado_revision": "Catálogo",
            "motivo_observacion": "Texto largo",
            "requiere_subsanacion": "Booleano",
            "fecha_subsanacion": "Fecha",
            "observaciones": "Texto largo",
        },
    },
}

CATALOGOS = {
    "zona": ["Zona 1", "Zona 2", "Zona 3"],
    "prioridad": ["1", "2", "3", "Por definir"],
    "tipo_afectacion": ["Físico", "Económico", "Físico-económico", "Por definir"],
    "estado_residencia": ["Residente", "No residente", "Por definir"],
    "parentesco": ["Jefe de hogar", "Cónyuge", "Hija/o", "Madre/Padre", "Otro"],
    "uso_principal": ["Residencial", "Agrícola", "Comercial", "Mixto", "Comunitario", "Productivo"],
    "tipo_tenencia": ["Propietario", "Poseedor", "Arrendatario", "Usuario", "Comunitario", "Por definir"],
    "estado_liberacion": ["No iniciado", "En proceso", "Liberado", "Restringido", "En disputa"],
    "categoria_documental": ["Identificación", "Tenencia", "Predial", "Social", "Avalúo", "Compensación", "Acuerdo", "Soporte fotográfico"],
    "vigencia_requerida": ["No aplica", "Vigente", "Por actualizar"],
    "estado_catalogo": ["Activo", "Inactivo"],
    "tipo_entidad_asociada": ["Hogar", "Persona", "Predio"],
    "estado_documento": ["Cargado", "Pendiente revisión", "Aprobado", "Observado", "Rechazado", "Vencido"],
    "tipo_expediente": ["Hogar", "Persona", "Predio"],
    "estado_expediente": ["Abierto", "En revisión", "Completo", "Incompleto", "Cerrado"],
    "estado_revision": ["Pendiente", "En revisión", "Validado", "Observado", "No aplica"],
    "resultado_revision": ["Aprobado", "Observado", "Rechazado", "Pendiente"],
    "rol_revisor": ["Social", "Predial", "Legal", "Documental", "ACP", "Socionaut"],
}

RELACIONES = {
    ("hogares", "id_lugar_poblado"): ("lugares_poblados", "id_lugar_poblado", "nombre_lugar_poblado"),
    ("personas", "id_hogar"): ("hogares", "id_hogar", "nombre_referencia_hogar"),
    ("predios", "id_hogar"): ("hogares", "id_hogar", "nombre_referencia_hogar"),
    ("predios", "id_lugar_poblado"): ("lugares_poblados", "id_lugar_poblado", "nombre_lugar_poblado"),
    ("documentos", "id_hogar"): ("hogares", "id_hogar", "nombre_referencia_hogar"),
    ("documentos", "id_persona"): ("personas", "id_persona", "nombres"),
    ("documentos", "id_predio"): ("predios", "id_predio", "uso_principal"),
    ("documentos", "id_lugar_poblado"): ("lugares_poblados", "id_lugar_poblado", "nombre_lugar_poblado"),
    ("documentos", "id_tipo_documento"): ("catalogo_documental", "id_tipo_documento", "tipo_documento"),
    ("expedientes", "id_hogar"): ("hogares", "id_hogar", "nombre_referencia_hogar"),
    ("expedientes", "id_persona"): ("personas", "id_persona", "nombres"),
    ("expedientes", "id_predio"): ("predios", "id_predio", "uso_principal"),
    ("expedientes", "id_lugar_poblado"): ("lugares_poblados", "id_lugar_poblado", "nombre_lugar_poblado"),
    ("checklist_documental", "id_expediente"): ("expedientes", "id_expediente", "tipo_expediente"),
    ("checklist_documental", "id_tipo_documento"): ("catalogo_documental", "id_tipo_documento", "tipo_documento"),
    ("checklist_documental", "id_documento_asociado"): ("documentos", "id_documento", "nombre_documento"),
    ("revisiones_documentales", "id_documento"): ("documentos", "id_documento", "nombre_documento"),
}

PREFIJOS_ID = {
    "lugares_poblados": {"id_lugar_poblado": "COM"},
    "hogares": {"id_hogar": "HOG"},
    "personas": {"id_persona": "PER"},
    "predios": {"id_predio": "PRE"},
    "catalogo_documental": {"id_tipo_documento": "TDO"},
    "documentos": {"id_documento": "DOC"},
    "expedientes": {"id_expediente": "EXP"},
    "checklist_documental": {"id_checklist": "CHK"},
    "revisiones_documentales": {"id_revision_documental": "REV"},
}

CAMPOS_ID_AUTOMATICOS = {(tabla, campo) for tabla, campos in PREFIJOS_ID.items() for campo in campos}

ETIQUETAS = {
    "id_lugar_poblado": "ID lugar poblado",
    "nombre_lugar_poblado": "Nombre del lugar poblado",
    "id_hogar": "ID hogar",
    "codigo_hogar_campo": "Código del hogar en campo",
    "nombre_referencia_hogar": "Nombre de referencia del hogar",
    "tipo_afectacion": "Tipo de afectación",
    "estado_residencia": "Estado de residencia",
    "id_persona": "ID persona",
    "documento_identidad": "Documento de identidad",
    "jefe_hogar": "¿Es jefe/a de hogar?",
    "id_predio": "ID predio",
    "cedula_catastral": "Cédula catastral",
    "uso_principal": "Uso principal",
    "tipo_tenencia": "Tipo de tenencia",
    "area_total_m2": "Área total (m²)",
    "area_afectada_m2": "Área afectada (m²)",
    "porcentaje_afectacion": "Porcentaje de afectación",
    "numero_vertices": "Número de vértices",
    "vertices_poligono": "Vértices del polígono",
    "estado_liberacion": "Estado de liberación",
    "id_tipo_documento": "ID tipo de documento",
    "categoria_documental": "Categoría documental",
    "tipo_documento": "Tipo de documento",
    "aplica_a_hogar": "¿Aplica a hogar?",
    "aplica_a_persona": "¿Aplica a persona?",
    "aplica_a_predio": "¿Aplica a predio?",
    "obligatorio": "¿Es obligatorio?",
    "estado_catalogo": "Estado del catálogo",
    "id_documento": "ID documento",
    "tipo_entidad_asociada": "Tipo de entidad asociada",
    "nombre_documento": "Nombre del documento",
    "fecha_documento": "Fecha del documento",
    "fecha_carga": "Fecha de carga",
    "estado_documento": "Estado del documento",
    "responsable_carga": "Responsable de carga",
    "ruta_archivo": "Ruta / referencia del archivo",
    "id_expediente": "ID expediente",
    "tipo_expediente": "Tipo de expediente",
    "estado_expediente": "Estado del expediente",
    "porcentaje_completitud": "Porcentaje de completitud",
    "fecha_apertura": "Fecha de apertura",
    "fecha_actualizacion": "Fecha de actualización",
    "responsable_expediente": "Responsable del expediente",
    "id_checklist": "ID checklist",
    "documento_requerido": "Documento requerido",
    "id_documento_asociado": "Documento asociado",
    "cumple": "¿Cumple?",
    "estado_revision": "Estado de revisión",
    "fecha_revision": "Fecha de revisión",
    "responsable_revision": "Responsable de revisión",
    "id_revision_documental": "ID revisión documental",
    "rol_revisor": "Rol revisor",
    "resultado_revision": "Resultado de revisión",
    "motivo_observacion": "Motivo de observación",
    "requiere_subsanacion": "¿Requiere subsanación?",
    "fecha_subsanacion": "Fecha de subsanación",
}

TOOLTIPS_PANTALLA = {
    "lugares_poblados": "Catálogo territorial base para asociar hogares, predios, expedientes y documentos.",
    "hogares": "Registra hogares de prueba y permite validar expedientes con uno o varios predios asociados.",
    "personas": "Registra personas asociadas a hogares para probar expedientes individuales y documentos personales.",
    "predios": "Registra predios vinculados a hogares y lugares poblados. Incluye polígonos irregulares para visualización espacial.",
    "catalogo_documental": "Define los tipos de documentos requeridos por hogar, persona o predio.",
    "documentos": "Registra documentos asociados a hogares, personas o predios, con estado documental y responsable de carga.",
    "expedientes": "Consolida expedientes por hogar, persona o predio y calcula completitud con base en checklist documental.",
    "checklist_documental": "Verifica documentos requeridos contra documentos cargados y registra cumplimiento.",
    "revisiones_documentales": "Registra revisión, aprobación, observaciones y subsanaciones por documento.",
}

TOOLTIPS_CAMPO = {
    campo: f"Capture o seleccione el valor correspondiente para {campo.replace('_', ' ')}."
    for tabla in ESQUEMA_M06.values()
    for campo in tabla["campos"]
}


# ============================================================
# 3. ESTILOS RESPONSIVE Y COMPATIBLES CON TEMA CLARO/OSCURO
# ============================================================

def aplicar_estilos():
    """Aplica estilos corporativos, modernos y compatibles con tema claro/oscuro."""
    st.markdown(
        f"""
        <style>
            :root {{
                --sir-primary: var(--primary-color, {COLOR_PRIMARIO_SOCIONAUT});
                --sir-accent: {COLOR_SECUNDARIO_SOCIONAUT};
                --sir-coral: {COLOR_CORAL};
                --sir-card: var(--secondary-background-color);
                --sir-bg: var(--background-color);
                --sir-text: var(--text-color);
                --sir-border: rgba(128,128,128,.28);
                --sir-shadow: rgba(0,0,0,.12);
            }}
            .main-title {{
                font-size: clamp(1.45rem, 2.6vw, 2.25rem);
                font-weight: 950;
                color: var(--sir-primary);
                letter-spacing: -0.035em;
                margin-bottom: .15rem;
            }}
            .sub-title {{
                opacity: .78;
                margin-bottom: 1rem;
            }}
            .section-card, .record-card-printable {{
                background: var(--sir-card);
                color: var(--sir-text);
                border: 1px solid var(--sir-border);
                border-radius: 22px;
                box-shadow: 0 10px 28px var(--sir-shadow);
                padding: 1.1rem 1.2rem;
                margin-bottom: 1rem;
            }}
            .screen-help {{
                border-left: 5px solid var(--sir-accent);
                background: color-mix(in srgb, var(--sir-card) 82%, var(--sir-accent) 12%);
                border-radius: 16px;
                padding: .85rem 1rem;
                margin-bottom: 1rem;
            }}
            .chip {{
                display:inline-block;
                padding:.25rem .65rem;
                border-radius:999px;
                font-size:.82rem;
                font-weight:850;
                border:1px solid var(--sir-border);
                margin-right:.35rem;
                margin-bottom:.35rem;
                background: color-mix(in srgb, var(--sir-card) 78%, var(--sir-primary) 12%);
                color:var(--sir-text);
            }}
            .chip-danger {{ background: rgba(220,38,38,.16); border-color: rgba(220,38,38,.38); }}
            .chip-warning {{ background: rgba(245,158,11,.18); border-color: rgba(245,158,11,.42); }}
            .chip-success {{ background: rgba(16,185,129,.16); border-color: rgba(16,185,129,.38); }}
            .record-hero {{
                display:flex;
                justify-content:space-between;
                gap:1rem;
                align-items:flex-start;
                border-bottom:1px solid var(--sir-border);
                padding-bottom:1rem;
            }}
            .record-kicker {{
                color:var(--sir-accent);
                font-weight:900;
                text-transform:uppercase;
                letter-spacing:.08em;
                font-size:.72rem;
            }}
            .record-title {{
                font-size:clamp(1.25rem,2.2vw,1.9rem);
                font-weight:950;
                letter-spacing:-.04em;
                margin:0;
            }}
            .record-subtitle {{ opacity:.72; margin-top:.35rem; }}
            .record-grid {{
                display:grid;
                grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
                gap:.75rem;
                margin-top:1rem;
            }}
            .record-section-title {{
                color:var(--sir-primary);
                font-weight:900;
                margin-top:1.15rem;
            }}
            .record-field {{
                border:1px solid var(--sir-border);
                border-radius:18px;
                padding:.78rem .9rem;
                min-height:4.15rem;
                background: color-mix(in srgb, var(--sir-card) 88%, var(--sir-primary) 5%);
                transition: all 180ms ease-in-out;
            }}
            .record-field:hover {{
                transform: translateY(-2px);
                border-color:var(--sir-primary);
                box-shadow: 0 12px 28px rgba(0,0,0,.14);
            }}
            .record-label {{
                opacity:.62;
                text-transform:uppercase;
                font-size:.68rem;
                letter-spacing:.06em;
                font-weight:850;
            }}
            .record-value {{
                font-size:.98rem;
                font-weight:750;
                overflow-wrap:anywhere;
            }}
            .stButton > button, .stDownloadButton > button {{
                min-height:2.65rem;
                border-radius:14px !important;
                font-weight:800 !important;
                border:1px solid var(--sir-border) !important;
                transition: all 160ms ease-in-out;
                box-shadow: 0 6px 16px rgba(0,0,0,.10);
            }}
            .stButton > button:hover, .stDownloadButton > button:hover {{
                transform:translateY(-1px);
                box-shadow:0 10px 22px rgba(0,0,0,.16);
            }}
            div[data-testid="stMetric"] {{
                background:var(--sir-card);
                border:1px solid var(--sir-border);
                border-radius:18px;
                padding:1rem;
                box-shadow: 0 8px 20px var(--sir-shadow);
            }}
            div[data-testid="stMetric"] label,
            div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
                color:var(--sir-text) !important;
            }}
            .stTextInput label,
            .stSelectbox label,
            .stDateInput label,
            .stNumberInput label,
            .stCheckbox label,
            .stTextArea label,
            .stRadio label,
            .stMultiSelect label {{
                color: var(--sir-text) !important;
            }}
            @media (max-width:768px) {{
                .record-hero {{ flex-direction:column; }}
                .section-card, .record-card-printable {{
                    padding:.9rem;
                    border-radius:18px;
                }}
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# 4. UTILIDADES GENERALES
# ============================================================

def etiqueta_campo(campo):
    """Convierte nombres técnicos de campos a etiquetas legibles."""
    return ETIQUETAS.get(campo, campo.replace("_", " ").capitalize())


def tooltip_campo(campo):
    """Devuelve ayuda contextual para el campo."""
    return TOOLTIPS_CAMPO.get(campo, f"Capture o seleccione el valor correspondiente para {etiqueta_campo(campo).lower()}.")


def normalizar_bool(valor):
    """Normaliza valores booleanos provenientes de distintos formatos."""
    if isinstance(valor, bool):
        return valor
    if isinstance(valor, str):
        return valor.strip().lower() in ["sí", "si", "true", "1", "yes"]
    return bool(valor)


def enmascarar_documento(valor):
    """Enmascara parcialmente un documento de identidad."""
    texto = str(valor or "")
    if len(texto) <= 4:
        return texto
    return f"{texto[:2]}***{texto[-3:]}"


def formatear_valor(campo, valor, proteger=True):
    """Formatea valores para visualización."""
    if valor is None or valor == "" or (isinstance(valor, float) and pd.isna(valor)):
        return "No registrado"
    if isinstance(valor, (date, datetime)):
        return valor.isoformat()
    if isinstance(valor, bool):
        return "Sí" if valor else "No"
    if isinstance(valor, list):
        return json.dumps(valor, ensure_ascii=False)
    if campo == "documento_identidad" and proteger:
        return enmascarar_documento(valor)
    return str(valor)


def serializar_valor(valor):
    """Convierte valores complejos para guardado JSON."""
    if isinstance(valor, (date, datetime)):
        return valor.isoformat()
    if isinstance(valor, float) and pd.isna(valor):
        return None
    return valor


def deserializar_valor(campo, valor):
    """Restaura fechas y listas desde JSON."""
    if valor in [None, ""]:
        return ""
    if any(token in campo for token in ["fecha", "date"]):
        try:
            return date.fromisoformat(str(valor)[:10])
        except ValueError:
            return valor
    if campo == "vertices_poligono":
        if isinstance(valor, list):
            return valor
        try:
            return json.loads(valor)
        except Exception:
            return valor
    return valor


def obtener_df(tabla):
    """Obtiene copia segura de una tabla desde session_state."""
    return st.session_state.data_m06.get(tabla, pd.DataFrame()).copy()


def obtener_opciones(tabla, campo):
    """Obtiene valores únicos para selectores y filtros."""
    df = obtener_df(tabla)
    if df.empty or campo not in df.columns:
        return []
    return sorted([str(v) for v in df[campo].dropna().unique().tolist() if str(v).strip()])


def normalizar_filtro_multiseleccion(valor):
    """Normaliza filtros multiselect."""
    if valor is None:
        return []
    if isinstance(valor, list):
        return [str(v) for v in valor if str(v) not in ["", "Todos"]]
    if str(valor) in ["", "Todos"]:
        return []
    return [str(valor)]


def obtener_unico_filtro(valor):
    """Devuelve único valor si el filtro tiene solo un elemento."""
    valores = normalizar_filtro_multiseleccion(valor)
    return valores[0] if len(valores) == 1 else ""


def extraer_numero_id(valor, prefijo):
    """Extrae número secuencial desde ID con prefijo."""
    match = re.match(rf"^{re.escape(prefijo)}-(\d+)$", str(valor or ""))
    return int(match.group(1)) if match else 0


def generar_id_secuencial(tabla, campo):
    """Genera ID secuencial automático por tabla."""
    prefijo = PREFIJOS_ID.get(tabla, {}).get(campo, "REG")
    df = obtener_df(tabla)
    if df.empty or campo not in df.columns:
        return f"{prefijo}-0001"
    numeros = [extraer_numero_id(v, prefijo) for v in df[campo].dropna().astype(str).tolist()]
    return f"{prefijo}-{(max(numeros) + 1 if numeros else 1):04d}"


def es_campo_id_automatico(tabla, campo):
    """Indica si un campo es ID automático."""
    return (tabla, campo) in CAMPOS_ID_AUTOMATICOS


def calcular_porcentaje_afectacion(area_afectada, area_total):
    """Calcula porcentaje de afectación."""
    try:
        area_total = float(area_total or 0)
        area_afectada = float(area_afectada or 0)
        if area_total <= 0:
            return 0.0
        return round((area_afectada / area_total) * 100, 2)
    except Exception:
        return 0.0


def numero_vertices(vertices):
    """Calcula número de vértices de un polígono."""
    if isinstance(vertices, str):
        try:
            vertices = json.loads(vertices)
        except Exception:
            return 0
    return len(vertices) if isinstance(vertices, list) else 0


def centroid_from_vertices(vertices):
    """Calcula centroide simple promedio para ubicar mapa."""
    if isinstance(vertices, str):
        try:
            vertices = json.loads(vertices)
        except Exception:
            return None
    if not isinstance(vertices, list) or not vertices:
        return None
    lat = sum(float(v[0]) for v in vertices) / len(vertices)
    lon = sum(float(v[1]) for v in vertices) / len(vertices)
    return [lat, lon]


def obtener_hogar_desde_persona(id_persona):
    """Obtiene hogar asociado a una persona."""
    if not id_persona:
        return ""
    personas = obtener_df("personas")
    fila = personas[personas["id_persona"].astype(str) == str(id_persona)] if not personas.empty else pd.DataFrame()
    return str(fila.iloc[0].get("id_hogar", "")) if not fila.empty else ""


def obtener_hogar_desde_predio(id_predio):
    """Obtiene hogar asociado a un predio."""
    if not id_predio:
        return ""
    predios = obtener_df("predios")
    fila = predios[predios["id_predio"].astype(str) == str(id_predio)] if not predios.empty else pd.DataFrame()
    return str(fila.iloc[0].get("id_hogar", "")) if not fila.empty else ""


def obtener_lugar_desde_hogar(id_hogar):
    """Obtiene lugar poblado asociado a hogar."""
    hogares = obtener_df("hogares")
    fila = hogares[hogares["id_hogar"].astype(str) == str(id_hogar)] if not hogares.empty else pd.DataFrame()
    return str(fila.iloc[0].get("id_lugar_poblado", "")) if not fila.empty else ""


def obtener_lugar_desde_predio(id_predio):
    """Obtiene lugar poblado asociado a predio."""
    predios = obtener_df("predios")
    fila = predios[predios["id_predio"].astype(str) == str(id_predio)] if not predios.empty else pd.DataFrame()
    return str(fila.iloc[0].get("id_lugar_poblado", "")) if not fila.empty else ""


def obtener_personas_por_hogar(id_hogar):
    """Devuelve las personas pertenecientes al hogar indicado."""
    personas = obtener_df("personas")
    if not id_hogar or personas.empty or "id_hogar" not in personas.columns:
        return personas.iloc[0:0].copy()
    return personas[personas["id_hogar"].astype(str) == str(id_hogar)].copy()


def obtener_predios_por_hogar(id_hogar):
    """Devuelve los predios vinculados al hogar indicado."""
    predios = obtener_df("predios")
    if not id_hogar or predios.empty or "id_hogar" not in predios.columns:
        return predios.iloc[0:0].copy()
    return predios[predios["id_hogar"].astype(str) == str(id_hogar)].copy()


def validar_pertenencia_hogar(id_hogar, id_persona="", id_predio=""):
    """Valida que persona y predio pertenezcan al hogar seleccionado."""
    errores = []
    if id_persona and obtener_hogar_desde_persona(id_persona) != str(id_hogar or ""):
        errores.append("La persona seleccionada no pertenece al hogar indicado.")
    hogar_predio = obtener_hogar_desde_predio(id_predio) if id_predio else ""
    if id_predio and hogar_predio and hogar_predio != str(id_hogar or ""):
        errores.append("El predio seleccionado no pertenece al hogar indicado.")
    return errores


def resolver_contexto_relacional(tabla, campo, valor):
    """Muestra ID + descripción legible para campos relacionales."""
    relacion = RELACIONES.get((tabla, campo))
    if not relacion or not valor:
        return formatear_valor(campo, valor)
    tabla_catalogo, campo_id, campo_desc = relacion
    df = obtener_df(tabla_catalogo)
    if df.empty or campo_id not in df.columns:
        return formatear_valor(campo, valor)
    fila = df[df[campo_id].astype(str) == str(valor)]
    if fila.empty:
        return formatear_valor(campo, valor)
    row = fila.iloc[0]
    if tabla_catalogo == "personas":
        desc = f"{row.get('nombres', '')} {row.get('apellidos', '')}".strip()
    else:
        desc = row.get(campo_desc, "") if campo_desc in df.columns else ""
    return f"{valor} · {desc}" if desc else str(valor)


def convertir_para_visualizacion(df):
    """Formatea dataframe para tabla visible."""
    df_vista = df.copy()
    for col in df_vista.columns:
        df_vista[col] = df_vista[col].apply(lambda x: formatear_valor(col, x, proteger=True))
    return df_vista


def buscar_en_dataframe(df, texto):
    """Busca texto libre en dataframe."""
    if not texto or df.empty:
        return df
    texto = str(texto).lower().strip()
    mascara = df.astype(str).apply(lambda col: col.str.lower().str.contains(texto, na=False)).any(axis=1)
    return df[mascara]


# ============================================================
# 5. DATA INTERNA DE PRUEBA Y MEMORIA LOCAL
# ============================================================

def poligonos_predios_simulados():
    """Devuelve polígonos irregulares simulados con distinto número de vértices."""
    return {
        "PRE-0001": [[9.19120, -80.08840], [9.19185, -80.08795], [9.19155, -80.08710], [9.19080, -80.08730], [9.19060, -80.08815]],
        "PRE-0002": [[9.19320, -80.09010], [9.19410, -80.08930], [9.19450, -80.08810], [9.19380, -80.08740], [9.19270, -80.08780], [9.19230, -80.08920]],
        "PRE-0003": [[9.19510, -80.09200], [9.19600, -80.09150], [9.19635, -80.09040], [9.19580, -80.08960], [9.19490, -80.08985], [9.19440, -80.09080], [9.19465, -80.09170]],
        "PRE-0004": [[9.20200, -80.10050], [9.20290, -80.09980], [9.20310, -80.09890], [9.20240, -80.09810], [9.20140, -80.09820], [9.20090, -80.09900], [9.20110, -80.10000], [9.20160, -80.10060]],
        "PRE-0005": [[9.20410, -80.10210], [9.20480, -80.10150], [9.20460, -80.10050], [9.20370, -80.10010], [9.20300, -80.10080], [9.20320, -80.10180]],
        "PRE-0006": [[9.16600, -80.13790], [9.16660, -80.13740], [9.16630, -80.13670], [9.16550, -80.13680], [9.16520, -80.13750]],
        "PRE-0007": [[9.16700, -80.13950], [9.16820, -80.13880], [9.16880, -80.13740], [9.16810, -80.13630], [9.16690, -80.13610], [9.16580, -80.13690], [9.16530, -80.13810], [9.16570, -80.13910], [9.16630, -80.13970]],
        "PRE-0008": [[9.16950, -80.14100], [9.17070, -80.14050], [9.17150, -80.13930], [9.17120, -80.13790], [9.17020, -80.13720], [9.16890, -80.13740], [9.16800, -80.13850], [9.16770, -80.13970], [9.16820, -80.14080], [9.16890, -80.14130]],
        "PRE-0009": [[9.17200, -80.13500], [9.17280, -80.13460], [9.17300, -80.13370], [9.17220, -80.13320], [9.17140, -80.13370], [9.17130, -80.13460]],
        "PRE-0010": [[9.20700, -80.06250], [9.20780, -80.06190], [9.20770, -80.06100], [9.20680, -80.06060], [9.20610, -80.06120], [9.20620, -80.06210], [9.20660, -80.06270]],
        "PRE-0011": [[9.20310, -80.10120], [9.20440, -80.10050], [9.20520, -80.09910], [9.20480, -80.09780], [9.20350, -80.09690], [9.20200, -80.09710], [9.20100, -80.09820], [9.20070, -80.09960], [9.20120, -80.10090], [9.20210, -80.10160], [9.20280, -80.10150]],
        "PRE-0012": [[9.20580, -80.10550], [9.20670, -80.10480], [9.20640, -80.10370], [9.20520, -80.10350], [9.20460, -80.10430], [9.20490, -80.10530]],
        "PRE-0013": [[9.20900, -80.11100], [9.21020, -80.11040], [9.21110, -80.10910], [9.21070, -80.10770], [9.20960, -80.10680], [9.20820, -80.10700], [9.20710, -80.10810], [9.20680, -80.10950], [9.20730, -80.11080], [9.20800, -80.11140], [9.20860, -80.11130], [9.20880, -80.11110]],
        "PRE-0014": [[9.21410, -80.11400], [9.21490, -80.11340], [9.21510, -80.11250], [9.21440, -80.11180], [9.21340, -80.11200], [9.21290, -80.11290], [9.21330, -80.11380]],
        "PRE-0015": [[9.21600, -80.11620], [9.21700, -80.11570], [9.21760, -80.11450], [9.21710, -80.11340], [9.21600, -80.11300], [9.21490, -80.11350], [9.21450, -80.11480], [9.21510, -80.11590]],
    }


def crear_data_inicial():
    """Crea data interna inicial con 10 hogares y predios 1:N."""
    lugares = pd.DataFrame([
        {"id_lugar_poblado": "COM-0001", "nombre_lugar_poblado": "Nueva Esperanza", "corregimiento": "Río Indio", "distrito": "Capira", "provincia": "Panamá Oeste", "zona": "Zona 1", "prioridad": "1", "lat": 9.1915, "lon": -80.0880},
        {"id_lugar_poblado": "COM-0002", "nombre_lugar_poblado": "El Progreso", "corregimiento": "Río Indio", "distrito": "Capira", "provincia": "Panamá Oeste", "zona": "Zona 1", "prioridad": "1", "lat": 9.2020, "lon": -80.1000},
        {"id_lugar_poblado": "COM-0003", "nombre_lugar_poblado": "Santa Rosa", "corregimiento": "Ciricito", "distrito": "Capira", "provincia": "Panamá Oeste", "zona": "Zona 2", "prioridad": "2", "lat": 9.1660, "lon": -80.1375},
        {"id_lugar_poblado": "COM-0004", "nombre_lugar_poblado": "Los Pinos", "corregimiento": "La Encantada", "distrito": "Chagres", "provincia": "Colón", "zona": "Zona 3", "prioridad": "2", "lat": 9.2072, "lon": -80.0621},
        {"id_lugar_poblado": "COM-0005", "nombre_lugar_poblado": "Río Claro", "corregimiento": "La Encantada", "distrito": "Chagres", "provincia": "Colón", "zona": "Zona 3", "prioridad": "3", "lat": 9.2140, "lon": -80.1140},
    ])

    nombres = ["María López", "Carlos Mendoza", "Rosa Martínez", "José Pérez", "Ana Rodríguez", "Luis García", "Elena Torres", "Miguel Castillo", "Carmen Díaz", "Roberto Herrera"]
    lugares_hogar = ["COM-0001", "COM-0001", "COM-0002", "COM-0002", "COM-0003", "COM-0003", "COM-0004", "COM-0004", "COM-0005", "COM-0005"]
    zonas = ["Zona 1", "Zona 1", "Zona 1", "Zona 2", "Zona 2", "Zona 2", "Zona 3", "Zona 3", "Zona 3", "Zona 1"]
    afectaciones = ["Físico", "Económico", "Físico", "Económico", "Físico-económico", "Económico", "Físico", "Económico", "Físico-económico", "Físico"]

    hogares, personas = [], []
    for i in range(1, 11):
        id_hogar = f"HOG-{i:04d}"
        hogares.append({
            "id_hogar": id_hogar,
            "codigo_hogar_campo": f"PA-RI-{i:03d}",
            "nombre_referencia_hogar": nombres[i - 1],
            "id_lugar_poblado": lugares_hogar[i - 1],
            "zona": zonas[i - 1],
            "tipo_afectacion": afectaciones[i - 1],
            "estado_residencia": "No residente" if i in [4, 8] else "Residente",
            "observaciones_generales": "Registro simulado para pruebas internas de relación documental y predial.",
        })
        personas.append({
            "id_persona": f"PER-{i:04d}",
            "id_hogar": id_hogar,
            "nombres": nombres[i - 1].split()[0],
            "apellidos": nombres[i - 1].split()[-1],
            "documento_identidad": f"8-{100+i}-{200+i}",
            "telefono": f"6{i:03d}-{1000+i}",
            "parentesco": "Jefe de hogar",
            "jefe_hogar": True,
            "observaciones": "Persona de referencia simulada del hogar.",
        })

    datos_predios = [
        ("PRE-0001", "HOG-0001", "COM-0001", "Residencial", "Poseedor", 2450.0, 1200.0),
        ("PRE-0002", "HOG-0002", "COM-0001", "Agrícola", "Propietario", 8300.0, 3900.0),
        ("PRE-0003", "HOG-0002", "COM-0001", "Productivo", "Poseedor", 4750.0, 1100.0),
        ("PRE-0004", "HOG-0003", "COM-0002", "Mixto", "Poseedor", 3200.0, 3200.0),
        ("PRE-0005", "", "COM-0002", "Comunitario", "Comunitario", 1350.0, 900.0),
        ("PRE-0006", "HOG-0005", "COM-0003", "Residencial", "Propietario", 950.0, 950.0),
        ("PRE-0007", "HOG-0005", "COM-0003", "Agrícola", "Usuario", 12800.0, 5400.0),
        ("PRE-0008", "HOG-0005", "COM-0003", "Productivo", "Poseedor", 6200.0, 2800.0),
        ("PRE-0009", "HOG-0006", "COM-0003", "Comercial", "Arrendatario", 1100.0, 450.0),
        ("PRE-0010", "HOG-0007", "COM-0004", "Residencial", "Poseedor", 2000.0, 800.0),
        ("PRE-0011", "HOG-0008", "COM-0004", "Agrícola", "Propietario", 15500.0, 7250.0),
        ("PRE-0012", "HOG-0008", "COM-0004", "Mixto", "Poseedor", 3100.0, 1600.0),
        ("PRE-0013", "HOG-0009", "COM-0005", "Productivo", "Usuario", 18700.0, 8900.0),
        ("PRE-0014", "HOG-0010", "COM-0005", "Residencial", "Propietario", 2850.0, 2100.0),
        ("PRE-0015", "HOG-0010", "COM-0005", "Agrícola", "Poseedor", 9400.0, 3300.0),
    ]

    poligonos = poligonos_predios_simulados()
    predios = []
    for id_predio, id_hogar, id_lugar, uso, tenencia, area_total, area_afectada in datos_predios:
        vertices = poligonos[id_predio]
        predios.append({
            "id_predio": id_predio,
            "id_hogar": id_hogar,
            "id_lugar_poblado": id_lugar,
            "cedula_catastral": f"CAT-{id_predio[-4:]}",
            "uso_principal": uso,
            "tipo_tenencia": tenencia,
            "area_total_m2": area_total,
            "area_afectada_m2": area_afectada,
            "porcentaje_afectacion": calcular_porcentaje_afectacion(area_afectada, area_total),
            "numero_vertices": len(vertices),
            "vertices_poligono": vertices,
            "estado_liberacion": ["No iniciado", "En proceso", "Liberado", "Restringido", "En disputa"][int(id_predio[-1]) % 5],
            "observaciones": "Polígono irregular simulado para pruebas de mapa y relación hogar-predio.",
        })

    catalogo = pd.DataFrame([
        {"id_tipo_documento": "TDO-0001", "categoria_documental": "Identificación", "tipo_documento": "Documento de identidad del jefe/a de hogar", "descripcion": "Documento personal de identificación.", "aplica_a_hogar": True, "aplica_a_persona": True, "aplica_a_predio": False, "obligatorio": True, "vigencia_requerida": "Vigente", "estado_catalogo": "Activo"},
        {"id_tipo_documento": "TDO-0002", "categoria_documental": "Social", "tipo_documento": "Ficha socioeconómica del hogar", "descripcion": "Ficha social o línea base del hogar.", "aplica_a_hogar": True, "aplica_a_persona": False, "aplica_a_predio": False, "obligatorio": True, "vigencia_requerida": "No aplica", "estado_catalogo": "Activo"},
        {"id_tipo_documento": "TDO-0003", "categoria_documental": "Tenencia", "tipo_documento": "Soporte de tenencia", "descripcion": "Título, constancia, declaración o soporte de ocupación.", "aplica_a_hogar": True, "aplica_a_persona": False, "aplica_a_predio": True, "obligatorio": True, "vigencia_requerida": "Por actualizar", "estado_catalogo": "Activo"},
        {"id_tipo_documento": "TDO-0004", "categoria_documental": "Predial", "tipo_documento": "Ficha predial", "descripcion": "Ficha técnica del predio.", "aplica_a_hogar": False, "aplica_a_persona": False, "aplica_a_predio": True, "obligatorio": True, "vigencia_requerida": "No aplica", "estado_catalogo": "Activo"},
        {"id_tipo_documento": "TDO-0005", "categoria_documental": "Avalúo", "tipo_documento": "Informe de avalúo", "descripcion": "Documento de valoración predial o de activos.", "aplica_a_hogar": False, "aplica_a_persona": False, "aplica_a_predio": True, "obligatorio": True, "vigencia_requerida": "Vigente", "estado_catalogo": "Activo"},
        {"id_tipo_documento": "TDO-0006", "categoria_documental": "Acuerdo", "tipo_documento": "Acuerdo individual", "descripcion": "Acuerdo individual de compensación o reposición.", "aplica_a_hogar": True, "aplica_a_persona": False, "aplica_a_predio": False, "obligatorio": True, "vigencia_requerida": "No aplica", "estado_catalogo": "Activo"},
        {"id_tipo_documento": "TDO-0007", "categoria_documental": "Soporte fotográfico", "tipo_documento": "Registro fotográfico", "descripcion": "Fotografías o evidencias asociadas a predio, activo o expediente.", "aplica_a_hogar": True, "aplica_a_persona": False, "aplica_a_predio": True, "obligatorio": False, "vigencia_requerida": "No aplica", "estado_catalogo": "Activo"},
    ])

    expedientes = []
    # Expedientes por hogar.
    for i in range(1, 11):
        expedientes.append({
            "id_expediente": f"EXP-HOG-{i:04d}",
            "tipo_expediente": "Hogar",
            "id_hogar": f"HOG-{i:04d}",
            "id_persona": "",
            "id_predio": "",
            "id_lugar_poblado": lugares_hogar[i - 1],
            "estado_expediente": "Abierto",
            "porcentaje_completitud": 0.0,
            "fecha_apertura": date(2026, 4, min(5 + i, 28)),
            "fecha_actualizacion": date(2026, 5, min(8 + i, 28)),
            "responsable_expediente": "Equipo documental",
            "observaciones": "Expediente de hogar generado para prueba.",
        })
    # Expedientes prediales.
    for idx, predio in enumerate(predios, start=1):
        expedientes.append({
            "id_expediente": f"EXP-PRE-{idx:04d}",
            "tipo_expediente": "Predio",
            "id_hogar": predio["id_hogar"],
            "id_persona": "",
            "id_predio": predio["id_predio"],
            "id_lugar_poblado": predio["id_lugar_poblado"],
            "estado_expediente": "Abierto",
            "porcentaje_completitud": 0.0,
            "fecha_apertura": date(2026, 4, min(10 + idx, 28)),
            "fecha_actualizacion": date(2026, 5, min(10 + idx, 28)),
            "responsable_expediente": "Equipo predial",
            "observaciones": "Expediente predial generado para prueba.",
        })

    documentos = []
    doc_counter = 1
    # Documentos de hogares.
    for i in range(1, 11):
        id_hogar = f"HOG-{i:04d}"
        for id_tipo in ["TDO-0001", "TDO-0002"]:
            cat = catalogo[catalogo["id_tipo_documento"] == id_tipo].iloc[0]
            estado = "Aprobado" if (i + doc_counter) % 3 != 0 else "Pendiente revisión"
            documentos.append({
                "id_documento": f"DOC-{doc_counter:04d}",
                "tipo_entidad_asociada": "Hogar",
                "id_hogar": id_hogar,
                "id_persona": "",
                "id_predio": "",
                "id_lugar_poblado": lugares_hogar[i - 1],
                "id_tipo_documento": id_tipo,
                "categoria_documental": cat["categoria_documental"],
                "nombre_documento": f"{cat['tipo_documento']} · {id_hogar}",
                "fecha_documento": date(2026, 4, min(5 + i, 28)),
                "fecha_carga": date(2026, 5, min(1 + doc_counter, 28)),
                "estado_documento": estado,
                "responsable_carga": "Analista documental",
                "ruta_archivo": f"/expedientes/{id_hogar}/DOC-{doc_counter:04d}.pdf",
                "observaciones": "Documento simulado de hogar.",
            })
            doc_counter += 1

    # Documentos de algunos predios, no todos, para probar completitud incompleta.
    for predio in predios:
        tipos = ["TDO-0003", "TDO-0004"]
        if predio["id_predio"] in ["PRE-0002", "PRE-0007", "PRE-0011", "PRE-0013"]:
            tipos.append("TDO-0005")
        for id_tipo in tipos:
            cat = catalogo[catalogo["id_tipo_documento"] == id_tipo].iloc[0]
            documentos.append({
                "id_documento": f"DOC-{doc_counter:04d}",
                "tipo_entidad_asociada": "Predio",
                "id_hogar": predio["id_hogar"],
                "id_persona": "",
                "id_predio": predio["id_predio"],
                "id_lugar_poblado": predio["id_lugar_poblado"],
                "id_tipo_documento": id_tipo,
                "categoria_documental": cat["categoria_documental"],
                "nombre_documento": f"{cat['tipo_documento']} · {predio['id_predio']}",
                "fecha_documento": date(2026, 4, min(7 + doc_counter % 20, 28)),
                "fecha_carga": date(2026, 5, min(3 + doc_counter % 20, 28)),
                "estado_documento": "Aprobado" if doc_counter % 4 != 0 else "Observado",
                "responsable_carga": "Analista predial",
                "ruta_archivo": f"/expedientes/{predio['id_predio']}/DOC-{doc_counter:04d}.pdf",
                "observaciones": "Documento simulado de predio.",
            })
            doc_counter += 1

    checklist = []
    chk_counter = 1
    exp_df_tmp = pd.DataFrame(expedientes)
    docs_df_tmp = pd.DataFrame(documentos)
    for _, exp in exp_df_tmp.iterrows():
        if exp["tipo_expediente"] == "Hogar":
            cat_req = catalogo[(catalogo["aplica_a_hogar"]) & (catalogo["obligatorio"])]
            docs_exp = docs_df_tmp[(docs_df_tmp["id_hogar"] == exp["id_hogar"]) & (docs_df_tmp["tipo_entidad_asociada"] == "Hogar")]
        else:
            cat_req = catalogo[(catalogo["aplica_a_predio"]) & (catalogo["obligatorio"])]
            docs_exp = docs_df_tmp[docs_df_tmp["id_predio"] == exp["id_predio"]]

        cumplidos = 0
        total_req = len(cat_req)
        for _, req in cat_req.iterrows():
            doc_match = docs_exp[docs_exp["id_tipo_documento"] == req["id_tipo_documento"]]
            id_doc = "" if doc_match.empty else str(doc_match.iloc[0]["id_documento"])
            cumple = bool(id_doc)
            cumplidos += 1 if cumple else 0
            checklist.append({
                "id_checklist": f"CHK-{chk_counter:04d}",
                "id_expediente": exp["id_expediente"],
                "id_tipo_documento": req["id_tipo_documento"],
                "documento_requerido": req["tipo_documento"],
                "id_documento_asociado": id_doc,
                "cumple": cumple,
                "estado_revision": "Validado" if cumple else "Pendiente",
                "fecha_revision": date(2026, 5, min(5 + chk_counter % 20, 28)),
                "responsable_revision": "Control documental",
                "observaciones": "Checklist generado automáticamente para prueba.",
            })
            chk_counter += 1
        pct = round((cumplidos / total_req) * 100, 2) if total_req else 0.0
        idx = [e["id_expediente"] for e in expedientes].index(exp["id_expediente"])
        expedientes[idx]["porcentaje_completitud"] = pct
        expedientes[idx]["estado_expediente"] = "Completo" if pct == 100 else "Incompleto"

    revisiones = []
    for i, doc in enumerate(documentos[:25], start=1):
        revisiones.append({
            "id_revision_documental": f"REV-{i:04d}",
            "id_documento": doc["id_documento"],
            "estado_revision": "Validado" if doc["estado_documento"] == "Aprobado" else "Observado",
            "fecha_revision": date(2026, 5, min(7 + i, 28)),
            "rol_revisor": ["Social", "Predial", "Legal", "Documental"][i % 4],
            "responsable_revision": "Revisor documental",
            "resultado_revision": "Aprobado" if doc["estado_documento"] == "Aprobado" else "Observado",
            "motivo_observacion": "" if doc["estado_documento"] == "Aprobado" else "Documento requiere validación o información complementaria.",
            "requiere_subsanacion": doc["estado_documento"] != "Aprobado",
            "fecha_subsanacion": date(2026, 5, min(12 + i, 28)) if doc["estado_documento"] != "Aprobado" else "",
            "observaciones": "Revisión simulada.",
        })

    data = {
        "lugares_poblados": lugares,
        "hogares": pd.DataFrame(hogares),
        "personas": pd.DataFrame(personas),
        "predios": pd.DataFrame(predios),
        "catalogo_documental": catalogo,
        "documentos": pd.DataFrame(documentos),
        "expedientes": pd.DataFrame(expedientes),
        "checklist_documental": pd.DataFrame(checklist),
        "revisiones_documentales": pd.DataFrame(revisiones),
    }

    return asegurar_columnas_data(data)


def asegurar_columnas_data(data):
    """Asegura columnas del esquema y auditoría."""
    data_ok = {}
    for tabla, config in ESQUEMA_M06.items():
        columnas = list(config["campos"].keys()) + ["fecha_creacion", "fecha_actualizacion", "usuario_actualizacion"]
        df = data.get(tabla, pd.DataFrame()) if isinstance(data, dict) else pd.DataFrame()
        if df is None or df.empty:
            df = pd.DataFrame(columns=columnas)
        for col in columnas:
            if col not in df.columns:
                df[col] = ""
        data_ok[tabla] = df
    return data_ok


def dataframes_a_json(data):
    """Convierte dataframes a payload JSON."""
    payload = {}
    for tabla, df in data.items():
        registros = []
        for _, fila in df.iterrows():
            registros.append({col: serializar_valor(fila[col]) for col in df.columns})
        payload[tabla] = registros
    return payload


def json_a_dataframes(payload):
    """Convierte payload JSON a dataframes."""
    data = {}
    for tabla, config in ESQUEMA_M06.items():
        registros = []
        for fila in payload.get(tabla, []):
            registros.append({campo: deserializar_valor(campo, valor) for campo, valor in fila.items()})
        data[tabla] = pd.DataFrame(registros)
    return asegurar_columnas_data(data)


def guardar_memoria_local():
    """Guarda memoria local JSON."""
    with ARCHIVO_MEMORIA.open("w", encoding="utf-8") as archivo:
        json.dump(dataframes_a_json(st.session_state.data_m06), archivo, ensure_ascii=False, indent=2)


def cargar_memoria_local():
    """Carga memoria local si existe; si no, carga data inicial."""
    if ARCHIVO_MEMORIA.exists():
        try:
            with ARCHIVO_MEMORIA.open("r", encoding="utf-8") as archivo:
                return json_a_dataframes(json.load(archivo))
        except Exception:
            st.warning("La memoria local no pudo leerse. Se cargó la data interna inicial.")
    return crear_data_inicial()


def inicializar_estado():
    """Inicializa session_state."""
    if "data_m06" not in st.session_state:
        st.session_state.data_m06 = cargar_memoria_local()
    else:
        st.session_state.data_m06 = asegurar_columnas_data(st.session_state.data_m06)
    st.session_state.setdefault("busqueda_global_m06", "")
    st.session_state.setdefault("panel_m06", "Visualización principal")
    st.session_state.setdefault("panel_destino_m06", None)
    st.session_state.setdefault("form_reset_counter_m06", 0)


# ============================================================
# 6. REGLAS AUTOMÁTICAS, VALIDACIÓN Y CRUD
# ============================================================

def aplicar_reglas_automaticas(tabla, registro):
    """Aplica reglas automáticas antes de guardar."""
    if tabla == "predios":
        registro["porcentaje_afectacion"] = calcular_porcentaje_afectacion(
            registro.get("area_afectada_m2"), registro.get("area_total_m2")
        )
        registro["numero_vertices"] = numero_vertices(registro.get("vertices_poligono"))
        if registro.get("id_hogar") and not registro.get("id_lugar_poblado"):
            registro["id_lugar_poblado"] = obtener_lugar_desde_hogar(registro.get("id_hogar"))

    if tabla == "documentos":
        tipo = registro.get("tipo_entidad_asociada")
        if tipo == "Persona":
            hogar = obtener_hogar_desde_persona(registro.get("id_persona"))
            if hogar:
                registro["id_hogar"] = hogar
                registro["id_lugar_poblado"] = obtener_lugar_desde_hogar(hogar)
            registro["id_predio"] = ""
        elif tipo == "Predio":
            hogar = obtener_hogar_desde_predio(registro.get("id_predio"))
            if hogar:
                registro["id_hogar"] = hogar
            registro["id_lugar_poblado"] = obtener_lugar_desde_predio(registro.get("id_predio"))
            registro["id_persona"] = ""
        elif tipo == "Hogar":
            registro["id_persona"] = ""
            registro["id_predio"] = ""
            if registro.get("id_hogar"):
                registro["id_lugar_poblado"] = obtener_lugar_desde_hogar(registro.get("id_hogar"))

        id_tipo = registro.get("id_tipo_documento")
        catalogo = obtener_df("catalogo_documental")
        fila = catalogo[catalogo["id_tipo_documento"].astype(str) == str(id_tipo)] if not catalogo.empty else pd.DataFrame()
        if not fila.empty:
            registro["categoria_documental"] = fila.iloc[0].get("categoria_documental", "")

    if tabla == "expedientes":
        tipo = registro.get("tipo_expediente")
        if tipo == "Persona":
            hogar = obtener_hogar_desde_persona(registro.get("id_persona"))
            if hogar:
                registro["id_hogar"] = hogar
                registro["id_lugar_poblado"] = obtener_lugar_desde_hogar(hogar)
            registro["id_predio"] = ""
        elif tipo == "Predio":
            hogar = obtener_hogar_desde_predio(registro.get("id_predio"))
            if hogar:
                registro["id_hogar"] = hogar
            registro["id_lugar_poblado"] = obtener_lugar_desde_predio(registro.get("id_predio"))
            registro["id_persona"] = ""
        elif tipo == "Hogar":
            registro["id_persona"] = ""
            registro["id_predio"] = ""
            if registro.get("id_hogar"):
                registro["id_lugar_poblado"] = obtener_lugar_desde_hogar(registro.get("id_hogar"))

    if tabla == "checklist_documental":
        id_tipo = registro.get("id_tipo_documento")
        catalogo = obtener_df("catalogo_documental")
        fila = catalogo[catalogo["id_tipo_documento"].astype(str) == str(id_tipo)] if not catalogo.empty else pd.DataFrame()
        if not fila.empty:
            registro["documento_requerido"] = fila.iloc[0].get("tipo_documento", "")
        registro["cumple"] = bool(registro.get("id_documento_asociado"))

    if tabla == "revisiones_documentales":
        if not normalizar_bool(registro.get("requiere_subsanacion")):
            registro["motivo_observacion"] = registro.get("motivo_observacion", "")
    return registro


def validar_registro(tabla, registro):
    """Valida reglas mínimas de integridad."""
    errores = []
    llave = ESQUEMA_M06[tabla]["llave"]
    if not str(registro.get(llave, "")).strip():
        errores.append(f"El campo '{etiqueta_campo(llave)}' es obligatorio.")

    # Validación de documentos según entidad asociada.
    if tabla == "documentos":
        tipo = registro.get("tipo_entidad_asociada")
        if not registro.get("id_hogar"):
            errores.append("Selecciona primero un hogar para registrar el documento.")
        if tipo == "Persona" and not registro.get("id_persona"):
            errores.append("Selecciona una persona para documentos asociados a persona.")
        if tipo == "Predio" and not registro.get("id_predio"):
            errores.append("Selecciona un predio para documentos asociados a predio.")

    if tabla == "expedientes":
        tipo = registro.get("tipo_expediente")
        if not registro.get("id_hogar"):
            errores.append("Selecciona primero un hogar para crear o actualizar el expediente.")
        if tipo == "Persona" and not registro.get("id_persona"):
            errores.append("Selecciona una persona perteneciente al hogar para el expediente de persona.")
        if tipo == "Predio" and not registro.get("id_predio"):
            errores.append("Selecciona un predio asociado al hogar para el expediente de predio.")

    if tabla in ["documentos", "expedientes"]:
        errores.extend(validar_pertenencia_hogar(
            registro.get("id_hogar"),
            registro.get("id_persona"),
            registro.get("id_predio"),
        ))

    # Validación relacional flexible: campos opcionales no obligan, pero si tienen valor deben existir.
    for (tabla_rel, campo_rel), (tabla_catalogo, campo_id, _) in RELACIONES.items():
        if tabla_rel == tabla and campo_rel in registro:
            valor = str(registro.get(campo_rel, "")).strip()
            if valor and valor not in obtener_opciones(tabla_catalogo, campo_id):
                errores.append(f"El valor '{valor}' de '{etiqueta_campo(campo_rel)}' no existe en '{tabla_catalogo}'.")

    return errores


def agregar_auditoria(registro, accion, existente=None):
    """Agrega campos de auditoría."""
    ahora = datetime.now().isoformat(timespec="seconds")
    registro["fecha_creacion"] = existente.get("fecha_creacion", ahora) if accion == "actualizado" and existente is not None else registro.get("fecha_creacion") or ahora
    registro["fecha_actualizacion"] = ahora
    registro["usuario_actualizacion"] = USUARIO_PROTOTIPO
    return registro


def guardar_registro(tabla, registro, llave):
    """Inserta o actualiza un registro en memoria local."""
    registro = aplicar_reglas_automaticas(tabla, registro)
    df = st.session_state.data_m06[tabla].copy()
    valor_llave = str(registro[llave]).strip()

    if df.empty:
        st.session_state.data_m06[tabla] = pd.DataFrame([agregar_auditoria(registro, "agregado")])
        guardar_memoria_local()
        return "agregado"

    df[llave] = df[llave].astype(str)
    existe = valor_llave in df[llave].values
    if existe:
        fila_existente = df[df[llave] == valor_llave].iloc[0].to_dict()
        registro = agregar_auditoria(registro, "actualizado", fila_existente)
        for campo, valor in registro.items():
            if campo not in df.columns:
                df[campo] = ""
            df.loc[df[llave] == valor_llave, campo] = valor
        accion = "actualizado"
    else:
        registro = agregar_auditoria(registro, "agregado")
        df = pd.concat([df, pd.DataFrame([registro])], ignore_index=True)
        accion = "agregado"

    st.session_state.data_m06[tabla] = df
    guardar_memoria_local()

    # Mantiene sincronizados documentos, checklist y expedientes sin duplicar IDs.
    if tabla in ["documentos", "catalogo_documental", "expedientes"]:
        sincronizar_checklist_expedientes()
    elif tabla == "checklist_documental":
        recalcular_completitud_expedientes()
    return accion


def documentos_del_expediente(expediente, documentos):
    """Obtiene los documentos correspondientes al alcance del expediente."""
    tipo = str(expediente.get("tipo_expediente", ""))
    if documentos.empty:
        return documentos
    if tipo == "Persona":
        return documentos[documentos["id_persona"].astype(str) == str(expediente.get("id_persona", ""))]
    if tipo == "Predio":
        return documentos[documentos["id_predio"].astype(str) == str(expediente.get("id_predio", ""))]
    return documentos[
        (documentos["id_hogar"].astype(str) == str(expediente.get("id_hogar", "")))
        & (documentos["tipo_entidad_asociada"].astype(str) == "Hogar")
    ]


def catalogo_requerido_expediente(expediente, catalogo):
    """Obtiene los tipos documentales obligatorios aplicables al expediente."""
    if catalogo.empty:
        return catalogo
    tipo = str(expediente.get("tipo_expediente", ""))
    campo_aplica = {"Hogar": "aplica_a_hogar", "Persona": "aplica_a_persona", "Predio": "aplica_a_predio"}.get(tipo)
    if not campo_aplica or campo_aplica not in catalogo.columns:
        return catalogo.iloc[0:0].copy()
    return catalogo[
        catalogo[campo_aplica].apply(normalizar_bool)
        & catalogo["obligatorio"].apply(normalizar_bool)
        & (catalogo["estado_catalogo"].astype(str) == "Activo")
    ].copy()


def sincronizar_checklist_expedientes():
    """Sincroniza checklist por expediente y tipo documental, reutilizando el mismo ID cuando existe."""
    expedientes = obtener_df("expedientes")
    catalogo = obtener_df("catalogo_documental")
    documentos = obtener_df("documentos")
    checklist = obtener_df("checklist_documental")
    if expedientes.empty:
        return

    filas = []
    ahora = datetime.now().isoformat(timespec="seconds")
    for _, exp in expedientes.iterrows():
        requeridos = catalogo_requerido_expediente(exp, catalogo)
        docs_exp = documentos_del_expediente(exp, documentos)
        for _, req in requeridos.iterrows():
            mascara = (
                (checklist["id_expediente"].astype(str) == str(exp.get("id_expediente", "")))
                & (checklist["id_tipo_documento"].astype(str) == str(req.get("id_tipo_documento", "")))
            ) if not checklist.empty else pd.Series(dtype=bool)
            existente = checklist[mascara].iloc[0].to_dict() if not checklist.empty and mascara.any() else {}
            candidatos = docs_exp[docs_exp["id_tipo_documento"].astype(str) == str(req.get("id_tipo_documento", ""))]
            if not candidatos.empty:
                aprobados = candidatos[candidatos["estado_documento"].astype(str) == "Aprobado"]
                doc = (aprobados if not aprobados.empty else candidatos).iloc[0]
                id_documento = str(doc.get("id_documento", ""))
                cumple = str(doc.get("estado_documento", "")) == "Aprobado"
            else:
                id_documento, cumple = "", False

            fila = dict(existente)
            fila.update({
                "id_checklist": existente.get("id_checklist") or generar_id_secuencial_desde_filas("CHK", checklist, filas, "id_checklist"),
                "id_expediente": exp.get("id_expediente", ""),
                "id_tipo_documento": req.get("id_tipo_documento", ""),
                "documento_requerido": req.get("tipo_documento", ""),
                "id_documento_asociado": id_documento,
                "cumple": cumple,
                "estado_revision": "Validado" if cumple else (existente.get("estado_revision") if existente.get("estado_revision") in ["En revisión", "Observado"] else "Pendiente"),
                "fecha_revision": existente.get("fecha_revision") or date.today(),
                "responsable_revision": existente.get("responsable_revision") or "Control documental",
                "observaciones": existente.get("observaciones") or "Checklist sincronizado con los documentos vigentes del expediente.",
                "fecha_creacion": existente.get("fecha_creacion") or ahora,
                "fecha_actualizacion": ahora,
                "usuario_actualizacion": USUARIO_PROTOTIPO,
            })
            filas.append(fila)

    st.session_state.data_m06["checklist_documental"] = asegurar_columnas_data({"checklist_documental": pd.DataFrame(filas)})["checklist_documental"]
    recalcular_completitud_expedientes()


def generar_id_secuencial_desde_filas(prefijo, df_existente, filas_nuevas, campo):
    """Genera un ID considerando registros existentes y los ya creados en la sincronización actual."""
    valores = []
    if not df_existente.empty and campo in df_existente.columns:
        valores.extend(df_existente[campo].dropna().astype(str).tolist())
    valores.extend(str(f.get(campo, "")) for f in filas_nuevas)
    numeros = [extraer_numero_id(v, prefijo) for v in valores]
    return f"{prefijo}-{(max(numeros) + 1 if numeros else 1):04d}"


def recalcular_completitud_expedientes():
    """Recalcula porcentaje de completitud por expediente con base en checklist."""
    expedientes = st.session_state.data_m06["expedientes"].copy()
    checklist = st.session_state.data_m06["checklist_documental"].copy()
    if expedientes.empty or checklist.empty:
        return
    for idx, exp in expedientes.iterrows():
        chk = checklist[checklist["id_expediente"].astype(str) == str(exp["id_expediente"])]
        if chk.empty:
            pct = 0.0
        else:
            pct = round((chk["cumple"].apply(normalizar_bool).sum() / len(chk)) * 100, 2)
        expedientes.at[idx, "porcentaje_completitud"] = pct
        expedientes.at[idx, "estado_expediente"] = "Completo" if pct == 100 else "Incompleto"
        expedientes.at[idx, "fecha_actualizacion"] = datetime.now().isoformat(timespec="seconds")
    st.session_state.data_m06["expedientes"] = expedientes
    guardar_memoria_local()


# ============================================================
# 7. FILTROS Y ENRIQUECIMIENTO
# ============================================================

def hogares_por_zona(zonas_sel):
    """Devuelve hogares asociados a zonas."""
    zonas_sel = normalizar_filtro_multiseleccion(zonas_sel)
    if not zonas_sel:
        return []
    hogares = obtener_df("hogares")
    if hogares.empty or "zona" not in hogares.columns:
        return []
    return hogares[hogares["zona"].astype(str).isin(zonas_sel)]["id_hogar"].astype(str).unique().tolist()


def predios_por_hogares(hogares_sel):
    """Devuelve predios asociados a hogares."""
    hogares_sel = normalizar_filtro_multiseleccion(hogares_sel)
    predios = obtener_df("predios")
    if not hogares_sel or predios.empty or "id_hogar" not in predios.columns:
        return []
    return predios[predios["id_hogar"].astype(str).isin(hogares_sel)]["id_predio"].astype(str).unique().tolist()


def filtrar_dataframe(tabla, filtros):
    """Aplica filtros globales a cualquier tabla."""
    df = obtener_df(tabla)
    if df.empty:
        return df

    zonas_sel = normalizar_filtro_multiseleccion(filtros.get("zona"))
    hogares_sel = normalizar_filtro_multiseleccion(filtros.get("id_hogar"))
    personas_sel = normalizar_filtro_multiseleccion(filtros.get("id_persona"))
    predios_sel = normalizar_filtro_multiseleccion(filtros.get("id_predio"))
    expedientes_sel = normalizar_filtro_multiseleccion(filtros.get("id_expediente"))

    if zonas_sel:
        if "zona" in df.columns:
            df = df[df["zona"].astype(str).isin(zonas_sel)]
        elif "id_hogar" in df.columns:
            ids_hogares = hogares_por_zona(zonas_sel)
            df = df[df["id_hogar"].astype(str).isin(ids_hogares)]
        elif "id_predio" in df.columns:
            ids_hogares = hogares_por_zona(zonas_sel)
            ids_predios = predios_por_hogares(ids_hogares)
            df = df[df["id_predio"].astype(str).isin(ids_predios)]

    if hogares_sel and "id_hogar" in df.columns:
        df = df[df["id_hogar"].astype(str).isin(hogares_sel)]

    if personas_sel and "id_persona" in df.columns:
        df = df[df["id_persona"].astype(str).isin(personas_sel)]

    if predios_sel and "id_predio" in df.columns:
        df = df[df["id_predio"].astype(str).isin(predios_sel)]

    if expedientes_sel and "id_expediente" in df.columns:
        df = df[df["id_expediente"].astype(str).isin(expedientes_sel)]

    for campo in ["estado_documento", "estado_expediente", "estado_revision", "categoria_documental", "tipo_entidad_asociada", "tipo_expediente"]:
        valores = normalizar_filtro_multiseleccion(filtros.get(campo))
        if valores and campo in df.columns:
            df = df[df[campo].astype(str).isin(valores)]

    return buscar_en_dataframe(df, filtros.get("busqueda"))


# ============================================================
# 8. MAPAS
# ============================================================

def crear_mapa_base(lat=9.19, lon=-80.10, zoom=11):
    """Crea mapa base."""
    return folium.Map(location=[lat, lon], zoom_start=zoom, tiles="CartoDB positron")


def agregar_predios_al_mapa(mapa, predios):
    """Agrega predios como polígonos irregulares."""
    for _, row in predios.iterrows():
        vertices = row.get("vertices_poligono", [])
        if isinstance(vertices, str):
            try:
                vertices = json.loads(vertices)
            except Exception:
                vertices = []
        if not vertices:
            continue

        popup = f"""
        <b>Predio:</b> {row.get('id_predio', '')}<br>
        <b>Hogar:</b> {row.get('id_hogar', '') or 'Sin hogar asociado'}<br>
        <b>Uso:</b> {row.get('uso_principal', '')}<br>
        <b>Área total:</b> {row.get('area_total_m2', 0)} m²<br>
        <b>Área afectada:</b> {row.get('area_afectada_m2', 0)} m²<br>
        <b>Afectación:</b> {row.get('porcentaje_afectacion', 0)}%<br>
        <b>Vértices:</b> {row.get('numero_vertices', 0)}
        """

        folium.Polygon(
            locations=vertices,
            color=COLOR_PRIMARIO_SOCIONAUT,
            fill=True,
            fill_opacity=0.36,
            weight=2,
            popup=folium.Popup(popup, max_width=360),
            tooltip=f"{row.get('id_predio', '')} · {row.get('numero_vertices', 0)} vértices",
        ).add_to(mapa)

    return mapa


# ============================================================
# 9. COMPONENTES DE INTERFAZ
# ============================================================

def mostrar_encabezado():
    """Muestra encabezado principal."""
    st.markdown('<div class="main-title">M06 · Gestión Documental y Expedientes</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Sistema de Información para Reasentamiento · ACP · PAR–PRMV · Enfoque IFC PS5</div>',
        unsafe_allow_html=True,
    )


def crear_chip(texto, tipo="default"):
    """Crea chip visual."""
    clase = {"danger": "chip-danger", "warning": "chip-warning", "success": "chip-success"}.get(tipo, "")
    return f'<span class="chip {clase}">{escape(str(texto))}</span>'


def tipo_chip_por_valor(valor):
    """Define color de chip según estado."""
    v = str(valor).lower()
    if v in ["observado", "rechazado", "vencido", "incompleto", "en disputa"]:
        return "danger"
    if v in ["pendiente", "pendiente revisión", "en revisión", "abierto", "no iniciado"]:
        return "warning"
    if v in ["aprobado", "validado", "completo", "liberado", "activo"]:
        return "success"
    return "default"


def mostrar_indicadores(filtros=None, tabla_activa=None, df_filtrado=None):
    """Muestra indicadores generales del módulo."""
    hogares = obtener_df("hogares")
    predios = obtener_df("predios")
    documentos = obtener_df("documentos")
    expedientes = obtener_df("expedientes")

    total_docs = len(documentos)
    docs_aprobados = len(documentos[documentos["estado_documento"].astype(str) == "Aprobado"]) if not documentos.empty else 0
    exp_completos = len(expedientes[expedientes["estado_expediente"].astype(str) == "Completo"]) if not expedientes.empty else 0
    pct_promedio = round(pd.to_numeric(expedientes["porcentaje_completitud"], errors="coerce").fillna(0).mean(), 2) if not expedientes.empty else 0

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Hogares", len(hogares))
    c2.metric("Predios", len(predios))
    c3.metric("Documentos", total_docs)
    c4.metric("Docs aprobados", docs_aprobados)
    c5.metric("Exp. completos", exp_completos)
    c6.metric("Completitud prom.", f"{pct_promedio}%")


def agrupar_campos_ficha(tabla, registro):
    """Agrupa campos para ficha de detalle."""
    grupos = {
        "Identificación": [],
        "Relaciones": [],
        "Caracterización": [],
        "Fechas y seguimiento": [],
        "Observaciones y auditoría": [],
    }

    for campo in ESQUEMA_M06[tabla]["campos"]:
        if campo not in registro:
            continue
        if campo.startswith("id_") or campo in ["codigo_hogar_campo", "nombre_documento", "nombre_referencia_hogar", "nombre_lugar_poblado"]:
            if campo in ["id_hogar", "id_persona", "id_predio", "id_lugar_poblado", "id_tipo_documento", "id_expediente", "id_documento_asociado"]:
                grupos["Relaciones"].append(campo)
            else:
                grupos["Identificación"].append(campo)
        elif "fecha" in campo or campo in ["estado_documento", "estado_expediente", "estado_revision", "resultado_revision", "porcentaje_completitud", "cumple"]:
            grupos["Fechas y seguimiento"].append(campo)
        elif "observ" in campo or "descripcion" in campo or "motivo" in campo:
            grupos["Observaciones y auditoría"].append(campo)
        else:
            grupos["Caracterización"].append(campo)

    return grupos


def html_campo_ficha(tabla, campo, valor):
    """Renderiza un campo de ficha en HTML."""
    if (tabla, campo) in RELACIONES:
        valor_txt = resolver_contexto_relacional(tabla, campo, valor)
    else:
        valor_txt = formatear_valor(campo, valor)
    return f"""
    <div class="record-field" title="{escape(tooltip_campo(campo))}">
        <div class="record-label">{escape(etiqueta_campo(campo))}</div>
        <div class="record-value">{escape(valor_txt)}</div>
    </div>
    """


def mostrar_ficha_registro(tabla, registro):
    """Muestra ficha completa del registro seleccionado."""
    llave = ESQUEMA_M06[tabla]["llave"]
    id_registro = str(registro.get(llave, ""))
    titulo = f"{id_registro} · {ESQUEMA_M06[tabla]['titulo']}"

    chips = []
    for campo in ["zona", "estado_documento", "estado_expediente", "estado_revision", "categoria_documental", "tipo_entidad_asociada", "tipo_expediente"]:
        if campo in registro and str(registro.get(campo, "")).strip():
            chips.append(crear_chip(f"{etiqueta_campo(campo)}: {formatear_valor(campo, registro.get(campo))}", tipo_chip_por_valor(registro.get(campo))))

    html = f"""
    <div class="record-card-printable">
        <div class="record-hero">
            <div>
                <div class="record-kicker">Ficha de detalle · {escape(ESQUEMA_M06[tabla]['titulo'])}</div>
                <h3 class="record-title">{escape(titulo)}</h3>
                <div class="record-subtitle">Información completa del registro seleccionado.</div>
            </div>
            <div>{''.join(chips)}</div>
        </div>
    """

    for grupo, campos in agrupar_campos_ficha(tabla, registro).items():
        if not campos:
            continue
        html += f"<div class='record-section-title'>{escape(grupo)}</div><div class='record-grid'>"
        for campo in campos:
            html += html_campo_ficha(tabla, campo, registro.get(campo))
        html += "</div>"

    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Editar este registro", use_container_width=True, key=f"editar_{tabla}_{id_registro}"):
            st.session_state[f"edicion_actual_{tabla}"] = id_registro
            st.session_state["panel_destino_m06"] = "Agregar / editar registro"
            st.rerun()
    with c2:
        st.download_button(
            "Descargar ficha CSV individual",
            data=pd.DataFrame([registro]).to_csv(index=False).encode("utf-8-sig"),
            file_name=f"ficha_{tabla}_{id_registro}.csv",
            mime="text/csv",
            use_container_width=True,
            key=f"csv_ficha_{tabla}_{id_registro}",
        )


def mostrar_resumen_hogar(ids_hogar):
    """Muestra ficha documental rápida cuando existe un único hogar filtrado."""
    ids = normalizar_filtro_multiseleccion(ids_hogar)
    if len(ids) != 1:
        return

    id_hogar = ids[0]
    hogares = obtener_df("hogares")
    personas = obtener_personas_por_hogar(id_hogar)
    predios = obtener_predios_por_hogar(id_hogar)
    documentos = obtener_df("documentos")
    expedientes = obtener_df("expedientes")
    checklist = obtener_df("checklist_documental")

    hogar_fila = hogares[hogares["id_hogar"].astype(str) == id_hogar] if not hogares.empty else pd.DataFrame()
    hogar = hogar_fila.iloc[0].to_dict() if not hogar_fila.empty else {}
    docs_h = documentos[documentos["id_hogar"].astype(str) == id_hogar] if not documentos.empty else pd.DataFrame()
    exp_h = expedientes[expedientes["id_hogar"].astype(str) == id_hogar] if not expedientes.empty else pd.DataFrame()
    ids_exp = exp_h["id_expediente"].astype(str).tolist() if not exp_h.empty else []
    chk_h = checklist[checklist["id_expediente"].astype(str).isin(ids_exp)] if ids_exp and not checklist.empty else pd.DataFrame()

    aprobados = len(docs_h[docs_h["estado_documento"].astype(str) == "Aprobado"]) if not docs_h.empty else 0
    pendientes = len(docs_h[docs_h["estado_documento"].astype(str).isin(["Pendiente revisión", "Observado", "Rechazado", "Vencido"])]) if not docs_h.empty else 0
    completitud = round(pd.to_numeric(exp_h.get("porcentaje_completitud", pd.Series(dtype=float)), errors="coerce").fillna(0).mean(), 2) if not exp_h.empty else 0
    faltantes = len(chk_h[~chk_h["cumple"].apply(normalizar_bool)]) if not chk_h.empty else 0

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown(f"#### Ficha documental del hogar · {id_hogar}")
    st.caption(f"{hogar.get('nombre_referencia_hogar', '')} · {hogar.get('zona', '')}")
    c1, c2, c3, c4 = st.columns(4)
    c1.info(f"**Personas / Predios**\n\n{len(personas)} / {len(predios)}")
    c2.info(f"**Documentos**\n\n{len(docs_h)} ({aprobados} aprobados)")
    c3.info(f"**Expedientes**\n\n{len(exp_h)} · {completitud}%")
    c4.info(f"**Pendientes / Faltantes**\n\n{pendientes} / {faltantes}")
    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# 10. FORMULARIOS
# ============================================================

def obtener_valor_inicial(df, llave, id_edicion, campo, tipo):
    """Obtiene valor inicial para formulario."""
    if id_edicion == "Nuevo registro" or df.empty or llave not in df.columns:
        if tipo == "Fecha":
            return date.today()
        if tipo == "Booleano":
            return False
        if tipo in ["Número", "Número calculado"]:
            return 0
        if tipo == "Decimal":
            return 0.0
        if campo == "vertices_poligono":
            return "[]"
        return ""

    fila = df[df[llave].astype(str) == str(id_edicion)]
    if fila.empty or campo not in fila.columns:
        return ""
    valor = fila.iloc[0][campo]
    if isinstance(valor, float) and pd.isna(valor):
        return ""
    return valor


def orden_campos_formulario(tabla):
    """Ordena relaciones para capturar siempre hogar antes que persona o predio."""
    campos = list(ESQUEMA_M06[tabla]["campos"].items())
    prioridad = {
        "documentos": ["id_documento", "tipo_entidad_asociada", "id_hogar", "id_persona", "id_predio"],
        "expedientes": ["id_expediente", "tipo_expediente", "id_hogar", "id_persona", "id_predio"],
        "personas": ["id_persona", "id_hogar"],
        "predios": ["id_predio", "id_hogar"],
    }.get(tabla, [])
    mapa = dict(campos)
    ordenados = [(campo, mapa[campo]) for campo in prioridad if campo in mapa]
    usados = {campo for campo, _ in ordenados}
    ordenados.extend((campo, tipo) for campo, tipo in campos if campo not in usados)
    return ordenados


def widget_key(tabla, campo, id_edicion):
    """Genera key única para widgets."""
    token = st.session_state.get("form_reset_counter_m06", 0)
    id_limpio = str(id_edicion).replace(" ", "_").replace("/", "_")
    return f"form_{tabla}_{id_limpio}_{token}_{campo}"


def obtener_opciones_relacionales(tabla_origen, campo_origen, filtro_hogar=None):
    """Obtiene opciones relacionales con etiqueta descriptiva."""
    relacion = RELACIONES.get((tabla_origen, campo_origen))
    if not relacion:
        return []
    tabla_catalogo, campo_id, campo_desc = relacion
    df = obtener_df(tabla_catalogo)
    if df.empty or campo_id not in df.columns:
        return []

    hogares_filtro = normalizar_filtro_multiseleccion(filtro_hogar)
    if tabla_catalogo in ["personas", "predios"] and not hogares_filtro:
        return []
    if hogares_filtro and "id_hogar" in df.columns:
        df = df[df["id_hogar"].astype(str).isin(hogares_filtro)]

    opciones = []
    for _, row in df.iterrows():
        valor = str(row.get(campo_id, ""))
        if not valor:
            continue
        if tabla_catalogo == "personas":
            desc = f"{row.get('nombres', '')} {row.get('apellidos', '')}".strip()
        else:
            desc = row.get(campo_desc, "") if campo_desc in df.columns else ""
        opciones.append((valor, f"{valor} · {desc}" if desc else valor))
    return opciones


def renderizar_selector_relacional(tabla, campo, valor_inicial, key, registro_parcial):
    """Renderiza selector relacional."""
    filtro_hogar = registro_parcial.get("id_hogar")
    opciones = obtener_opciones_relacionales(tabla, campo, filtro_hogar=filtro_hogar)
    opcional = "opcional" in ESQUEMA_M06[tabla]["campos"].get(campo, "").lower()

    if opcional:
        opciones = [("", "Sin asociar")] + opciones

    if not opciones:
        st.warning(f"No hay opciones disponibles para {etiqueta_campo(campo)}. Selecciona primero un hogar con registros asociados.")
        return ""

    valores = [valor for valor, _ in opciones]
    etiquetas = {valor: etiqueta for valor, etiqueta in opciones}
    valor_inicial = str(valor_inicial or "")
    index = valores.index(valor_inicial) if valor_inicial in valores else 0
    return st.selectbox(
        etiqueta_campo(campo),
        valores,
        index=index,
        format_func=lambda x: etiquetas.get(x, x),
        key=key,
        help=tooltip_campo(campo),
    )


def campo_formulario(tabla, campo, tipo, valor_inicial, id_edicion, registro_parcial=None):
    """Renderiza widget según tipo de campo."""
    registro_parcial = registro_parcial or {}
    key = widget_key(tabla, campo, id_edicion)

    if es_campo_id_automatico(tabla, campo):
        valor_auto = str(valor_inicial or "")
        st.text_input(etiqueta_campo(campo), value=valor_auto, disabled=True, key=key, help=tooltip_campo(campo))
        return valor_auto

    if tipo == "Número calculado":
        valor = float(valor_inicial or 0) if campo == "porcentaje_completitud" or campo == "porcentaje_afectacion" else int(valor_inicial or 0)
        if campo in ["porcentaje_completitud", "porcentaje_afectacion"]:
            return st.number_input(etiqueta_campo(campo), value=float(valor), step=0.01, disabled=True, key=key, help=tooltip_campo(campo))
        return st.number_input(etiqueta_campo(campo), value=int(valor), step=1, disabled=True, key=key, help=tooltip_campo(campo))

    if tipo == "Texto autollenado":
        st.text_input(etiqueta_campo(campo), value=str(valor_inicial or ""), disabled=True, key=key, help=tooltip_campo(campo))
        return str(valor_inicial or "")

    if (tabla, campo) in RELACIONES:
        return renderizar_selector_relacional(tabla, campo, valor_inicial, key, registro_parcial)

    if tipo == "Catálogo" or campo in CATALOGOS:
        opciones = CATALOGOS.get(campo, [])
        if not opciones:
            return st.text_input(etiqueta_campo(campo), value=str(valor_inicial or ""), key=key, help=tooltip_campo(campo))
        index = opciones.index(valor_inicial) if valor_inicial in opciones else 0
        return st.selectbox(etiqueta_campo(campo), opciones, index=index, key=key, help=tooltip_campo(campo))

    if tipo == "Fecha":
        if not isinstance(valor_inicial, date):
            valor_inicial = date.today()
        return st.date_input(etiqueta_campo(campo), value=valor_inicial, key=key, help=tooltip_campo(campo))

    if tipo == "Booleano":
        return st.checkbox(etiqueta_campo(campo), value=normalizar_bool(valor_inicial), key=key, help=tooltip_campo(campo))

    if tipo == "Número":
        return st.number_input(etiqueta_campo(campo), value=int(valor_inicial or 0), step=1, key=key, help=tooltip_campo(campo))

    if tipo == "Decimal":
        return st.number_input(etiqueta_campo(campo), value=float(valor_inicial or 0.0), step=0.01, key=key, help=tooltip_campo(campo))

    if "Texto largo" in tipo:
        if campo == "vertices_poligono":
            if isinstance(valor_inicial, list):
                valor_inicial = json.dumps(valor_inicial, ensure_ascii=False, indent=2)
            return st.text_area(
                etiqueta_campo(campo),
                value=str(valor_inicial or "[]"),
                height=180,
                key=key,
                help="Captura una lista JSON de vértices: [[lat, lon], [lat, lon], ...].",
            )
        return st.text_area(etiqueta_campo(campo), value=str(valor_inicial or ""), key=key, help=tooltip_campo(campo))

    return st.text_input(etiqueta_campo(campo), value=str(valor_inicial or ""), key=key, help=tooltip_campo(campo))


def preajustar_valor_por_filtro(tabla, campo, valor_inicial, filtros):
    """Usa filtros activos para prellenar formularios nuevos."""
    if campo == "id_hogar":
        hogar_unico = obtener_unico_filtro(filtros.get("id_hogar"))
        return hogar_unico or valor_inicial
    if campo == "id_persona":
        persona_unica = obtener_unico_filtro(filtros.get("id_persona"))
        return persona_unica or valor_inicial
    if campo == "id_predio":
        predio_unico = obtener_unico_filtro(filtros.get("id_predio"))
        return predio_unico or valor_inicial
    return valor_inicial


def normalizar_vertices_formulario(valor):
    """Convierte vértices desde texto JSON a lista."""
    if isinstance(valor, list):
        return valor
    try:
        data = json.loads(valor)
        if isinstance(data, list):
            return data
    except Exception:
        pass
    return []


def mostrar_formulario(tabla, filtros):
    """Formulario genérico para agregar/editar registros."""
    config = ESQUEMA_M06[tabla]
    llave = config["llave"]
    df = obtener_df(tabla)
    ids = obtener_opciones(tabla, llave)
    target_key = f"edicion_actual_{tabla}"
    st.session_state.setdefault(target_key, "Nuevo registro")
    target = st.session_state.get(target_key, "Nuevo registro")

    if target not in ["Nuevo registro"] + ids:
        target = "Nuevo registro"
        st.session_state[target_key] = target

    selector_key = f"selector_edicion_{tabla}_{st.session_state.get('form_reset_counter_m06', 0)}"
    opcion_edicion = st.selectbox(
        "Selecciona registro para editar o crea uno nuevo",
        ["Nuevo registro"] + ids,
        index=(["Nuevo registro"] + ids).index(target),
        key=selector_key,
        help="Selecciona un registro existente o deja Nuevo registro para capturar información nueva.",
    )
    st.session_state[target_key] = opcion_edicion

    st.markdown(f"#### Formulario completo · {config['titulo']}")
    st.markdown(
        f"<div class='screen-help'>💡 {escape(TOOLTIPS_PANTALLA.get(tabla, 'Captura la información solicitada en esta pantalla.'))}</div>",
        unsafe_allow_html=True,
    )

    registro = {}
    campos = orden_campos_formulario(tabla)
    columnas = st.columns(2)

    for i, (campo, tipo) in enumerate(campos):
        # Ocultar campos relacionales no aplicables según tipo de entidad/documento/expediente.
        if tabla == "documentos":
            tipo_entidad = registro.get("tipo_entidad_asociada")
            if campo == "id_hogar" and tipo_entidad not in ["Hogar", "Persona", "Predio", None, ""]:
                registro[campo] = ""
                continue
            if campo == "id_persona" and tipo_entidad != "Persona":
                registro[campo] = ""
                continue
            if campo == "id_predio" and tipo_entidad != "Predio":
                registro[campo] = ""
                continue

        if tabla == "expedientes":
            tipo_expediente = registro.get("tipo_expediente")
            if campo == "id_persona" and tipo_expediente != "Persona":
                registro[campo] = ""
                continue
            if campo == "id_predio" and tipo_expediente != "Predio":
                registro[campo] = ""
                continue

        with columnas[i % 2]:
            valor_inicial = obtener_valor_inicial(df, llave, opcion_edicion, campo, tipo)
            if opcion_edicion == "Nuevo registro" and es_campo_id_automatico(tabla, campo):
                valor_inicial = generar_id_secuencial(tabla, campo)
            if opcion_edicion == "Nuevo registro":
                valor_inicial = preajustar_valor_por_filtro(tabla, campo, valor_inicial, filtros)

            registro[campo] = campo_formulario(
                tabla,
                campo,
                tipo,
                valor_inicial,
                opcion_edicion,
                registro_parcial=registro,
            )

    if tabla == "predios":
        registro["vertices_poligono"] = normalizar_vertices_formulario(registro.get("vertices_poligono"))
    registro = aplicar_reglas_automaticas(tabla, registro)

    if tabla == "predios":
        st.info(
            f"Polígono calculado: **{registro.get('numero_vertices', 0)} vértices** · "
            f"Afectación: **{registro.get('porcentaje_afectacion', 0)}%**"
        )

    c_guardar, c_limpiar = st.columns([2, 1])
    with c_guardar:
        guardar = st.button("Guardar registro", type="primary", use_container_width=True, key=f"guardar_{tabla}_{opcion_edicion}")
    with c_limpiar:
        limpiar = st.button("Limpiar formulario", use_container_width=True, key=f"limpiar_{tabla}_{opcion_edicion}")

    if limpiar:
        st.session_state[target_key] = "Nuevo registro"
        st.session_state["form_reset_counter_m06"] += 1
        st.rerun()

    if guardar:
        errores = validar_registro(tabla, registro)
        if errores:
            for error in errores:
                st.error(error)
        else:
            accion = guardar_registro(tabla, registro, llave)
            st.success(f"Registro {accion} correctamente en {config['titulo']}.")
            st.session_state[target_key] = "Nuevo registro"
            st.session_state["form_reset_counter_m06"] += 1
            st.session_state["panel_destino_m06"] = "Agregar / editar registro"
            st.rerun()


# ============================================================
# 11. VISUALIZACIÓN, FILTROS Y NAVEGACIÓN
# ============================================================

def mostrar_tabla_y_ficha(tabla, filtros):
    """Muestra tabla filtrada y ficha de registro seleccionado."""
    config = ESQUEMA_M06[tabla]
    llave = config["llave"]
    df_filtrado = filtrar_dataframe(tabla, filtros)
    campos = [c for c in config["campos_principales"] if c in df_filtrado.columns]

    st.markdown(f"#### Visualización principal · {config['titulo']}")
    st.markdown(
        f"<div class='screen-help'>🔎 {escape(TOOLTIPS_PANTALLA.get(tabla, 'Consulta y selecciona registros para ver su ficha de detalle.'))}</div>",
        unsafe_allow_html=True,
    )

    if df_filtrado.empty:
        st.warning("No hay registros para los filtros seleccionados.")
        return df_filtrado

    df_vista = convertir_para_visualizacion(df_filtrado[campos])
    id_seleccionado = None

    try:
        evento = st.dataframe(
            df_vista,
            use_container_width=True,
            hide_index=True,
            key=f"df_{tabla}_{st.session_state.get('form_reset_counter_m06', 0)}",
            on_select="rerun",
            selection_mode="single-row",
        )
        filas = evento.selection.rows
        if filas:
            id_seleccionado = str(df_filtrado.iloc[filas[0]][llave])
    except TypeError:
        st.dataframe(df_vista, use_container_width=True, hide_index=True)
    except Exception:
        id_seleccionado = None

    opciones_ids = df_filtrado[llave].astype(str).tolist() if llave in df_filtrado.columns else []
    if not id_seleccionado and opciones_ids:
        id_seleccionado = st.selectbox(
            "Selecciona un registro para ver su ficha completa",
            opciones_ids,
            key=f"selector_ficha_{tabla}_{st.session_state.get('form_reset_counter_m06', 0)}",
        )

    if id_seleccionado:
        fila = df_filtrado[df_filtrado[llave].astype(str) == id_seleccionado]
        if not fila.empty:
            mostrar_ficha_registro(tabla, fila.iloc[0].to_dict())

    st.download_button(
        "Descargar tabla filtrada CSV",
        data=convertir_para_visualizacion(df_filtrado).to_csv(index=False).encode("utf-8-sig"),
        file_name=f"{tabla}_filtrada.csv",
        mime="text/csv",
        use_container_width=True,
        help="Descarga únicamente los registros visibles después de aplicar filtros.",
    )

    return df_filtrado


def multiselect_con_todos(label, opciones, key, default=None, help_text=""):
    """Multiselect con opción Todos."""
    opciones = sorted([str(o) for o in opciones if str(o).strip()])
    opciones_ui = ["Todos"] + opciones
    if default is None:
        default = ["Todos"]
    valor = st.sidebar.multiselect(label, opciones_ui, default=default, key=key, help=help_text)
    if not valor or "Todos" in valor:
        return []
    return valor


def mostrar_sidebar():
    """Renderiza controles laterales."""
    st.sidebar.title("M06 · Controles")
    tabla = st.sidebar.radio(
        "Pantalla / tabla",
        list(ESQUEMA_M06.keys()),
        format_func=lambda x: ESQUEMA_M06[x]["titulo"],
        help="Selecciona la pantalla de trabajo del módulo.",
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("Filtros de pantalla")
    filtros = {"busqueda": ""}

    zonas = sorted(set(obtener_opciones("hogares", "zona") + obtener_opciones("lugares_poblados", "zona")))
    filtros["zona"] = multiselect_con_todos(
        "Zona",
        zonas,
        key=f"filtro_zona_global_{tabla}",
        help_text="Filtro global por zona. En tablas sin campo zona, se aplica indirectamente por hogar o predio asociado.",
    )

    hogares_df = obtener_df("hogares")
    zonas_sel = normalizar_filtro_multiseleccion(filtros.get("zona"))
    if zonas_sel and not hogares_df.empty and "zona" in hogares_df.columns:
        hogares_df = hogares_df[hogares_df["zona"].astype(str).isin(zonas_sel)]
    opciones_hogar = hogares_df["id_hogar"].dropna().astype(str).unique().tolist() if not hogares_df.empty else []

    campos_tabla = ESQUEMA_M06[tabla]["campos"].keys()

    if tabla == "hogares" or "id_hogar" in campos_tabla:
        filtros["id_hogar"] = multiselect_con_todos("Hogar", opciones_hogar, key=f"filtro_hogar_{tabla}", help_text="Selecciona uno o varios hogares.")
    else:
        filtros["id_hogar"] = []

    personas = obtener_df("personas")
    hogares_sel = normalizar_filtro_multiseleccion(filtros.get("id_hogar"))
    if hogares_sel and not personas.empty and "id_hogar" in personas.columns:
        personas = personas[personas["id_hogar"].astype(str).isin(hogares_sel)]
    opciones_persona = sorted(personas["id_persona"].dropna().astype(str).unique().tolist()) if not personas.empty and "id_persona" in personas.columns else []

    if tabla == "personas" or "id_persona" in campos_tabla:
        filtros["id_persona"] = multiselect_con_todos("Persona", opciones_persona, key=f"filtro_persona_{tabla}", help_text="Selecciona una o varias personas.")
    else:
        filtros["id_persona"] = []

    predios = obtener_df("predios")
    if hogares_sel and not predios.empty and "id_hogar" in predios.columns:
        predios = predios[predios["id_hogar"].astype(str).isin(hogares_sel)]
    elif zonas_sel and not predios.empty and "id_hogar" in predios.columns:
        ids_hogares_zona = hogares_df["id_hogar"].dropna().astype(str).unique().tolist() if not hogares_df.empty else []
        predios = predios[predios["id_hogar"].astype(str).isin(ids_hogares_zona)]
    opciones_predio = sorted(predios["id_predio"].dropna().astype(str).unique().tolist()) if not predios.empty and "id_predio" in predios.columns else []

    if tabla == "predios" or "id_predio" in campos_tabla:
        filtros["id_predio"] = multiselect_con_todos("Predio", opciones_predio, key=f"filtro_predio_{tabla}", help_text="Selecciona uno o varios predios.")
    else:
        filtros["id_predio"] = []

    if tabla == "expedientes" or "id_expediente" in campos_tabla:
        expedientes_df = obtener_df("expedientes")
        if hogares_sel and not expedientes_df.empty:
            expedientes_df = expedientes_df[expedientes_df["id_hogar"].astype(str).isin(hogares_sel)]
        personas_sel = normalizar_filtro_multiseleccion(filtros.get("id_persona"))
        predios_sel = normalizar_filtro_multiseleccion(filtros.get("id_predio"))
        if personas_sel and "id_persona" in expedientes_df.columns:
            expedientes_df = expedientes_df[expedientes_df["id_persona"].astype(str).isin(personas_sel)]
        if predios_sel and "id_predio" in expedientes_df.columns:
            expedientes_df = expedientes_df[expedientes_df["id_predio"].astype(str).isin(predios_sel)]
        opciones_expediente = expedientes_df["id_expediente"].dropna().astype(str).unique().tolist() if not expedientes_df.empty else []
        filtros["id_expediente"] = multiselect_con_todos(
            "Expediente",
            opciones_expediente,
            key=f"filtro_expediente_{tabla}",
            help_text="Selecciona expedientes del hogar y, cuando aplique, de la persona o predio filtrado.",
        )
    else:
        filtros["id_expediente"] = []

    for campo in ["estado_documento", "estado_expediente", "estado_revision", "categoria_documental", "tipo_entidad_asociada", "tipo_expediente"]:
        if campo in campos_tabla:
            filtros[campo] = multiselect_con_todos(
                etiqueta_campo(campo),
                obtener_opciones(tabla, campo),
                key=f"filtro_{tabla}_{campo}",
                help_text=tooltip_campo(campo),
            )

    filtros["busqueda"] = st.sidebar.text_input(
        "Buscador en pantalla",
        value=st.session_state.busqueda_global_m06,
        placeholder="Buscar ID, nombre, estado, documento...",
        help="Busca dentro de los registros visibles de la pantalla activa.",
    )
    st.session_state.busqueda_global_m06 = filtros["busqueda"]

    st.sidebar.markdown("---")
    st.sidebar.caption("Los filtros son multiselección. Zona aplica directa o indirectamente mediante hogar/predio.")
    if st.sidebar.button("Guardar memoria local", use_container_width=True):
        guardar_memoria_local()
        st.sidebar.success("Memoria local guardada.")
    if st.sidebar.button("Reiniciar con data de prueba", use_container_width=True):
        st.session_state.data_m06 = crear_data_inicial()
        guardar_memoria_local()
        st.session_state["form_reset_counter_m06"] += 1
        st.sidebar.success("Data de prueba restaurada.")
        st.rerun()

    return tabla, filtros


def preparar_panel_destino():
    """Envía a formulario cuando se presiona editar desde ficha."""
    destino = st.session_state.get("panel_destino_m06")
    if destino:
        st.session_state["panel_m06"] = destino
        st.session_state["panel_destino_m06"] = None


# ============================================================
# 12. INICIO / DASHBOARD DEL MÓDULO
# ============================================================

def pantalla_inicio(filtros):
    """Dashboard del M06 con mapa y resumen documental."""
    st.markdown("### Inicio del módulo")
    st.markdown(
        "<div class='screen-help'>📁 Dashboard de control documental, expedientes, checklist y relación predial simulada.</div>",
        unsafe_allow_html=True,
    )

    predios = filtrar_dataframe("predios", filtros)
    documentos = filtrar_dataframe("documentos", filtros)
    expedientes = filtrar_dataframe("expedientes", filtros)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Predios visibles", len(predios))
    c2.metric("Documentos visibles", len(documentos))
    c3.metric("Expedientes visibles", len(expedientes))
    c4.metric(
        "Completitud visible",
        f"{round(pd.to_numeric(expedientes.get('porcentaje_completitud', pd.Series(dtype=float)), errors='coerce').fillna(0).mean(), 2) if not expedientes.empty else 0}%",
    )

    st.markdown("#### Mapa de predios con polígonos irregulares")
    mapa = crear_mapa_base()
    mapa = agregar_predios_al_mapa(mapa, predios)
    st_folium(mapa, width=None, height=520, returned_objects=[])

    st.markdown("#### Relación hogares-predios")
    if not predios.empty:
        resumen = predios.groupby("id_hogar", dropna=False).agg(
            predios_asociados=("id_predio", "count"),
            area_total_m2=("area_total_m2", "sum"),
            area_afectada_m2=("area_afectada_m2", "sum"),
        ).reset_index()
        resumen["id_hogar"] = resumen["id_hogar"].replace("", "Sin hogar asociado")
        resumen["porcentaje_afectacion_promedio"] = resumen.apply(
            lambda r: calcular_porcentaje_afectacion(r["area_afectada_m2"], r["area_total_m2"]),
            axis=1,
        )
        st.dataframe(resumen, use_container_width=True, hide_index=True)


# ============================================================
# 13. MAIN
# ============================================================

def main():
    """Controlador principal del módulo."""
    aplicar_estilos()
    inicializar_estado()
    preparar_panel_destino()
    mostrar_encabezado()

    tabla, filtros = mostrar_sidebar()
    df_filtrado = filtrar_dataframe(tabla, filtros)

    mostrar_indicadores(filtros=filtros, tabla_activa=tabla, df_filtrado=df_filtrado)
    mostrar_resumen_hogar(filtros.get("id_hogar"))

    st.markdown("---")
    panel = st.radio(
        "Sección de trabajo",
        ["Inicio del módulo", "Visualización principal", "Agregar / editar registro"],
        horizontal=True,
        key="panel_m06",
    )

    if panel == "Inicio del módulo":
        pantalla_inicio(filtros)
    elif panel == "Visualización principal":
        mostrar_tabla_y_ficha(tabla, filtros)
    else:
        mostrar_formulario(tabla, filtros)


if __name__ == "__main__":
    main()
