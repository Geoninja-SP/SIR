# ============================================================
# SIR ACP - M06 Gestión Documental y Expedientes
# Versión v3 - Catálogo legal PAC integrado
# ============================================================
# - Tres pantallas principales: Lugares poblados, Hogares y Personas.
# - Los datos maestros se consultan como referencias de otros módulos.
# - El catálogo documental proviene del Excel PAC entregado.
# - Checklist obligatorio y progreso exclusivamente para Hogares.
# - Cada documento requiere un revisor distinto del usuario que lo carga.
# - Actualización por ID único, sin duplicar registros.
# - Memoria activa con st.session_state y persistencia local JSON.
# ============================================================

import json
import re
from pathlib import Path
from datetime import date, datetime

import pandas as pd
import streamlit as st


# ============================================================
# 1. CONFIGURACIÓN GENERAL
# ============================================================

st.set_page_config(
    page_title="SIR ACP | M06 Gestión Documental",
    page_icon="📁",
    layout="wide",
    initial_sidebar_state="expanded",
)

COLOR_PRIMARIO = "#073B5A"
COLOR_SECUNDARIO = "#00A6A6"
COLOR_CORAL = "#F05A43"

ARCHIVO_MEMORIA = Path("memoria_m06_gestion_documental_v3.json")

USUARIOS = [
    "ana.documental",
    "carlos.legal",
    "diana.social",
    "elena.control",
    "francisco.acp",
]

ESTADOS_EXPEDIENTE = ["Abierto", "En gestión", "En revisión", "Completo", "Cerrado"]
ESTADOS_APLICABILIDAD = ["Pendiente de determinar", "Aplica", "No aplica"]
ESTADOS_REVISION = [
    "Pendiente de asignación",
    "Pendiente de revisión",
    "En revisión",
    "Aprobado",
    "Observado",
    "Rechazado",
]


# ============================================================
# 2. CATÁLOGO DOCUMENTAL INTEGRADO DESDE EXCEL
# ============================================================

