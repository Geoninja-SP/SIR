# ============================================================
# SIR ACP - M06 Gestión Documental y Expedientes
# Versión v7 - Índice documental, series y control de versiones
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
import uuid
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

ARCHIVO_MEMORIA = Path("memoria_m06_gestion_documental_v7.json")

# En producción debe ser False: quien carga no puede revisar el mismo documento.
# En beta/testing se habilita True para evaluar el flujo completo con un solo usuario.
MODO_BETA_AUTORREVISION = True
USUARIO_BETA = "usuario.beta"

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
        "id_documento", "id_serie_documental", "id_documento_padre", "tipo_registro", "es_version_vigente", "token_transaccion",
        "id_expediente", "nivel",
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
        "id_checklist", "id_expediente", "nivel",
        "id_lugar_poblado", "id_hogar", "id_persona",
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
        except Exception as error:
            st.session_state["error_carga_memoria_m06"] = str(error)
    return asegurar_columnas({})


def inicializar_estado():
    if "maestros_m06" not in st.session_state:
        st.session_state.maestros_m06 = crear_maestros_referencia()
    if "data_m06" not in st.session_state:
        st.session_state.data_m06 = cargar_memoria()
    else:
        st.session_state.data_m06 = asegurar_columnas(st.session_state.data_m06)
    migrar_documentos_legacy()
    st.session_state.setdefault("usuario_actual", USUARIO_BETA)
    st.session_state.setdefault("pantalla_m06", "Índice")


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
    """Genera identificadores no secuenciales para evitar colisiones entre sesiones."""
    return f"{prefijo}-{uuid.uuid4().hex[:12].upper()}"


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



def migrar_documentos_legacy():
    """Completa series y vigencia en registros creados por versiones anteriores."""
    docs = st.session_state.data_m06["documentos"].copy()
    if docs.empty:
        return
    cambio = False
    for idx, row in docs.iterrows():
        if not str(row.get("id_serie_documental", "")).strip():
            docs.at[idx, "id_serie_documental"] = f"SER-LEGACY-{str(row.get('id_documento','')).replace('DOC-','')}"
            docs.at[idx, "tipo_registro"] = "Documento nuevo"
            docs.at[idx, "id_documento_padre"] = ""
            docs.at[idx, "es_version_vigente"] = True
            cambio = True
    if cambio:
        st.session_state.data_m06["documentos"] = docs
        guardar_memoria()


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

def crear_checklist_expediente(expediente):
    """Crea el checklist del catálogo correspondiente al nivel del expediente."""
    checklist = st.session_state.data_m06["checklist_hogar"].copy()
    id_expediente = str(expediente.get("id_expediente", ""))
    nivel = str(expediente.get("nivel", ""))
    if not id_expediente or nivel not in ["Lugares poblados", "Hogares", "Personas"]:
        return

    existentes = set()
    if not checklist.empty:
        sub = checklist[checklist["id_expediente"].astype(str).eq(id_expediente)]
        existentes = set(sub["codigo_documento"].astype(str))

    nuevos = []
    numeros_existentes = []
    if not checklist.empty:
        for valor in checklist["id_checklist"].astype(str):
            match = re.search(r"(\d+)$", valor)
            if match:
                numeros_existentes.append(int(match.group(1)))
    siguiente_checklist = max(numeros_existentes, default=0) + 1

    for _, item in catalogo_nivel(nivel).iterrows():
        if str(item["codigo_documento"]) in existentes:
            continue
        id_checklist = f"CHK-{siguiente_checklist:05d}"
        siguiente_checklist += 1
        nuevos.append({
            "id_checklist": id_checklist,
            "id_expediente": id_expediente,
            "nivel": nivel,
            "id_lugar_poblado": expediente.get("id_lugar_poblado", ""),
            "id_hogar": expediente.get("id_hogar", ""),
            "id_persona": expediente.get("id_persona", ""),
            "codigo_carpeta": item["codigo_carpeta"],
            "carpeta": item["carpeta"],
            "codigo_documento": item["codigo_documento"],
            "tipo_documental": item["tipo_documental"],
            "aplicabilidad": "Requerido",
            "justificacion_no_aplica": "",
            "id_documento_asociado": "",
            "estado_carga": "No cargado",
            "estado_revision": "Pendiente de asignación",
            "cumple": False,
            "fecha_actualizacion": ahora(),
        })
        # Reservar el siguiente ID dentro del DataFrame temporal para evitar repetidos.
        checklist = pd.concat([checklist, pd.DataFrame([nuevos[-1]])], ignore_index=True)

    if nuevos:
        st.session_state.data_m06["checklist_hogar"] = checklist[COLUMNAS["checklist_hogar"]]
        guardar_memoria()


def recalcular_progreso_expediente(id_expediente):
    """Actualiza únicamente la completitud; no sobrescribe el estado administrativo."""
    chk = st.session_state.data_m06["checklist_hogar"]
    sub = chk[chk["id_expediente"].astype(str).eq(str(id_expediente))].copy()
    aplica = sub[~sub["aplicabilidad"].astype(str).eq("No aplica")]
    total = len(aplica)
    aprobados = int(aplica["cumple"].apply(normalizar_bool).sum()) if total else 0
    porcentaje = round(aprobados / total * 100, 2) if total else 0.0
    exp = st.session_state.data_m06["expedientes"].copy()
    mask = exp["id_expediente"].astype(str).eq(str(id_expediente))
    if mask.any():
        exp.loc[mask, "porcentaje_completitud"] = porcentaje
        exp.loc[mask, "fecha_actualizacion"] = ahora()
        st.session_state.data_m06["expedientes"] = exp
    guardar_memoria()


def sincronizar_checklist_documento(id_documento):
    """Cumple el tipo documental cuando al menos una serie tiene su versión vigente aprobada."""
    docs = st.session_state.data_m06["documentos"].copy()
    fila = docs[docs["id_documento"].astype(str).eq(str(id_documento))]
    if fila.empty:
        return
    doc = fila.iloc[0].to_dict()
    expediente = expediente_existente(doc.get("nivel", ""), doc.get("id_lugar_poblado", ""), doc.get("id_hogar", ""), doc.get("id_persona", ""))
    if not expediente:
        return
    crear_checklist_expediente(expediente)
    chk = st.session_state.data_m06["checklist_hogar"].copy()
    mask = chk["id_expediente"].astype(str).eq(str(doc["id_expediente"])) & chk["codigo_documento"].astype(str).eq(str(doc["codigo_documento"]))
    if not mask.any():
        return
    grupo = docs[docs["id_expediente"].astype(str).eq(str(doc["id_expediente"])) & docs["codigo_documento"].astype(str).eq(str(doc["codigo_documento"]))].copy()
    grupo["_version"] = pd.to_numeric(grupo["version"], errors="coerce").fillna(1)
    vigentes = grupo[grupo["es_version_vigente"].apply(normalizar_bool)].copy()
    if vigentes.empty:
        vigentes = grupo.sort_values(["id_serie_documental", "_version"], ascending=[True, False]).drop_duplicates("id_serie_documental")
    aprobados = vigentes[vigentes["estado_revision"].astype(str).eq("Aprobado") & vigentes["confirmado"].apply(normalizar_bool)]
    cumple = not aprobados.empty
    referencia = aprobados.sort_values("_version", ascending=False).iloc[0] if cumple else vigentes.sort_values("_version", ascending=False).iloc[0]
    chk.loc[mask, "id_documento_asociado"] = str(referencia.get("id_documento", ""))
    chk.loc[mask, "estado_carga"] = referencia.get("estado_carga", "")
    chk.loc[mask, "estado_revision"] = "Aprobado" if cumple else referencia.get("estado_revision", "")
    chk.loc[mask, "cumple"] = bool(cumple)
    chk.loc[mask, "fecha_actualizacion"] = ahora()
    st.session_state.data_m06["checklist_hogar"] = chk
    recalcular_progreso_expediente(doc["id_expediente"])


def progreso_por_carpeta(id_expediente):
    chk = st.session_state.data_m06["checklist_hogar"]
    sub = chk[chk["id_expediente"].astype(str).eq(str(id_expediente))].copy()
    salida = []
    for (codigo, carpeta), grupo in sub.groupby(["codigo_carpeta", "carpeta"], sort=False):
        total = len(grupo)
        aprobados = int(grupo["cumple"].apply(normalizar_bool).sum()) if total else 0
        salida.append({
            "Código": codigo,
            "Carpeta": carpeta,
            "Requeridos": total,
            "Aprobados": aprobados,
            "Pendientes": max(total - aprobados, 0),
            "Progreso": round(aprobados / total * 100, 2) if total else 0.0,
        })
    return pd.DataFrame(salida)



# ============================================================
# 8. EXPEDIENTES, DOCUMENTOS Y REVISIONES
# ============================================================

def crear_o_actualizar_expediente(
    nivel, id_lugar="", id_hogar="", id_persona="",
    responsable="", estado="Abierto", observaciones=""
):
    """Mantiene un expediente único por lugar poblado, hogar o persona."""
    if nivel == "Personas":
        exp_hogar = expediente_existente("Hogares", id_hogar=id_hogar)
        if not exp_hogar:
            raise ValueError("No se puede crear el expediente personal: primero debe existir el expediente del hogar.")
        persona = obtener_persona(id_persona)
        if not persona or str(persona.get("id_hogar")) != str(id_hogar):
            raise ValueError("La persona seleccionada no pertenece al hogar indicado.")

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
    expediente_actual = expediente_existente(nivel, id_lugar, id_hogar, id_persona)
    crear_checklist_expediente(expediente_actual)
    recalcular_progreso_expediente(id_expediente)
    return accion, id_expediente