CATALOGO_DOCUMENTAL = [{'orden': 1, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-01', 'carpeta': '01 Reuniones', 'codigo_documento': 'ACT-REU', 'tipo_documental': 'Acta de reunión', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 2, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-01', 'carpeta': '01 Reuniones', 'codigo_documento': 'MIN-REU', 'tipo_documental': 'Minuta de reunión', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 3, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-01', 'carpeta': '01 Reuniones', 'codigo_documento': 'LIS-ASIS', 'tipo_documental': 'Lista de asistencia', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 4, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-01', 'carpeta': '01 Reuniones', 'codigo_documento': 'CONV-REU', 'tipo_documental': 'Convocatoria de reunión', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 5, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-01', 'carpeta': '01 Reuniones', 'codigo_documento': 'REG-ACU', 'tipo_documental': 'Registro de acuerdos y compromisos', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 6, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-02', 'carpeta': '02 Comunicaciones y notificaciones oficiales', 'codigo_documento': 'COM-OFI', 'tipo_documental': 'Comunicación oficial', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 7, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-02', 'carpeta': '02 Comunicaciones y notificaciones oficiales', 'codigo_documento': 'NOT-OFI', 'tipo_documental': 'Notificación oficial', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 8, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-02', 'carpeta': '02 Comunicaciones y notificaciones oficiales', 'codigo_documento': 'CIR-INF', 'tipo_documental': 'Circular informativa', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 9, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-02', 'carpeta': '02 Comunicaciones y notificaciones oficiales', 'codigo_documento': 'AVI-PUB', 'tipo_documental': 'Aviso público', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 10, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-02', 'carpeta': '02 Comunicaciones y notificaciones oficiales', 'codigo_documento': 'CON-ENT', 'tipo_documental': 'Constancia de entrega o recepción de comunicación', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 11, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-03', 'carpeta': '03 Acuerdos comunitarios', 'codigo_documento': 'ACU-LP', 'tipo_documental': 'Acuerdo con el lugar poblado', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 12, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-03', 'carpeta': '03 Acuerdos comunitarios', 'codigo_documento': 'ACT-APR', 'tipo_documental': 'Acta de aprobación de acuerdo', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 13, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-03', 'carpeta': '03 Acuerdos comunitarios', 'codigo_documento': 'ACT-RAT', 'tipo_documental': 'Acta de ratificación de acuerdo', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 14, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-03', 'carpeta': '03 Acuerdos comunitarios', 'codigo_documento': 'ADD-ACU', 'tipo_documental': 'Adenda a acuerdo', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 15, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-03', 'carpeta': '03 Acuerdos comunitarios', 'codigo_documento': 'REG-FIR', 'tipo_documental': 'Registro de firmas del acuerdo', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 16, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-04', 'carpeta': '04 Convenios y compromisos', 'codigo_documento': 'CONV-COL', 'tipo_documental': 'Convenio colectivo', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 17, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-04', 'carpeta': '04 Convenios y compromisos', 'codigo_documento': 'CAR-COM', 'tipo_documental': 'Carta de compromiso', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 18, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-04', 'carpeta': '04 Convenios y compromisos', 'codigo_documento': 'MEM-ENT', 'tipo_documental': 'Memorando de entendimiento', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 19, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-04', 'carpeta': '04 Convenios y compromisos', 'codigo_documento': 'ACT-COM', 'tipo_documental': 'Acta de compromiso', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 20, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-04', 'carpeta': '04 Convenios y compromisos', 'codigo_documento': 'ADD-CONV', 'tipo_documental': 'Adenda a convenio', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 21, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-05', 'carpeta': '05 Bienes', 'codigo_documento': 'INV-BIE-COL', 'tipo_documental': 'Inventario de bienes colectivos', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 22, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-05', 'carpeta': '05 Bienes', 'codigo_documento': 'ACT-INS-BIE', 'tipo_documental': 'Acta de inspección de bienes', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 23, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-05', 'carpeta': '05 Bienes', 'codigo_documento': 'ACT-VAL-BIE', 'tipo_documental': 'Acta de validación de inventario', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 24, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-05', 'carpeta': '05 Bienes', 'codigo_documento': 'DOC-PRO-BIE', 'tipo_documental': 'Documento de propiedad o titularidad del bien', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 25, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-05', 'carpeta': '05 Bienes', 'codigo_documento': 'AVA-BIE', 'tipo_documental': 'Avalúo de bien', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 26, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-05', 'carpeta': '05 Bienes', 'codigo_documento': 'REG-FOT-BIE', 'tipo_documental': 'Registro fotográfico del bien', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 27, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-05', 'carpeta': '05 Bienes', 'codigo_documento': 'ACT-AFE-BIE', 'tipo_documental': 'Acta de afectación del bien', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 28, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-06', 'carpeta': '06 Salvataje', 'codigo_documento': 'SOL-SALV-COL', 'tipo_documental': 'Solicitud de salvataje', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 29, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-06', 'carpeta': '06 Salvataje', 'codigo_documento': 'AUT-SALV-COL', 'tipo_documental': 'Autorización de salvataje', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 30, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-06', 'carpeta': '06 Salvataje', 'codigo_documento': 'INV-SALV-COL', 'tipo_documental': 'Inventario de bienes de salvataje', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 31, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-06', 'carpeta': '06 Salvataje', 'codigo_documento': 'ACT-ENT-SALV-COL', 'tipo_documental': 'Acta de entrega de bienes de salvataje', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 32, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-06', 'carpeta': '06 Salvataje', 'codigo_documento': 'ACT-RET-SALV-COL', 'tipo_documental': 'Acta de retiro de bienes de salvataje', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 33, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-06', 'carpeta': '06 Salvataje', 'codigo_documento': 'CON-REC-SALV-COL', 'tipo_documental': 'Constancia de recepción de bienes de salvataje', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 34, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-07', 'carpeta': '07 Entrega, reubicación y recepción', 'codigo_documento': 'ACT-ENT-BIE-COL', 'tipo_documental': 'Acta de entrega de bienes colectivos', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 35, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-07', 'carpeta': '07 Entrega, reubicación y recepción', 'codigo_documento': 'ACT-REC-BIE-COL', 'tipo_documental': 'Acta de recepción de bienes colectivos', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 36, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-07', 'carpeta': '07 Entrega, reubicación y recepción', 'codigo_documento': 'ACT-REU-COL', 'tipo_documental': 'Acta de reubicación colectiva', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 37, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-07', 'carpeta': '07 Entrega, reubicación y recepción', 'codigo_documento': 'ACT-ENT-LLA-COL', 'tipo_documental': 'Acta de entrega de llaves', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 38, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-07', 'carpeta': '07 Entrega, reubicación y recepción', 'codigo_documento': 'INV-ENT-COL', 'tipo_documental': 'Inventario de bienes entregados', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 39, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-07', 'carpeta': '07 Entrega, reubicación y recepción', 'codigo_documento': 'CON-REC-COL', 'tipo_documental': 'Constancia de recepción conforme', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 40, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-07', 'carpeta': '07 Entrega, reubicación y recepción', 'codigo_documento': 'GAR-BIE-COL', 'tipo_documental': 'Garantía de bienes entregados', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 41, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-08', 'carpeta': '08 Quejas y respuestas formales', 'codigo_documento': 'QUE-COL', 'tipo_documental': 'Queja colectiva', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 42, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-08', 'carpeta': '08 Quejas y respuestas formales', 'codigo_documento': 'REC-COL', 'tipo_documental': 'Reclamo colectivo', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 43, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-08', 'carpeta': '08 Quejas y respuestas formales', 'codigo_documento': 'SOL-FOR', 'tipo_documental': 'Solicitud formal', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 44, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-08', 'carpeta': '08 Quejas y respuestas formales', 'codigo_documento': 'ACU-REC', 'tipo_documental': 'Acuse de recibo', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 45, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-08', 'carpeta': '08 Quejas y respuestas formales', 'codigo_documento': 'RES-FOR', 'tipo_documental': 'Respuesta formal', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 46, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-08', 'carpeta': '08 Quejas y respuestas formales', 'codigo_documento': 'ACT-MED-COL', 'tipo_documental': 'Acta de mediación', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 47, 'nivel': 'Lugares poblados', 'codigo_carpeta': 'LP-08', 'carpeta': '08 Quejas y respuestas formales', 'codigo_documento': 'ACT-RES-COL', 'tipo_documental': 'Acta de resolución', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 48, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-01', 'carpeta': '01 Apertura e identificación del expediente', 'codigo_documento': 'CAR-APE', 'tipo_documental': 'Carátula de apertura del expediente', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 49, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-01', 'carpeta': '01 Apertura e identificación del expediente', 'codigo_documento': 'SOL-APE', 'tipo_documental': 'Solicitud de apertura del expediente', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 50, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-01', 'carpeta': '01 Apertura e identificación del expediente', 'codigo_documento': 'ACT-APER', 'tipo_documental': 'Acta de apertura del expediente', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 51, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-01', 'carpeta': '01 Apertura e identificación del expediente', 'codigo_documento': 'REL-INT', 'tipo_documental': 'Relación de integrantes del hogar', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 52, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-01', 'carpeta': '01 Apertura e identificación del expediente', 'codigo_documento': 'DES-REP', 'tipo_documental': 'Designación de representante del hogar', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 53, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-02', 'carpeta': '02 Documentos de tenencia, posesión u ocupación', 'codigo_documento': 'TIT-PRO', 'tipo_documental': 'Título de propiedad', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 54, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-02', 'carpeta': '02 Documentos de tenencia, posesión u ocupación', 'codigo_documento': 'ESC-PUB', 'tipo_documental': 'Escritura pública', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 55, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-02', 'carpeta': '02 Documentos de tenencia, posesión u ocupación', 'codigo_documento': 'CER-REG', 'tipo_documental': 'Certificación registral', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 56, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-02', 'carpeta': '02 Documentos de tenencia, posesión u ocupación', 'codigo_documento': 'CON-ARR', 'tipo_documental': 'Contrato de arrendamiento', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 57, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-02', 'carpeta': '02 Documentos de tenencia, posesión u ocupación', 'codigo_documento': 'CON-COM', 'tipo_documental': 'Contrato de compraventa', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 58, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-02', 'carpeta': '02 Documentos de tenencia, posesión u ocupación', 'codigo_documento': 'CES-DER', 'tipo_documental': 'Cesión de derechos', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 59, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-02', 'carpeta': '02 Documentos de tenencia, posesión u ocupación', 'codigo_documento': 'CON-POSE', 'tipo_documental': 'Constancia de posesión', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 60, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-02', 'carpeta': '02 Documentos de tenencia, posesión u ocupación', 'codigo_documento': 'CER-OCU', 'tipo_documental': 'Certificación de ocupación', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 61, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-02', 'carpeta': '02 Documentos de tenencia, posesión u ocupación', 'codigo_documento': 'DEC-POSE', 'tipo_documental': 'Declaración jurada de posesión u ocupación', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 62, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-02', 'carpeta': '02 Documentos de tenencia, posesión u ocupación', 'codigo_documento': 'AUT-USO', 'tipo_documental': 'Autorización de uso del inmueble', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 63, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-03', 'carpeta': '03 Documentos del predio o vivienda', 'codigo_documento': 'PLA-CAT', 'tipo_documental': 'Plano catastral', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 64, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-03', 'carpeta': '03 Documentos del predio o vivienda', 'codigo_documento': 'CER-CAT', 'tipo_documental': 'Certificación catastral', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 65, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-03', 'carpeta': '03 Documentos del predio o vivienda', 'codigo_documento': 'FOL-REA', 'tipo_documental': 'Folio real o ficha registral', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 66, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-03', 'carpeta': '03 Documentos del predio o vivienda', 'codigo_documento': 'DES-LIN', 'tipo_documental': 'Descripción de linderos', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 67, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-03', 'carpeta': '03 Documentos del predio o vivienda', 'codigo_documento': 'PER-CON', 'tipo_documental': 'Permiso de construcción', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 68, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-03', 'carpeta': '03 Documentos del predio o vivienda', 'codigo_documento': 'PER-OCU', 'tipo_documental': 'Permiso de ocupación', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 69, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-03', 'carpeta': '03 Documentos del predio o vivienda', 'codigo_documento': 'AVA-INM', 'tipo_documental': 'Avalúo del inmueble', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 70, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-03', 'carpeta': '03 Documentos del predio o vivienda', 'codigo_documento': 'ACT-INS', 'tipo_documental': 'Acta de inspección del inmueble', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 71, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-03', 'carpeta': '03 Documentos del predio o vivienda', 'codigo_documento': 'CER-GRA', 'tipo_documental': 'Certificación de gravámenes', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 72, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-03', 'carpeta': '03 Documentos del predio o vivienda', 'codigo_documento': 'PAZ-SAL', 'tipo_documental': 'Paz y salvo fiscal de la finca', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 73, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-04', 'carpeta': '04 Notificaciones y citaciones', 'codigo_documento': 'NOT-CIT', 'tipo_documental': 'Notificación de citación', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 74, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-04', 'carpeta': '04 Notificaciones y citaciones', 'codigo_documento': 'CIT-COM', 'tipo_documental': 'Citación a comparecer', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 75, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-04', 'carpeta': '04 Notificaciones y citaciones', 'codigo_documento': 'NOT-AFE', 'tipo_documental': 'Notificación de afectación', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 76, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-04', 'carpeta': '04 Notificaciones y citaciones', 'codigo_documento': 'NOT-NEG', 'tipo_documental': 'Notificación de inicio de negociación', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 77, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-04', 'carpeta': '04 Notificaciones y citaciones', 'codigo_documento': 'NOT-OFE', 'tipo_documental': 'Notificación de oferta', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 78, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-04', 'carpeta': '04 Notificaciones y citaciones', 'codigo_documento': 'NOT-PAG', 'tipo_documental': 'Notificación de pago', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 79, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-04', 'carpeta': '04 Notificaciones y citaciones', 'codigo_documento': 'NOT-ENT', 'tipo_documental': 'Notificación de entrega o reubicación', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 80, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-04', 'carpeta': '04 Notificaciones y citaciones', 'codigo_documento': 'CON-NOT', 'tipo_documental': 'Constancia de notificación', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 81, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-05', 'carpeta': '05 Actas y minutas con el hogar', 'codigo_documento': 'ACT-INF', 'tipo_documental': 'Acta informativa con el hogar', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 82, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-05', 'carpeta': '05 Actas y minutas con el hogar', 'codigo_documento': 'MIN-INF', 'tipo_documental': 'Minuta informativa con el hogar', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 83, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-05', 'carpeta': '05 Actas y minutas con el hogar', 'codigo_documento': 'ACT-NEG', 'tipo_documental': 'Acta de negociación', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 84, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-05', 'carpeta': '05 Actas y minutas con el hogar', 'codigo_documento': 'MIN-NEG', 'tipo_documental': 'Minuta de negociación', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 85, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-05', 'carpeta': '05 Actas y minutas con el hogar', 'codigo_documento': 'ACT-SEG', 'tipo_documental': 'Acta de seguimiento', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 86, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-05', 'carpeta': '05 Actas y minutas con el hogar', 'codigo_documento': 'MIN-SEG', 'tipo_documental': 'Minuta de seguimiento', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 87, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-05', 'carpeta': '05 Actas y minutas con el hogar', 'codigo_documento': 'REG-COMP', 'tipo_documental': 'Registro de compromisos con el hogar', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 88, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-05', 'carpeta': '05 Actas y minutas con el hogar', 'codigo_documento': 'LIS-ASIH', 'tipo_documental': 'Lista de asistentes del hogar', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 89, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-06', 'carpeta': '06 Acuerdos de negociación', 'codigo_documento': 'OFE-COM', 'tipo_documental': 'Oferta de compensación', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 90, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-06', 'carpeta': '06 Acuerdos de negociación', 'codigo_documento': 'CON-OFE', 'tipo_documental': 'Contraoferta', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 91, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-06', 'carpeta': '06 Acuerdos de negociación', 'codigo_documento': 'ACT-ACE', 'tipo_documental': 'Acta de aceptación de oferta', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 92, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-06', 'carpeta': '06 Acuerdos de negociación', 'codigo_documento': 'ACT-RECZ', 'tipo_documental': 'Acta de rechazo de oferta', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 93, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-06', 'carpeta': '06 Acuerdos de negociación', 'codigo_documento': 'ACU-NEG', 'tipo_documental': 'Acuerdo de negociación', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 94, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-06', 'carpeta': '06 Acuerdos de negociación', 'codigo_documento': 'MAT-COM', 'tipo_documental': 'Matriz de compensaciones acordadas', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 95, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-06', 'carpeta': '06 Acuerdos de negociación', 'codigo_documento': 'ADD-NEG', 'tipo_documental': 'Adenda al acuerdo de negociación', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 96, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-06', 'carpeta': '06 Acuerdos de negociación', 'codigo_documento': 'ACT-CIE-NEG', 'tipo_documental': 'Acta de cierre de negociación', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 97, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-07', 'carpeta': '07 Convenios o actas de compensación', 'codigo_documento': 'CON-COMP', 'tipo_documental': 'Convenio de compensación', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 98, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-07', 'carpeta': '07 Convenios o actas de compensación', 'codigo_documento': 'ACT-COMP', 'tipo_documental': 'Acta de compensación', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 99, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-07', 'carpeta': '07 Convenios o actas de compensación', 'codigo_documento': 'ACU-PAG', 'tipo_documental': 'Acuerdo de pago', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 100, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-07', 'carpeta': '07 Convenios o actas de compensación', 'codigo_documento': 'AUT-DEPO', 'tipo_documental': 'Autorización de depósito o transferencia', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 101, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-07', 'carpeta': '07 Convenios o actas de compensación', 'codigo_documento': 'REC-PAG', 'tipo_documental': 'Recibo de pago', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 102, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-07', 'carpeta': '07 Convenios o actas de compensación', 'codigo_documento': 'COM-TRAN', 'tipo_documental': 'Comprobante de transferencia', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 103, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-07', 'carpeta': '07 Convenios o actas de compensación', 'codigo_documento': 'FIN-COM', 'tipo_documental': 'Finiquito de compensación', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 104, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-07', 'carpeta': '07 Convenios o actas de compensación', 'codigo_documento': 'ADD-COMP', 'tipo_documental': 'Adenda al convenio de compensación', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 105, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-08', 'carpeta': '08 Salvataje', 'codigo_documento': 'SOL-SALV-HOG', 'tipo_documental': 'Solicitud de salvataje', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 106, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-08', 'carpeta': '08 Salvataje', 'codigo_documento': 'AUT-SALV-HOG', 'tipo_documental': 'Autorización de salvataje', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 107, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-08', 'carpeta': '08 Salvataje', 'codigo_documento': 'INV-SALV-HOG', 'tipo_documental': 'Inventario de bienes de salvataje', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 108, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-08', 'carpeta': '08 Salvataje', 'codigo_documento': 'ACT-ENT-SALV-HOG', 'tipo_documental': 'Acta de entrega de bienes de salvataje', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 109, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-08', 'carpeta': '08 Salvataje', 'codigo_documento': 'ACT-RET-SALV-HOG', 'tipo_documental': 'Acta de retiro de bienes de salvataje', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 110, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-08', 'carpeta': '08 Salvataje', 'codigo_documento': 'CON-REC-SALV-HOG', 'tipo_documental': 'Constancia de recepción de bienes de salvataje', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 111, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-09', 'carpeta': '09 Entrega, reubicación y recepción', 'codigo_documento': 'ACT-ENT-VIV', 'tipo_documental': 'Acta de entrega de vivienda', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 112, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-09', 'carpeta': '09 Entrega, reubicación y recepción', 'codigo_documento': 'ACT-REC-VIV', 'tipo_documental': 'Acta de recepción de vivienda', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 113, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-09', 'carpeta': '09 Entrega, reubicación y recepción', 'codigo_documento': 'ACT-ENT-BIE', 'tipo_documental': 'Acta de entrega de bienes', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 114, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-09', 'carpeta': '09 Entrega, reubicación y recepción', 'codigo_documento': 'ACT-ENT-LLA', 'tipo_documental': 'Acta de entrega de llaves', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 115, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-09', 'carpeta': '09 Entrega, reubicación y recepción', 'codigo_documento': 'ACT-REU', 'tipo_documental': 'Acta de reubicación', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 116, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-09', 'carpeta': '09 Entrega, reubicación y recepción', 'codigo_documento': 'CON-REC', 'tipo_documental': 'Constancia de recepción conforme', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 117, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-09', 'carpeta': '09 Entrega, reubicación y recepción', 'codigo_documento': 'INV-ENT', 'tipo_documental': 'Inventario de bienes entregados', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 118, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-09', 'carpeta': '09 Entrega, reubicación y recepción', 'codigo_documento': 'GAR-BIE', 'tipo_documental': 'Garantía del bien entregado', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 119, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-09', 'carpeta': '09 Entrega, reubicación y recepción', 'codigo_documento': 'ACT-OCU-NUE', 'tipo_documental': 'Acta de ocupación de nueva vivienda', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 120, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-10', 'carpeta': '10 Quejas, reclamos y respuestas', 'codigo_documento': 'QUE-HOG', 'tipo_documental': 'Queja del hogar', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 121, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-10', 'carpeta': '10 Quejas, reclamos y respuestas', 'codigo_documento': 'REC-HOG', 'tipo_documental': 'Reclamo del hogar', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 122, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-10', 'carpeta': '10 Quejas, reclamos y respuestas', 'codigo_documento': 'SOL-REV', 'tipo_documental': 'Solicitud de revisión', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 123, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-10', 'carpeta': '10 Quejas, reclamos y respuestas', 'codigo_documento': 'ACU-RECH', 'tipo_documental': 'Acuse de recibo de queja o reclamo', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 124, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-10', 'carpeta': '10 Quejas, reclamos y respuestas', 'codigo_documento': 'RES-QUE', 'tipo_documental': 'Respuesta a queja', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 125, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-10', 'carpeta': '10 Quejas, reclamos y respuestas', 'codigo_documento': 'RES-REC', 'tipo_documental': 'Respuesta a reclamo', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 126, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-10', 'carpeta': '10 Quejas, reclamos y respuestas', 'codigo_documento': 'ACT-MED', 'tipo_documental': 'Acta de mediación', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 127, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-10', 'carpeta': '10 Quejas, reclamos y respuestas', 'codigo_documento': 'ACT-RES-H', 'tipo_documental': 'Acta de resolución', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 128, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-10', 'carpeta': '10 Quejas, reclamos y respuestas', 'codigo_documento': 'NOT-DEC', 'tipo_documental': 'Notificación de decisión', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 129, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-11', 'carpeta': '11 Personas del hogar', 'codigo_documento': 'REL-PER', 'tipo_documental': 'Relación de personas del hogar', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 130, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-11', 'carpeta': '11 Personas del hogar', 'codigo_documento': 'VIN-PER', 'tipo_documental': 'Constancia de vinculación de persona al hogar', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 131, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-11', 'carpeta': '11 Personas del hogar', 'codigo_documento': 'ACT-INC', 'tipo_documental': 'Acta de incorporación de persona al expediente', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 132, 'nivel': 'Hogares', 'codigo_carpeta': 'HOG-11', 'carpeta': '11 Personas del hogar', 'codigo_documento': 'ACT-DESV', 'tipo_documental': 'Acta de desvinculación de persona del expediente', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 133, 'nivel': 'Personas', 'codigo_carpeta': 'PER-01', 'carpeta': '01 Identificación personal', 'codigo_documento': 'CED-ID', 'tipo_documental': 'Documento nacional de identidad', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 134, 'nivel': 'Personas', 'codigo_carpeta': 'PER-01', 'carpeta': '01 Identificación personal', 'codigo_documento': 'PAS-ID', 'tipo_documental': 'Pasaporte', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 135, 'nivel': 'Personas', 'codigo_carpeta': 'PER-01', 'carpeta': '01 Identificación personal', 'codigo_documento': 'CER-NAC', 'tipo_documental': 'Certificado de nacimiento', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 136, 'nivel': 'Personas', 'codigo_carpeta': 'PER-01', 'carpeta': '01 Identificación personal', 'codigo_documento': 'CAR-MIG', 'tipo_documental': 'Carné migratorio o permiso de residencia', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 137, 'nivel': 'Personas', 'codigo_carpeta': 'PER-01', 'carpeta': '01 Identificación personal', 'codigo_documento': 'CER-VID', 'tipo_documental': 'Fe de vida', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 138, 'nivel': 'Personas', 'codigo_carpeta': 'PER-02', 'carpeta': '02 Estado civil y parentesco', 'codigo_documento': 'CER-MAT', 'tipo_documental': 'Certificado de matrimonio', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 139, 'nivel': 'Personas', 'codigo_carpeta': 'PER-02', 'carpeta': '02 Estado civil y parentesco', 'codigo_documento': 'CER-UNI', 'tipo_documental': 'Certificación de unión de hecho', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 140, 'nivel': 'Personas', 'codigo_carpeta': 'PER-02', 'carpeta': '02 Estado civil y parentesco', 'codigo_documento': 'SEN-DIV', 'tipo_documental': 'Sentencia o certificado de divorcio', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 141, 'nivel': 'Personas', 'codigo_carpeta': 'PER-02', 'carpeta': '02 Estado civil y parentesco', 'codigo_documento': 'CER-DEF', 'tipo_documental': 'Certificado de defunción', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 142, 'nivel': 'Personas', 'codigo_carpeta': 'PER-02', 'carpeta': '02 Estado civil y parentesco', 'codigo_documento': 'RES-TUT', 'tipo_documental': 'Resolución de tutela, curatela o guarda', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 143, 'nivel': 'Personas', 'codigo_carpeta': 'PER-02', 'carpeta': '02 Estado civil y parentesco', 'codigo_documento': 'DEC-PAR', 'tipo_documental': 'Declaración jurada de parentesco', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 144, 'nivel': 'Personas', 'codigo_carpeta': 'PER-03', 'carpeta': '03 Poderes, representación o autorizaciones', 'codigo_documento': 'POD-GEN', 'tipo_documental': 'Poder general', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 145, 'nivel': 'Personas', 'codigo_carpeta': 'PER-03', 'carpeta': '03 Poderes, representación o autorizaciones', 'codigo_documento': 'POD-ESP', 'tipo_documental': 'Poder especial', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 146, 'nivel': 'Personas', 'codigo_carpeta': 'PER-03', 'carpeta': '03 Poderes, representación o autorizaciones', 'codigo_documento': 'AUT-REP', 'tipo_documental': 'Autorización de representación', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 147, 'nivel': 'Personas', 'codigo_carpeta': 'PER-03', 'carpeta': '03 Poderes, representación o autorizaciones', 'codigo_documento': 'DES-APO', 'tipo_documental': 'Designación de apoderado', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 148, 'nivel': 'Personas', 'codigo_carpeta': 'PER-03', 'carpeta': '03 Poderes, representación o autorizaciones', 'codigo_documento': 'REV-POD', 'tipo_documental': 'Revocatoria de poder', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 149, 'nivel': 'Personas', 'codigo_carpeta': 'PER-03', 'carpeta': '03 Poderes, representación o autorizaciones', 'codigo_documento': 'ACE-REP', 'tipo_documental': 'Aceptación de representación', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 150, 'nivel': 'Personas', 'codigo_carpeta': 'PER-04', 'carpeta': '04 Consentimientos firmados', 'codigo_documento': 'CON-DAT', 'tipo_documental': 'Consentimiento para tratamiento de datos personales', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 151, 'nivel': 'Personas', 'codigo_carpeta': 'PER-04', 'carpeta': '04 Consentimientos firmados', 'codigo_documento': 'CON-VER', 'tipo_documental': 'Consentimiento para verificación documental', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 152, 'nivel': 'Personas', 'codigo_carpeta': 'PER-04', 'carpeta': '04 Consentimientos firmados', 'codigo_documento': 'AUT-COM', 'tipo_documental': 'Autorización para comunicaciones y notificaciones', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 153, 'nivel': 'Personas', 'codigo_carpeta': 'PER-04', 'carpeta': '04 Consentimientos firmados', 'codigo_documento': 'AUT-IMG', 'tipo_documental': 'Autorización de uso de imagen', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 154, 'nivel': 'Personas', 'codigo_carpeta': 'PER-04', 'carpeta': '04 Consentimientos firmados', 'codigo_documento': 'CON-PAR', 'tipo_documental': 'Consentimiento de participación', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 155, 'nivel': 'Personas', 'codigo_carpeta': 'PER-04', 'carpeta': '04 Consentimientos firmados', 'codigo_documento': 'CON-FIR', 'tipo_documental': 'Consentimiento informado firmado', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 156, 'nivel': 'Personas', 'codigo_carpeta': 'PER-05', 'carpeta': '05 Declaraciones juradas', 'codigo_documento': 'DEC-DOM', 'tipo_documental': 'Declaración jurada de domicilio', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 157, 'nivel': 'Personas', 'codigo_carpeta': 'PER-05', 'carpeta': '05 Declaraciones juradas', 'codigo_documento': 'DEC-DEP', 'tipo_documental': 'Declaración jurada de dependencia económica', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 158, 'nivel': 'Personas', 'codigo_carpeta': 'PER-05', 'carpeta': '05 Declaraciones juradas', 'codigo_documento': 'DEC-TEN', 'tipo_documental': 'Declaración jurada de tenencia u ocupación', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 159, 'nivel': 'Personas', 'codigo_carpeta': 'PER-05', 'carpeta': '05 Declaraciones juradas', 'codigo_documento': 'DEC-NO-PRO', 'tipo_documental': 'Declaración jurada de no propiedad', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 160, 'nivel': 'Personas', 'codigo_carpeta': 'PER-05', 'carpeta': '05 Declaraciones juradas', 'codigo_documento': 'DEC-BEN', 'tipo_documental': 'Declaración jurada de beneficiario', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 161, 'nivel': 'Personas', 'codigo_carpeta': 'PER-05', 'carpeta': '05 Declaraciones juradas', 'codigo_documento': 'DEC-VER', 'tipo_documental': 'Declaración jurada de veracidad de información', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 162, 'nivel': 'Personas', 'codigo_carpeta': 'PER-06', 'carpeta': '06 Actas y minutas individuales', 'codigo_documento': 'ACT-ENT-P', 'tipo_documental': 'Acta de entrevista individual', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 163, 'nivel': 'Personas', 'codigo_carpeta': 'PER-06', 'carpeta': '06 Actas y minutas individuales', 'codigo_documento': 'MIN-ENT-P', 'tipo_documental': 'Minuta de entrevista individual', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 164, 'nivel': 'Personas', 'codigo_carpeta': 'PER-06', 'carpeta': '06 Actas y minutas individuales', 'codigo_documento': 'ACT-NOT-P', 'tipo_documental': 'Acta de notificación individual', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 165, 'nivel': 'Personas', 'codigo_carpeta': 'PER-06', 'carpeta': '06 Actas y minutas individuales', 'codigo_documento': 'ACT-NEG-P', 'tipo_documental': 'Acta de negociación individual', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 166, 'nivel': 'Personas', 'codigo_carpeta': 'PER-06', 'carpeta': '06 Actas y minutas individuales', 'codigo_documento': 'MIN-NEG-P', 'tipo_documental': 'Minuta de negociación individual', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 167, 'nivel': 'Personas', 'codigo_carpeta': 'PER-06', 'carpeta': '06 Actas y minutas individuales', 'codigo_documento': 'ACT-SEG-P', 'tipo_documental': 'Acta de seguimiento individual', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 168, 'nivel': 'Personas', 'codigo_carpeta': 'PER-06', 'carpeta': '06 Actas y minutas individuales', 'codigo_documento': 'REG-COM-P', 'tipo_documental': 'Registro de compromisos individuales', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 169, 'nivel': 'Personas', 'codigo_carpeta': 'PER-07', 'carpeta': '07 Acuerdos o compensaciones individuales', 'codigo_documento': 'ACU-COMP-P', 'tipo_documental': 'Acuerdo de compensación individual', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 170, 'nivel': 'Personas', 'codigo_carpeta': 'PER-07', 'carpeta': '07 Acuerdos o compensaciones individuales', 'codigo_documento': 'ACT-ACE-P', 'tipo_documental': 'Acta de aceptación individual', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 171, 'nivel': 'Personas', 'codigo_carpeta': 'PER-07', 'carpeta': '07 Acuerdos o compensaciones individuales', 'codigo_documento': 'REC-PAG-P', 'tipo_documental': 'Recibo de pago individual', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 172, 'nivel': 'Personas', 'codigo_carpeta': 'PER-07', 'carpeta': '07 Acuerdos o compensaciones individuales', 'codigo_documento': 'COM-TRA-P', 'tipo_documental': 'Comprobante de transferencia individual', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 173, 'nivel': 'Personas', 'codigo_carpeta': 'PER-07', 'carpeta': '07 Acuerdos o compensaciones individuales', 'codigo_documento': 'FIN-IND', 'tipo_documental': 'Finiquito individual', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 174, 'nivel': 'Personas', 'codigo_carpeta': 'PER-07', 'carpeta': '07 Acuerdos o compensaciones individuales', 'codigo_documento': 'ADD-IND', 'tipo_documental': 'Adenda a acuerdo individual', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 175, 'nivel': 'Personas', 'codigo_carpeta': 'PER-08', 'carpeta': '08 Quejas y respuestas', 'codigo_documento': 'QUE-IND', 'tipo_documental': 'Queja individual', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 176, 'nivel': 'Personas', 'codigo_carpeta': 'PER-08', 'carpeta': '08 Quejas y respuestas', 'codigo_documento': 'REC-IND', 'tipo_documental': 'Reclamo individual', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 177, 'nivel': 'Personas', 'codigo_carpeta': 'PER-08', 'carpeta': '08 Quejas y respuestas', 'codigo_documento': 'SOL-REV-P', 'tipo_documental': 'Solicitud individual de revisión', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 178, 'nivel': 'Personas', 'codigo_carpeta': 'PER-08', 'carpeta': '08 Quejas y respuestas', 'codigo_documento': 'ACU-REC-P', 'tipo_documental': 'Acuse de recibo individual', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 179, 'nivel': 'Personas', 'codigo_carpeta': 'PER-08', 'carpeta': '08 Quejas y respuestas', 'codigo_documento': 'RES-IND', 'tipo_documental': 'Respuesta individual', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 180, 'nivel': 'Personas', 'codigo_carpeta': 'PER-08', 'carpeta': '08 Quejas y respuestas', 'codigo_documento': 'ACT-MED-P', 'tipo_documental': 'Acta de mediación individual', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}, {'orden': 181, 'nivel': 'Personas', 'codigo_carpeta': 'PER-08', 'carpeta': '08 Quejas y respuestas', 'codigo_documento': 'NOT-RES-P', 'tipo_documental': 'Notificación de resolución individual', 'aplicabilidad_catalogo': 'Según aplique', 'activo': 'Sí'}]