def guardar_documento(registro):
    """Inserta una carga única y mantiene una sola versión vigente por serie."""
    if not MODO_BETA_AUTORREVISION and registro["usuario_carga"] == registro["usuario_revisor_asignado"]:
        raise ValueError("El usuario que carga no puede ser responsable de la revisión.")
    if not str(registro.get("nombre_archivo", "")).strip():
        raise ValueError("Capture el nombre o referencia del archivo.")
    if not str(registro.get("ruta_archivo", "")).strip():
        raise ValueError("Capture el vínculo o ruta del documento.")
    if registro.get("nivel") == "Personas" and not expediente_existente("Hogares", id_hogar=registro.get("id_hogar", "")):
        raise ValueError("No se puede cargar documentación personal sin expediente de hogar.")
    df = st.session_state.data_m06["documentos"].copy()
    token = str(registro.get("token_transaccion", ""))
    if token and not df.empty and df["token_transaccion"].astype(str).eq(token).any():
        raise ValueError("Esta acción de guardado ya fue procesada.")
    if str(registro.get("tipo_registro")) == "Nueva versión":
        serie = str(registro.get("id_serie_documental", ""))
        anteriores = df[df["id_serie_documental"].astype(str).eq(serie)]
        if anteriores.empty:
            raise ValueError("No se encontró el documento base para crear la nueva versión.")
        df.loc[df["id_serie_documental"].astype(str).eq(serie), "es_version_vigente"] = False
    registro["estado_revision"] = "Pendiente de revisión"
    registro["confirmado"] = False
    registro["es_version_vigente"] = True
    for col in COLUMNAS["documentos"]:
        registro.setdefault(col, "")
    if not df.empty and df["id_documento"].astype(str).eq(str(registro["id_documento"])).any():
        raise ValueError("El identificador del documento ya existe.")
    df = pd.concat([df, pd.DataFrame([registro])[COLUMNAS["documentos"]]], ignore_index=True)
    st.session_state.data_m06["documentos"] = df
    guardar_memoria()
    sincronizar_checklist_documento(registro["id_documento"])
    return "creado"


def registrar_revision(id_documento, resultado, observaciones, requiere_subsanacion):
    docs = st.session_state.data_m06["documentos"].copy()
    mask = docs["id_documento"].astype(str).eq(str(id_documento))
    if not mask.any():
        raise ValueError("El documento no existe.")

    doc = docs[mask].iloc[0].to_dict()
    usuario = st.session_state.usuario_actual

    if not MODO_BETA_AUTORREVISION:
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
        c2.info(f"**Código de campo:** {dato.get('codigo_hogar_campo', '')}")
        c3.info(f"**Lugar poblado:** {lugar.get('nombre_lugar_poblado', '')}")
    else:
        persona = obtener_persona(id_persona)
        c1, c2, c3 = st.columns(3)
        c1.info(f"**ID hogar:** {id_hogar}")
        c2.info(f"**ID persona:** {id_persona}")
        c3.info(f"**Persona:** {persona.get('nombres', '')} {persona.get('apellidos', '')}")


def selectores_contexto(nivel, key_prefix, solo_con_expediente=False):
    """Selecciona contexto; en vistas operativas solo muestra entidades con expediente."""
    id_lugar = id_hogar = id_persona = ""
    hogares = maestro("hogares")
    personas = maestro("personas")
    lugares = maestro("lugares_poblados")
    expedientes = st.session_state.data_m06["expedientes"]

    if nivel == "Lugares poblados":
        if solo_con_expediente:
            ids = expedientes[expedientes["nivel"].eq("Lugares poblados")]["id_lugar_poblado"].astype(str).unique().tolist()
            lugares = lugares[lugares["id_lugar_poblado"].astype(str).isin(ids)]
        if lugares.empty:
            st.warning("No hay lugares poblados con expediente creado para esta vista.")
            return "", "", ""
        opciones = lugares["id_lugar_poblado"].astype(str).tolist()
        etiquetas = {r["id_lugar_poblado"]: f"{r['id_lugar_poblado']} · {r['nombre_lugar_poblado']}" for _, r in lugares.iterrows()}
        id_lugar = st.selectbox("Lugar poblado", opciones, format_func=lambda x: etiquetas.get(x, x), key=f"{key_prefix}_lugar")
        mostrar_datos_referencia(nivel, id_lugar, id_hogar, id_persona)
        return id_lugar, id_hogar, id_persona

    if nivel == "Hogares":
        if solo_con_expediente:
            ids = expedientes[expedientes["nivel"].eq("Hogares")]["id_hogar"].astype(str).unique().tolist()
            hogares = hogares[hogares["id_hogar"].astype(str).isin(ids)]
        if hogares.empty:
            st.warning("No hay hogares con expediente creado para esta vista.")
            return "", "", ""
        opciones = hogares["id_hogar"].astype(str).tolist()
        id_hogar = st.selectbox("ID_HOGAR", opciones, key=f"{key_prefix}_hogar")
        id_lugar = obtener_hogar(id_hogar).get("id_lugar_poblado", "")
        mostrar_datos_referencia(nivel, id_lugar, id_hogar, id_persona)
        return id_lugar, id_hogar, id_persona

    # Personas: siempre dependen de hogares con expediente.
    ids_hogares_exp = expedientes[expedientes["nivel"].eq("Hogares")]["id_hogar"].astype(str).unique().tolist()
    hogares = hogares[hogares["id_hogar"].astype(str).isin(ids_hogares_exp)]
    if hogares.empty:
        st.warning("Primero debe existir al menos un expediente de hogar.")
        return "", "", ""
    opciones_hogar = hogares["id_hogar"].astype(str).tolist()
    id_hogar = st.selectbox("ID_HOGAR", opciones_hogar, key=f"{key_prefix}_hogar")
    id_lugar = obtener_hogar(id_hogar).get("id_lugar_poblado", "")

    personas_hogar = personas[personas["id_hogar"].astype(str).eq(str(id_hogar))]
    if solo_con_expediente:
        ids_persona = expedientes[
            expedientes["nivel"].eq("Personas")
            & expedientes["id_hogar"].astype(str).eq(str(id_hogar))
        ]["id_persona"].astype(str).unique().tolist()
        personas_hogar = personas_hogar[personas_hogar["id_persona"].astype(str).isin(ids_persona)]
    if personas_hogar.empty:
        mensaje = "No hay personas con expediente creado para esta vista." if solo_con_expediente else "No hay personas disponibles para el hogar seleccionado."
        st.warning(mensaje)
        return id_lugar, id_hogar, ""
    opciones_persona = personas_hogar["id_persona"].astype(str).tolist()
    etiquetas_persona = {r["id_persona"]: f"{r['id_persona']} · {r['nombres']} {r['apellidos']}" for _, r in personas_hogar.iterrows()}
    id_persona = st.selectbox("ID_PERSONA", opciones_persona, format_func=lambda x: etiquetas_persona.get(x, x), key=f"{key_prefix}_persona")
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
    docs = st.session_state.data_m06["documentos"].copy()
    carpetas = opciones_carpetas(nivel)
    codigos = [c for c, _ in carpetas]
    etiquetas = {c: f"{c} · {n}" for c, n in carpetas}
    codigo_carpeta = st.selectbox("Carpeta", codigos, format_func=lambda x: etiquetas.get(x, x), key=f"carpeta_{nivel}_{id_exp}")
    opciones_tipo = tipos_por_carpeta(nivel, codigo_carpeta)
    codigos_doc = opciones_tipo["codigo_documento"].astype(str).tolist()
    etiquetas_doc = {r["codigo_documento"]: f"{r['codigo_documento']} · {r['tipo_documental']}" for _, r in opciones_tipo.iterrows()}
    codigo_documento = st.selectbox("Tipo documental", codigos_doc, format_func=lambda x: etiquetas_doc.get(x, x), key=f"tipo_{nivel}_{id_exp}_{codigo_carpeta}")
    item = opciones_tipo[opciones_tipo["codigo_documento"].eq(codigo_documento)].iloc[0]
    existentes = docs[docs["id_expediente"].astype(str).eq(str(id_exp)) & docs["codigo_documento"].astype(str).eq(str(codigo_documento))].copy() if not docs.empty else docs
    modo = "Registrar documento nuevo"
    if not existentes.empty:
        modo = st.radio("¿Qué deseas registrar?", ["Registrar documento nuevo", "Agregar nueva versión"], horizontal=True, key=f"modo_{id_exp}_{codigo_documento}")
    serie_base = ""
    documento_padre = ""
    version = 1
    if modo == "Agregar nueva versión":
        series = existentes.sort_values(["id_serie_documental", "version"]).groupby("id_serie_documental", as_index=False).tail(1)
        opciones_series = series["id_serie_documental"].astype(str).tolist()
        labels = {r["id_serie_documental"]: f"{r['nombre_archivo']} · serie {r['id_serie_documental']} · versión vigente v{int(pd.to_numeric(r['version'], errors='coerce') or 1)}" for _, r in series.iterrows()}
        serie_base = st.selectbox("Documento al que agregarás la versión", opciones_series, format_func=lambda x: labels.get(x, x), key=f"serie_{id_exp}_{codigo_documento}")
        base = existentes[existentes["id_serie_documental"].astype(str).eq(str(serie_base))].copy()
        base["_v"] = pd.to_numeric(base["version"], errors="coerce").fillna(1)
        vigente = base.sort_values("_v", ascending=False).iloc[0]
        documento_padre = vigente["id_documento"]
        version = int(vigente["_v"]) + 1
        st.info(f"Se registrará la versión {version} de la serie seleccionada. La versión anterior permanecerá en el histórico.")
    token_key = f"token_carga_{id_exp}"
    st.session_state.setdefault(token_key, 0)
    token = int(st.session_state[token_key])
    with st.form(f"form_documento_{nivel}_{id_exp}_{codigo_documento}_{token}"):
        c1, c2 = st.columns(2)
        nombre_archivo = c1.text_input("Nombre o referencia del archivo")
        ruta_archivo = c2.text_input("Link o ruta del documento")
        fecha_documento = st.date_input("Fecha del documento", value=date.today())
        revisores = [st.session_state.usuario_actual] if MODO_BETA_AUTORREVISION else [u for u in USUARIOS if u != st.session_state.usuario_actual]
        revisor = st.selectbox("Responsable de revisión", revisores)
        observaciones = st.text_area("Observaciones de carga")
        guardar = st.form_submit_button("Registrar documento", type="primary", use_container_width=True)
    if guardar:
        id_documento = generar_id("documentos", "DOC")
        id_serie = serie_base or generar_id("documentos", "SER")
        registro = {
            "id_documento": id_documento, "id_serie_documental": id_serie,
            "id_documento_padre": documento_padre, "tipo_registro": "Nueva versión" if modo == "Agregar nueva versión" else "Documento nuevo",
            "es_version_vigente": True, "token_transaccion": f"{id_exp}|{codigo_documento}|{token}|{uuid.uuid4().hex}",
            "id_expediente": id_exp, "nivel": nivel,
            "id_lugar_poblado": expediente.get("id_lugar_poblado", ""), "id_hogar": expediente.get("id_hogar", ""), "id_persona": expediente.get("id_persona", ""),
            "codigo_carpeta": codigo_carpeta, "carpeta": item["carpeta"], "codigo_documento": codigo_documento, "tipo_documental": item["tipo_documental"],
            "aplicabilidad": "Aplica", "justificacion_no_aplica": "", "nombre_archivo": nombre_archivo, "ruta_archivo": ruta_archivo,
            "fecha_documento": fecha_documento.isoformat(), "fecha_carga": date.today().isoformat(), "estado_carga": "Cargado",
            "usuario_carga": st.session_state.usuario_actual, "usuario_revisor_asignado": revisor, "version": version,
            "observaciones_carga": observaciones, "fecha_creacion": ahora(), "fecha_actualizacion": ahora(), "usuario_actualizacion": st.session_state.usuario_actual,
        }
        try:
            guardar_documento(registro)
            st.session_state[token_key] = token + 1
            st.success(f"Registro guardado una sola vez: {registro['tipo_registro']} · versión {version}.")
            st.rerun()
        except Exception as error:
            st.error(str(error))