def catalogo_df():
    """Devuelve el catálogo documental activo como DataFrame."""
    df = pd.DataFrame(CATALOGO_DOCUMENTAL)
    if df.empty:
        return df
    return df[df["activo"].str.lower().eq("sí")].copy()


# ============================================================
# 3. DATOS MAESTROS SIMULADOS DE OTROS MÓDULOS
# ============================================================

def crear_maestros_referencia():
    """Simula datos que en producción serán consultados desde otros módulos."""
    lugares = pd.DataFrame([
        {"id_lugar_poblado": "LP-REF-001", "nombre_lugar_poblado": "Nueva Esperanza", "zona": "Zona 1"},
        {"id_lugar_poblado": "LP-REF-002", "nombre_lugar_poblado": "El Progreso", "zona": "Zona 1"},
        {"id_lugar_poblado": "LP-REF-003", "nombre_lugar_poblado": "Santa Rosa", "zona": "Zona 2"},
        {"id_lugar_poblado": "LP-REF-004", "nombre_lugar_poblado": "Los Pinos", "zona": "Zona 3"},
        {"id_lugar_poblado": "LP-REF-005", "nombre_lugar_poblado": "Río Claro", "zona": "Zona 3"},
    ])

    nombres = [
        "María López", "Carlos Mendoza", "Rosa Martínez", "José Pérez",
        "Ana Rodríguez", "Luis García", "Elena Torres", "Miguel Castillo",
        "Carmen Díaz", "Roberto Herrera",
    ]
    hogares, personas = [], []
    for i, nombre in enumerate(nombres, start=1):
        id_hogar = f"HOG-{i:04d}"
        id_lugar = f"LP-REF-{((i - 1) % 5) + 1:03d}"
        hogares.append({
            "id_hogar": id_hogar,
            "nombre_referencia_hogar": nombre,
            "id_lugar_poblado": id_lugar,
            "codigo_hogar_campo": f"PAC-HOG-{i:03d}",
        })
        personas.append({
            "id_persona": f"PER-{i:04d}",
            "id_hogar": id_hogar,
            "nombres": nombre.split()[0],
            "apellidos": nombre.split()[-1],
            "documento_identidad": f"8-{100+i}-{200+i}",
        })
        if i <= 5:
            personas.append({
                "id_persona": f"PER-{i+10:04d}",
                "id_hogar": id_hogar,
                "nombres": f"Integrante {i}",
                "apellidos": nombre.split()[-1],
                "documento_identidad": f"8-{300+i}-{400+i}",
            })

    return {
        "lugares_poblados": lugares,
        "hogares": pd.DataFrame(hogares),
        "personas": pd.DataFrame(personas),
    }