def mostrar_contexto_activo(nivel, expediente):
    lugar = obtener_lugar(expediente.get("id_lugar_poblado", ""))
    hogar = obtener_hogar(expediente.get("id_hogar", ""))
    persona = obtener_persona(expediente.get("id_persona", ""))
    st.markdown("#### Contexto activo")
    if nivel == "Lugares poblados":
        cols = st.columns(3)
        cols[0].info(f"**Expediente:**\n\n{expediente.get('id_expediente', '')}")
        cols[1].info(f"**Lugar poblado:**\n\n{lugar.get('nombre_lugar_poblado', '')}")
        cols[2].info(f"**ID lugar poblado:**\n\n{expediente.get('id_lugar_poblado', '')}")
    elif nivel == "Hogares":
        cols = st.columns(4)
        cols[0].info(f"**Expediente:**\n\n{expediente.get('id_expediente', '')}")
        cols[1].info(f"**ID hogar:**\n\n{expediente.get('id_hogar', '')}")
        cols[2].info(f"**Código de campo:**\n\n{hogar.get('codigo_hogar_campo', '')}")
        cols[3].info(f"**Lugar poblado:**\n\n{lugar.get('nombre_lugar_poblado', '')}")
    else:
        cols = st.columns(4)
        cols[0].info(f"**Expediente:**\n\n{expediente.get('id_expediente', '')}")
        cols[1].info(f"**ID hogar:**\n\n{expediente.get('id_hogar', '')}")
        cols[2].info(f"**ID persona:**\n\n{expediente.get('id_persona', '')}")
        cols[3].info(f"**Persona:**\n\n{persona.get('nombres', '')} {persona.get('apellidos', '')}")


def enlace_valido(valor):
    texto = str(valor or "").strip()
    return texto.startswith("http://") or texto.startswith("https://")


def tabla_documentos(expediente):
    docs = st.session_state.data_m06["documentos"]
    sub = docs[docs["id_expediente"].astype(str).eq(str(expediente["id_expediente"]))].copy()
    st.markdown("#### Documentos registrados")
    if sub.empty:
        st.info("Todavía no hay documentos registrados.")
        return
    sub["version"] = pd.to_numeric(sub["version"], errors="coerce").fillna(1).astype(int)
    solo_vigentes = st.toggle("Mostrar solo versiones vigentes", value=True, key=f"vigentes_{expediente['id_expediente']}")
    vista = sub[sub["es_version_vigente"].apply(normalizar_bool)].copy() if solo_vigentes else sub.copy()
    vista = vista.sort_values(["codigo_documento", "id_serie_documental", "version"], ascending=[True, True, False])
    cols = ["id_documento", "id_serie_documental", "tipo_registro", "tipo_documental", "nombre_archivo", "version", "es_version_vigente", "estado_revision", "fecha_documento", "ruta_archivo"]
    st.dataframe(vista[cols], use_container_width=True, hide_index=True, column_config={"ruta_archivo": st.column_config.LinkColumn("Link", display_text="Abrir documento")})
    st.caption(f"{vista['id_serie_documental'].nunique()} documentos únicos · {len(vista)} cargas visibles · {len(sub)} cargas históricas.")
    opciones = vista["id_documento"].astype(str).tolist()
    etiquetas = {r["id_documento"]: f"{r['tipo_documental']} · {r['id_serie_documental']} · v{r['version']}" for _, r in vista.iterrows()}
    id_doc = st.selectbox("Ver detalle", opciones, format_func=lambda x: etiquetas.get(x, x), key=f"detalle_doc_{expediente['id_expediente']}")
    doc = vista[vista["id_documento"].astype(str).eq(id_doc)].iloc[0].to_dict()
    st.write(f"**Serie documental:** {doc.get('id_serie_documental', '')} · **Tipo de registro:** {doc.get('tipo_registro', '')} · **Versión:** {doc.get('version', '')}")
    st.write(f"**Archivo:** {doc.get('nombre_archivo', '')}")
    ruta = str(doc.get("ruta_archivo") or "").strip()
    if enlace_valido(ruta): st.link_button("Abrir documento", ruta, use_container_width=True)
    elif ruta: st.code(ruta)


def vista_historico(expediente):
    """Muestra todas las cargas y revisiones, sin colapsar versiones."""
    docs = st.session_state.data_m06["documentos"]
    rev = st.session_state.data_m06["revisiones"]
    sub_docs = docs[docs["id_expediente"].astype(str).eq(str(expediente["id_expediente"]))].copy()
    st.markdown("#### Histórico documental")
    if sub_docs.empty:
        st.info("El expediente todavía no tiene movimientos documentales.")
        return
    sub_docs["version"] = pd.to_numeric(sub_docs["version"], errors="coerce").fillna(1).astype(int)
    movimientos = sub_docs[["id_documento", "id_serie_documental", "id_documento_padre", "tipo_registro", "es_version_vigente", "codigo_documento", "tipo_documental", "nombre_archivo", "version", "fecha_documento", "fecha_carga", "usuario_carga", "estado_revision", "fecha_actualizacion", "ruta_archivo"]].copy()
    movimientos = movimientos.sort_values(["tipo_documental", "version", "fecha_actualizacion"], ascending=[True, False, False])
    st.dataframe(movimientos, use_container_width=True, hide_index=True, column_config={"ruta_archivo": st.column_config.LinkColumn("Link", display_text="Abrir")})
    st.caption(f"Histórico completo: {len(movimientos)} cargas registradas.")

    ids = sub_docs["id_documento"].astype(str).tolist()
    sub_rev = rev[rev["id_documento"].astype(str).isin(ids)].copy() if not rev.empty else rev
    st.markdown("#### Histórico de revisiones")
    if sub_rev.empty:
        st.info("Todavía no se han registrado revisiones para estos documentos.")
    else:
        st.dataframe(sub_rev.sort_values("fecha_actualizacion", ascending=False), use_container_width=True, hide_index=True)


def vista_checklist_expediente(expediente):
    id_exp = expediente["id_expediente"]
    crear_checklist_expediente(expediente)
    docs = st.session_state.data_m06["documentos"]
    ids_docs = docs[docs["id_expediente"].astype(str).eq(str(id_exp))]["id_documento"].astype(str).tolist() if not docs.empty else []
    for id_doc in ids_docs:
        sincronizar_checklist_documento(id_doc)

    chk = st.session_state.data_m06["checklist_hogar"]
    sub = chk[chk["id_expediente"].astype(str).eq(str(id_exp))].copy()
    if sub.empty:
        st.error("No fue posible generar el checklist del expediente.")
        return

    st.markdown("#### Progreso por carpeta")
    resumen = progreso_por_carpeta(id_exp)
    st.dataframe(
        resumen,
        use_container_width=True,
        hide_index=True,
        column_config={"Progreso": st.column_config.ProgressColumn("Progreso", min_value=0, max_value=100, format="%.1f%%")},
    )

    st.markdown(f"#### Checklist documental · {expediente.get('nivel', '')}")
    c1, c2 = st.columns(2)
    carpetas = ["Todas"] + sorted(sub["carpeta"].dropna().astype(str).unique().tolist())
    carpeta_sel = c1.selectbox("Filtrar por carpeta", carpetas, key=f"chk_carpeta_{id_exp}")
    estado_sel = c2.selectbox("Filtrar por revisión", ["Todos"] + ESTADOS_REVISION, key=f"chk_estado_{id_exp}")
    vista = sub.copy()
    if carpeta_sel != "Todas":
        vista = vista[vista["carpeta"].eq(carpeta_sel)]
    if estado_sel != "Todos":
        vista = vista[vista["estado_revision"].eq(estado_sel)]
    cols = ["codigo_carpeta", "carpeta", "codigo_documento", "tipo_documental", "id_documento_asociado", "estado_carga", "estado_revision", "cumple"]
    st.dataframe(vista[cols], use_container_width=True, hide_index=True)



def construir_indice_documental():
    docs = st.session_state.data_m06["documentos"].copy()
    if docs.empty:
        return docs
    lugares = maestro("lugares_poblados")[["id_lugar_poblado", "nombre_lugar_poblado"]].copy()
    hogares = maestro("hogares")[["id_hogar", "nombre_referencia_hogar", "codigo_hogar_campo"]].copy()
    personas = maestro("personas")[["id_persona", "nombres", "apellidos"]].copy()
    personas["nombre_persona"] = (personas["nombres"].fillna("") + " " + personas["apellidos"].fillna("")).str.strip()
    docs = docs.merge(lugares, on="id_lugar_poblado", how="left").merge(hogares, on="id_hogar", how="left").merge(personas[["id_persona", "nombre_persona"]], on="id_persona", how="left")
    docs["version"] = pd.to_numeric(docs["version"], errors="coerce").fillna(1).astype(int)
    return docs