# ============================================================
# 4. ESTRUCTURA DE DATOS OPERATIVOS
# ============================================================

COLUMNAS = {
    "expedientes": [
        "id_expediente", "nivel", "id_lugar_poblado", "id_hogar", "id_persona",
        "fecha_apertura", "responsable_expediente", "estado_expediente",
        "porcentaje_completitud", "observaciones",
        "fecha_creacion", "fecha_actualizacion", "usuario_actualizacion",
    ],
    "documentos": [
        "id_documento", "id_expediente", "nivel",
        "id_lugar_poblado", "id_hogar", "id_persona",
        "codigo_carpeta", "carpeta", "codigo_documento", "tipo_documental",
        "aplicabilidad", "justificacion_no_aplica",
        "nombre_archivo", "ruta_archivo", "fecha_documento", "fecha_carga",
        "estado_carga", "usuario_carga", "usuario_revisor_asignado",
        "estado_revision", "confirmado", "version",
        "observaciones_carga",
        "fecha_creacion", "fecha_actualizacion", "usuario_actualizacion",
    ],
    "revisiones": [
        "id_revision", "id_documento", "usuario_revisor",
        "fecha_revision", "resultado_revision", "observaciones_revision",
        "requiere_subsanacion", "fecha_subsanacion",
        "fecha_creacion", "fecha_actualizacion",
    ],
    "checklist_hogar": [
        "id_checklist", "id_expediente", "id_hogar",
        "codigo_carpeta", "carpeta", "codigo_documento", "tipo_documental",
        "aplicabilidad", "justificacion_no_aplica",
        "id_documento_asociado", "estado_carga", "estado_revision",
        "cumple", "fecha_actualizacion",
    ],
}