def pantalla_indice():
    st.markdown("### Índice documental")
    st.markdown('<div class="sir-help">Consulta consolidada de todos los documentos y versiones del módulo. Los filtros se combinan entre sí.</div>', unsafe_allow_html=True)
    df = construir_indice_documental()
    if df.empty:
        st.info("Todavía no hay documentos registrados.")
        return
    c1, c2, c3 = st.columns(3)
    texto = c1.text_input("Buscar en todos los campos", placeholder="ID, archivo, persona, hogar, lugar, carpeta...")
    nivel = c2.multiselect("Nivel", sorted(df["nivel"].dropna().astype(str).unique()))
    solo_vigentes = c3.toggle("Solo versiones vigentes", value=True)
    c1, c2, c3 = st.columns(3)
    lugares = c1.multiselect("Lugar poblado", sorted(df["nombre_lugar_poblado"].dropna().astype(str).unique()))
    hogares = c2.multiselect("Hogar", sorted(df["id_hogar"].dropna().astype(str).loc[lambda x: x.ne("")].unique()))
    personas = c3.multiselect("Persona", sorted(df["nombre_persona"].dropna().astype(str).loc[lambda x: x.ne("")].unique()))
    c1, c2, c3 = st.columns(3)
    carpetas = c1.multiselect("Carpeta", sorted(df["carpeta"].dropna().astype(str).unique()))
    tipos = c2.multiselect("Tipo documental", sorted(df["tipo_documental"].dropna().astype(str).unique()))
    estados = c3.multiselect("Estado de revisión", sorted(df["estado_revision"].dropna().astype(str).unique()))
    vista = df.copy()
    filtros = [("nivel", nivel), ("nombre_lugar_poblado", lugares), ("id_hogar", hogares), ("nombre_persona", personas), ("carpeta", carpetas), ("tipo_documental", tipos), ("estado_revision", estados)]
    for campo, valores in filtros:
        if valores: vista = vista[vista[campo].astype(str).isin(valores)]
    if solo_vigentes: vista = vista[vista["es_version_vigente"].apply(normalizar_bool)]
    if texto.strip():
        q = texto.strip().lower()
        columnas_busqueda = ["id_documento", "id_serie_documental", "id_expediente", "id_lugar_poblado", "nombre_lugar_poblado", "id_hogar", "nombre_referencia_hogar", "id_persona", "nombre_persona", "carpeta", "tipo_documental", "nombre_archivo", "observaciones_carga"]
        mascara = pd.Series(False, index=vista.index)
        for col in columnas_busqueda:
            if col in vista.columns: mascara |= vista[col].fillna("").astype(str).str.lower().str.contains(q, regex=False)
        vista = vista[mascara]
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Resultados", len(vista)); m2.metric("Documentos únicos", vista["id_serie_documental"].nunique()); m3.metric("Versiones vigentes", int(vista["es_version_vigente"].apply(normalizar_bool).sum())); m4.metric("Aprobados", int(vista["estado_revision"].astype(str).eq("Aprobado").sum()))
    cols = ["id_documento", "id_serie_documental", "version", "es_version_vigente", "nivel", "nombre_lugar_poblado", "id_hogar", "nombre_persona", "carpeta", "tipo_documental", "nombre_archivo", "fecha_documento", "estado_revision", "ruta_archivo"]
    st.dataframe(vista[cols].sort_values(["fecha_documento", "id_serie_documental", "version"], ascending=[False, True, False]), use_container_width=True, hide_index=True, column_config={"ruta_archivo": st.column_config.LinkColumn("Documento", display_text="Abrir")})
    csv = vista[cols].to_csv(index=False).encode("utf-8-sig")
    st.download_button("Descargar resultados en CSV", csv, "indice_documental_m06.csv", "text/csv", use_container_width=True)
    if not vista.empty:
        opciones = vista["id_documento"].astype(str).tolist()
        labels = {r["id_documento"]: f"{r['tipo_documental']} · {r['nombre_archivo']} · v{r['version']}" for _, r in vista.iterrows()}
        seleccionado = st.selectbox("Detalle del documento", opciones, format_func=lambda x: labels.get(x, x))
        doc = vista[vista["id_documento"].astype(str).eq(seleccionado)].iloc[0]
        st.write(f"**Expediente:** {doc['id_expediente']} · **Serie:** {doc['id_serie_documental']} · **Versión:** {doc['version']}")
        st.write(f"**Ubicación:** {doc.get('nombre_lugar_poblado','')} · **Hogar:** {doc.get('id_hogar','')} · **Persona:** {doc.get('nombre_persona','')}")
        ruta = str(doc.get("ruta_archivo") or "")
        if enlace_valido(ruta): st.link_button("Abrir documento seleccionado", ruta, use_container_width=True)


def bandeja_revision():
    st.markdown("### Bandeja de revisión documental")
    usuario = st.session_state.usuario_actual
    docs = st.session_state.data_m06["documentos"]
    pendientes = docs[
        docs["usuario_revisor_asignado"].astype(str).eq(usuario)
        & docs["estado_revision"].isin(["Pendiente de revisión", "En revisión", "Observado"])
    ].copy() if not docs.empty else docs
    if pendientes.empty:
        st.info("No tienes documentos pendientes de revisión.")
        return
    opciones = pendientes["id_documento"].astype(str).tolist()
    etiquetas = {r["id_documento"]: f"{r['id_documento']} · {r['tipo_documental']} · v{r['version']}" for _, r in pendientes.iterrows()}
    id_doc = st.selectbox("Documento asignado", opciones, format_func=lambda x: etiquetas.get(x, x))
    doc = pendientes[pendientes["id_documento"].eq(id_doc)].iloc[0].to_dict()
    st.write(f"**Expediente:** {doc['id_expediente']}")
    st.write(f"**Hogar:** {doc.get('id_hogar', '')} · **Persona:** {doc.get('id_persona', '')} · **Lugar poblado:** {doc.get('id_lugar_poblado', '')}")
    st.write(f"**Documento:** {doc['tipo_documental']} · **Versión:** {doc['version']}")
    ruta = str(doc.get('ruta_archivo') or '')
    if enlace_valido(ruta): st.link_button("Abrir documento", ruta)
    elif ruta: st.code(ruta)
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
                st.success("Revisión registrada y checklist actualizado.")
                st.rerun()
            except ValueError as e: st.error(str(e))


def metricas_generales():
    exp = st.session_state.data_m06["expedientes"]
    docs = st.session_state.data_m06["documentos"]
    hogares = exp[exp["nivel"].eq("Hogares")] if not exp.empty else exp
    aprobados = docs[docs["estado_revision"].eq("Aprobado")] if not docs.empty else docs
    pendientes = docs[docs["estado_revision"].eq("Pendiente de revisión")] if not docs.empty else docs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Expedientes", len(exp))
    c2.metric("Expedientes de hogar", len(hogares))
    c3.metric("Documentos únicos", docs["id_serie_documental"].nunique() if not docs.empty else 0)
    c4.metric("Pendientes de revisión", len(pendientes))


def formulario_expediente_y_tabs(nivel):
    opciones = ["Resumen", "Expediente", "Agregar documentos", "Documentos", "Histórico", "Checklist y progreso"]
    vista = st.radio("Vista de trabajo", opciones, horizontal=True, key=f"vista_interna_{nivel}")
    solo_con_expediente = vista != "Expediente"
    id_lugar, id_hogar, id_persona = selectores_contexto(
        nivel,
        f"ctx_{nivel}_{vista}",
        solo_con_expediente=solo_con_expediente,
    )
    if nivel == "Personas" and (not id_hogar or not id_persona):
        return
    if nivel == "Lugares poblados" and not id_lugar:
        return
    if nivel == "Hogares" and not id_hogar:
        return

    expediente = expediente_existente(nivel, id_lugar, id_hogar, id_persona)
    if vista == "Expediente":
        formulario_expediente(nivel, id_lugar, id_hogar, id_persona)
        return

    if not expediente:
        st.warning("La entidad seleccionada no tiene expediente; no puede gestionar documentación.")
        return
    mostrar_contexto_activo(nivel, expediente)

    if nivel == "Personas" and not expediente_existente("Hogares", id_hogar=id_hogar):
        st.error("El expediente del hogar no existe; se bloqueó la documentación personal.")
        return

    if vista == "Resumen":
        crear_checklist_expediente(expediente)
        recalcular_progreso_expediente(expediente["id_expediente"])
        exp_actual = expediente_existente(nivel, id_lugar, id_hogar, id_persona)
        docs = st.session_state.data_m06["documentos"]
        sub = docs[docs["id_expediente"].astype(str).eq(str(expediente["id_expediente"]))]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("ID expediente", expediente["id_expediente"])
        c2.metric("Estado", exp_actual.get("estado_expediente", expediente.get("estado_expediente", "")))
        c3.metric("Cargas documentales", len(sub))
        c4.metric("Aprobadas", int((sub["estado_revision"] == "Aprobado").sum()) if not sub.empty else 0)
        pct = pd.to_numeric(exp_actual.get("porcentaje_completitud", 0), errors="coerce")
        pct = 0 if pd.isna(pct) else float(pct)
        st.progress(min(max(pct / 100, 0), 1), text=f"Completitud documental: {pct:.1f}%")
    elif vista == "Agregar documentos":
        formulario_documento(nivel, expediente)
    elif vista == "Documentos":
        tabla_documentos(expediente)
    elif vista == "Histórico":
        vista_historico(expediente)
    elif vista == "Checklist y progreso":
        vista_checklist_expediente(expediente)



def pantalla_entidad(nivel):
    st.markdown(f"### {nivel}")
    if nivel == "Lugares poblados":
        mensaje = (
            "Cada lugar poblado con expediente dispone de checklist y progreso documental según su catálogo."
        )
    elif nivel == "Hogares":
        mensaje = (
            "Cada hogar tiene un expediente único. Las 11 carpetas del catálogo generan checklist y progreso por documentos aprobados."
        )
    else:
        mensaje = (
            "Primero se selecciona un hogar con expediente y después una persona del hogar. Cada expediente personal dispone de checklist y progreso."
        )
    st.markdown(f'<div class="sir-help">{mensaje}</div>', unsafe_allow_html=True)
    formulario_expediente_y_tabs(nivel)


def mostrar_sidebar():
    st.sidebar.title("M06 · Controles")
    usuarios_disponibles = [USUARIO_BETA] + USUARIOS if MODO_BETA_AUTORREVISION else USUARIOS
    st.session_state.usuario_actual = st.sidebar.selectbox("Usuario activo", usuarios_disponibles, index=0, key="selector_usuario_m06")
    st.sidebar.info(
        "Modo beta: el mismo usuario puede cargar y revisar para probar el flujo completo. "
        "En producción, MODO_BETA_AUTORREVISION debe configurarse en False."
    )

    pantalla = st.sidebar.radio(
        "Pantalla",
        ["Índice", "Lugares poblados", "Hogares", "Personas", "Bandeja de revisión"],
        key="pantalla_m06",
    )

    st.sidebar.markdown("---")
    if st.sidebar.button("Guardar memoria local", use_container_width=True):
        guardar_memoria()
        st.sidebar.success("Memoria guardada.")
    confirmar_reinicio = st.sidebar.checkbox("Confirmar reinicio total")
    if st.sidebar.button("Reiniciar datos operativos", use_container_width=True, disabled=not confirmar_reinicio):
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
    if st.session_state.get("error_carga_memoria_m06"):
        st.error(f"No fue posible leer la memoria local: {st.session_state['error_carga_memoria_m06']}")
    pantalla = mostrar_sidebar()
    metricas_generales()
    st.markdown("---")

    if pantalla == "Índice":
        pantalla_indice()
    elif pantalla == "Bandeja de revisión":
        bandeja_revision()
    else:
        pantalla_entidad(pantalla)


if __name__ == "__main__":
    main()