def df_vacio(nombre):
    return pd.DataFrame(columns=COLUMNAS[nombre])


def asegurar_columnas(data):
    salida = {}
    for nombre, columnas in COLUMNAS.items():
        df = data.get(nombre, df_vacio(nombre)).copy()
        for col in columnas:
            if col not in df.columns:
                df[col] = ""
        salida[nombre] = df[columnas]
    return salida


# ============================================================
# 5. MEMORIA Y PERSISTENCIA
# ============================================================

def serializar(valor):
    if isinstance(valor, (date, datetime)):
        return valor.isoformat()
    if isinstance(valor, float) and pd.isna(valor):
        return None
    return valor


def data_a_json(data):
    return {
        nombre: [
            {col: serializar(row[col]) for col in df.columns}
            for _, row in df.iterrows()
        ]
        for nombre, df in data.items()
    }


def json_a_data(payload):
    data = {}
    for nombre, columnas in COLUMNAS.items():
        registros = payload.get(nombre, [])
        data[nombre] = pd.DataFrame(registros, columns=columnas) if registros else df_vacio(nombre)
    return asegurar_columnas(data)


def guardar_memoria():
    with ARCHIVO_MEMORIA.open("w", encoding="utf-8") as f:
        json.dump(data_a_json(st.session_state.data_m06), f, ensure_ascii=False, indent=2)


def cargar_memoria():
    if ARCHIVO_MEMORIA.exists():
        try:
            with ARCHIVO_MEMORIA.open("r", encoding="utf-8") as f:
                return json_a_data(json.load(f))
        except Exception:
            pass
    return asegurar_columnas({})


def inicializar_estado():
    if "maestros_m06" not in st.session_state:
        st.session_state.maestros_m06 = crear_maestros_referencia()
    if "data_m06" not in st.session_state:
        st.session_state.data_m06 = cargar_memoria()
    else:
        st.session_state.data_m06 = asegurar_columnas(st.session_state.data_m06)
    st.session_state.setdefault("usuario_actual", USUARIOS[0])
    st.session_state.setdefault("pantalla_m06", "Hogares")


# ============================================================
# 6. UTILIDADES
# ============================================================

def ahora():
    return datetime.now().isoformat(timespec="seconds")


def normalizar_bool(valor):
    if isinstance(valor, bool):
        return valor
    return str(valor).strip().lower() in ["true", "1", "sí", "si", "yes"]


def generar_id(tabla, prefijo):
    df = st.session_state.data_m06[tabla]
    campo = COLUMNAS[tabla][0]
    maximo = 0
    if not df.empty:
        for valor in df[campo].astype(str):
            m = re.search(r"(\d+)$", valor)
            if m:
                maximo = max(maximo, int(m.group(1)))
    return f"{prefijo}-{maximo + 1:05d}"


def upsert(tabla, registro, llave):
    df = st.session_state.data_m06[tabla].copy()
    valor = str(registro.get(llave, "")).strip()
    if not valor:
        raise ValueError(f"Falta la llave {llave}")

    if df.empty or valor not in df[llave].astype(str).values:
        for col in COLUMNAS[tabla]:
            registro.setdefault(col, "")
        df = pd.concat([df, pd.DataFrame([registro])[COLUMNAS[tabla]]], ignore_index=True)
        accion = "creado"
    else:
        idx = df.index[df[llave].astype(str) == valor][0]
        for col, val in registro.items():
            if col in df.columns:
                df.at[idx, col] = val
        accion = "actualizado"

    st.session_state.data_m06[tabla] = df
    guardar_memoria()
    return accion


def maestro(nombre):
    return st.session_state.maestros_m06[nombre].copy()


def obtener_hogar(id_hogar):
    df = maestro("hogares")
    fila = df[df["id_hogar"].astype(str) == str(id_hogar)]
    return fila.iloc[0].to_dict() if not fila.empty else {}


def obtener_persona(id_persona):
    df = maestro("personas")
    fila = df[df["id_persona"].astype(str) == str(id_persona)]
    return fila.iloc[0].to_dict() if not fila.empty else {}


def obtener_lugar(id_lugar):
    df = maestro("lugares_poblados")
    fila = df[df["id_lugar_poblado"].astype(str) == str(id_lugar)]
    return fila.iloc[0].to_dict() if not fila.empty else {}


def expediente_existente(nivel, id_lugar="", id_hogar="", id_persona=""):
    df = st.session_state.data_m06["expedientes"]
    if df.empty:
        return {}
    filtro = df["nivel"].astype(str).eq(nivel)
    if nivel == "Lugares poblados":
        filtro &= df["id_lugar_poblado"].astype(str).eq(str(id_lugar))
    elif nivel == "Hogares":
        filtro &= df["id_hogar"].astype(str).eq(str(id_hogar))
    else:
        filtro &= df["id_persona"].astype(str).eq(str(id_persona))
    filas = df[filtro]
    return filas.iloc[0].to_dict() if not filas.empty else {}


def catalogo_nivel(nivel):
    df = catalogo_df()
    return df[df["nivel"].eq(nivel)].copy()


def opciones_carpetas(nivel):
    df = catalogo_nivel(nivel)
    return list(dict.fromkeys(
        (row["codigo_carpeta"], row["carpeta"])
        for _, row in df.iterrows()
    ))


def tipos_por_carpeta(nivel, codigo_carpeta):
    df = catalogo_nivel(nivel)
    return df[df["codigo_carpeta"].eq(codigo_carpeta)].copy()


# ============================================================
# 7. CHECKLIST Y PROGRESO DE HOGARES
# ============================================================

def crear_checklist_hogar(id_expediente, id_hogar):
    checklist = st.session_state.data_m06["checklist_hogar"].copy()
    existentes = set()
    if not checklist.empty:
        sub = checklist[checklist["id_expediente"].astype(str).eq(str(id_expediente))]
        existentes = set(sub["codigo_documento"].astype(str))

    nuevos = []
    contador = 1
    for _, item in catalogo_nivel("Hogares").iterrows():
        if item["codigo_documento"] in existentes:
            continue
        while True:
            candidato = f"CHK-{contador:05d}"
            if checklist.empty or candidato not in checklist["id_checklist"].astype(str).values:
                break
            contador += 1
        nuevos.append({
            "id_checklist": candidato,
            "id_expediente": id_expediente,
            "id_hogar": id_hogar,
            "codigo_carpeta": item["codigo_carpeta"],
            "carpeta": item["carpeta"],
            "codigo_documento": item["codigo_documento"],
            "tipo_documental": item["tipo_documental"],
            "aplicabilidad": "Pendiente de determinar",
            "justificacion_no_aplica": "",
            "id_documento_asociado": "",
            "estado_carga": "No cargado",
            "estado_revision": "Pendiente de asignación",
            "cumple": False,
            "fecha_actualizacion": ahora(),
        })
        contador += 1

    if nuevos:
        checklist = pd.concat([checklist, pd.DataFrame(nuevos)], ignore_index=True)
        st.session_state.data_m06["checklist_hogar"] = checklist[COLUMNAS["checklist_hogar"]]
        guardar_memoria()


def recalcular_progreso_hogar(id_expediente):
    chk = st.session_state.data_m06["checklist_hogar"]
    sub = chk[chk["id_expediente"].astype(str).eq(str(id_expediente))].copy()
    aplicables = sub[sub["aplicabilidad"].eq("Aplica")]
    total = len(aplicables)
    aprobados = int(aplicables["cumple"].apply(normalizar_bool).sum()) if total else 0
    porcentaje = round(aprobados / total * 100, 2) if total else 0.0

    exp = st.session_state.data_m06["expedientes"].copy()
    mask = exp["id_expediente"].astype(str).eq(str(id_expediente))
    if mask.any():
        exp.loc[mask, "porcentaje_completitud"] = porcentaje
        if total and porcentaje == 100:
            exp.loc[mask, "estado_expediente"] = "Completo"
        elif total:
            exp.loc[mask, "estado_expediente"] = "En gestión"
        exp.loc[mask, "fecha_actualizacion"] = ahora()
        st.session_state.data_m06["expedientes"] = exp
    guardar_memoria()


def sincronizar_checklist_documento(id_documento):
    docs = st.session_state.data_m06["documentos"]
    fila = docs[docs["id_documento"].astype(str).eq(str(id_documento))]
    if fila.empty:
        return
    doc = fila.iloc[0].to_dict()
    if doc.get("nivel") != "Hogares":
        return

    chk = st.session_state.data_m06["checklist_hogar"].copy()
    mask = (
        chk["id_expediente"].astype(str).eq(str(doc["id_expediente"]))
        & chk["codigo_documento"].astype(str).eq(str(doc["codigo_documento"]))
    )
    if not mask.any():
        return

    cumple = (
        doc.get("aplicabilidad") == "No aplica"
        or (
            doc.get("aplicabilidad") == "Aplica"
            and doc.get("estado_revision") == "Aprobado"
            and normalizar_bool(doc.get("confirmado"))
        )
    )
    chk.loc[mask, "aplicabilidad"] = doc.get("aplicabilidad", "Pendiente de determinar")
    chk.loc[mask, "justificacion_no_aplica"] = doc.get("justificacion_no_aplica", "")
    chk.loc[mask, "id_documento_asociado"] = doc.get("id_documento", "")
    chk.loc[mask, "estado_carga"] = doc.get("estado_carga", "")
    chk.loc[mask, "estado_revision"] = doc.get("estado_revision", "")
    chk.loc[mask, "cumple"] = bool(cumple)
    chk.loc[mask, "fecha_actualizacion"] = ahora()
    st.session_state.data_m06["checklist_hogar"] = chk
    recalcular_progreso_hogar(doc["id_expediente"])


def progreso_por_carpeta(id_expediente):
    chk = st.session_state.data_m06["checklist_hogar"]
    sub = chk[chk["id_expediente"].astype(str).eq(str(id_expediente))].copy()
    salida = []
    for (codigo, carpeta), grupo in sub.groupby(["codigo_carpeta", "carpeta"], sort=False):
        aplicables = grupo[grupo["aplicabilidad"].eq("Aplica")]
        total = len(aplicables)
        aprobados = int(aplicables["cumple"].apply(normalizar_bool).sum()) if total else 0
        salida.append({
            "Código": codigo,
            "Carpeta": carpeta,
            "Aplicables": total,
            "Aprobados": aprobados,
            "Progreso": round(aprobados / total * 100, 2) if total else 0.0,
            "Pendientes de determinar": int((grupo["aplicabilidad"] == "Pendiente de determinar").sum()),
            "No aplica": int((grupo["aplicabilidad"] == "No aplica").sum()),
        })
    return pd.DataFrame(salida)


# ============================================================
# 8. EXPEDIENTES, DOCUMENTOS Y REVISIONES
# ============================================================

def crear_o_actualizar_expediente(
    nivel, id_lugar="", id_hogar="", id_persona="",
    responsable="", estado="Abierto", observaciones=""
):
    existente = expediente_existente(nivel, id_lugar, id_hogar, id_persona)
    id_expediente = existente.get("id_expediente") or generar_id("expedientes", "EXP")
    registro = {
        "id_expediente": id_expediente,
        "nivel": nivel,
        "id_lugar_poblado": id_lugar,
        "id_hogar": id_hogar,
        "id_persona": id_persona,
        "fecha_apertura": existente.get("fecha_apertura") or date.today().isoformat(),
        "responsable_expediente": responsable,
        "estado_expediente": estado,
        "porcentaje_completitud": existente.get("porcentaje_completitud", 0.0),
        "observaciones": observaciones,
        "fecha_creacion": existente.get("fecha_creacion") or ahora(),
        "fecha_actualizacion": ahora(),
        "usuario_actualizacion": st.session_state.usuario_actual,
    }
    accion = upsert("expedientes", registro, "id_expediente")
    if nivel == "Hogares":
        crear_checklist_hogar(id_expediente, id_hogar)
        recalcular_progreso_hogar(id_expediente)
    return accion, id_expediente


def guardar_documento(registro):
    if registro["usuario_carga"] == registro["usuario_revisor_asignado"]:
        raise ValueError("El usuario que carga no puede ser responsable de la revisión.")

    if registro["aplicabilidad"] == "No aplica":
        if not registro["justificacion_no_aplica"].strip():
            raise ValueError("Debe justificar por qué el documento no aplica.")
        registro["estado_carga"] = "No cargado"
        registro["estado_revision"] = "Aprobado"
        registro["confirmado"] = True
        registro["nombre_archivo"] = ""
        registro["ruta_archivo"] = ""
    else:
        if registro["aplicabilidad"] == "Pendiente de determinar":
            raise ValueError("Defina si el documento aplica o no aplica.")
        if not registro["nombre_archivo"].strip():
            raise ValueError("Capture el nombre o referencia del archivo.")
        registro["estado_revision"] = "Pendiente de revisión"
        registro["confirmado"] = False

    accion = upsert("documentos", registro, "id_documento")
    sincronizar_checklist_documento(registro["id_documento"])
    return accion


def registrar_revision(id_documento, resultado, observaciones, requiere_subsanacion):
    docs = st.session_state.data_m06["documentos"].copy()
    mask = docs["id_documento"].astype(str).eq(str(id_documento))
    if not mask.any():
        raise ValueError("El documento no existe.")

    doc = docs[mask].iloc[0].to_dict()
    usuario = st.session_state.usuario_actual

    if doc.get("usuario_carga") == usuario:
        raise ValueError("La persona que cargó el documento no puede revisarlo.")
    if doc.get("usuario_revisor_asignado") != usuario:
        raise ValueError("El documento está asignado a otro responsable de revisión.")

    id_revision = generar_id("revisiones", "REV")
    revision = {
        "id_revision": id_revision,
        "id_documento": id_documento,
        "usuario_revisor": usuario,
        "fecha_revision": date.today().isoformat(),
        "resultado_revision": resultado,
        "observaciones_revision": observaciones,
        "requiere_subsanacion": bool(requiere_subsanacion),
        "fecha_subsanacion": "",
        "fecha_creacion": ahora(),
        "fecha_actualizacion": ahora(),
    }
    upsert("revisiones", revision, "id_revision")

    docs.loc[mask, "estado_revision"] = resultado
    docs.loc[mask, "confirmado"] = resultado == "Aprobado"
    docs.loc[mask, "fecha_actualizacion"] = ahora()
    docs.loc[mask, "usuario_actualizacion"] = usuario
    st.session_state.data_m06["documentos"] = docs
    guardar_memoria()
    sincronizar_checklist_documento(id_documento)


# ============================================================
# 9. INTERFAZ
# ============================================================

def aplicar_estilos():
    st.markdown(
        f"""
        <style>
            :root {{
                --sir-primary: {COLOR_PRIMARIO};
                --sir-accent: {COLOR_SECUNDARIO};
                --sir-coral: {COLOR_CORAL};
                --sir-border: rgba(128,128,128,.28);
            }}
            .main-title {{
                font-size: clamp(1.55rem, 2.7vw, 2.35rem);
                font-weight: 950;
                color: var(--sir-primary);
                letter-spacing: -.035em;
            }}
            .sub-title {{ opacity: .75; margin-bottom: 1rem; }}
            .sir-help {{
                border-left: 5px solid var(--sir-accent);
                padding: .8rem 1rem;
                border-radius: 14px;
                background: color-mix(in srgb, var(--secondary-background-color) 88%, var(--sir-accent) 8%);
                margin-bottom: 1rem;
            }}
            div[data-testid="stMetric"] {{
                border: 1px solid var(--sir-border);
                border-radius: 16px;
                padding: .8rem;
                background: var(--secondary-background-color);
            }}
            .stButton > button, .stDownloadButton > button {{
                border-radius: 12px !important;
                font-weight: 800 !important;
                min-height: 2.6rem;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def encabezado():
    st.markdown('<div class="main-title">M06 · Gestión Documental y Expedientes</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Expedientes por lugares poblados, hogares y personas · Catálogo legal PAC</div>',
        unsafe_allow_html=True,
    )


def mostrar_datos_referencia(nivel, id_lugar="", id_hogar="", id_persona=""):
    if nivel == "Lugares poblados":
        dato = obtener_lugar(id_lugar)
        c1, c2, c3 = st.columns(3)
        c1.info(f"**ID:** {dato.get('id_lugar_poblado', '')}")
        c2.info(f"**Lugar poblado:** {dato.get('nombre_lugar_poblado', '')}")
        c3.info(f"**Zona:** {dato.get('zona', '')}")
    elif nivel == "Hogares":
        dato = obtener_hogar(id_hogar)
        lugar = obtener_lugar(dato.get("id_lugar_poblado", ""))
        c1, c2, c3 = st.columns(3)
        c1.info(f"**ID hogar:** {dato.get('id_hogar', '')}")
        c2.info(f"**Referencia:** {dato.get('nombre_referencia_hogar', '')}")
        c3.info(f"**Lugar poblado:** {lugar.get('nombre_lugar_poblado', '')}")
    else:
        persona = obtener_persona(id_persona)
        c1, c2, c3 = st.columns(3)
        c1.info(f"**ID hogar:** {id_hogar}")
        c2.info(f"**ID persona:** {id_persona}")
        c3.info(f"**Persona:** {persona.get('nombres', '')} {persona.get('apellidos', '')}")


def selectores_contexto(nivel, key_prefix):
    id_lugar = id_hogar = id_persona = ""
    hogares = maestro("hogares")
    personas = maestro("personas")
    lugares = maestro("lugares_poblados")

    if nivel == "Lugares poblados":
        opciones = lugares["id_lugar_poblado"].astype(str).tolist()
        etiquetas = {
            r["id_lugar_poblado"]: f"{r['id_lugar_poblado']} · {r['nombre_lugar_poblado']}"
            for _, r in lugares.iterrows()
        }
        id_lugar = st.selectbox(
            "Lugar poblado",
            opciones,
            format_func=lambda x: etiquetas.get(x, x),
            key=f"{key_prefix}_lugar",
        )
    else:
        opciones_hogar = hogares["id_hogar"].astype(str).tolist()
        etiquetas_hogar = {
            r["id_hogar"]: f"{r['id_hogar']} · {r['nombre_referencia_hogar']}"
            for _, r in hogares.iterrows()
        }
        id_hogar = st.selectbox(
            "ID_HOGAR",
            opciones_hogar,
            format_func=lambda x: etiquetas_hogar.get(x, x),
            key=f"{key_prefix}_hogar",
        )
        hogar = obtener_hogar(id_hogar)
        id_lugar = hogar.get("id_lugar_poblado", "")

        if nivel == "Personas":
            personas_hogar = personas[personas["id_hogar"].astype(str).eq(str(id_hogar))]
            opciones_persona = personas_hogar["id_persona"].astype(str).tolist()
            etiquetas_persona = {
                r["id_persona"]: f"{r['id_persona']} · {r['nombres']} {r['apellidos']}"
                for _, r in personas_hogar.iterrows()
            }
            id_persona = st.selectbox(
                "ID_PERSONA",
                opciones_persona,
                format_func=lambda x: etiquetas_persona.get(x, x),
                key=f"{key_prefix}_persona",
            )

    mostrar_datos_referencia(nivel, id_lugar, id_hogar, id_persona)
    return id_lugar, id_hogar, id_persona


def formulario_expediente(nivel, id_lugar, id_hogar, id_persona):
    existente = expediente_existente(nivel, id_lugar, id_hogar, id_persona)
    with st.form(f"form_expediente_{nivel}_{id_lugar}_{id_hogar}_{id_persona}"):
        st.markdown("#### Expediente")
        if existente:
            st.success(f"Expediente existente: {existente['id_expediente']}")
        responsable = st.selectbox(
            "Responsable del expediente",
            USUARIOS,
            index=USUARIOS.index(existente.get("responsable_expediente"))
            if existente.get("responsable_expediente") in USUARIOS else 0,
        )
        estado = st.selectbox(
            "Estado del expediente",
            ESTADOS_EXPEDIENTE,
            index=ESTADOS_EXPEDIENTE.index(existente.get("estado_expediente"))
            if existente.get("estado_expediente") in ESTADOS_EXPEDIENTE else 0,
        )
        observaciones = st.text_area("Observaciones", value=str(existente.get("observaciones", "")))
        guardar = st.form_submit_button(
            "Actualizar expediente" if existente else "Crear expediente",
            type="primary",
            use_container_width=True,
        )

    if guardar:
        accion, id_exp = crear_o_actualizar_expediente(
            nivel, id_lugar, id_hogar, id_persona,
            responsable, estado, observaciones,
        )
        st.success(f"Expediente {accion}: {id_exp}")
        st.rerun()


def formulario_documento(nivel, expediente):
    if not expediente:
        st.warning("Primero crea o selecciona el expediente.")
        return

    id_exp = expediente["id_expediente"]
    docs = st.session_state.data_m06["documentos"]
    docs_exp = docs[docs["id_expediente"].astype(str).eq(str(id_exp))] if not docs.empty else docs

    carpetas = opciones_carpetas(nivel)
    codigos = [c for c, _ in carpetas]
    etiquetas = {c: f"{c} · {n}" for c, n in carpetas}

    codigo_carpeta = st.selectbox(
        "Carpeta",
        codigos,
        format_func=lambda x: etiquetas.get(x, x),
        key=f"carpeta_{nivel}_{id_exp}",
    )
    opciones_tipo = tipos_por_carpeta(nivel, codigo_carpeta)
    codigos_doc = opciones_tipo["codigo_documento"].astype(str).tolist()
    etiquetas_doc = {
        r["codigo_documento"]: f"{r['codigo_documento']} · {r['tipo_documental']}"
        for _, r in opciones_tipo.iterrows()
    }

    with st.form(f"form_documento_{nivel}_{id_exp}_{codigo_carpeta}"):
        st.markdown("#### Agregar documentación")
        codigo_documento = st.selectbox(
            "Tipo documental",
            codigos_doc,
            format_func=lambda x: etiquetas_doc.get(x, x),
        )
        item = opciones_tipo[opciones_tipo["codigo_documento"].eq(codigo_documento)].iloc[0]

        aplicabilidad = st.selectbox(
            "Aplicabilidad",
            ESTADOS_APLICABILIDAD,
            index=1 if nivel != "Hogares" else 0,
        )
        justificacion = st.text_area(
            "Justificación de no aplicabilidad",
            disabled=aplicabilidad != "No aplica",
        )
        c1, c2 = st.columns(2)
        nombre_archivo = c1.text_input(
            "Nombre o referencia del archivo",
            disabled=aplicabilidad == "No aplica",
        )
        ruta_archivo = c2.text_input(
            "Ruta o vínculo del archivo",
            disabled=aplicabilidad == "No aplica",
        )
        fecha_documento = st.date_input(
            "Fecha del documento",
            value=date.today(),
            disabled=aplicabilidad == "No aplica",
        )

        revisores = [u for u in USUARIOS if u != st.session_state.usuario_actual]
        revisor = st.selectbox("Responsable de revisión", revisores)
        observaciones = st.text_area("Observaciones de carga")
        guardar = st.form_submit_button(
            "Registrar documento",
            type="primary",
            use_container_width=True,
        )

    if guardar:
        existente = docs_exp[
            docs_exp["codigo_documento"].astype(str).eq(str(codigo_documento))
        ] if nivel == "Hogares" and not docs_exp.empty else pd.DataFrame()

        if not existente.empty:
            anterior = existente.iloc[0].to_dict()
            id_documento = anterior["id_documento"]
            version_anterior = pd.to_numeric(anterior.get("version", 1), errors="coerce")
            version = int(1 if pd.isna(version_anterior) else version_anterior) + 1
            estado_carga = "Reemplazado"
            fecha_creacion = anterior.get("fecha_creacion") or ahora()
        else:
            id_documento = generar_id("documentos", "DOC")
            version = 1
            estado_carga = "Cargado" if aplicabilidad != "No aplica" else "No cargado"
            fecha_creacion = ahora()

        registro = {
            "id_documento": id_documento,
            "id_expediente": id_exp,
            "nivel": nivel,
            "id_lugar_poblado": expediente.get("id_lugar_poblado", ""),
            "id_hogar": expediente.get("id_hogar", ""),
            "id_persona": expediente.get("id_persona", ""),
            "codigo_carpeta": codigo_carpeta,
            "carpeta": item["carpeta"],
            "codigo_documento": codigo_documento,
            "tipo_documental": item["tipo_documental"],
            "aplicabilidad": aplicabilidad,
            "justificacion_no_aplica": justificacion,
            "nombre_archivo": nombre_archivo,
            "ruta_archivo": ruta_archivo,
            "fecha_documento": fecha_documento.isoformat(),
            "fecha_carga": date.today().isoformat(),
            "estado_carga": estado_carga,
            "usuario_carga": st.session_state.usuario_actual,
            "usuario_revisor_asignado": revisor,
            "estado_revision": "Pendiente de revisión",
            "confirmado": False,
            "version": version,
            "observaciones_carga": observaciones,
            "fecha_creacion": fecha_creacion,
            "fecha_actualizacion": ahora(),
            "usuario_actualizacion": st.session_state.usuario_actual,
        }
        try:
            accion = guardar_documento(registro)
            st.success(f"Documento {accion} y enviado a revisión.")
            st.rerun()
        except ValueError as e:
            st.error(str(e))


def tabla_documentos(expediente):
    docs = st.session_state.data_m06["documentos"]
    sub = docs[docs["id_expediente"].astype(str).eq(str(expediente["id_expediente"]))].copy()
    st.markdown("#### Documentos registrados")
    if sub.empty:
        st.info("Todavía no hay documentos registrados.")
        return
    cols = [
        "id_documento", "codigo_carpeta", "tipo_documental", "aplicabilidad",
        "estado_carga", "estado_revision", "confirmado",
        "usuario_carga", "usuario_revisor_asignado", "version",
    ]
    st.dataframe(sub[cols], use_container_width=True, hide_index=True)


def vista_checklist_hogar(expediente):
    id_exp = expediente["id_expediente"]
    chk = st.session_state.data_m06["checklist_hogar"]
    sub = chk[chk["id_expediente"].astype(str).eq(str(id_exp))].copy()

    st.markdown("#### Progreso por carpeta")
    resumen = progreso_por_carpeta(id_exp)
    if not resumen.empty:
        st.dataframe(
            resumen,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Progreso": st.column_config.ProgressColumn(
                    "Progreso", min_value=0, max_value=100, format="%.1f%%"
                )
            },
        )

    st.markdown("#### Checklist documental del hogar")
    c1, c2 = st.columns(2)
    carpetas = ["Todas"] + sorted(sub["carpeta"].dropna().astype(str).unique().tolist())
    carpeta_sel = c1.selectbox("Filtrar por carpeta", carpetas)
    estado_sel = c2.selectbox("Filtrar por revisión", ["Todos"] + ESTADOS_REVISION)

    vista = sub.copy()
    if carpeta_sel != "Todas":
        vista = vista[vista["carpeta"].eq(carpeta_sel)]
    if estado_sel != "Todos":
        vista = vista[vista["estado_revision"].eq(estado_sel)]

    cols = [
        "codigo_carpeta", "carpeta", "codigo_documento", "tipo_documental",
        "aplicabilidad", "estado_carga", "estado_revision", "cumple",
    ]
    st.dataframe(vista[cols], use_container_width=True, hide_index=True)


def bandeja_revision():
    st.markdown("### Bandeja de revisión documental")
    usuario = st.session_state.usuario_actual
    docs = st.session_state.data_m06["documentos"]
    pendientes = docs[
        docs["usuario_revisor_asignado"].astype(str).eq(usuario)
        & docs["estado_revision"].isin(["Pendiente de revisión", "En revisión", "Observado"])
        & docs["aplicabilidad"].ne("No aplica")
    ].copy() if not docs.empty else docs

    if pendientes.empty:
        st.info("No tienes documentos pendientes de revisión.")
        return

    opciones = pendientes["id_documento"].astype(str).tolist()
    etiquetas = {
        r["id_documento"]: (
            f"{r['id_documento']} · {r['nivel']} · "
            f"{r['tipo_documental']} · Cargó: {r['usuario_carga']}"
        )
        for _, r in pendientes.iterrows()
    }
    id_doc = st.selectbox(
        "Documento asignado",
        opciones,
        format_func=lambda x: etiquetas.get(x, x),
    )
    doc = pendientes[pendientes["id_documento"].eq(id_doc)].iloc[0].to_dict()

    c1, c2, c3 = st.columns(3)
    c1.info(f"**Expediente:** {doc['id_expediente']}")
    c2.info(f"**Carpeta:** {doc['carpeta']}")
    c3.info(f"**Versión:** {doc['version']}")
    st.write(f"**Documento:** {doc['tipo_documental']}")
    st.write(f"**Archivo:** {doc['nombre_archivo'] or 'Sin referencia'}")
    st.write(f"**Ruta:** {doc['ruta_archivo'] or 'Sin ruta'}")
    st.write(f"**Observaciones de carga:** {doc['observaciones_carga'] or 'Sin observaciones'}")

    with st.form(f"revision_{id_doc}"):
        resultado = st.selectbox("Resultado de revisión", ["Aprobado", "Observado", "Rechazado"])
        observaciones = st.text_area("Observaciones del revisor")
        requiere = st.checkbox("Requiere subsanación")
        enviar = st.form_submit_button("Registrar revisión", type="primary", use_container_width=True)

    if enviar:
        if resultado != "Aprobado" and not observaciones.strip():
            st.error("Debe registrar observaciones cuando el documento no es aprobado.")
        else:
            try:
                registrar_revision(id_doc, resultado, observaciones, requiere)
                st.success("Revisión registrada y progreso actualizado.")
                st.rerun()
            except ValueError as e:
                st.error(str(e))


def metricas_generales():
    exp = st.session_state.data_m06["expedientes"]
    docs = st.session_state.data_m06["documentos"]
    hogares = exp[exp["nivel"].eq("Hogares")] if not exp.empty else exp
    aprobados = docs[docs["estado_revision"].eq("Aprobado")] if not docs.empty else docs
    pendientes = docs[docs["estado_revision"].eq("Pendiente de revisión")] if not docs.empty else docs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Expedientes", len(exp))
    c2.metric("Expedientes de hogar", len(hogares))
    c3.metric("Documentos confirmados", len(aprobados))
    c4.metric("Pendientes de revisión", len(pendientes))


def formulario_expediente_y_tabs(nivel):
    id_lugar, id_hogar, id_persona = selectores_contexto(nivel, f"ctx_{nivel}")
    formulario_expediente(nivel, id_lugar, id_hogar, id_persona)
    expediente = expediente_existente(nivel, id_lugar, id_hogar, id_persona)
    if not expediente:
        return

    st.markdown("---")
    etiquetas_tabs = ["Resumen", "Agregar documentación", "Documentos"]
    if nivel == "Hogares":
        etiquetas_tabs.append("Checklist y progreso")
    tabs = st.tabs(etiquetas_tabs)

    with tabs[0]:
        c1, c2, c3 = st.columns(3)
        c1.metric("ID expediente", expediente["id_expediente"])
        c2.metric("Estado", expediente["estado_expediente"])
        if nivel == "Hogares":
            pct = pd.to_numeric(expediente.get("porcentaje_completitud", 0), errors="coerce")
            pct = 0 if pd.isna(pct) else float(pct)
            c3.metric("Completitud", f"{pct:.1f}%")
        else:
            docs = st.session_state.data_m06["documentos"]
            total = len(docs[docs["id_expediente"].astype(str).eq(str(expediente["id_expediente"]))])
            c3.metric("Documentos", total)
    with tabs[1]:
        formulario_documento(nivel, expediente)
    with tabs[2]:
        tabla_documentos(expediente)
    if nivel == "Hogares":
        with tabs[3]:
            vista_checklist_hogar(expediente)


def pantalla_entidad(nivel):
    st.markdown(f"### {nivel}")
    if nivel == "Lugares poblados":
        mensaje = (
            "El catálogo organiza la documentación del lugar poblado. "
            "No genera checklist obligatorio ni porcentaje de completitud."
        )
    elif nivel == "Hogares":
        mensaje = (
            "Cada hogar tiene un expediente único. Las 11 carpetas del catálogo "
            "generan checklist y progreso por documentos aplicables aprobados."
        )
    else:
        mensaje = (
            "Primero se selecciona el hogar y después una persona perteneciente "
            "a ese hogar. La documentación personal no genera progreso independiente."
        )
    st.markdown(f'<div class="sir-help">{mensaje}</div>', unsafe_allow_html=True)
    formulario_expediente_y_tabs(nivel)


def mostrar_sidebar():
    st.sidebar.title("M06 · Controles")
    st.session_state.usuario_actual = st.sidebar.selectbox(
        "Usuario activo",
        USUARIOS,
        index=USUARIOS.index(st.session_state.usuario_actual),
        help="El usuario activo se usa para carga y revisión documental.",
    )
    st.sidebar.caption("El usuario que carga un documento no puede revisarlo.")

    pantalla = st.sidebar.radio(
        "Pantalla",
        ["Lugares poblados", "Hogares", "Personas", "Bandeja de revisión"],
        key="pantalla_m06",
    )

    st.sidebar.markdown("---")
    if st.sidebar.button("Guardar memoria local", use_container_width=True):
        guardar_memoria()
        st.sidebar.success("Memoria guardada.")
    if st.sidebar.button("Reiniciar datos operativos", use_container_width=True):
        st.session_state.data_m06 = asegurar_columnas({})
        guardar_memoria()
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "Hogares, personas y lugares poblados son referencias de otros módulos; "
        "no se crean dentro del M06."
    )
    return pantalla


# ============================================================
# 10. MAIN
# ============================================================

def main():
    aplicar_estilos()
    inicializar_estado()
    encabezado()
    pantalla = mostrar_sidebar()
    metricas_generales()
    st.markdown("---")

    if pantalla == "Bandeja de revisión":
        bandeja_revision()
    else:
        pantalla_entidad(pantalla)


if __name__ == "__main__":
    main()
