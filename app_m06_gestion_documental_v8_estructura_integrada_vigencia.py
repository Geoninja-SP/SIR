
# ============================================================
# SIR ACP - M06 Gestión Documental y Expedientes
# Versión v8 - Estructura documental integrada, relaciones y vigencia
# ============================================================
# Base funcional:
# - Adaptación de M06 v7.
# - Catálogo maestro integrado sin duplicidad de tipos documentales.
# - Siete niveles: Persona, Hogar, Persona no residente,
#   Organización comunitaria o productiva, Lugar poblado,
#   Hogar sin censo y Proyecto.
# - Documento lógico único con múltiples relaciones a entidades.
# - Control de versiones, revisión, checklist, índice y vigencia.
# - Datos maestros simulados, preparados para migrar a base de datos.
# ============================================================

from __future__ import annotations

import hashlib
import json
import re
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

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
COLOR_AZUL_CLARO = "#E8F2F7"

ARCHIVO_MEMORIA = Path("memoria_m06_gestion_documental_v8.json")

MODO_BETA_AUTORREVISION = True
USUARIO_BETA = "usuario.beta"

USUARIOS = [
    "ana.documental",
    "carlos.legal",
    "diana.social",
    "elena.control",
    "francisco.acp",
]

NIVELES = [
    "Persona",
    "Hogar",
    "Persona no residente",
    "Organización comunitaria o productiva",
    "Lugar poblado",
    "Hogar sin censo",
    "Proyecto",
]

FASES = [
    "Transversal",
    "Identificación y seguimiento",
    "Pre-reasentamiento",
    "Durante el reasentamiento",
    "Post-reasentamiento",
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
ESTADOS_VIGENCIA = ["Vigente", "Próximo a vencer", "Vencido", "No aplica"]
CONFIDENCIALIDADES = ["Público institucional", "Uso interno", "Confidencial", "Sensitivo"]
DIAS_ALERTA_VENCIMIENTO = 30


# ============================================================
# 2. CATÁLOGO DOCUMENTAL MAESTRO
# ============================================================

CATALOGO_DOCUMENTAL = [
  {
    "orden": 1,
    "nivel": "Persona",
    "fase": "Transversal",
    "codigo_carpeta": "PER-TRA-01",
    "carpeta": "01 Identificación personal",
    "codigo_documento": "PER-TRA-01-D0001",
    "tipo_documental": "Carné migratorio o permiso de residencia",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 2,
    "nivel": "Persona",
    "fase": "Transversal",
    "codigo_carpeta": "PER-TRA-01",
    "carpeta": "01 Identificación personal",
    "codigo_documento": "PER-TRA-01-D0002",
    "tipo_documental": "Certificado de nacimiento",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Sensitivo",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 3,
    "nivel": "Persona",
    "fase": "Transversal",
    "codigo_carpeta": "PER-TRA-01",
    "carpeta": "01 Identificación personal",
    "codigo_documento": "PER-TRA-01-D0003",
    "tipo_documental": "Documento nacional de identidad",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 4,
    "nivel": "Persona",
    "fase": "Transversal",
    "codigo_carpeta": "PER-TRA-01",
    "carpeta": "01 Identificación personal",
    "codigo_documento": "PER-TRA-01-D0004",
    "tipo_documental": "Fe de vida",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 5,
    "nivel": "Persona",
    "fase": "Transversal",
    "codigo_carpeta": "PER-TRA-02",
    "carpeta": "Consentimientos",
    "codigo_documento": "PER-TRA-02-D0005",
    "tipo_documental": "Consentimiento de participación",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 6,
    "nivel": "Persona",
    "fase": "Transversal",
    "codigo_carpeta": "PER-TRA-02",
    "carpeta": "Consentimientos",
    "codigo_documento": "PER-TRA-02-D0006",
    "tipo_documental": "Consentimiento informado firmado",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 7,
    "nivel": "Persona",
    "fase": "Transversal",
    "codigo_carpeta": "PER-TRA-02",
    "carpeta": "Consentimientos",
    "codigo_documento": "PER-TRA-02-D0007",
    "tipo_documental": "Consentimiento para tratamiento de datos personales",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 8,
    "nivel": "Persona",
    "fase": "Transversal",
    "codigo_carpeta": "PER-TRA-02",
    "carpeta": "Consentimientos",
    "codigo_documento": "PER-TRA-02-D0008",
    "tipo_documental": "Consentimiento para verificación documental",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 9,
    "nivel": "Persona",
    "fase": "Transversal",
    "codigo_carpeta": "PER-TRA-03",
    "carpeta": "Declaraciones y actas personales",
    "codigo_documento": "PER-TRA-03-D0009",
    "tipo_documental": "Declaración jurada de beneficiario",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 10,
    "nivel": "Persona",
    "fase": "Transversal",
    "codigo_carpeta": "PER-TRA-03",
    "carpeta": "Declaraciones y actas personales",
    "codigo_documento": "PER-TRA-03-D0010",
    "tipo_documental": "Declaración jurada de dependencia económica",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 11,
    "nivel": "Persona",
    "fase": "Transversal",
    "codigo_carpeta": "PER-TRA-03",
    "carpeta": "Declaraciones y actas personales",
    "codigo_documento": "PER-TRA-03-D0011",
    "tipo_documental": "Declaración jurada de domicilio",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 12,
    "nivel": "Persona",
    "fase": "Transversal",
    "codigo_carpeta": "PER-TRA-03",
    "carpeta": "Declaraciones y actas personales",
    "codigo_documento": "PER-TRA-03-D0012",
    "tipo_documental": "Declaración jurada de no propiedad",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente, Predio",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 13,
    "nivel": "Persona",
    "fase": "Transversal",
    "codigo_carpeta": "PER-TRA-03",
    "carpeta": "Declaraciones y actas personales",
    "codigo_documento": "PER-TRA-03-D0013",
    "tipo_documental": "Declaración jurada de parentesco",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 14,
    "nivel": "Persona",
    "fase": "Transversal",
    "codigo_carpeta": "PER-TRA-03",
    "carpeta": "Declaraciones y actas personales",
    "codigo_documento": "PER-TRA-03-D0014",
    "tipo_documental": "Declaración jurada de posesión u ocupación",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente, Predio",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 15,
    "nivel": "Persona",
    "fase": "Transversal",
    "codigo_carpeta": "PER-TRA-03",
    "carpeta": "Declaraciones y actas personales",
    "codigo_documento": "PER-TRA-03-D0015",
    "tipo_documental": "Declaración jurada de tenencia u ocupación",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente, Predio",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 16,
    "nivel": "Persona",
    "fase": "Transversal",
    "codigo_carpeta": "PER-TRA-03",
    "carpeta": "Declaraciones y actas personales",
    "codigo_documento": "PER-TRA-03-D0016",
    "tipo_documental": "Declaración jurada de veracidad de información",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 17,
    "nivel": "Persona",
    "fase": "Transversal",
    "codigo_carpeta": "PER-TRA-04",
    "carpeta": "Estado civil y parentesco",
    "codigo_documento": "PER-TRA-04-D0017",
    "tipo_documental": "Certificado de unión libre",
    "aplicabilidad_catalogo": "Según composición del hogar, condición legal, tenencia y circunstancias particulares.",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): requisitos generales; censo, elegibilidad, derechos y compensación; desplazamiento físico y económico.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 1, 2 y 4 — alcance, línea base, elegibilidad, compensación y planificación."
  },
  {
    "orden": 18,
    "nivel": "Persona",
    "fase": "Transversal",
    "codigo_carpeta": "PER-TRA-05",
    "carpeta": "Identificación",
    "codigo_documento": "PER-TRA-05-D0018",
    "tipo_documental": "Cédula de identidad de integrante del hogar",
    "aplicabilidad_catalogo": "Según composición del hogar, condición legal, tenencia y circunstancias particulares.",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Sensitivo",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): requisitos generales; censo, elegibilidad, derechos y compensación; desplazamiento físico y económico.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 1, 2 y 4 — alcance, línea base, elegibilidad, compensación y planificación."
  },
  {
    "orden": 19,
    "nivel": "Persona",
    "fase": "Transversal",
    "codigo_carpeta": "PER-TRA-05",
    "carpeta": "Identificación",
    "codigo_documento": "PER-TRA-05-D0019",
    "tipo_documental": "Cédula de identidad personal",
    "aplicabilidad_catalogo": "Según identidad, tenencia, edad y condición legal de la persona.",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Sensitivo",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): requisitos generales; censo, elegibilidad, derechos y compensación; desplazamiento físico y económico.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 1, 2 y 4 — alcance, línea base, elegibilidad, compensación y planificación."
  },
  {
    "orden": 20,
    "nivel": "Persona",
    "fase": "Transversal",
    "codigo_carpeta": "PER-TRA-05",
    "carpeta": "Identificación",
    "codigo_documento": "PER-TRA-05-D0020",
    "tipo_documental": "Cédula de identidad personal del jefe de hogar",
    "aplicabilidad_catalogo": "Según composición del hogar, condición legal, tenencia y circunstancias particulares.",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Sensitivo",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): requisitos generales; censo, elegibilidad, derechos y compensación; desplazamiento físico y económico.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 1, 2 y 4 — alcance, línea base, elegibilidad, compensación y planificación."
  },
  {
    "orden": 21,
    "nivel": "Persona",
    "fase": "Transversal",
    "codigo_carpeta": "PER-TRA-05",
    "carpeta": "Identificación",
    "codigo_documento": "PER-TRA-05-D0021",
    "tipo_documental": "Cédula juvenil",
    "aplicabilidad_catalogo": "Según composición del hogar, condición legal, tenencia y circunstancias particulares.",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Sensitivo",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): requisitos generales; censo, elegibilidad, derechos y compensación; desplazamiento físico y económico.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 1, 2 y 4 — alcance, línea base, elegibilidad, compensación y planificación."
  },
  {
    "orden": 22,
    "nivel": "Persona",
    "fase": "Transversal",
    "codigo_carpeta": "PER-TRA-05",
    "carpeta": "Identificación",
    "codigo_documento": "PER-TRA-05-D0022",
    "tipo_documental": "Pasaporte",
    "aplicabilidad_catalogo": "Según composición del hogar, condición legal, tenencia y circunstancias particulares.",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Sensitivo",
    "activo": "Sí",
    "origen": "SIR + Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "ND5 (2012): requisitos generales; censo, elegibilidad, derechos y compensación; desplazamiento físico y económico.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 1, 2 y 4 — alcance, línea base, elegibilidad, compensación y planificación."
  },
  {
    "orden": 23,
    "nivel": "Persona",
    "fase": "Transversal",
    "codigo_carpeta": "PER-TRA-06",
    "carpeta": "Otros documentos personales",
    "codigo_documento": "PER-TRA-06-D0023",
    "tipo_documental": "Certificación de discapacidad",
    "aplicabilidad_catalogo": "Según composición del hogar, condición legal, tenencia y circunstancias particulares.",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Sensitivo",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): requisitos generales; censo, elegibilidad, derechos y compensación; desplazamiento físico y económico.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 1, 2 y 4 — alcance, línea base, elegibilidad, compensación y planificación."
  },
  {
    "orden": 24,
    "nivel": "Persona",
    "fase": "Transversal",
    "codigo_carpeta": "PER-TRA-06",
    "carpeta": "Otros documentos personales",
    "codigo_documento": "PER-TRA-06-D0024",
    "tipo_documental": "Certificación de jubilación",
    "aplicabilidad_catalogo": "Según composición del hogar, condición legal, tenencia y circunstancias particulares.",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Sensitivo",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): requisitos generales; censo, elegibilidad, derechos y compensación; desplazamiento físico y económico.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 1, 2 y 4 — alcance, línea base, elegibilidad, compensación y planificación."
  },
  {
    "orden": 25,
    "nivel": "Persona",
    "fase": "Transversal",
    "codigo_carpeta": "PER-TRA-06",
    "carpeta": "Otros documentos personales",
    "codigo_documento": "PER-TRA-06-D0025",
    "tipo_documental": "Certificación de pensión",
    "aplicabilidad_catalogo": "Según composición del hogar, condición legal, tenencia y circunstancias particulares.",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Sensitivo",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): requisitos generales; censo, elegibilidad, derechos y compensación; desplazamiento físico y económico.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 1, 2 y 4 — alcance, línea base, elegibilidad, compensación y planificación."
  },
  {
    "orden": 26,
    "nivel": "Persona",
    "fase": "Transversal",
    "codigo_carpeta": "PER-TRA-06",
    "carpeta": "Otros documentos personales",
    "codigo_documento": "PER-TRA-06-D0026",
    "tipo_documental": "Constancia de inscripción en centro escolar",
    "aplicabilidad_catalogo": "Según composición del hogar, condición legal, tenencia y circunstancias particulares.",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): requisitos generales; censo, elegibilidad, derechos y compensación; desplazamiento físico y económico.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 1, 2 y 4 — alcance, línea base, elegibilidad, compensación y planificación."
  },
  {
    "orden": 27,
    "nivel": "Persona",
    "fase": "Transversal",
    "codigo_carpeta": "PER-TRA-06",
    "carpeta": "Otros documentos personales",
    "codigo_documento": "PER-TRA-06-D0027",
    "tipo_documental": "Constancia de subsidio estatal",
    "aplicabilidad_catalogo": "Según composición del hogar, condición legal, tenencia y circunstancias particulares.",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Sensitivo",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): requisitos generales; censo, elegibilidad, derechos y compensación; desplazamiento físico y económico.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 1, 2 y 4 — alcance, línea base, elegibilidad, compensación y planificación."
  },
  {
    "orden": 28,
    "nivel": "Persona",
    "fase": "Transversal",
    "codigo_carpeta": "PER-TRA-06",
    "carpeta": "Otros documentos personales",
    "codigo_documento": "PER-TRA-06-D0028",
    "tipo_documental": "Informe o certificación geriátrica",
    "aplicabilidad_catalogo": "Según composición del hogar, condición legal, tenencia y circunstancias particulares.",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Sensitivo",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): requisitos generales; censo, elegibilidad, derechos y compensación; desplazamiento físico y económico.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 1, 2 y 4 — alcance, línea base, elegibilidad, compensación y planificación."
  },
  {
    "orden": 29,
    "nivel": "Persona",
    "fase": "Transversal",
    "codigo_carpeta": "PER-TRA-07",
    "carpeta": "Representación y autorizaciones",
    "codigo_documento": "PER-TRA-07-D0029",
    "tipo_documental": "Designación de apoderado",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 30,
    "nivel": "Persona",
    "fase": "Transversal",
    "codigo_carpeta": "PER-TRA-07",
    "carpeta": "Representación y autorizaciones",
    "codigo_documento": "PER-TRA-07-D0030",
    "tipo_documental": "Documento de representación legal",
    "aplicabilidad_catalogo": "Según composición del hogar, condición legal, tenencia y circunstancias particulares.",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): requisitos generales; censo, elegibilidad, derechos y compensación; desplazamiento físico y económico.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 1, 2 y 4 — alcance, línea base, elegibilidad, compensación y planificación."
  },
  {
    "orden": 31,
    "nivel": "Persona",
    "fase": "Transversal",
    "codigo_carpeta": "PER-TRA-07",
    "carpeta": "Representación y autorizaciones",
    "codigo_documento": "PER-TRA-07-D0031",
    "tipo_documental": "Poder especial",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 32,
    "nivel": "Persona",
    "fase": "Transversal",
    "codigo_carpeta": "PER-TRA-07",
    "carpeta": "Representación y autorizaciones",
    "codigo_documento": "PER-TRA-07-D0032",
    "tipo_documental": "Poder general",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 33,
    "nivel": "Persona",
    "fase": "Transversal",
    "codigo_carpeta": "PER-TRA-07",
    "carpeta": "Representación y autorizaciones",
    "codigo_documento": "PER-TRA-07-D0033",
    "tipo_documental": "Revocatoria de poder",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 34,
    "nivel": "Persona",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PER-PRE-01",
    "carpeta": "02 Estado civil y parentesco",
    "codigo_documento": "PER-PRE-01-D0034",
    "tipo_documental": "Certificación de unión de hecho",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 35,
    "nivel": "Persona",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PER-PRE-01",
    "carpeta": "02 Estado civil y parentesco",
    "codigo_documento": "PER-PRE-01-D0035",
    "tipo_documental": "Resolución de tutela, curatela o guarda",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 36,
    "nivel": "Persona",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PER-PRE-01",
    "carpeta": "02 Estado civil y parentesco",
    "codigo_documento": "PER-PRE-01-D0036",
    "tipo_documental": "Sentencia o certificado de divorcio",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 37,
    "nivel": "Persona",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PER-PRE-02",
    "carpeta": "03 Poderes, representación o autorizaciones",
    "codigo_documento": "PER-PRE-02-D0037",
    "tipo_documental": "Aceptación de representación",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 38,
    "nivel": "Persona",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PER-PRE-02",
    "carpeta": "03 Poderes, representación o autorizaciones",
    "codigo_documento": "PER-PRE-02-D0038",
    "tipo_documental": "Autorización de representación",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 39,
    "nivel": "Persona",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PER-PRE-03",
    "carpeta": "04 Consentimientos firmados",
    "codigo_documento": "PER-PRE-03-D0039",
    "tipo_documental": "Autorización de uso de imagen",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 40,
    "nivel": "Persona",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PER-PRE-03",
    "carpeta": "04 Consentimientos firmados",
    "codigo_documento": "PER-PRE-03-D0040",
    "tipo_documental": "Autorización para comunicaciones y notificaciones",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 41,
    "nivel": "Persona",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PER-PRE-04",
    "carpeta": "06 Actas y minutas individuales",
    "codigo_documento": "PER-PRE-04-D0041",
    "tipo_documental": "Acta de entrevista individual",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 42,
    "nivel": "Persona",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PER-PRE-04",
    "carpeta": "06 Actas y minutas individuales",
    "codigo_documento": "PER-PRE-04-D0042",
    "tipo_documental": "Acta de negociación individual",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 43,
    "nivel": "Persona",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PER-PRE-04",
    "carpeta": "06 Actas y minutas individuales",
    "codigo_documento": "PER-PRE-04-D0043",
    "tipo_documental": "Acta de notificación individual",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 44,
    "nivel": "Persona",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PER-PRE-04",
    "carpeta": "06 Actas y minutas individuales",
    "codigo_documento": "PER-PRE-04-D0044",
    "tipo_documental": "Acta de seguimiento individual",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 45,
    "nivel": "Persona",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PER-PRE-04",
    "carpeta": "06 Actas y minutas individuales",
    "codigo_documento": "PER-PRE-04-D0045",
    "tipo_documental": "Minuta de entrevista individual",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 46,
    "nivel": "Persona",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PER-PRE-04",
    "carpeta": "06 Actas y minutas individuales",
    "codigo_documento": "PER-PRE-04-D0046",
    "tipo_documental": "Minuta de negociación individual",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 47,
    "nivel": "Persona",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PER-PRE-04",
    "carpeta": "06 Actas y minutas individuales",
    "codigo_documento": "PER-PRE-04-D0047",
    "tipo_documental": "Registro de compromisos individuales",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 48,
    "nivel": "Persona",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PER-PRE-05",
    "carpeta": "07 Acuerdos o compensaciones individuales",
    "codigo_documento": "PER-PRE-05-D0048",
    "tipo_documental": "Acta de aceptación individual",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 49,
    "nivel": "Persona",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PER-PRE-05",
    "carpeta": "07 Acuerdos o compensaciones individuales",
    "codigo_documento": "PER-PRE-05-D0049",
    "tipo_documental": "Acuerdo de compensación individual",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 50,
    "nivel": "Persona",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PER-PRE-05",
    "carpeta": "07 Acuerdos o compensaciones individuales",
    "codigo_documento": "PER-PRE-05-D0050",
    "tipo_documental": "Adenda a acuerdo individual",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 51,
    "nivel": "Persona",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PER-PRE-05",
    "carpeta": "07 Acuerdos o compensaciones individuales",
    "codigo_documento": "PER-PRE-05-D0051",
    "tipo_documental": "Comprobante de transferencia individual",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 52,
    "nivel": "Persona",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PER-PRE-05",
    "carpeta": "07 Acuerdos o compensaciones individuales",
    "codigo_documento": "PER-PRE-05-D0052",
    "tipo_documental": "Finiquito individual",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 53,
    "nivel": "Persona",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PER-PRE-05",
    "carpeta": "07 Acuerdos o compensaciones individuales",
    "codigo_documento": "PER-PRE-05-D0053",
    "tipo_documental": "Recibo de pago individual",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 54,
    "nivel": "Persona",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PER-PRE-06",
    "carpeta": "08 Quejas y respuestas",
    "codigo_documento": "PER-PRE-06-D0054",
    "tipo_documental": "Acta de mediación individual",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 55,
    "nivel": "Persona",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PER-PRE-06",
    "carpeta": "08 Quejas y respuestas",
    "codigo_documento": "PER-PRE-06-D0055",
    "tipo_documental": "Acuse de recibo individual",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 56,
    "nivel": "Persona",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PER-PRE-06",
    "carpeta": "08 Quejas y respuestas",
    "codigo_documento": "PER-PRE-06-D0056",
    "tipo_documental": "Notificación de resolución individual",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 57,
    "nivel": "Persona",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PER-PRE-06",
    "carpeta": "08 Quejas y respuestas",
    "codigo_documento": "PER-PRE-06-D0057",
    "tipo_documental": "Queja individual",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 58,
    "nivel": "Persona",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PER-PRE-06",
    "carpeta": "08 Quejas y respuestas",
    "codigo_documento": "PER-PRE-06-D0058",
    "tipo_documental": "Reclamo individual",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 59,
    "nivel": "Persona",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PER-PRE-06",
    "carpeta": "08 Quejas y respuestas",
    "codigo_documento": "PER-PRE-06-D0059",
    "tipo_documental": "Respuesta individual",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 60,
    "nivel": "Persona",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PER-PRE-06",
    "carpeta": "08 Quejas y respuestas",
    "codigo_documento": "PER-PRE-06-D0060",
    "tipo_documental": "Solicitud individual de revisión",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Hogar, Persona no residente",
    "llaves_relacion": "id_persona",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 61,
    "nivel": "Hogar",
    "fase": "Transversal",
    "codigo_carpeta": "HOG-TRA-01",
    "carpeta": "01 Apertura e identificación del expediente",
    "codigo_documento": "HOG-TRA-01-D0061",
    "tipo_documental": "Acta de apertura del expediente",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 62,
    "nivel": "Hogar",
    "fase": "Transversal",
    "codigo_carpeta": "HOG-TRA-01",
    "carpeta": "01 Apertura e identificación del expediente",
    "codigo_documento": "HOG-TRA-01-D0062",
    "tipo_documental": "Carátula de apertura del expediente",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 63,
    "nivel": "Hogar",
    "fase": "Transversal",
    "codigo_carpeta": "HOG-TRA-01",
    "carpeta": "01 Apertura e identificación del expediente",
    "codigo_documento": "HOG-TRA-01-D0063",
    "tipo_documental": "Designación de representante del hogar",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 64,
    "nivel": "Hogar",
    "fase": "Transversal",
    "codigo_carpeta": "HOG-TRA-01",
    "carpeta": "01 Apertura e identificación del expediente",
    "codigo_documento": "HOG-TRA-01-D0064",
    "tipo_documental": "Relación de integrantes del hogar",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 65,
    "nivel": "Hogar",
    "fase": "Transversal",
    "codigo_carpeta": "HOG-TRA-01",
    "carpeta": "01 Apertura e identificación del expediente",
    "codigo_documento": "HOG-TRA-01-D0065",
    "tipo_documental": "Solicitud de apertura del expediente",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 66,
    "nivel": "Hogar",
    "fase": "Transversal",
    "codigo_carpeta": "HOG-TRA-02",
    "carpeta": "Índice del expediente",
    "codigo_documento": "HOG-TRA-02-D0066",
    "tipo_documental": "Registro de documentos sustituidos o actualizados",
    "aplicabilidad_catalogo": "Todos los expedientes de hogar.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): documentación del censo, elegibilidad, medidas, implementación y resultados de seguimiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 2, 6 y 7 — gestión de información, línea base, implementación y seguimiento."
  },
  {
    "orden": 67,
    "nivel": "Hogar",
    "fase": "Transversal",
    "codigo_carpeta": "HOG-TRA-02",
    "carpeta": "Índice del expediente",
    "codigo_documento": "HOG-TRA-02-D0067",
    "tipo_documental": "Registro de documentos vigentes",
    "aplicabilidad_catalogo": "Todos los expedientes de hogar.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): documentación del censo, elegibilidad, medidas, implementación y resultados de seguimiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 2, 6 y 7 — gestión de información, línea base, implementación y seguimiento."
  },
  {
    "orden": 68,
    "nivel": "Hogar",
    "fase": "Transversal",
    "codigo_carpeta": "HOG-TRA-02",
    "carpeta": "Índice del expediente",
    "codigo_documento": "HOG-TRA-02-D0068",
    "tipo_documental": "Registro de referencias cruzadas",
    "aplicabilidad_catalogo": "Todos los expedientes de hogar.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): documentación del censo, elegibilidad, medidas, implementación y resultados de seguimiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 2, 6 y 7 — gestión de información, línea base, implementación y seguimiento."
  },
  {
    "orden": 69,
    "nivel": "Hogar",
    "fase": "Transversal",
    "codigo_carpeta": "HOG-TRA-02",
    "carpeta": "Índice del expediente",
    "codigo_documento": "HOG-TRA-02-D0069",
    "tipo_documental": "Relación actualizada de documentos",
    "aplicabilidad_catalogo": "Todos los expedientes de hogar.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): documentación del censo, elegibilidad, medidas, implementación y resultados de seguimiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 2, 6 y 7 — gestión de información, línea base, implementación y seguimiento."
  },
  {
    "orden": 70,
    "nivel": "Hogar",
    "fase": "Transversal",
    "codigo_carpeta": "HOG-TRA-02",
    "carpeta": "Índice del expediente",
    "codigo_documento": "HOG-TRA-02-D0070",
    "tipo_documental": "Índice general del expediente",
    "aplicabilidad_catalogo": "Todos los expedientes de hogar.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): documentación del censo, elegibilidad, medidas, implementación y resultados de seguimiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 2, 6 y 7 — gestión de información, línea base, implementación y seguimiento."
  },
  {
    "orden": 71,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-01",
    "carpeta": "04 Notificaciones y citaciones",
    "codigo_documento": "HOG-PRE-01-D0071",
    "tipo_documental": "Citación a comparecer",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 72,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-01",
    "carpeta": "04 Notificaciones y citaciones",
    "codigo_documento": "HOG-PRE-01-D0072",
    "tipo_documental": "Constancia de notificación",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 73,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-01",
    "carpeta": "04 Notificaciones y citaciones",
    "codigo_documento": "HOG-PRE-01-D0073",
    "tipo_documental": "Notificación de afectación",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 74,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-01",
    "carpeta": "04 Notificaciones y citaciones",
    "codigo_documento": "HOG-PRE-01-D0074",
    "tipo_documental": "Notificación de citación",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 75,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-01",
    "carpeta": "04 Notificaciones y citaciones",
    "codigo_documento": "HOG-PRE-01-D0075",
    "tipo_documental": "Notificación de entrega o reubicación",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 76,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-01",
    "carpeta": "04 Notificaciones y citaciones",
    "codigo_documento": "HOG-PRE-01-D0076",
    "tipo_documental": "Notificación de inicio de negociación",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 77,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-01",
    "carpeta": "04 Notificaciones y citaciones",
    "codigo_documento": "HOG-PRE-01-D0077",
    "tipo_documental": "Notificación de oferta",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 78,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-01",
    "carpeta": "04 Notificaciones y citaciones",
    "codigo_documento": "HOG-PRE-01-D0078",
    "tipo_documental": "Notificación de pago",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 79,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-02",
    "carpeta": "05 Actas y minutas con el hogar",
    "codigo_documento": "HOG-PRE-02-D0079",
    "tipo_documental": "Acta de negociación",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 80,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-02",
    "carpeta": "05 Actas y minutas con el hogar",
    "codigo_documento": "HOG-PRE-02-D0080",
    "tipo_documental": "Acta de seguimiento",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 81,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-02",
    "carpeta": "05 Actas y minutas con el hogar",
    "codigo_documento": "HOG-PRE-02-D0081",
    "tipo_documental": "Acta informativa con el hogar",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 82,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-02",
    "carpeta": "05 Actas y minutas con el hogar",
    "codigo_documento": "HOG-PRE-02-D0082",
    "tipo_documental": "Lista de asistentes del hogar",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 83,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-02",
    "carpeta": "05 Actas y minutas con el hogar",
    "codigo_documento": "HOG-PRE-02-D0083",
    "tipo_documental": "Minuta de negociación",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 84,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-02",
    "carpeta": "05 Actas y minutas con el hogar",
    "codigo_documento": "HOG-PRE-02-D0084",
    "tipo_documental": "Minuta de seguimiento",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 85,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-02",
    "carpeta": "05 Actas y minutas con el hogar",
    "codigo_documento": "HOG-PRE-02-D0085",
    "tipo_documental": "Minuta informativa con el hogar",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 86,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-02",
    "carpeta": "05 Actas y minutas con el hogar",
    "codigo_documento": "HOG-PRE-02-D0086",
    "tipo_documental": "Registro de compromisos con el hogar",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 87,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-03",
    "carpeta": "06 Acuerdos de negociación",
    "codigo_documento": "HOG-PRE-03-D0087",
    "tipo_documental": "Acta de aceptación de oferta",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 88,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-03",
    "carpeta": "06 Acuerdos de negociación",
    "codigo_documento": "HOG-PRE-03-D0088",
    "tipo_documental": "Acta de cierre de negociación",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 89,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-03",
    "carpeta": "06 Acuerdos de negociación",
    "codigo_documento": "HOG-PRE-03-D0089",
    "tipo_documental": "Acta de rechazo de oferta",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 90,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-03",
    "carpeta": "06 Acuerdos de negociación",
    "codigo_documento": "HOG-PRE-03-D0090",
    "tipo_documental": "Acuerdo de negociación",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 91,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-03",
    "carpeta": "06 Acuerdos de negociación",
    "codigo_documento": "HOG-PRE-03-D0091",
    "tipo_documental": "Adenda al acuerdo de negociación",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 92,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-03",
    "carpeta": "06 Acuerdos de negociación",
    "codigo_documento": "HOG-PRE-03-D0092",
    "tipo_documental": "Contraoferta",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 93,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-03",
    "carpeta": "06 Acuerdos de negociación",
    "codigo_documento": "HOG-PRE-03-D0093",
    "tipo_documental": "Matriz de compensaciones acordadas",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 94,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-03",
    "carpeta": "06 Acuerdos de negociación",
    "codigo_documento": "HOG-PRE-03-D0094",
    "tipo_documental": "Oferta de compensación",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 95,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-04",
    "carpeta": "10 Quejas, reclamos y respuestas",
    "codigo_documento": "HOG-PRE-04-D0095",
    "tipo_documental": "Acuse de recibo de queja o reclamo",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 96,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-04",
    "carpeta": "10 Quejas, reclamos y respuestas",
    "codigo_documento": "HOG-PRE-04-D0096",
    "tipo_documental": "Notificación de decisión",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 97,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-04",
    "carpeta": "10 Quejas, reclamos y respuestas",
    "codigo_documento": "HOG-PRE-04-D0097",
    "tipo_documental": "Queja del hogar",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 98,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-04",
    "carpeta": "10 Quejas, reclamos y respuestas",
    "codigo_documento": "HOG-PRE-04-D0098",
    "tipo_documental": "Reclamo del hogar",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 99,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-04",
    "carpeta": "10 Quejas, reclamos y respuestas",
    "codigo_documento": "HOG-PRE-04-D0099",
    "tipo_documental": "Respuesta a queja",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 100,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-04",
    "carpeta": "10 Quejas, reclamos y respuestas",
    "codigo_documento": "HOG-PRE-04-D0100",
    "tipo_documental": "Respuesta a reclamo",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 101,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-04",
    "carpeta": "10 Quejas, reclamos y respuestas",
    "codigo_documento": "HOG-PRE-04-D0101",
    "tipo_documental": "Solicitud de revisión",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 102,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-05",
    "carpeta": "11 Personas del hogar",
    "codigo_documento": "HOG-PRE-05-D0102",
    "tipo_documental": "Acta de desvinculación de persona del expediente",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 103,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-05",
    "carpeta": "11 Personas del hogar",
    "codigo_documento": "HOG-PRE-05-D0103",
    "tipo_documental": "Acta de incorporación de persona al expediente",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 104,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-05",
    "carpeta": "11 Personas del hogar",
    "codigo_documento": "HOG-PRE-05-D0104",
    "tipo_documental": "Constancia de vinculación de persona al hogar",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 105,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-05",
    "carpeta": "11 Personas del hogar",
    "codigo_documento": "HOG-PRE-05-D0105",
    "tipo_documental": "Relación de personas del hogar",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 106,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-06",
    "carpeta": "Avalúos",
    "codigo_documento": "HOG-PRE-06-D0106",
    "tipo_documental": "Anexo técnico del avalúo",
    "aplicabilidad_catalogo": "Hogares con predios, viviendas, mejoras o activos sujetos a valoración.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "Anexo técnico de avalúos",
    "fuente_nd5": "ND5 (2012): compensación a costo de reposición y documentación de la valoración de tierras y activos.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 4 — valoración, costo de reposición, compensación y acuerdos."
  },
  {
    "orden": 107,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-06",
    "carpeta": "Avalúos",
    "codigo_documento": "HOG-PRE-06-D0107",
    "tipo_documental": "Autorización de ingreso para avalúo",
    "aplicabilidad_catalogo": "Hogares con predios, viviendas, mejoras o activos sujetos a valoración.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): compensación a costo de reposición y documentación de la valoración de tierras y activos.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 4 — valoración, costo de reposición, compensación y acuerdos."
  },
  {
    "orden": 108,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-06",
    "carpeta": "Avalúos",
    "codigo_documento": "HOG-PRE-06-D0108",
    "tipo_documental": "Documento de aceptación del valor del avalúo",
    "aplicabilidad_catalogo": "Hogares con predios, viviendas, mejoras o activos sujetos a valoración.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): compensación a costo de reposición y documentación de la valoración de tierras y activos.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 4 — valoración, costo de reposición, compensación y acuerdos."
  },
  {
    "orden": 109,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-06",
    "carpeta": "Avalúos",
    "codigo_documento": "HOG-PRE-06-D0109",
    "tipo_documental": "Documento de entrega del resultado del avalúo",
    "aplicabilidad_catalogo": "Hogares con predios, viviendas, mejoras o activos sujetos a valoración.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): compensación a costo de reposición y documentación de la valoración de tierras y activos.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 4 — valoración, costo de reposición, compensación y acuerdos."
  },
  {
    "orden": 110,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-06",
    "carpeta": "Avalúos",
    "codigo_documento": "HOG-PRE-06-D0110",
    "tipo_documental": "Informe de avalúo de activos",
    "aplicabilidad_catalogo": "Hogares con predios, viviendas, mejoras o activos sujetos a valoración.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): compensación a costo de reposición y documentación de la valoración de tierras y activos.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 4 — valoración, costo de reposición, compensación y acuerdos."
  },
  {
    "orden": 111,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-06",
    "carpeta": "Avalúos",
    "codigo_documento": "HOG-PRE-06-D0111",
    "tipo_documental": "Informe de avalúo de la vivienda",
    "aplicabilidad_catalogo": "Hogares con predios, viviendas, mejoras o activos sujetos a valoración.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): compensación a costo de reposición y documentación de la valoración de tierras y activos.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 4 — valoración, costo de reposición, compensación y acuerdos."
  },
  {
    "orden": 112,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-06",
    "carpeta": "Avalúos",
    "codigo_documento": "HOG-PRE-06-D0112",
    "tipo_documental": "Informe de avalúo de mejoras",
    "aplicabilidad_catalogo": "Hogares con predios, viviendas, mejoras o activos sujetos a valoración.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): compensación a costo de reposición y documentación de la valoración de tierras y activos.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 4 — valoración, costo de reposición, compensación y acuerdos."
  },
  {
    "orden": 113,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-06",
    "carpeta": "Avalúos",
    "codigo_documento": "HOG-PRE-06-D0113",
    "tipo_documental": "Informe de avalúo del predio",
    "aplicabilidad_catalogo": "Hogares con predios, viviendas, mejoras o activos sujetos a valoración.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): compensación a costo de reposición y documentación de la valoración de tierras y activos.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 4 — valoración, costo de reposición, compensación y acuerdos."
  },
  {
    "orden": 114,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-06",
    "carpeta": "Avalúos",
    "codigo_documento": "HOG-PRE-06-D0114",
    "tipo_documental": "Memoria de cálculo del avalúo",
    "aplicabilidad_catalogo": "Hogares con predios, viviendas, mejoras o activos sujetos a valoración.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): compensación a costo de reposición y documentación de la valoración de tierras y activos.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 4 — valoración, costo de reposición, compensación y acuerdos."
  },
  {
    "orden": 115,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-06",
    "carpeta": "Avalúos",
    "codigo_documento": "HOG-PRE-06-D0115",
    "tipo_documental": "Permiso de avalúo",
    "aplicabilidad_catalogo": "Hogares con predios, viviendas, mejoras o activos sujetos a valoración.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): compensación a costo de reposición y documentación de la valoración de tierras y activos.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 4 — valoración, costo de reposición, compensación y acuerdos."
  },
  {
    "orden": 116,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-06",
    "carpeta": "Avalúos",
    "codigo_documento": "HOG-PRE-06-D0116",
    "tipo_documental": "Registro fotográfico del avalúo",
    "aplicabilidad_catalogo": "Hogares con predios, viviendas, mejoras o activos sujetos a valoración.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): compensación a costo de reposición y documentación de la valoración de tierras y activos.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 4 — valoración, costo de reposición, compensación y acuerdos."
  },
  {
    "orden": 117,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-07",
    "carpeta": "Compensaciones",
    "codigo_documento": "HOG-PRE-07-D0117",
    "tipo_documental": "Acuerdo individual de compensación",
    "aplicabilidad_catalogo": "Hogares elegibles con medidas de compensación, asistencia o reasentamiento definidas.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): compensación, alternativas de reasentamiento, asistencia y formalización previa al desplazamiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 4 y 6 — compensación, vivienda de reposición, acuerdos e implementación."
  },
  {
    "orden": 118,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-07",
    "carpeta": "Compensaciones",
    "codigo_documento": "HOG-PRE-07-D0118",
    "tipo_documental": "Acuerdo individual para el reasentamiento",
    "aplicabilidad_catalogo": "Hogares elegibles con medidas de compensación, asistencia o reasentamiento definidas.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): compensación, alternativas de reasentamiento, asistencia y formalización previa al desplazamiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 4 y 6 — compensación, vivienda de reposición, acuerdos e implementación."
  },
  {
    "orden": 119,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-07",
    "carpeta": "Compensaciones",
    "codigo_documento": "HOG-PRE-07-D0119",
    "tipo_documental": "Anexo del acuerdo o contrato",
    "aplicabilidad_catalogo": "Hogares elegibles con medidas de compensación, asistencia o reasentamiento definidas.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "Anexo de acuerdo o contrato",
    "fuente_nd5": "ND5 (2012): compensación, alternativas de reasentamiento, asistencia y formalización previa al desplazamiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 4 y 6 — compensación, vivienda de reposición, acuerdos e implementación."
  },
  {
    "orden": 120,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-07",
    "carpeta": "Compensaciones",
    "codigo_documento": "HOG-PRE-07-D0120",
    "tipo_documental": "Contrato de reasentamiento",
    "aplicabilidad_catalogo": "Hogares elegibles con medidas de compensación, asistencia o reasentamiento definidas.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): compensación, alternativas de reasentamiento, asistencia y formalización previa al desplazamiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 4 y 6 — compensación, vivienda de reposición, acuerdos e implementación."
  },
  {
    "orden": 121,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-07",
    "carpeta": "Compensaciones",
    "codigo_documento": "HOG-PRE-07-D0121",
    "tipo_documental": "Documento de aceptación de medidas",
    "aplicabilidad_catalogo": "Hogares elegibles con medidas de compensación, asistencia o reasentamiento definidas.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): compensación, alternativas de reasentamiento, asistencia y formalización previa al desplazamiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 4 y 6 — compensación, vivienda de reposición, acuerdos e implementación."
  },
  {
    "orden": 122,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-07",
    "carpeta": "Compensaciones",
    "codigo_documento": "HOG-PRE-07-D0122",
    "tipo_documental": "Documento de definición de asistencias",
    "aplicabilidad_catalogo": "Hogares elegibles con medidas de compensación, asistencia o reasentamiento definidas.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): compensación, alternativas de reasentamiento, asistencia y formalización previa al desplazamiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 4 y 6 — compensación, vivienda de reposición, acuerdos e implementación."
  },
  {
    "orden": 123,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-07",
    "carpeta": "Compensaciones",
    "codigo_documento": "HOG-PRE-07-D0123",
    "tipo_documental": "Documento de definición de compensaciones",
    "aplicabilidad_catalogo": "Hogares elegibles con medidas de compensación, asistencia o reasentamiento definidas.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): compensación, alternativas de reasentamiento, asistencia y formalización previa al desplazamiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 4 y 6 — compensación, vivienda de reposición, acuerdos e implementación."
  },
  {
    "orden": 124,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-07",
    "carpeta": "Compensaciones",
    "codigo_documento": "HOG-PRE-07-D0124",
    "tipo_documental": "Marco de Compensación firmado",
    "aplicabilidad_catalogo": "Hogares elegibles con medidas de compensación, asistencia o reasentamiento definidas.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): compensación, alternativas de reasentamiento, asistencia y formalización previa al desplazamiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 4 y 6 — compensación, vivienda de reposición, acuerdos e implementación."
  },
  {
    "orden": 125,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-08",
    "carpeta": "Compensaciones y acuerdos",
    "codigo_documento": "HOG-PRE-08-D0125",
    "tipo_documental": "Acta de compensación",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 126,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-08",
    "carpeta": "Compensaciones y acuerdos",
    "codigo_documento": "HOG-PRE-08-D0126",
    "tipo_documental": "Acuerdo de pago",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 127,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-08",
    "carpeta": "Compensaciones y acuerdos",
    "codigo_documento": "HOG-PRE-08-D0127",
    "tipo_documental": "Adenda al convenio de compensación",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 128,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-08",
    "carpeta": "Compensaciones y acuerdos",
    "codigo_documento": "HOG-PRE-08-D0128",
    "tipo_documental": "Autorización de depósito o transferencia",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 129,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-08",
    "carpeta": "Compensaciones y acuerdos",
    "codigo_documento": "HOG-PRE-08-D0129",
    "tipo_documental": "Comprobante de transferencia",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 130,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-08",
    "carpeta": "Compensaciones y acuerdos",
    "codigo_documento": "HOG-PRE-08-D0130",
    "tipo_documental": "Convenio de compensación",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 131,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-08",
    "carpeta": "Compensaciones y acuerdos",
    "codigo_documento": "HOG-PRE-08-D0131",
    "tipo_documental": "Finiquito de compensación",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 132,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-08",
    "carpeta": "Compensaciones y acuerdos",
    "codigo_documento": "HOG-PRE-08-D0132",
    "tipo_documental": "Recibo de pago",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 133,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-09",
    "carpeta": "Evaluación socioeconómica",
    "codigo_documento": "HOG-PRE-09-D0133",
    "tipo_documental": "Cuestionario de censo socioeconómico del hogar",
    "aplicabilidad_catalogo": "Todos los hogares censados; documentos técnicos según afectación y activos asociados.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): censo, información socioeconómica de línea base, identificación de personas afectadas y fecha de corte.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 2 — levantamiento de línea base, censo, inventario de activos y estudios socioeconómicos."
  },
  {
    "orden": 134,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-09",
    "carpeta": "Evaluación socioeconómica",
    "codigo_documento": "HOG-PRE-09-D0134",
    "tipo_documental": "Ficha de levantamiento topográfico",
    "aplicabilidad_catalogo": "Todos los hogares censados; documentos técnicos según afectación y activos asociados.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): censo, información socioeconómica de línea base, identificación de personas afectadas y fecha de corte.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 2 — levantamiento de línea base, censo, inventario de activos y estudios socioeconómicos."
  },
  {
    "orden": 135,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-09",
    "carpeta": "Evaluación socioeconómica",
    "codigo_documento": "HOG-PRE-09-D0135",
    "tipo_documental": "Ficha socioeconómica del hogar",
    "aplicabilidad_catalogo": "Todos los hogares censados; documentos técnicos según afectación y activos asociados.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Sensitivo",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): censo, información socioeconómica de línea base, identificación de personas afectadas y fecha de corte.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 2 — levantamiento de línea base, censo, inventario de activos y estudios socioeconómicos."
  },
  {
    "orden": 136,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-09",
    "carpeta": "Evaluación socioeconómica",
    "codigo_documento": "HOG-PRE-09-D0136",
    "tipo_documental": "Identificación georreferenciada del hogar",
    "aplicabilidad_catalogo": "Todos los hogares censados; documentos técnicos según afectación y activos asociados.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): censo, información socioeconómica de línea base, identificación de personas afectadas y fecha de corte.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 2 — levantamiento de línea base, censo, inventario de activos y estudios socioeconómicos."
  },
  {
    "orden": 137,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-09",
    "carpeta": "Evaluación socioeconómica",
    "codigo_documento": "HOG-PRE-09-D0137",
    "tipo_documental": "Medición de la vivienda",
    "aplicabilidad_catalogo": "Todos los hogares censados; documentos técnicos según afectación y activos asociados.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): censo, información socioeconómica de línea base, identificación de personas afectadas y fecha de corte.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 2 — levantamiento de línea base, censo, inventario de activos y estudios socioeconómicos."
  },
  {
    "orden": 138,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-09",
    "carpeta": "Evaluación socioeconómica",
    "codigo_documento": "HOG-PRE-09-D0138",
    "tipo_documental": "Medición del predio",
    "aplicabilidad_catalogo": "Todos los hogares censados; documentos técnicos según afectación y activos asociados.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): censo, información socioeconómica de línea base, identificación de personas afectadas y fecha de corte.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 2 — levantamiento de línea base, censo, inventario de activos y estudios socioeconómicos."
  },
  {
    "orden": 139,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-09",
    "carpeta": "Evaluación socioeconómica",
    "codigo_documento": "HOG-PRE-09-D0139",
    "tipo_documental": "Registro de condición inicial del hogar",
    "aplicabilidad_catalogo": "Todos los hogares censados; documentos técnicos según afectación y activos asociados.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): censo, información socioeconómica de línea base, identificación de personas afectadas y fecha de corte.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 2 — levantamiento de línea base, censo, inventario de activos y estudios socioeconómicos."
  },
  {
    "orden": 140,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-09",
    "carpeta": "Evaluación socioeconómica",
    "codigo_documento": "HOG-PRE-09-D0140",
    "tipo_documental": "Registro técnico de la vivienda",
    "aplicabilidad_catalogo": "Todos los hogares censados; documentos técnicos según afectación y activos asociados.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "Registro técnico de viviendas",
    "fuente_nd5": "ND5 (2012): censo, información socioeconómica de línea base, identificación de personas afectadas y fecha de corte.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 2 — levantamiento de línea base, censo, inventario de activos y estudios socioeconómicos."
  },
  {
    "orden": 141,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-09",
    "carpeta": "Evaluación socioeconómica",
    "codigo_documento": "HOG-PRE-09-D0141",
    "tipo_documental": "Registro técnico del predio",
    "aplicabilidad_catalogo": "Todos los hogares censados; documentos técnicos según afectación y activos asociados.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "Registro técnico de predios",
    "fuente_nd5": "ND5 (2012): censo, información socioeconómica de línea base, identificación de personas afectadas y fecha de corte.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 2 — levantamiento de línea base, censo, inventario de activos y estudios socioeconómicos."
  },
  {
    "orden": 142,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-09",
    "carpeta": "Evaluación socioeconómica",
    "codigo_documento": "HOG-PRE-09-D0142",
    "tipo_documental": "Resultado del análisis de vulnerabilidad del hogar",
    "aplicabilidad_catalogo": "Todos los hogares censados; documentos técnicos según afectación y activos asociados.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): censo, información socioeconómica de línea base, identificación de personas afectadas y fecha de corte.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 2 — levantamiento de línea base, censo, inventario de activos y estudios socioeconómicos."
  },
  {
    "orden": 143,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-10",
    "carpeta": "Seguimiento social",
    "codigo_documento": "HOG-PRE-10-D0143",
    "tipo_documental": "Acuse de recibo de información",
    "aplicabilidad_catalogo": "Según actividades, seguimiento, participación, atención psicosocial y casos CDQR asociados.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): participación informada, consulta, divulgación, mecanismo de quejas y atención a grupos vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — participación de partes interesadas, divulgación y mecanismo de quejas."
  },
  {
    "orden": 144,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-10",
    "carpeta": "Seguimiento social",
    "codigo_documento": "HOG-PRE-10-D0144",
    "tipo_documental": "Consulta, denuncia, queja o reclamo presentado",
    "aplicabilidad_catalogo": "Según actividades, seguimiento, participación, atención psicosocial y casos CDQR asociados.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): participación informada, consulta, divulgación, mecanismo de quejas y atención a grupos vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — participación de partes interesadas, divulgación y mecanismo de quejas."
  },
  {
    "orden": 145,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-10",
    "carpeta": "Seguimiento social",
    "codigo_documento": "HOG-PRE-10-D0145",
    "tipo_documental": "Convocatoria o constancia de convocatoria",
    "aplicabilidad_catalogo": "Según actividades, seguimiento, participación, atención psicosocial y casos CDQR asociados.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): participación informada, consulta, divulgación, mecanismo de quejas y atención a grupos vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — participación de partes interesadas, divulgación y mecanismo de quejas."
  },
  {
    "orden": 146,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-10",
    "carpeta": "Seguimiento social",
    "codigo_documento": "HOG-PRE-10-D0146",
    "tipo_documental": "Diagnóstico psicosocial de la familia",
    "aplicabilidad_catalogo": "Según actividades, seguimiento, participación, atención psicosocial y casos CDQR asociados.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Sensitivo",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): participación informada, consulta, divulgación, mecanismo de quejas y atención a grupos vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — participación de partes interesadas, divulgación y mecanismo de quejas."
  },
  {
    "orden": 147,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-10",
    "carpeta": "Seguimiento social",
    "codigo_documento": "HOG-PRE-10-D0147",
    "tipo_documental": "Evidencia de participación en actividades",
    "aplicabilidad_catalogo": "Según actividades, seguimiento, participación, atención psicosocial y casos CDQR asociados.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): participación informada, consulta, divulgación, mecanismo de quejas y atención a grupos vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — participación de partes interesadas, divulgación y mecanismo de quejas."
  },
  {
    "orden": 148,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-10",
    "carpeta": "Seguimiento social",
    "codigo_documento": "HOG-PRE-10-D0148",
    "tipo_documental": "Formato de seguimiento al hogar",
    "aplicabilidad_catalogo": "Según actividades, seguimiento, participación, atención psicosocial y casos CDQR asociados.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): participación informada, consulta, divulgación, mecanismo de quejas y atención a grupos vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — participación de partes interesadas, divulgación y mecanismo de quejas."
  },
  {
    "orden": 149,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-10",
    "carpeta": "Seguimiento social",
    "codigo_documento": "HOG-PRE-10-D0149",
    "tipo_documental": "Informe de acompañamiento psicosocial",
    "aplicabilidad_catalogo": "Según actividades, seguimiento, participación, atención psicosocial y casos CDQR asociados.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Sensitivo",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): participación informada, consulta, divulgación, mecanismo de quejas y atención a grupos vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — participación de partes interesadas, divulgación y mecanismo de quejas."
  },
  {
    "orden": 150,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-10",
    "carpeta": "Seguimiento social",
    "codigo_documento": "HOG-PRE-10-D0150",
    "tipo_documental": "Lista de asistencia",
    "aplicabilidad_catalogo": "Según actividades, seguimiento, participación, atención psicosocial y casos CDQR asociados.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR + Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "ND5 (2012): participación informada, consulta, divulgación, mecanismo de quejas y atención a grupos vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — participación de partes interesadas, divulgación y mecanismo de quejas."
  },
  {
    "orden": 151,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-10",
    "carpeta": "Seguimiento social",
    "codigo_documento": "HOG-PRE-10-D0151",
    "tipo_documental": "Minuta o acta de reunión con el hogar",
    "aplicabilidad_catalogo": "Según actividades, seguimiento, participación, atención psicosocial y casos CDQR asociados.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): participación informada, consulta, divulgación, mecanismo de quejas y atención a grupos vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — participación de partes interesadas, divulgación y mecanismo de quejas."
  },
  {
    "orden": 152,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-10",
    "carpeta": "Seguimiento social",
    "codigo_documento": "HOG-PRE-10-D0152",
    "tipo_documental": "Referencia o constancia de atención interinstitucional",
    "aplicabilidad_catalogo": "Según actividades, seguimiento, participación, atención psicosocial y casos CDQR asociados.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): participación informada, consulta, divulgación, mecanismo de quejas y atención a grupos vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — participación de partes interesadas, divulgación y mecanismo de quejas."
  },
  {
    "orden": 153,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-10",
    "carpeta": "Seguimiento social",
    "codigo_documento": "HOG-PRE-10-D0153",
    "tipo_documental": "Registro de acercamiento con el hogar",
    "aplicabilidad_catalogo": "Según actividades, seguimiento, participación, atención psicosocial y casos CDQR asociados.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): participación informada, consulta, divulgación, mecanismo de quejas y atención a grupos vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — participación de partes interesadas, divulgación y mecanismo de quejas."
  },
  {
    "orden": 154,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-10",
    "carpeta": "Seguimiento social",
    "codigo_documento": "HOG-PRE-10-D0154",
    "tipo_documental": "Registro de participación familiar o comunitaria",
    "aplicabilidad_catalogo": "Según actividades, seguimiento, participación, atención psicosocial y casos CDQR asociados.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): participación informada, consulta, divulgación, mecanismo de quejas y atención a grupos vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — participación de partes interesadas, divulgación y mecanismo de quejas."
  },
  {
    "orden": 155,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-10",
    "carpeta": "Seguimiento social",
    "codigo_documento": "HOG-PRE-10-D0155",
    "tipo_documental": "Registro de visita al hogar",
    "aplicabilidad_catalogo": "Según actividades, seguimiento, participación, atención psicosocial y casos CDQR asociados.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): participación informada, consulta, divulgación, mecanismo de quejas y atención a grupos vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — participación de partes interesadas, divulgación y mecanismo de quejas."
  },
  {
    "orden": 156,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-10",
    "carpeta": "Seguimiento social",
    "codigo_documento": "HOG-PRE-10-D0156",
    "tipo_documental": "Respuesta a consulta, denuncia, queja o reclamo",
    "aplicabilidad_catalogo": "Según actividades, seguimiento, participación, atención psicosocial y casos CDQR asociados.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): participación informada, consulta, divulgación, mecanismo de quejas y atención a grupos vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — participación de partes interesadas, divulgación y mecanismo de quejas."
  },
  {
    "orden": 157,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-11",
    "carpeta": "Situación legal y tenencia",
    "codigo_documento": "HOG-PRE-11-D0157",
    "tipo_documental": "Acta de inspección del inmueble",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 158,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-11",
    "carpeta": "Situación legal y tenencia",
    "codigo_documento": "HOG-PRE-11-D0158",
    "tipo_documental": "Autorización de uso del inmueble",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 159,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-11",
    "carpeta": "Situación legal y tenencia",
    "codigo_documento": "HOG-PRE-11-D0159",
    "tipo_documental": "Avalúo del inmueble",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 160,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-11",
    "carpeta": "Situación legal y tenencia",
    "codigo_documento": "HOG-PRE-11-D0160",
    "tipo_documental": "Certificación catastral",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 161,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-11",
    "carpeta": "Situación legal y tenencia",
    "codigo_documento": "HOG-PRE-11-D0161",
    "tipo_documental": "Certificación de gravámenes",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 162,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-11",
    "carpeta": "Situación legal y tenencia",
    "codigo_documento": "HOG-PRE-11-D0162",
    "tipo_documental": "Certificación de ocupación",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 163,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-11",
    "carpeta": "Situación legal y tenencia",
    "codigo_documento": "HOG-PRE-11-D0163",
    "tipo_documental": "Certificación registral",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 164,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-11",
    "carpeta": "Situación legal y tenencia",
    "codigo_documento": "HOG-PRE-11-D0164",
    "tipo_documental": "Certificado de capacitación",
    "aplicabilidad_catalogo": "Según composición del hogar, condición legal, tenencia y circunstancias particulares.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): requisitos generales; censo, elegibilidad, derechos y compensación; desplazamiento físico y económico.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 1, 2 y 4 — alcance, línea base, elegibilidad, compensación y planificación."
  },
  {
    "orden": 165,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-11",
    "carpeta": "Situación legal y tenencia",
    "codigo_documento": "HOG-PRE-11-D0165",
    "tipo_documental": "Certificado de defunción",
    "aplicabilidad_catalogo": "Según composición del hogar, condición legal, tenencia y circunstancias particulares.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Sensitivo",
    "activo": "Sí",
    "origen": "SIR + Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "ND5 (2012): requisitos generales; censo, elegibilidad, derechos y compensación; desplazamiento físico y económico.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 1, 2 y 4 — alcance, línea base, elegibilidad, compensación y planificación."
  },
  {
    "orden": 166,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-11",
    "carpeta": "Situación legal y tenencia",
    "codigo_documento": "HOG-PRE-11-D0166",
    "tipo_documental": "Certificado de estudios",
    "aplicabilidad_catalogo": "Según composición del hogar, condición legal, tenencia y circunstancias particulares.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): requisitos generales; censo, elegibilidad, derechos y compensación; desplazamiento físico y económico.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 1, 2 y 4 — alcance, línea base, elegibilidad, compensación y planificación."
  },
  {
    "orden": 167,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-11",
    "carpeta": "Situación legal y tenencia",
    "codigo_documento": "HOG-PRE-11-D0167",
    "tipo_documental": "Certificado de matrimonio",
    "aplicabilidad_catalogo": "Según composición del hogar, condición legal, tenencia y circunstancias particulares.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Sensitivo",
    "activo": "Sí",
    "origen": "SIR + Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "ND5 (2012): requisitos generales; censo, elegibilidad, derechos y compensación; desplazamiento físico y económico.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 1, 2 y 4 — alcance, línea base, elegibilidad, compensación y planificación."
  },
  {
    "orden": 168,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-11",
    "carpeta": "Situación legal y tenencia",
    "codigo_documento": "HOG-PRE-11-D0168",
    "tipo_documental": "Cesión de derechos",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 169,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-11",
    "carpeta": "Situación legal y tenencia",
    "codigo_documento": "HOG-PRE-11-D0169",
    "tipo_documental": "Constancia de posesión",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 170,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-11",
    "carpeta": "Situación legal y tenencia",
    "codigo_documento": "HOG-PRE-11-D0170",
    "tipo_documental": "Contrato de arrendamiento",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 171,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-11",
    "carpeta": "Situación legal y tenencia",
    "codigo_documento": "HOG-PRE-11-D0171",
    "tipo_documental": "Contrato de compraventa",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 172,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-11",
    "carpeta": "Situación legal y tenencia",
    "codigo_documento": "HOG-PRE-11-D0172",
    "tipo_documental": "Contrato de servicio público o social",
    "aplicabilidad_catalogo": "Según composición del hogar, condición legal, tenencia y circunstancias particulares.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): requisitos generales; censo, elegibilidad, derechos y compensación; desplazamiento físico y económico.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 1, 2 y 4 — alcance, línea base, elegibilidad, compensación y planificación."
  },
  {
    "orden": 173,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-11",
    "carpeta": "Situación legal y tenencia",
    "codigo_documento": "HOG-PRE-11-D0173",
    "tipo_documental": "Descripción de linderos",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 174,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-11",
    "carpeta": "Situación legal y tenencia",
    "codigo_documento": "HOG-PRE-11-D0174",
    "tipo_documental": "Documento de adquisición del predio",
    "aplicabilidad_catalogo": "Según composición del hogar, condición legal, tenencia y circunstancias particulares.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): requisitos generales; censo, elegibilidad, derechos y compensación; desplazamiento físico y económico.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 1, 2 y 4 — alcance, línea base, elegibilidad, compensación y planificación."
  },
  {
    "orden": 175,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-11",
    "carpeta": "Situación legal y tenencia",
    "codigo_documento": "HOG-PRE-11-D0175",
    "tipo_documental": "Documento de proceso legal",
    "aplicabilidad_catalogo": "Según composición del hogar, condición legal, tenencia y circunstancias particulares.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): requisitos generales; censo, elegibilidad, derechos y compensación; desplazamiento físico y económico.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 1, 2 y 4 — alcance, línea base, elegibilidad, compensación y planificación."
  },
  {
    "orden": 176,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-11",
    "carpeta": "Situación legal y tenencia",
    "codigo_documento": "HOG-PRE-11-D0176",
    "tipo_documental": "Documento de tenencia",
    "aplicabilidad_catalogo": "Según composición del hogar, condición legal, tenencia y circunstancias particulares.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): requisitos generales; censo, elegibilidad, derechos y compensación; desplazamiento físico y económico.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 1, 2 y 4 — alcance, línea base, elegibilidad, compensación y planificación."
  },
  {
    "orden": 177,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-11",
    "carpeta": "Situación legal y tenencia",
    "codigo_documento": "HOG-PRE-11-D0177",
    "tipo_documental": "Documento de trámite del nuevo título de propiedad",
    "aplicabilidad_catalogo": "Según composición del hogar, condición legal, tenencia y circunstancias particulares.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): requisitos generales; censo, elegibilidad, derechos y compensación; desplazamiento físico y económico.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 1, 2 y 4 — alcance, línea base, elegibilidad, compensación y planificación."
  },
  {
    "orden": 178,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-11",
    "carpeta": "Situación legal y tenencia",
    "codigo_documento": "HOG-PRE-11-D0178",
    "tipo_documental": "Escritura de propiedad",
    "aplicabilidad_catalogo": "Según composición del hogar, condición legal, tenencia y circunstancias particulares.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): requisitos generales; censo, elegibilidad, derechos y compensación; desplazamiento físico y económico.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 1, 2 y 4 — alcance, línea base, elegibilidad, compensación y planificación."
  },
  {
    "orden": 179,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-11",
    "carpeta": "Situación legal y tenencia",
    "codigo_documento": "HOG-PRE-11-D0179",
    "tipo_documental": "Escritura pública",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 180,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-11",
    "carpeta": "Situación legal y tenencia",
    "codigo_documento": "HOG-PRE-11-D0180",
    "tipo_documental": "Factura o recibo de servicio público",
    "aplicabilidad_catalogo": "Según composición del hogar, condición legal, tenencia y circunstancias particulares.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): requisitos generales; censo, elegibilidad, derechos y compensación; desplazamiento físico y económico.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 1, 2 y 4 — alcance, línea base, elegibilidad, compensación y planificación."
  },
  {
    "orden": 181,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-11",
    "carpeta": "Situación legal y tenencia",
    "codigo_documento": "HOG-PRE-11-D0181",
    "tipo_documental": "Folio real o ficha registral",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 182,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-11",
    "carpeta": "Situación legal y tenencia",
    "codigo_documento": "HOG-PRE-11-D0182",
    "tipo_documental": "Fotografía de integrante del hogar",
    "aplicabilidad_catalogo": "Según composición del hogar, condición legal, tenencia y circunstancias particulares.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): requisitos generales; censo, elegibilidad, derechos y compensación; desplazamiento físico y económico.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 1, 2 y 4 — alcance, línea base, elegibilidad, compensación y planificación."
  },
  {
    "orden": 183,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-11",
    "carpeta": "Situación legal y tenencia",
    "codigo_documento": "HOG-PRE-11-D0183",
    "tipo_documental": "Partida de nacimiento",
    "aplicabilidad_catalogo": "Según composición del hogar, condición legal, tenencia y circunstancias particulares.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Sensitivo",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): requisitos generales; censo, elegibilidad, derechos y compensación; desplazamiento físico y económico.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 1, 2 y 4 — alcance, línea base, elegibilidad, compensación y planificación."
  },
  {
    "orden": 184,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-11",
    "carpeta": "Situación legal y tenencia",
    "codigo_documento": "HOG-PRE-11-D0184",
    "tipo_documental": "Paz y salvo fiscal de la finca",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 185,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-11",
    "carpeta": "Situación legal y tenencia",
    "codigo_documento": "HOG-PRE-11-D0185",
    "tipo_documental": "Permiso de construcción",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 186,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-11",
    "carpeta": "Situación legal y tenencia",
    "codigo_documento": "HOG-PRE-11-D0186",
    "tipo_documental": "Permiso de ocupación",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 187,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-11",
    "carpeta": "Situación legal y tenencia",
    "codigo_documento": "HOG-PRE-11-D0187",
    "tipo_documental": "Permiso de residencia",
    "aplicabilidad_catalogo": "Según composición del hogar, condición legal, tenencia y circunstancias particulares.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): requisitos generales; censo, elegibilidad, derechos y compensación; desplazamiento físico y económico.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 1, 2 y 4 — alcance, línea base, elegibilidad, compensación y planificación."
  },
  {
    "orden": 188,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-11",
    "carpeta": "Situación legal y tenencia",
    "codigo_documento": "HOG-PRE-11-D0188",
    "tipo_documental": "Plano catastral",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 189,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-11",
    "carpeta": "Situación legal y tenencia",
    "codigo_documento": "HOG-PRE-11-D0189",
    "tipo_documental": "Tarjeta de vacunación",
    "aplicabilidad_catalogo": "Según composición del hogar, condición legal, tenencia y circunstancias particulares.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Sensitivo",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): requisitos generales; censo, elegibilidad, derechos y compensación; desplazamiento físico y económico.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 1, 2 y 4 — alcance, línea base, elegibilidad, compensación y planificación."
  },
  {
    "orden": 190,
    "nivel": "Hogar",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "HOG-PRE-11",
    "carpeta": "Situación legal y tenencia",
    "codigo_documento": "HOG-PRE-11-D0190",
    "tipo_documental": "Título de propiedad",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 191,
    "nivel": "Hogar",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "HOG-DUR-01",
    "carpeta": "09 Entrega, reubicación y recepción",
    "codigo_documento": "HOG-DUR-01-D0191",
    "tipo_documental": "Acta de entrega de bienes",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 192,
    "nivel": "Hogar",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "HOG-DUR-01",
    "carpeta": "09 Entrega, reubicación y recepción",
    "codigo_documento": "HOG-DUR-01-D0192",
    "tipo_documental": "Acta de ocupación de nueva vivienda",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 193,
    "nivel": "Hogar",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "HOG-DUR-01",
    "carpeta": "09 Entrega, reubicación y recepción",
    "codigo_documento": "HOG-DUR-01-D0193",
    "tipo_documental": "Acta de recepción de vivienda",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 194,
    "nivel": "Hogar",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "HOG-DUR-01",
    "carpeta": "09 Entrega, reubicación y recepción",
    "codigo_documento": "HOG-DUR-01-D0194",
    "tipo_documental": "Acta de reubicación",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 195,
    "nivel": "Hogar",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "HOG-DUR-02",
    "carpeta": "Compensaciones",
    "codigo_documento": "HOG-DUR-02-D0195",
    "tipo_documental": "Acta de entrega de la vivienda",
    "aplicabilidad_catalogo": "Hogares en implementación de compensación, entrega o traslado.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR + Catálogo legal PAC",
    "alias": "Acta de entrega de vivienda",
    "fuente_nd5": "ND5 (2012): compensación, alternativas de reasentamiento, asistencia y formalización previa al desplazamiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 4 y 6 — compensación, vivienda de reposición, acuerdos e implementación."
  },
  {
    "orden": 196,
    "nivel": "Hogar",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "HOG-DUR-02",
    "carpeta": "Compensaciones",
    "codigo_documento": "HOG-DUR-02-D0196",
    "tipo_documental": "Acta de entrega del predio",
    "aplicabilidad_catalogo": "Hogares en implementación de compensación, entrega o traslado.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): compensación, alternativas de reasentamiento, asistencia y formalización previa al desplazamiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 4 y 6 — compensación, vivienda de reposición, acuerdos e implementación."
  },
  {
    "orden": 197,
    "nivel": "Hogar",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "HOG-DUR-02",
    "carpeta": "Compensaciones",
    "codigo_documento": "HOG-DUR-02-D0197",
    "tipo_documental": "Acta de traslado",
    "aplicabilidad_catalogo": "Hogares en implementación de compensación, entrega o traslado.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): compensación, alternativas de reasentamiento, asistencia y formalización previa al desplazamiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 4 y 6 — compensación, vivienda de reposición, acuerdos e implementación."
  },
  {
    "orden": 198,
    "nivel": "Hogar",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "HOG-DUR-02",
    "carpeta": "Compensaciones",
    "codigo_documento": "HOG-DUR-02-D0198",
    "tipo_documental": "Constancia de entrega o recepción de compensación",
    "aplicabilidad_catalogo": "Hogares en implementación de compensación, entrega o traslado.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "SIR + Catálogo legal PAC",
    "alias": "Constancia de entrega o recepción de comunicación",
    "fuente_nd5": "ND5 (2012): compensación, alternativas de reasentamiento, asistencia y formalización previa al desplazamiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 4 y 6 — compensación, vivienda de reposición, acuerdos e implementación."
  },
  {
    "orden": 199,
    "nivel": "Hogar",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "HOG-DUR-02",
    "carpeta": "Compensaciones",
    "codigo_documento": "HOG-DUR-02-D0199",
    "tipo_documental": "Documento de entrega de medidas de asistencia",
    "aplicabilidad_catalogo": "Hogares en implementación de compensación, entrega o traslado.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): compensación, alternativas de reasentamiento, asistencia y formalización previa al desplazamiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 4 y 6 — compensación, vivienda de reposición, acuerdos e implementación."
  },
  {
    "orden": 200,
    "nivel": "Hogar",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "HOG-DUR-02",
    "carpeta": "Compensaciones",
    "codigo_documento": "HOG-DUR-02-D0200",
    "tipo_documental": "Documento de liquidación de compensaciones",
    "aplicabilidad_catalogo": "Hogares en implementación de compensación, entrega o traslado.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): compensación, alternativas de reasentamiento, asistencia y formalización previa al desplazamiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 4 y 6 — compensación, vivienda de reposición, acuerdos e implementación."
  },
  {
    "orden": 201,
    "nivel": "Hogar",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "HOG-DUR-02",
    "carpeta": "Compensaciones",
    "codigo_documento": "HOG-DUR-02-D0201",
    "tipo_documental": "Soporte o comprobante de pago",
    "aplicabilidad_catalogo": "Hogares en implementación de compensación, entrega o traslado.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): compensación, alternativas de reasentamiento, asistencia y formalización previa al desplazamiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 4 y 6 — compensación, vivienda de reposición, acuerdos e implementación."
  },
  {
    "orden": 202,
    "nivel": "Hogar",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "HOG-DUR-03",
    "carpeta": "Seguimiento social",
    "codigo_documento": "HOG-DUR-03-D0202",
    "tipo_documental": "Acta de acompañamiento",
    "aplicabilidad_catalogo": "Hogares durante traslado, transición o entrega de medidas.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 203,
    "nivel": "Hogar",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "HOG-DUR-03",
    "carpeta": "Seguimiento social",
    "codigo_documento": "HOG-DUR-03-D0203",
    "tipo_documental": "Evidencia fotográfica del traslado",
    "aplicabilidad_catalogo": "Hogares durante traslado, transición o entrega de medidas.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 204,
    "nivel": "Hogar",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "HOG-DUR-03",
    "carpeta": "Seguimiento social",
    "codigo_documento": "HOG-DUR-03-D0204",
    "tipo_documental": "Formato de acompañamiento al traslado",
    "aplicabilidad_catalogo": "Hogares durante traslado, transición o entrega de medidas.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 205,
    "nivel": "Hogar",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "HOG-DUR-03",
    "carpeta": "Seguimiento social",
    "codigo_documento": "HOG-DUR-03-D0205",
    "tipo_documental": "Informe de seguimiento durante el reasentamiento",
    "aplicabilidad_catalogo": "Hogares durante traslado, transición o entrega de medidas.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 206,
    "nivel": "Hogar",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "HOG-DUR-03",
    "carpeta": "Seguimiento social",
    "codigo_documento": "HOG-DUR-03-D0206",
    "tipo_documental": "Informe del proceso de traslado o transición",
    "aplicabilidad_catalogo": "Hogares durante traslado, transición o entrega de medidas.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 207,
    "nivel": "Hogar",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "HOG-DUR-03",
    "carpeta": "Seguimiento social",
    "codigo_documento": "HOG-DUR-03-D0207",
    "tipo_documental": "Registro de visita o verificación operativa",
    "aplicabilidad_catalogo": "Hogares durante traslado, transición o entrega de medidas.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 208,
    "nivel": "Hogar",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "HOG-DUR-03",
    "carpeta": "Seguimiento social",
    "codigo_documento": "HOG-DUR-03-D0208",
    "tipo_documental": "Registro y atención de incidencia",
    "aplicabilidad_catalogo": "Hogares durante traslado, transición o entrega de medidas.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 209,
    "nivel": "Hogar",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "HOG-POS-01",
    "carpeta": "Cierre del expediente",
    "codigo_documento": "HOG-POS-01-D0209",
    "tipo_documental": "Certificación de cierre del expediente",
    "aplicabilidad_catalogo": "Hogares que concluyeron las medidas, verificaciones y compromisos aplicables.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 210,
    "nivel": "Hogar",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "HOG-POS-01",
    "carpeta": "Cierre del expediente",
    "codigo_documento": "HOG-POS-01-D0210",
    "tipo_documental": "Constancia de cumplimiento de compromisos",
    "aplicabilidad_catalogo": "Hogares que concluyeron las medidas, verificaciones y compromisos aplicables.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 211,
    "nivel": "Hogar",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "HOG-POS-01",
    "carpeta": "Cierre del expediente",
    "codigo_documento": "HOG-POS-01-D0211",
    "tipo_documental": "Documento o acta de cierre del proceso",
    "aplicabilidad_catalogo": "Hogares que concluyeron las medidas, verificaciones y compromisos aplicables.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 212,
    "nivel": "Hogar",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "HOG-POS-01",
    "carpeta": "Cierre del expediente",
    "codigo_documento": "HOG-POS-01-D0212",
    "tipo_documental": "Informe final del hogar",
    "aplicabilidad_catalogo": "Hogares que concluyeron las medidas, verificaciones y compromisos aplicables.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 213,
    "nivel": "Hogar",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "HOG-POS-01",
    "carpeta": "Cierre del expediente",
    "codigo_documento": "HOG-POS-01-D0213",
    "tipo_documental": "Registro de validación del cierre",
    "aplicabilidad_catalogo": "Hogares que concluyeron las medidas, verificaciones y compromisos aplicables.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 214,
    "nivel": "Hogar",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "HOG-POS-01",
    "carpeta": "Cierre del expediente",
    "codigo_documento": "HOG-POS-01-D0214",
    "tipo_documental": "Soporte de entrega de reconocimiento económico",
    "aplicabilidad_catalogo": "Hogares que concluyeron las medidas, verificaciones y compromisos aplicables.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 215,
    "nivel": "Hogar",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "HOG-POS-01",
    "carpeta": "Cierre del expediente",
    "codigo_documento": "HOG-POS-01-D0215",
    "tipo_documental": "Soporte de medida de asistencia aplicada",
    "aplicabilidad_catalogo": "Hogares que concluyeron las medidas, verificaciones y compromisos aplicables.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 216,
    "nivel": "Hogar",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "HOG-POS-02",
    "carpeta": "Seguimiento social",
    "codigo_documento": "HOG-POS-02-D0216",
    "tipo_documental": "Certificación de restablecimiento de medio de vida instalado",
    "aplicabilidad_catalogo": "Hogares reasentados o con medidas de restablecimiento y seguimiento posterior.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): restablecimiento y mejora de medios de subsistencia, asistencia transitoria y atención a personas vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 5 — restablecimiento y mejora de medios de subsistencia."
  },
  {
    "orden": 217,
    "nivel": "Hogar",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "HOG-POS-02",
    "carpeta": "Seguimiento social",
    "codigo_documento": "HOG-POS-02-D0217",
    "tipo_documental": "Constancia de participación en actividades del PARRMS",
    "aplicabilidad_catalogo": "Hogares reasentados o con medidas de restablecimiento y seguimiento posterior.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): restablecimiento y mejora de medios de subsistencia, asistencia transitoria y atención a personas vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 5 — restablecimiento y mejora de medios de subsistencia."
  },
  {
    "orden": 218,
    "nivel": "Hogar",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "HOG-POS-02",
    "carpeta": "Seguimiento social",
    "codigo_documento": "HOG-POS-02-D0218",
    "tipo_documental": "Evidencia de asistencia aplicada",
    "aplicabilidad_catalogo": "Hogares reasentados o con medidas de restablecimiento y seguimiento posterior.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): restablecimiento y mejora de medios de subsistencia, asistencia transitoria y atención a personas vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 5 — restablecimiento y mejora de medios de subsistencia."
  },
  {
    "orden": 219,
    "nivel": "Hogar",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "HOG-POS-02",
    "carpeta": "Seguimiento social",
    "codigo_documento": "HOG-POS-02-D0219",
    "tipo_documental": "Evidencia fotográfica de seguimiento",
    "aplicabilidad_catalogo": "Hogares reasentados o con medidas de restablecimiento y seguimiento posterior.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): restablecimiento y mejora de medios de subsistencia, asistencia transitoria y atención a personas vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 5 — restablecimiento y mejora de medios de subsistencia."
  },
  {
    "orden": 220,
    "nivel": "Hogar",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "HOG-POS-02",
    "carpeta": "Seguimiento social",
    "codigo_documento": "HOG-POS-02-D0220",
    "tipo_documental": "Formato o acta de visita post-reasentamiento",
    "aplicabilidad_catalogo": "Hogares reasentados o con medidas de restablecimiento y seguimiento posterior.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): restablecimiento y mejora de medios de subsistencia, asistencia transitoria y atención a personas vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 5 — restablecimiento y mejora de medios de subsistencia."
  },
  {
    "orden": 221,
    "nivel": "Hogar",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "HOG-POS-02",
    "carpeta": "Seguimiento social",
    "codigo_documento": "HOG-POS-02-D0221",
    "tipo_documental": "Informe de acompañamiento social o psicosocial",
    "aplicabilidad_catalogo": "Hogares reasentados o con medidas de restablecimiento y seguimiento posterior.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Sensitivo",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): restablecimiento y mejora de medios de subsistencia, asistencia transitoria y atención a personas vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 5 — restablecimiento y mejora de medios de subsistencia."
  },
  {
    "orden": 222,
    "nivel": "Hogar",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "HOG-POS-02",
    "carpeta": "Seguimiento social",
    "codigo_documento": "HOG-POS-02-D0222",
    "tipo_documental": "Informe de estabilización del hogar",
    "aplicabilidad_catalogo": "Hogares reasentados o con medidas de restablecimiento y seguimiento posterior.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): restablecimiento y mejora de medios de subsistencia, asistencia transitoria y atención a personas vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 5 — restablecimiento y mejora de medios de subsistencia."
  },
  {
    "orden": 223,
    "nivel": "Hogar",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "HOG-POS-02",
    "carpeta": "Seguimiento social",
    "codigo_documento": "HOG-POS-02-D0223",
    "tipo_documental": "Informe de seguimiento post-reasentamiento",
    "aplicabilidad_catalogo": "Hogares reasentados o con medidas de restablecimiento y seguimiento posterior.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): restablecimiento y mejora de medios de subsistencia, asistencia transitoria y atención a personas vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 5 — restablecimiento y mejora de medios de subsistencia."
  },
  {
    "orden": 224,
    "nivel": "Hogar",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "HOG-POS-02",
    "carpeta": "Seguimiento social",
    "codigo_documento": "HOG-POS-02-D0224",
    "tipo_documental": "Registro de seguimiento final o verificación complementaria",
    "aplicabilidad_catalogo": "Hogares reasentados o con medidas de restablecimiento y seguimiento posterior.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): restablecimiento y mejora de medios de subsistencia, asistencia transitoria y atención a personas vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 5 — restablecimiento y mejora de medios de subsistencia."
  },
  {
    "orden": 225,
    "nivel": "Hogar",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "HOG-POS-02",
    "carpeta": "Seguimiento social",
    "codigo_documento": "HOG-POS-02-D0225",
    "tipo_documental": "Registro de verificación de condiciones",
    "aplicabilidad_catalogo": "Hogares reasentados o con medidas de restablecimiento y seguimiento posterior.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_hogar; id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): restablecimiento y mejora de medios de subsistencia, asistencia transitoria y atención a personas vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 5 — restablecimiento y mejora de medios de subsistencia."
  },
  {
    "orden": 226,
    "nivel": "Persona no residente",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PNR-PRE-01",
    "carpeta": "Avalúos",
    "codigo_documento": "PNR-PRE-01-D0226",
    "tipo_documental": "Documento de aceptación del valor",
    "aplicabilidad_catalogo": "Personas no residentes con activos sujetos a valoración.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): compensación a costo de reposición y documentación de la valoración de tierras y activos.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 4 — valoración, costo de reposición, compensación y acuerdos."
  },
  {
    "orden": 227,
    "nivel": "Persona no residente",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PNR-PRE-01",
    "carpeta": "Avalúos",
    "codigo_documento": "PNR-PRE-01-D0227",
    "tipo_documental": "Documento de entrega del resultado",
    "aplicabilidad_catalogo": "Personas no residentes con activos sujetos a valoración.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): compensación a costo de reposición y documentación de la valoración de tierras y activos.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 4 — valoración, costo de reposición, compensación y acuerdos."
  },
  {
    "orden": 228,
    "nivel": "Persona no residente",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PNR-PRE-01",
    "carpeta": "Avalúos",
    "codigo_documento": "PNR-PRE-01-D0228",
    "tipo_documental": "Informe de avalúo de vivienda, mejoras o activos",
    "aplicabilidad_catalogo": "Personas no residentes con activos sujetos a valoración.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): compensación a costo de reposición y documentación de la valoración de tierras y activos.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 4 — valoración, costo de reposición, compensación y acuerdos."
  },
  {
    "orden": 229,
    "nivel": "Persona no residente",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PNR-PRE-01",
    "carpeta": "Avalúos",
    "codigo_documento": "PNR-PRE-01-D0229",
    "tipo_documental": "Permiso o autorización de avalúo",
    "aplicabilidad_catalogo": "Personas no residentes con activos sujetos a valoración.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): compensación a costo de reposición y documentación de la valoración de tierras y activos.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 4 — valoración, costo de reposición, compensación y acuerdos."
  },
  {
    "orden": 230,
    "nivel": "Persona no residente",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PNR-PRE-02",
    "carpeta": "Evaluación socioeconómica",
    "codigo_documento": "PNR-PRE-02-D0230",
    "tipo_documental": "Censo de la persona no residente",
    "aplicabilidad_catalogo": "Personas no residentes identificadas con activos o derechos afectados.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): censo, información socioeconómica de línea base, identificación de personas afectadas y fecha de corte.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 2 — levantamiento de línea base, censo, inventario de activos y estudios socioeconómicos."
  },
  {
    "orden": 231,
    "nivel": "Persona no residente",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PNR-PRE-02",
    "carpeta": "Evaluación socioeconómica",
    "codigo_documento": "PNR-PRE-02-D0231",
    "tipo_documental": "Ficha socioeconómica",
    "aplicabilidad_catalogo": "Personas no residentes identificadas con activos o derechos afectados.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Sensitivo",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): censo, información socioeconómica de línea base, identificación de personas afectadas y fecha de corte.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 2 — levantamiento de línea base, censo, inventario de activos y estudios socioeconómicos."
  },
  {
    "orden": 232,
    "nivel": "Persona no residente",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PNR-PRE-02",
    "carpeta": "Evaluación socioeconómica",
    "codigo_documento": "PNR-PRE-02-D0232",
    "tipo_documental": "Identificación georreferenciada de activos",
    "aplicabilidad_catalogo": "Personas no residentes identificadas con activos o derechos afectados.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): censo, información socioeconómica de línea base, identificación de personas afectadas y fecha de corte.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 2 — levantamiento de línea base, censo, inventario de activos y estudios socioeconómicos."
  },
  {
    "orden": 233,
    "nivel": "Persona no residente",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PNR-PRE-02",
    "carpeta": "Evaluación socioeconómica",
    "codigo_documento": "PNR-PRE-02-D0233",
    "tipo_documental": "Registro de condición inicial de activos",
    "aplicabilidad_catalogo": "Personas no residentes identificadas con activos o derechos afectados.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): censo, información socioeconómica de línea base, identificación de personas afectadas y fecha de corte.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 2 — levantamiento de línea base, censo, inventario de activos y estudios socioeconómicos."
  },
  {
    "orden": 234,
    "nivel": "Persona no residente",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PNR-PRE-03",
    "carpeta": "Seguimiento social",
    "codigo_documento": "PNR-PRE-03-D0234",
    "tipo_documental": "Minuta o acta de reunión",
    "aplicabilidad_catalogo": "Según acciones de relacionamiento y casos CDQR.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): participación informada, consulta, divulgación, mecanismo de quejas y atención a grupos vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — participación de partes interesadas, divulgación y mecanismo de quejas."
  },
  {
    "orden": 235,
    "nivel": "Persona no residente",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PNR-PRE-03",
    "carpeta": "Seguimiento social",
    "codigo_documento": "PNR-PRE-03-D0235",
    "tipo_documental": "Registro de acercamiento o seguimiento",
    "aplicabilidad_catalogo": "Según acciones de relacionamiento y casos CDQR.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): participación informada, consulta, divulgación, mecanismo de quejas y atención a grupos vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — participación de partes interesadas, divulgación y mecanismo de quejas."
  },
  {
    "orden": 236,
    "nivel": "Persona no residente",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PNR-PRE-03",
    "carpeta": "Seguimiento social",
    "codigo_documento": "PNR-PRE-03-D0236",
    "tipo_documental": "Registro de visita",
    "aplicabilidad_catalogo": "Según acciones de relacionamiento y casos CDQR.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): participación informada, consulta, divulgación, mecanismo de quejas y atención a grupos vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — participación de partes interesadas, divulgación y mecanismo de quejas."
  },
  {
    "orden": 237,
    "nivel": "Persona no residente",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PNR-PRE-04",
    "carpeta": "Situación legal",
    "codigo_documento": "PNR-PRE-04-D0237",
    "tipo_documental": "Contrato, factura o recibo de servicio",
    "aplicabilidad_catalogo": "Según identidad, tenencia, edad y condición legal de la persona.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): requisitos generales; censo, elegibilidad, derechos y compensación; desplazamiento físico y económico.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 1, 2 y 4 — alcance, línea base, elegibilidad, compensación y planificación."
  },
  {
    "orden": 238,
    "nivel": "Persona no residente",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "PNR-DUR-01",
    "carpeta": "Seguimiento social",
    "codigo_documento": "PNR-DUR-01-D0238",
    "tipo_documental": "Formato de acompañamiento",
    "aplicabilidad_catalogo": "Personas no residentes identificadas como vulnerables.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): restablecimiento y mejora de medios de subsistencia, asistencia transitoria y atención a personas vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 5 — restablecimiento y mejora de medios de subsistencia."
  },
  {
    "orden": 239,
    "nivel": "Persona no residente",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "PNR-DUR-01",
    "carpeta": "Seguimiento social",
    "codigo_documento": "PNR-DUR-01-D0239",
    "tipo_documental": "Informe de seguimiento a persona vulnerable",
    "aplicabilidad_catalogo": "Personas no residentes identificadas como vulnerables.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): restablecimiento y mejora de medios de subsistencia, asistencia transitoria y atención a personas vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 5 — restablecimiento y mejora de medios de subsistencia."
  },
  {
    "orden": 240,
    "nivel": "Persona no residente",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "PNR-DUR-01",
    "carpeta": "Seguimiento social",
    "codigo_documento": "PNR-DUR-01-D0240",
    "tipo_documental": "Registro de visita a persona vulnerable",
    "aplicabilidad_catalogo": "Personas no residentes identificadas como vulnerables.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): restablecimiento y mejora de medios de subsistencia, asistencia transitoria y atención a personas vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 5 — restablecimiento y mejora de medios de subsistencia."
  },
  {
    "orden": 241,
    "nivel": "Persona no residente",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "PNR-POS-01",
    "carpeta": "Cierre del expediente",
    "codigo_documento": "PNR-POS-01-D0241",
    "tipo_documental": "Acta de cierre del proceso",
    "aplicabilidad_catalogo": "Personas cuyo proceso y medidas aplicables han concluido.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 242,
    "nivel": "Persona no residente",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "PNR-POS-01",
    "carpeta": "Cierre del expediente",
    "codigo_documento": "PNR-POS-01-D0242",
    "tipo_documental": "Informe final de la persona no residente",
    "aplicabilidad_catalogo": "Personas cuyo proceso y medidas aplicables han concluido.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 243,
    "nivel": "Persona no residente",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "PNR-POS-01",
    "carpeta": "Cierre del expediente",
    "codigo_documento": "PNR-POS-01-D0243",
    "tipo_documental": "Soporte documental de medida de asistencia aplicada",
    "aplicabilidad_catalogo": "Personas cuyo proceso y medidas aplicables han concluido.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 244,
    "nivel": "Persona no residente",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "PNR-POS-02",
    "carpeta": "Seguimiento social",
    "codigo_documento": "PNR-POS-02-D0244",
    "tipo_documental": "Evidencia de asistencia a persona vulnerable",
    "aplicabilidad_catalogo": "Personas vulnerables que requieren seguimiento posterior.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 245,
    "nivel": "Persona no residente",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "PNR-POS-02",
    "carpeta": "Seguimiento social",
    "codigo_documento": "PNR-POS-02-D0245",
    "tipo_documental": "Formato de visita firmado",
    "aplicabilidad_catalogo": "Personas vulnerables que requieren seguimiento posterior.",
    "niveles_relacionados": "Persona, Predio, Vivienda, Activo",
    "llaves_relacion": "id_persona; id_predio; id_vivienda; id_activo",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 246,
    "nivel": "Organización comunitaria o productiva",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "ORG-PRE-01",
    "carpeta": "Evaluación socioeconómica",
    "codigo_documento": "ORG-PRE-01-D0246",
    "tipo_documental": "Entrevista a informante clave",
    "aplicabilidad_catalogo": "Organizaciones comunitarias y productivas identificadas en el área del proyecto.",
    "niveles_relacionados": "Lugar poblado, Proyecto",
    "llaves_relacion": "id_organizacion; id_lugar_poblado; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): censo, información socioeconómica de línea base, identificación de personas afectadas y fecha de corte.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 2 — levantamiento de línea base, censo, inventario de activos y estudios socioeconómicos."
  },
  {
    "orden": 247,
    "nivel": "Organización comunitaria o productiva",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "ORG-PRE-01",
    "carpeta": "Evaluación socioeconómica",
    "codigo_documento": "ORG-PRE-01-D0247",
    "tipo_documental": "Evidencia documental aportada por la organización",
    "aplicabilidad_catalogo": "Organizaciones comunitarias y productivas identificadas en el área del proyecto.",
    "niveles_relacionados": "Lugar poblado, Proyecto",
    "llaves_relacion": "id_organizacion; id_lugar_poblado; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): censo, información socioeconómica de línea base, identificación de personas afectadas y fecha de corte.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 2 — levantamiento de línea base, censo, inventario de activos y estudios socioeconómicos."
  },
  {
    "orden": 248,
    "nivel": "Organización comunitaria o productiva",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "ORG-PRE-01",
    "carpeta": "Evaluación socioeconómica",
    "codigo_documento": "ORG-PRE-01-D0248",
    "tipo_documental": "Ficha comunitaria",
    "aplicabilidad_catalogo": "Organizaciones comunitarias y productivas identificadas en el área del proyecto.",
    "niveles_relacionados": "Lugar poblado, Proyecto",
    "llaves_relacion": "id_organizacion; id_lugar_poblado; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): censo, información socioeconómica de línea base, identificación de personas afectadas y fecha de corte.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 2 — levantamiento de línea base, censo, inventario de activos y estudios socioeconómicos."
  },
  {
    "orden": 249,
    "nivel": "Organización comunitaria o productiva",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "ORG-PRE-01",
    "carpeta": "Evaluación socioeconómica",
    "codigo_documento": "ORG-PRE-01-D0249",
    "tipo_documental": "Ficha de identificación de la organización",
    "aplicabilidad_catalogo": "Organizaciones comunitarias y productivas identificadas en el área del proyecto.",
    "niveles_relacionados": "Lugar poblado, Proyecto",
    "llaves_relacion": "id_organizacion; id_lugar_poblado; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): censo, información socioeconómica de línea base, identificación de personas afectadas y fecha de corte.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 2 — levantamiento de línea base, censo, inventario de activos y estudios socioeconómicos."
  },
  {
    "orden": 250,
    "nivel": "Organización comunitaria o productiva",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "ORG-PRE-01",
    "carpeta": "Evaluación socioeconómica",
    "codigo_documento": "ORG-PRE-01-D0250",
    "tipo_documental": "Registro de actividad productiva",
    "aplicabilidad_catalogo": "Organizaciones comunitarias y productivas identificadas en el área del proyecto.",
    "niveles_relacionados": "Lugar poblado, Proyecto",
    "llaves_relacion": "id_organizacion; id_lugar_poblado; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): censo, información socioeconómica de línea base, identificación de personas afectadas y fecha de corte.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 2 — levantamiento de línea base, censo, inventario de activos y estudios socioeconómicos."
  },
  {
    "orden": 251,
    "nivel": "Organización comunitaria o productiva",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "ORG-PRE-01",
    "carpeta": "Evaluación socioeconómica",
    "codigo_documento": "ORG-PRE-01-D0251",
    "tipo_documental": "Registro de caracterización de la organización",
    "aplicabilidad_catalogo": "Organizaciones comunitarias y productivas identificadas en el área del proyecto.",
    "niveles_relacionados": "Lugar poblado, Proyecto",
    "llaves_relacion": "id_organizacion; id_lugar_poblado; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): censo, información socioeconómica de línea base, identificación de personas afectadas y fecha de corte.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 2 — levantamiento de línea base, censo, inventario de activos y estudios socioeconómicos."
  },
  {
    "orden": 252,
    "nivel": "Organización comunitaria o productiva",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "ORG-PRE-01",
    "carpeta": "Evaluación socioeconómica",
    "codigo_documento": "ORG-PRE-01-D0252",
    "tipo_documental": "Registro de integrantes o representantes",
    "aplicabilidad_catalogo": "Organizaciones comunitarias y productivas identificadas en el área del proyecto.",
    "niveles_relacionados": "Lugar poblado, Proyecto",
    "llaves_relacion": "id_organizacion; id_lugar_poblado; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): censo, información socioeconómica de línea base, identificación de personas afectadas y fecha de corte.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 2 — levantamiento de línea base, censo, inventario de activos y estudios socioeconómicos."
  },
  {
    "orden": 253,
    "nivel": "Organización comunitaria o productiva",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "ORG-PRE-01",
    "carpeta": "Evaluación socioeconómica",
    "codigo_documento": "ORG-PRE-01-D0253",
    "tipo_documental": "Registro de ámbito territorial",
    "aplicabilidad_catalogo": "Organizaciones comunitarias y productivas identificadas en el área del proyecto.",
    "niveles_relacionados": "Lugar poblado, Proyecto",
    "llaves_relacion": "id_organizacion; id_lugar_poblado; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): censo, información socioeconómica de línea base, identificación de personas afectadas y fecha de corte.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 2 — levantamiento de línea base, censo, inventario de activos y estudios socioeconómicos."
  },
  {
    "orden": 254,
    "nivel": "Organización comunitaria o productiva",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "ORG-PRE-02",
    "carpeta": "Seguimiento social",
    "codigo_documento": "ORG-PRE-02-D0254",
    "tipo_documental": "Diagnóstico participativo",
    "aplicabilidad_catalogo": "Según procesos participativos y acciones de relacionamiento.",
    "niveles_relacionados": "Lugar poblado, Proyecto",
    "llaves_relacion": "id_organizacion; id_lugar_poblado; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): participación informada, consulta, divulgación, mecanismo de quejas y atención a grupos vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — participación de partes interesadas, divulgación y mecanismo de quejas."
  },
  {
    "orden": 255,
    "nivel": "Organización comunitaria o productiva",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "ORG-PRE-02",
    "carpeta": "Seguimiento social",
    "codigo_documento": "ORG-PRE-02-D0255",
    "tipo_documental": "Evidencia de participación",
    "aplicabilidad_catalogo": "Según procesos participativos y acciones de relacionamiento.",
    "niveles_relacionados": "Lugar poblado, Proyecto",
    "llaves_relacion": "id_organizacion; id_lugar_poblado; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): participación informada, consulta, divulgación, mecanismo de quejas y atención a grupos vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — participación de partes interesadas, divulgación y mecanismo de quejas."
  },
  {
    "orden": 256,
    "nivel": "Organización comunitaria o productiva",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "ORG-PRE-02",
    "carpeta": "Seguimiento social",
    "codigo_documento": "ORG-PRE-02-D0256",
    "tipo_documental": "Informe de liderazgo comunitario",
    "aplicabilidad_catalogo": "Según procesos participativos y acciones de relacionamiento.",
    "niveles_relacionados": "Lugar poblado, Proyecto",
    "llaves_relacion": "id_organizacion; id_lugar_poblado; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): participación informada, consulta, divulgación, mecanismo de quejas y atención a grupos vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — participación de partes interesadas, divulgación y mecanismo de quejas."
  },
  {
    "orden": 257,
    "nivel": "Organización comunitaria o productiva",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "ORG-PRE-02",
    "carpeta": "Seguimiento social",
    "codigo_documento": "ORG-PRE-02-D0257",
    "tipo_documental": "Informe de organizaciones presentes en la comunidad",
    "aplicabilidad_catalogo": "Según procesos participativos y acciones de relacionamiento.",
    "niveles_relacionados": "Lugar poblado, Proyecto",
    "llaves_relacion": "id_organizacion; id_lugar_poblado; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): participación informada, consulta, divulgación, mecanismo de quejas y atención a grupos vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — participación de partes interesadas, divulgación y mecanismo de quejas."
  },
  {
    "orden": 258,
    "nivel": "Organización comunitaria o productiva",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "ORG-PRE-02",
    "carpeta": "Seguimiento social",
    "codigo_documento": "ORG-PRE-02-D0258",
    "tipo_documental": "Informe de reorganización comunitaria",
    "aplicabilidad_catalogo": "Según procesos participativos y acciones de relacionamiento.",
    "niveles_relacionados": "Lugar poblado, Proyecto",
    "llaves_relacion": "id_organizacion; id_lugar_poblado; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): participación informada, consulta, divulgación, mecanismo de quejas y atención a grupos vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — participación de partes interesadas, divulgación y mecanismo de quejas."
  },
  {
    "orden": 259,
    "nivel": "Organización comunitaria o productiva",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "ORG-DUR-01",
    "carpeta": "Compensación y fortalecimiento",
    "codigo_documento": "ORG-DUR-01-D0259",
    "tipo_documental": "Evidencia de integración de acciones en la organización",
    "aplicabilidad_catalogo": "Organizaciones sujetas a medidas de mejora, fortalecimiento, capacitación o asistencia.",
    "niveles_relacionados": "Lugar poblado, Proyecto",
    "llaves_relacion": "id_organizacion; id_lugar_poblado; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): restablecimiento y mejora de medios de subsistencia, asistencia transitoria y atención a personas vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 5 — restablecimiento y mejora de medios de subsistencia."
  },
  {
    "orden": 260,
    "nivel": "Organización comunitaria o productiva",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "ORG-DUR-01",
    "carpeta": "Compensación y fortalecimiento",
    "codigo_documento": "ORG-DUR-01-D0260",
    "tipo_documental": "Lista de asistencia a capacitación",
    "aplicabilidad_catalogo": "Organizaciones sujetas a medidas de mejora, fortalecimiento, capacitación o asistencia.",
    "niveles_relacionados": "Lugar poblado, Proyecto",
    "llaves_relacion": "id_organizacion; id_lugar_poblado; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): restablecimiento y mejora de medios de subsistencia, asistencia transitoria y atención a personas vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 5 — restablecimiento y mejora de medios de subsistencia."
  },
  {
    "orden": 261,
    "nivel": "Organización comunitaria o productiva",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "ORG-DUR-01",
    "carpeta": "Compensación y fortalecimiento",
    "codigo_documento": "ORG-DUR-01-D0261",
    "tipo_documental": "Material de capacitación",
    "aplicabilidad_catalogo": "Organizaciones sujetas a medidas de mejora, fortalecimiento, capacitación o asistencia.",
    "niveles_relacionados": "Lugar poblado, Proyecto",
    "llaves_relacion": "id_organizacion; id_lugar_poblado; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): restablecimiento y mejora de medios de subsistencia, asistencia transitoria y atención a personas vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 5 — restablecimiento y mejora de medios de subsistencia."
  },
  {
    "orden": 262,
    "nivel": "Organización comunitaria o productiva",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "ORG-DUR-01",
    "carpeta": "Compensación y fortalecimiento",
    "codigo_documento": "ORG-DUR-01-D0262",
    "tipo_documental": "Plan o informe de plan de mejora",
    "aplicabilidad_catalogo": "Organizaciones sujetas a medidas de mejora, fortalecimiento, capacitación o asistencia.",
    "niveles_relacionados": "Lugar poblado, Proyecto",
    "llaves_relacion": "id_organizacion; id_lugar_poblado; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): restablecimiento y mejora de medios de subsistencia, asistencia transitoria y atención a personas vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 5 — restablecimiento y mejora de medios de subsistencia."
  },
  {
    "orden": 263,
    "nivel": "Organización comunitaria o productiva",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "ORG-DUR-01",
    "carpeta": "Compensación y fortalecimiento",
    "codigo_documento": "ORG-DUR-01-D0263",
    "tipo_documental": "Soporte de capacitación",
    "aplicabilidad_catalogo": "Organizaciones sujetas a medidas de mejora, fortalecimiento, capacitación o asistencia.",
    "niveles_relacionados": "Lugar poblado, Proyecto",
    "llaves_relacion": "id_organizacion; id_lugar_poblado; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): restablecimiento y mejora de medios de subsistencia, asistencia transitoria y atención a personas vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 5 — restablecimiento y mejora de medios de subsistencia."
  },
  {
    "orden": 264,
    "nivel": "Organización comunitaria o productiva",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "ORG-DUR-01",
    "carpeta": "Compensación y fortalecimiento",
    "codigo_documento": "ORG-DUR-01-D0264",
    "tipo_documental": "Soporte o informe de acompañamiento",
    "aplicabilidad_catalogo": "Organizaciones sujetas a medidas de mejora, fortalecimiento, capacitación o asistencia.",
    "niveles_relacionados": "Lugar poblado, Proyecto",
    "llaves_relacion": "id_organizacion; id_lugar_poblado; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): restablecimiento y mejora de medios de subsistencia, asistencia transitoria y atención a personas vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 5 — restablecimiento y mejora de medios de subsistencia."
  },
  {
    "orden": 265,
    "nivel": "Organización comunitaria o productiva",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "ORG-DUR-01",
    "carpeta": "Compensación y fortalecimiento",
    "codigo_documento": "ORG-DUR-01-D0265",
    "tipo_documental": "Soporte o informe de asistencia técnica",
    "aplicabilidad_catalogo": "Organizaciones sujetas a medidas de mejora, fortalecimiento, capacitación o asistencia.",
    "niveles_relacionados": "Lugar poblado, Proyecto",
    "llaves_relacion": "id_organizacion; id_lugar_poblado; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): restablecimiento y mejora de medios de subsistencia, asistencia transitoria y atención a personas vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 5 — restablecimiento y mejora de medios de subsistencia."
  },
  {
    "orden": 266,
    "nivel": "Organización comunitaria o productiva",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "ORG-DUR-01",
    "carpeta": "Compensación y fortalecimiento",
    "codigo_documento": "ORG-DUR-01-D0266",
    "tipo_documental": "Soporte o informe de diálogo de saberes",
    "aplicabilidad_catalogo": "Organizaciones sujetas a medidas de mejora, fortalecimiento, capacitación o asistencia.",
    "niveles_relacionados": "Lugar poblado, Proyecto",
    "llaves_relacion": "id_organizacion; id_lugar_poblado; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): restablecimiento y mejora de medios de subsistencia, asistencia transitoria y atención a personas vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 5 — restablecimiento y mejora de medios de subsistencia."
  },
  {
    "orden": 267,
    "nivel": "Organización comunitaria o productiva",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "ORG-DUR-02",
    "carpeta": "Seguimiento social",
    "codigo_documento": "ORG-DUR-02-D0267",
    "tipo_documental": "Informe de diagnóstico participativo actualizado",
    "aplicabilidad_catalogo": "Según seguimiento de la organización y de sus procesos participativos.",
    "niveles_relacionados": "Lugar poblado, Proyecto",
    "llaves_relacion": "id_organizacion; id_lugar_poblado; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): participación informada, consulta, divulgación, mecanismo de quejas y atención a grupos vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — participación de partes interesadas, divulgación y mecanismo de quejas."
  },
  {
    "orden": 268,
    "nivel": "Organización comunitaria o productiva",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "ORG-DUR-02",
    "carpeta": "Seguimiento social",
    "codigo_documento": "ORG-DUR-02-D0268",
    "tipo_documental": "Informe de seguimiento a liderazgos",
    "aplicabilidad_catalogo": "Según seguimiento de la organización y de sus procesos participativos.",
    "niveles_relacionados": "Lugar poblado, Proyecto",
    "llaves_relacion": "id_organizacion; id_lugar_poblado; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): participación informada, consulta, divulgación, mecanismo de quejas y atención a grupos vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — participación de partes interesadas, divulgación y mecanismo de quejas."
  },
  {
    "orden": 269,
    "nivel": "Organización comunitaria o productiva",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "ORG-DUR-02",
    "carpeta": "Seguimiento social",
    "codigo_documento": "ORG-DUR-02-D0269",
    "tipo_documental": "Informe de seguimiento a organizaciones",
    "aplicabilidad_catalogo": "Según seguimiento de la organización y de sus procesos participativos.",
    "niveles_relacionados": "Lugar poblado, Proyecto",
    "llaves_relacion": "id_organizacion; id_lugar_poblado; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "Informe de seguimiento a la reorganización | Informe de seguimiento de organizaciones",
    "fuente_nd5": "ND5 (2012): participación informada, consulta, divulgación, mecanismo de quejas y atención a grupos vulnerables.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — participación de partes interesadas, divulgación y mecanismo de quejas."
  },
  {
    "orden": 270,
    "nivel": "Organización comunitaria o productiva",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "ORG-POS-01",
    "carpeta": "Cierre del expediente",
    "codigo_documento": "ORG-POS-01-D0270",
    "tipo_documental": "Acta de cierre del proceso con la organización",
    "aplicabilidad_catalogo": "Organizaciones cuyo proceso y acciones aplicables han concluido.",
    "niveles_relacionados": "Lugar poblado, Proyecto",
    "llaves_relacion": "id_organizacion; id_lugar_poblado; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 271,
    "nivel": "Organización comunitaria o productiva",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "ORG-POS-01",
    "carpeta": "Cierre del expediente",
    "codigo_documento": "ORG-POS-01-D0271",
    "tipo_documental": "Constancia de cumplimiento de acciones",
    "aplicabilidad_catalogo": "Organizaciones cuyo proceso y acciones aplicables han concluido.",
    "niveles_relacionados": "Lugar poblado, Proyecto",
    "llaves_relacion": "id_organizacion; id_lugar_poblado; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 272,
    "nivel": "Organización comunitaria o productiva",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "ORG-POS-01",
    "carpeta": "Cierre del expediente",
    "codigo_documento": "ORG-POS-01-D0272",
    "tipo_documental": "Documento de cierre",
    "aplicabilidad_catalogo": "Organizaciones cuyo proceso y acciones aplicables han concluido.",
    "niveles_relacionados": "Lugar poblado, Proyecto",
    "llaves_relacion": "id_organizacion; id_lugar_poblado; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 273,
    "nivel": "Organización comunitaria o productiva",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "ORG-POS-01",
    "carpeta": "Cierre del expediente",
    "codigo_documento": "ORG-POS-01-D0273",
    "tipo_documental": "Informe final de la organización",
    "aplicabilidad_catalogo": "Organizaciones cuyo proceso y acciones aplicables han concluido.",
    "niveles_relacionados": "Lugar poblado, Proyecto",
    "llaves_relacion": "id_organizacion; id_lugar_poblado; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 274,
    "nivel": "Organización comunitaria o productiva",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "ORG-POS-02",
    "carpeta": "Seguimiento social",
    "codigo_documento": "ORG-POS-02-D0274",
    "tipo_documental": "Informe de seguimiento de la organización participativa",
    "aplicabilidad_catalogo": "Organizaciones con seguimiento posterior a medidas o procesos de reorganización.",
    "niveles_relacionados": "Lugar poblado, Proyecto",
    "llaves_relacion": "id_organizacion; id_lugar_poblado; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 275,
    "nivel": "Organización comunitaria o productiva",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "ORG-POS-02",
    "carpeta": "Seguimiento social",
    "codigo_documento": "ORG-POS-02-D0275",
    "tipo_documental": "Informe de verificación final",
    "aplicabilidad_catalogo": "Organizaciones con seguimiento posterior a medidas o procesos de reorganización.",
    "niveles_relacionados": "Lugar poblado, Proyecto",
    "llaves_relacion": "id_organizacion; id_lugar_poblado; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 276,
    "nivel": "Lugar poblado",
    "fase": "Transversal",
    "codigo_carpeta": "LPO-TRA-01",
    "carpeta": "Comunicaciones y notificaciones",
    "codigo_documento": "LPO-TRA-01-D0276",
    "tipo_documental": "Aviso público",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 277,
    "nivel": "Lugar poblado",
    "fase": "Transversal",
    "codigo_carpeta": "LPO-TRA-01",
    "carpeta": "Comunicaciones y notificaciones",
    "codigo_documento": "LPO-TRA-01-D0277",
    "tipo_documental": "Circular informativa",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 278,
    "nivel": "Lugar poblado",
    "fase": "Transversal",
    "codigo_carpeta": "LPO-TRA-01",
    "carpeta": "Comunicaciones y notificaciones",
    "codigo_documento": "LPO-TRA-01-D0278",
    "tipo_documental": "Comunicación oficial",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 279,
    "nivel": "Lugar poblado",
    "fase": "Transversal",
    "codigo_carpeta": "LPO-TRA-01",
    "carpeta": "Comunicaciones y notificaciones",
    "codigo_documento": "LPO-TRA-01-D0279",
    "tipo_documental": "Notificación oficial",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 280,
    "nivel": "Lugar poblado",
    "fase": "Transversal",
    "codigo_carpeta": "LPO-TRA-02",
    "carpeta": "Convenios y compromisos",
    "codigo_documento": "LPO-TRA-02-D0280",
    "tipo_documental": "Acta de compromiso",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 281,
    "nivel": "Lugar poblado",
    "fase": "Transversal",
    "codigo_carpeta": "LPO-TRA-02",
    "carpeta": "Convenios y compromisos",
    "codigo_documento": "LPO-TRA-02-D0281",
    "tipo_documental": "Adenda a convenio",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 282,
    "nivel": "Lugar poblado",
    "fase": "Transversal",
    "codigo_carpeta": "LPO-TRA-02",
    "carpeta": "Convenios y compromisos",
    "codigo_documento": "LPO-TRA-02-D0282",
    "tipo_documental": "Carta de compromiso",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 283,
    "nivel": "Lugar poblado",
    "fase": "Transversal",
    "codigo_carpeta": "LPO-TRA-02",
    "carpeta": "Convenios y compromisos",
    "codigo_documento": "LPO-TRA-02-D0283",
    "tipo_documental": "Convenio colectivo",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 284,
    "nivel": "Lugar poblado",
    "fase": "Transversal",
    "codigo_carpeta": "LPO-TRA-02",
    "carpeta": "Convenios y compromisos",
    "codigo_documento": "LPO-TRA-02-D0284",
    "tipo_documental": "Memorando de entendimiento",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 285,
    "nivel": "Lugar poblado",
    "fase": "Transversal",
    "codigo_carpeta": "LPO-TRA-03",
    "carpeta": "Quejas, reclamos y respuestas",
    "codigo_documento": "LPO-TRA-03-D0285",
    "tipo_documental": "Acta de mediación",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 286,
    "nivel": "Lugar poblado",
    "fase": "Transversal",
    "codigo_carpeta": "LPO-TRA-03",
    "carpeta": "Quejas, reclamos y respuestas",
    "codigo_documento": "LPO-TRA-03-D0286",
    "tipo_documental": "Acta de resolución",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 287,
    "nivel": "Lugar poblado",
    "fase": "Transversal",
    "codigo_carpeta": "LPO-TRA-03",
    "carpeta": "Quejas, reclamos y respuestas",
    "codigo_documento": "LPO-TRA-03-D0287",
    "tipo_documental": "Queja colectiva",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 288,
    "nivel": "Lugar poblado",
    "fase": "Transversal",
    "codigo_carpeta": "LPO-TRA-03",
    "carpeta": "Quejas, reclamos y respuestas",
    "codigo_documento": "LPO-TRA-03-D0288",
    "tipo_documental": "Reclamo colectivo",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 289,
    "nivel": "Lugar poblado",
    "fase": "Transversal",
    "codigo_carpeta": "LPO-TRA-03",
    "carpeta": "Quejas, reclamos y respuestas",
    "codigo_documento": "LPO-TRA-03-D0289",
    "tipo_documental": "Respuesta formal",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 290,
    "nivel": "Lugar poblado",
    "fase": "Transversal",
    "codigo_carpeta": "LPO-TRA-03",
    "carpeta": "Quejas, reclamos y respuestas",
    "codigo_documento": "LPO-TRA-03-D0290",
    "tipo_documental": "Solicitud formal",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 291,
    "nivel": "Lugar poblado",
    "fase": "Transversal",
    "codigo_carpeta": "LPO-TRA-04",
    "carpeta": "Reuniones y acuerdos",
    "codigo_documento": "LPO-TRA-04-D0291",
    "tipo_documental": "Acta de reunión",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 292,
    "nivel": "Lugar poblado",
    "fase": "Transversal",
    "codigo_carpeta": "LPO-TRA-04",
    "carpeta": "Reuniones y acuerdos",
    "codigo_documento": "LPO-TRA-04-D0292",
    "tipo_documental": "Convocatoria de reunión",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 293,
    "nivel": "Lugar poblado",
    "fase": "Transversal",
    "codigo_carpeta": "LPO-TRA-04",
    "carpeta": "Reuniones y acuerdos",
    "codigo_documento": "LPO-TRA-04-D0293",
    "tipo_documental": "Minuta de reunión",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 294,
    "nivel": "Lugar poblado",
    "fase": "Transversal",
    "codigo_carpeta": "LPO-TRA-04",
    "carpeta": "Reuniones y acuerdos",
    "codigo_documento": "LPO-TRA-04-D0294",
    "tipo_documental": "Registro de acuerdos y compromisos",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 295,
    "nivel": "Lugar poblado",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "LPO-PRE-01",
    "carpeta": "03 Acuerdos comunitarios",
    "codigo_documento": "LPO-PRE-01-D0295",
    "tipo_documental": "Acta de aprobación de acuerdo",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 296,
    "nivel": "Lugar poblado",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "LPO-PRE-01",
    "carpeta": "03 Acuerdos comunitarios",
    "codigo_documento": "LPO-PRE-01-D0296",
    "tipo_documental": "Acta de ratificación de acuerdo",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 297,
    "nivel": "Lugar poblado",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "LPO-PRE-01",
    "carpeta": "03 Acuerdos comunitarios",
    "codigo_documento": "LPO-PRE-01-D0297",
    "tipo_documental": "Acuerdo con el lugar poblado",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 298,
    "nivel": "Lugar poblado",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "LPO-PRE-01",
    "carpeta": "03 Acuerdos comunitarios",
    "codigo_documento": "LPO-PRE-01-D0298",
    "tipo_documental": "Adenda a acuerdo",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 299,
    "nivel": "Lugar poblado",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "LPO-PRE-01",
    "carpeta": "03 Acuerdos comunitarios",
    "codigo_documento": "LPO-PRE-01-D0299",
    "tipo_documental": "Registro de firmas del acuerdo",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 300,
    "nivel": "Lugar poblado",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "LPO-PRE-02",
    "carpeta": "Bienes colectivos",
    "codigo_documento": "LPO-PRE-02-D0300",
    "tipo_documental": "Acta de afectación del bien",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 301,
    "nivel": "Lugar poblado",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "LPO-PRE-02",
    "carpeta": "Bienes colectivos",
    "codigo_documento": "LPO-PRE-02-D0301",
    "tipo_documental": "Acta de inspección de bienes",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 302,
    "nivel": "Lugar poblado",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "LPO-PRE-02",
    "carpeta": "Bienes colectivos",
    "codigo_documento": "LPO-PRE-02-D0302",
    "tipo_documental": "Acta de validación de inventario",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 303,
    "nivel": "Lugar poblado",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "LPO-PRE-02",
    "carpeta": "Bienes colectivos",
    "codigo_documento": "LPO-PRE-02-D0303",
    "tipo_documental": "Avalúo de bien",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 304,
    "nivel": "Lugar poblado",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "LPO-PRE-02",
    "carpeta": "Bienes colectivos",
    "codigo_documento": "LPO-PRE-02-D0304",
    "tipo_documental": "Documento de propiedad o titularidad del bien",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 305,
    "nivel": "Lugar poblado",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "LPO-PRE-02",
    "carpeta": "Bienes colectivos",
    "codigo_documento": "LPO-PRE-02-D0305",
    "tipo_documental": "Inventario de bienes colectivos",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 306,
    "nivel": "Lugar poblado",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "LPO-PRE-02",
    "carpeta": "Bienes colectivos",
    "codigo_documento": "LPO-PRE-02-D0306",
    "tipo_documental": "Registro fotográfico del bien",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 307,
    "nivel": "Lugar poblado",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "LPO-DUR-01",
    "carpeta": "Entrega, reubicación y recepción",
    "codigo_documento": "LPO-DUR-01-D0307",
    "tipo_documental": "Acta de entrega de bienes colectivos",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 308,
    "nivel": "Lugar poblado",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "LPO-DUR-01",
    "carpeta": "Entrega, reubicación y recepción",
    "codigo_documento": "LPO-DUR-01-D0308",
    "tipo_documental": "Acta de entrega de llaves",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 309,
    "nivel": "Lugar poblado",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "LPO-DUR-01",
    "carpeta": "Entrega, reubicación y recepción",
    "codigo_documento": "LPO-DUR-01-D0309",
    "tipo_documental": "Acta de recepción de bienes colectivos",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 310,
    "nivel": "Lugar poblado",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "LPO-DUR-01",
    "carpeta": "Entrega, reubicación y recepción",
    "codigo_documento": "LPO-DUR-01-D0310",
    "tipo_documental": "Acta de reubicación colectiva",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 311,
    "nivel": "Lugar poblado",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "LPO-DUR-01",
    "carpeta": "Entrega, reubicación y recepción",
    "codigo_documento": "LPO-DUR-01-D0311",
    "tipo_documental": "Constancia de recepción conforme",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 312,
    "nivel": "Lugar poblado",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "LPO-DUR-01",
    "carpeta": "Entrega, reubicación y recepción",
    "codigo_documento": "LPO-DUR-01-D0312",
    "tipo_documental": "Garantía de bienes entregados",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "Garantía del bien entregado",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 313,
    "nivel": "Lugar poblado",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "LPO-DUR-01",
    "carpeta": "Entrega, reubicación y recepción",
    "codigo_documento": "LPO-DUR-01-D0313",
    "tipo_documental": "Inventario de bienes entregados",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 314,
    "nivel": "Lugar poblado",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "LPO-DUR-02",
    "carpeta": "Salvataje",
    "codigo_documento": "LPO-DUR-02-D0314",
    "tipo_documental": "Acta de entrega de bienes de salvataje",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 315,
    "nivel": "Lugar poblado",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "LPO-DUR-02",
    "carpeta": "Salvataje",
    "codigo_documento": "LPO-DUR-02-D0315",
    "tipo_documental": "Acta de retiro de bienes de salvataje",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 316,
    "nivel": "Lugar poblado",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "LPO-DUR-02",
    "carpeta": "Salvataje",
    "codigo_documento": "LPO-DUR-02-D0316",
    "tipo_documental": "Autorización de salvataje",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 317,
    "nivel": "Lugar poblado",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "LPO-DUR-02",
    "carpeta": "Salvataje",
    "codigo_documento": "LPO-DUR-02-D0317",
    "tipo_documental": "Constancia de recepción de bienes de salvataje",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 318,
    "nivel": "Lugar poblado",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "LPO-DUR-02",
    "carpeta": "Salvataje",
    "codigo_documento": "LPO-DUR-02-D0318",
    "tipo_documental": "Inventario de bienes de salvataje",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 319,
    "nivel": "Lugar poblado",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "LPO-DUR-02",
    "carpeta": "Salvataje",
    "codigo_documento": "LPO-DUR-02-D0319",
    "tipo_documental": "Solicitud de salvataje",
    "aplicabilidad_catalogo": "Según aplique",
    "niveles_relacionados": "Organización comunitaria o productiva, Activo, Proyecto",
    "llaves_relacion": "id_lugar_poblado; id_activo; id_organizacion; id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "https://www.ifc.org/content/dam/ifc/doc/2010/2012-ifc-performance-standard-5-es.pdf",
    "fuente_guia_ifc": "https://www.ifc.org/content/dam/ifc/doc/2023/ifc-handbook-for-land-acquisition-and-involuntary-resettlement.pdf"
  },
  {
    "orden": 320,
    "nivel": "Hogar sin censo",
    "fase": "Identificación y seguimiento",
    "codigo_carpeta": "HSC-IDN-01",
    "carpeta": "Seguimiento e identificación",
    "codigo_documento": "HSC-IDN-01-D0320",
    "tipo_documental": "Acta o minuta de visita",
    "aplicabilidad_catalogo": "Casos sin censo por ausencia, desocupación, abandono, rechazo u otra causal documentada.",
    "niveles_relacionados": "Predio, Activo, Lugar poblado",
    "llaves_relacion": "id_registro_sin_censo; id_predio; id_activo; id_lugar_poblado",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): censo, información socioeconómica de línea base, identificación de personas afectadas y fecha de corte.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 2 — levantamiento de línea base, censo, inventario de activos y estudios socioeconómicos."
  },
  {
    "orden": 321,
    "nivel": "Hogar sin censo",
    "fase": "Identificación y seguimiento",
    "codigo_carpeta": "HSC-IDN-01",
    "carpeta": "Seguimiento e identificación",
    "codigo_documento": "HSC-IDN-01-D0321",
    "tipo_documental": "Descripción del estado observado",
    "aplicabilidad_catalogo": "Casos sin censo por ausencia, desocupación, abandono, rechazo u otra causal documentada.",
    "niveles_relacionados": "Predio, Activo, Lugar poblado",
    "llaves_relacion": "id_registro_sin_censo; id_predio; id_activo; id_lugar_poblado",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): censo, información socioeconómica de línea base, identificación de personas afectadas y fecha de corte.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 2 — levantamiento de línea base, censo, inventario de activos y estudios socioeconómicos."
  },
  {
    "orden": 322,
    "nivel": "Hogar sin censo",
    "fase": "Identificación y seguimiento",
    "codigo_carpeta": "HSC-IDN-01",
    "carpeta": "Seguimiento e identificación",
    "codigo_documento": "HSC-IDN-01-D0322",
    "tipo_documental": "Documento de asociación con hogar posteriormente identificado",
    "aplicabilidad_catalogo": "Casos sin censo por ausencia, desocupación, abandono, rechazo u otra causal documentada.",
    "niveles_relacionados": "Predio, Activo, Lugar poblado",
    "llaves_relacion": "id_registro_sin_censo; id_predio; id_activo; id_lugar_poblado",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): censo, información socioeconómica de línea base, identificación de personas afectadas y fecha de corte.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 2 — levantamiento de línea base, censo, inventario de activos y estudios socioeconómicos."
  },
  {
    "orden": 323,
    "nivel": "Hogar sin censo",
    "fase": "Identificación y seguimiento",
    "codigo_carpeta": "HSC-IDN-01",
    "carpeta": "Seguimiento e identificación",
    "codigo_documento": "HSC-IDN-01-D0323",
    "tipo_documental": "Documento de información secundaria",
    "aplicabilidad_catalogo": "Casos sin censo por ausencia, desocupación, abandono, rechazo u otra causal documentada.",
    "niveles_relacionados": "Predio, Activo, Lugar poblado",
    "llaves_relacion": "id_registro_sin_censo; id_predio; id_activo; id_lugar_poblado",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): censo, información socioeconómica de línea base, identificación de personas afectadas y fecha de corte.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 2 — levantamiento de línea base, censo, inventario de activos y estudios socioeconómicos."
  },
  {
    "orden": 324,
    "nivel": "Hogar sin censo",
    "fase": "Identificación y seguimiento",
    "codigo_carpeta": "HSC-IDN-01",
    "carpeta": "Seguimiento e identificación",
    "codigo_documento": "HSC-IDN-01-D0324",
    "tipo_documental": "Documento de unificación o separación de registros",
    "aplicabilidad_catalogo": "Casos sin censo por ausencia, desocupación, abandono, rechazo u otra causal documentada.",
    "niveles_relacionados": "Predio, Activo, Lugar poblado",
    "llaves_relacion": "id_registro_sin_censo; id_predio; id_activo; id_lugar_poblado",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): censo, información socioeconómica de línea base, identificación de personas afectadas y fecha de corte.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 2 — levantamiento de línea base, censo, inventario de activos y estudios socioeconómicos."
  },
  {
    "orden": 325,
    "nivel": "Hogar sin censo",
    "fase": "Identificación y seguimiento",
    "codigo_carpeta": "HSC-IDN-01",
    "carpeta": "Seguimiento e identificación",
    "codigo_documento": "HSC-IDN-01-D0325",
    "tipo_documental": "Evidencia de intentos de contacto",
    "aplicabilidad_catalogo": "Casos sin censo por ausencia, desocupación, abandono, rechazo u otra causal documentada.",
    "niveles_relacionados": "Predio, Activo, Lugar poblado",
    "llaves_relacion": "id_registro_sin_censo; id_predio; id_activo; id_lugar_poblado",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): censo, información socioeconómica de línea base, identificación de personas afectadas y fecha de corte.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 2 — levantamiento de línea base, censo, inventario de activos y estudios socioeconómicos."
  },
  {
    "orden": 326,
    "nivel": "Hogar sin censo",
    "fase": "Identificación y seguimiento",
    "codigo_carpeta": "HSC-IDN-01",
    "carpeta": "Seguimiento e identificación",
    "codigo_documento": "HSC-IDN-01-D0326",
    "tipo_documental": "Informe de identificación preliminar",
    "aplicabilidad_catalogo": "Casos sin censo por ausencia, desocupación, abandono, rechazo u otra causal documentada.",
    "niveles_relacionados": "Predio, Activo, Lugar poblado",
    "llaves_relacion": "id_registro_sin_censo; id_predio; id_activo; id_lugar_poblado",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): censo, información socioeconómica de línea base, identificación de personas afectadas y fecha de corte.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 2 — levantamiento de línea base, censo, inventario de activos y estudios socioeconómicos."
  },
  {
    "orden": 327,
    "nivel": "Hogar sin censo",
    "fase": "Identificación y seguimiento",
    "codigo_carpeta": "HSC-IDN-01",
    "carpeta": "Seguimiento e identificación",
    "codigo_documento": "HSC-IDN-01-D0327",
    "tipo_documental": "Insumo georreferenciado o registro de coordenadas",
    "aplicabilidad_catalogo": "Casos sin censo por ausencia, desocupación, abandono, rechazo u otra causal documentada.",
    "niveles_relacionados": "Predio, Activo, Lugar poblado",
    "llaves_relacion": "id_registro_sin_censo; id_predio; id_activo; id_lugar_poblado",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): censo, información socioeconómica de línea base, identificación de personas afectadas y fecha de corte.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 2 — levantamiento de línea base, censo, inventario de activos y estudios socioeconómicos."
  },
  {
    "orden": 328,
    "nivel": "Hogar sin censo",
    "fase": "Identificación y seguimiento",
    "codigo_carpeta": "HSC-IDN-01",
    "carpeta": "Seguimiento e identificación",
    "codigo_documento": "HSC-IDN-01-D0328",
    "tipo_documental": "Plano del activo o predio",
    "aplicabilidad_catalogo": "Casos sin censo por ausencia, desocupación, abandono, rechazo u otra causal documentada.",
    "niveles_relacionados": "Predio, Activo, Lugar poblado",
    "llaves_relacion": "id_registro_sin_censo; id_predio; id_activo; id_lugar_poblado",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): censo, información socioeconómica de línea base, identificación de personas afectadas y fecha de corte.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 2 — levantamiento de línea base, censo, inventario de activos y estudios socioeconómicos."
  },
  {
    "orden": 329,
    "nivel": "Hogar sin censo",
    "fase": "Identificación y seguimiento",
    "codigo_carpeta": "HSC-IDN-01",
    "carpeta": "Seguimiento e identificación",
    "codigo_documento": "HSC-IDN-01-D0329",
    "tipo_documental": "Registro de actualización del caso",
    "aplicabilidad_catalogo": "Casos sin censo por ausencia, desocupación, abandono, rechazo u otra causal documentada.",
    "niveles_relacionados": "Predio, Activo, Lugar poblado",
    "llaves_relacion": "id_registro_sin_censo; id_predio; id_activo; id_lugar_poblado",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): censo, información socioeconómica de línea base, identificación de personas afectadas y fecha de corte.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 2 — levantamiento de línea base, censo, inventario de activos y estudios socioeconómicos."
  },
  {
    "orden": 330,
    "nivel": "Hogar sin censo",
    "fase": "Identificación y seguimiento",
    "codigo_carpeta": "HSC-IDN-01",
    "carpeta": "Seguimiento e identificación",
    "codigo_documento": "HSC-IDN-01-D0330",
    "tipo_documental": "Registro de fecha y localización de visita",
    "aplicabilidad_catalogo": "Casos sin censo por ausencia, desocupación, abandono, rechazo u otra causal documentada.",
    "niveles_relacionados": "Predio, Activo, Lugar poblado",
    "llaves_relacion": "id_registro_sin_censo; id_predio; id_activo; id_lugar_poblado",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): censo, información socioeconómica de línea base, identificación de personas afectadas y fecha de corte.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 2 — levantamiento de línea base, censo, inventario de activos y estudios socioeconómicos."
  },
  {
    "orden": 331,
    "nivel": "Hogar sin censo",
    "fase": "Identificación y seguimiento",
    "codigo_carpeta": "HSC-IDN-01",
    "carpeta": "Seguimiento e identificación",
    "codigo_documento": "HSC-IDN-01-D0331",
    "tipo_documental": "Registro de hogar ausente",
    "aplicabilidad_catalogo": "Casos sin censo por ausencia, desocupación, abandono, rechazo u otra causal documentada.",
    "niveles_relacionados": "Predio, Activo, Lugar poblado",
    "llaves_relacion": "id_registro_sin_censo; id_predio; id_activo; id_lugar_poblado",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): censo, información socioeconómica de línea base, identificación de personas afectadas y fecha de corte.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 2 — levantamiento de línea base, censo, inventario de activos y estudios socioeconómicos."
  },
  {
    "orden": 332,
    "nivel": "Hogar sin censo",
    "fase": "Identificación y seguimiento",
    "codigo_carpeta": "HSC-IDN-01",
    "carpeta": "Seguimiento e identificación",
    "codigo_documento": "HSC-IDN-01-D0332",
    "tipo_documental": "Registro de información proporcionada por terceros",
    "aplicabilidad_catalogo": "Casos sin censo por ausencia, desocupación, abandono, rechazo u otra causal documentada.",
    "niveles_relacionados": "Predio, Activo, Lugar poblado",
    "llaves_relacion": "id_registro_sin_censo; id_predio; id_activo; id_lugar_poblado",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): censo, información socioeconómica de línea base, identificación de personas afectadas y fecha de corte.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 2 — levantamiento de línea base, censo, inventario de activos y estudios socioeconómicos."
  },
  {
    "orden": 333,
    "nivel": "Hogar sin censo",
    "fase": "Identificación y seguimiento",
    "codigo_carpeta": "HSC-IDN-01",
    "carpeta": "Seguimiento e identificación",
    "codigo_documento": "HSC-IDN-01-D0333",
    "tipo_documental": "Registro de otra causal documentada",
    "aplicabilidad_catalogo": "Casos sin censo por ausencia, desocupación, abandono, rechazo u otra causal documentada.",
    "niveles_relacionados": "Predio, Activo, Lugar poblado",
    "llaves_relacion": "id_registro_sin_censo; id_predio; id_activo; id_lugar_poblado",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): censo, información socioeconómica de línea base, identificación de personas afectadas y fecha de corte.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 2 — levantamiento de línea base, censo, inventario de activos y estudios socioeconómicos."
  },
  {
    "orden": 334,
    "nivel": "Hogar sin censo",
    "fase": "Identificación y seguimiento",
    "codigo_carpeta": "HSC-IDN-01",
    "carpeta": "Seguimiento e identificación",
    "codigo_documento": "HSC-IDN-01-D0334",
    "tipo_documental": "Registro de predio abandonado o vivienda desocupada",
    "aplicabilidad_catalogo": "Casos sin censo por ausencia, desocupación, abandono, rechazo u otra causal documentada.",
    "niveles_relacionados": "Predio, Activo, Lugar poblado",
    "llaves_relacion": "id_registro_sin_censo; id_predio; id_activo; id_lugar_poblado",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): censo, información socioeconómica de línea base, identificación de personas afectadas y fecha de corte.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 2 — levantamiento de línea base, censo, inventario de activos y estudios socioeconómicos."
  },
  {
    "orden": 335,
    "nivel": "Hogar sin censo",
    "fase": "Identificación y seguimiento",
    "codigo_carpeta": "HSC-IDN-01",
    "carpeta": "Seguimiento e identificación",
    "codigo_documento": "HSC-IDN-01-D0335",
    "tipo_documental": "Registro de rechazo al censo",
    "aplicabilidad_catalogo": "Casos sin censo por ausencia, desocupación, abandono, rechazo u otra causal documentada.",
    "niveles_relacionados": "Predio, Activo, Lugar poblado",
    "llaves_relacion": "id_registro_sin_censo; id_predio; id_activo; id_lugar_poblado",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): censo, información socioeconómica de línea base, identificación de personas afectadas y fecha de corte.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 2 — levantamiento de línea base, censo, inventario de activos y estudios socioeconómicos."
  },
  {
    "orden": 336,
    "nivel": "Hogar sin censo",
    "fase": "Identificación y seguimiento",
    "codigo_carpeta": "HSC-IDN-01",
    "carpeta": "Seguimiento e identificación",
    "codigo_documento": "HSC-IDN-01-D0336",
    "tipo_documental": "Registro o formato de visita al predio",
    "aplicabilidad_catalogo": "Casos sin censo por ausencia, desocupación, abandono, rechazo u otra causal documentada.",
    "niveles_relacionados": "Predio, Activo, Lugar poblado",
    "llaves_relacion": "id_registro_sin_censo; id_predio; id_activo; id_lugar_poblado",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): censo, información socioeconómica de línea base, identificación de personas afectadas y fecha de corte.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 2 — levantamiento de línea base, censo, inventario de activos y estudios socioeconómicos."
  },
  {
    "orden": 337,
    "nivel": "Hogar sin censo",
    "fase": "Identificación y seguimiento",
    "codigo_carpeta": "HSC-IDN-01",
    "carpeta": "Seguimiento e identificación",
    "codigo_documento": "HSC-IDN-01-D0337",
    "tipo_documental": "Soporte fotográfico",
    "aplicabilidad_catalogo": "Casos sin censo por ausencia, desocupación, abandono, rechazo u otra causal documentada.",
    "niveles_relacionados": "Predio, Activo, Lugar poblado",
    "llaves_relacion": "id_registro_sin_censo; id_predio; id_activo; id_lugar_poblado",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): censo, información socioeconómica de línea base, identificación de personas afectadas y fecha de corte.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 2 — levantamiento de línea base, censo, inventario de activos y estudios socioeconómicos."
  },
  {
    "orden": 338,
    "nivel": "Proyecto",
    "fase": "Transversal",
    "codigo_carpeta": "PRY-TRA-01",
    "carpeta": "Índice general",
    "codigo_documento": "PRY-TRA-01-D0338",
    "tipo_documental": "Inventario documental del proyecto",
    "aplicabilidad_catalogo": "Archivo documental general del proyecto.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): documentación del censo, elegibilidad, medidas, implementación y resultados de seguimiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 2, 6 y 7 — gestión de información, línea base, implementación y seguimiento."
  },
  {
    "orden": 339,
    "nivel": "Proyecto",
    "fase": "Transversal",
    "codigo_carpeta": "PRY-TRA-01",
    "carpeta": "Índice general",
    "codigo_documento": "PRY-TRA-01-D0339",
    "tipo_documental": "Índice general del archivo de proyecto",
    "aplicabilidad_catalogo": "Archivo documental general del proyecto.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): documentación del censo, elegibilidad, medidas, implementación y resultados de seguimiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 2, 6 y 7 — gestión de información, línea base, implementación y seguimiento."
  },
  {
    "orden": 340,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-01",
    "carpeta": "Base de datos",
    "codigo_documento": "PRY-PRE-01-D0340",
    "tipo_documental": "Base de datos general del proceso",
    "aplicabilidad_catalogo": "Bases, catálogos y registros maestros del proyecto.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): documentación del censo, elegibilidad, medidas, implementación y resultados de seguimiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 2, 6 y 7 — gestión de información, línea base, implementación y seguimiento."
  },
  {
    "orden": 341,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-01",
    "carpeta": "Base de datos",
    "codigo_documento": "PRY-PRE-01-D0341",
    "tipo_documental": "Base maestra",
    "aplicabilidad_catalogo": "Bases, catálogos y registros maestros del proyecto.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): documentación del censo, elegibilidad, medidas, implementación y resultados de seguimiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 2, 6 y 7 — gestión de información, línea base, implementación y seguimiento."
  },
  {
    "orden": 342,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-01",
    "carpeta": "Base de datos",
    "codigo_documento": "PRY-PRE-01-D0342",
    "tipo_documental": "Catálogo de valores",
    "aplicabilidad_catalogo": "Bases, catálogos y registros maestros del proyecto.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): documentación del censo, elegibilidad, medidas, implementación y resultados de seguimiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 2, 6 y 7 — gestión de información, línea base, implementación y seguimiento."
  },
  {
    "orden": 343,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-01",
    "carpeta": "Base de datos",
    "codigo_documento": "PRY-PRE-01-D0343",
    "tipo_documental": "Catálogo de variables",
    "aplicabilidad_catalogo": "Bases, catálogos y registros maestros del proyecto.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): documentación del censo, elegibilidad, medidas, implementación y resultados de seguimiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 2, 6 y 7 — gestión de información, línea base, implementación y seguimiento."
  },
  {
    "orden": 344,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-01",
    "carpeta": "Base de datos",
    "codigo_documento": "PRY-PRE-01-D0344",
    "tipo_documental": "Diccionario de datos",
    "aplicabilidad_catalogo": "Bases, catálogos y registros maestros del proyecto.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): documentación del censo, elegibilidad, medidas, implementación y resultados de seguimiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 2, 6 y 7 — gestión de información, línea base, implementación y seguimiento."
  },
  {
    "orden": 345,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-01",
    "carpeta": "Base de datos",
    "codigo_documento": "PRY-PRE-01-D0345",
    "tipo_documental": "Modelo de datos",
    "aplicabilidad_catalogo": "Bases, catálogos y registros maestros del proyecto.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): documentación del censo, elegibilidad, medidas, implementación y resultados de seguimiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 2, 6 y 7 — gestión de información, línea base, implementación y seguimiento."
  },
  {
    "orden": 346,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-01",
    "carpeta": "Base de datos",
    "codigo_documento": "PRY-PRE-01-D0346",
    "tipo_documental": "Registro de validación o informe de calidad de datos",
    "aplicabilidad_catalogo": "Bases, catálogos y registros maestros del proyecto.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): documentación del censo, elegibilidad, medidas, implementación y resultados de seguimiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 2, 6 y 7 — gestión de información, línea base, implementación y seguimiento."
  },
  {
    "orden": 347,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-01",
    "carpeta": "Base de datos",
    "codigo_documento": "PRY-PRE-01-D0347",
    "tipo_documental": "Registro maestro de activos",
    "aplicabilidad_catalogo": "Bases, catálogos y registros maestros del proyecto.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): documentación del censo, elegibilidad, medidas, implementación y resultados de seguimiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 2, 6 y 7 — gestión de información, línea base, implementación y seguimiento."
  },
  {
    "orden": 348,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-01",
    "carpeta": "Base de datos",
    "codigo_documento": "PRY-PRE-01-D0348",
    "tipo_documental": "Registro maestro de documentos",
    "aplicabilidad_catalogo": "Bases, catálogos y registros maestros del proyecto.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): documentación del censo, elegibilidad, medidas, implementación y resultados de seguimiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 2, 6 y 7 — gestión de información, línea base, implementación y seguimiento."
  },
  {
    "orden": 349,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-01",
    "carpeta": "Base de datos",
    "codigo_documento": "PRY-PRE-01-D0349",
    "tipo_documental": "Registro maestro de hogares",
    "aplicabilidad_catalogo": "Bases, catálogos y registros maestros del proyecto.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): documentación del censo, elegibilidad, medidas, implementación y resultados de seguimiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 2, 6 y 7 — gestión de información, línea base, implementación y seguimiento."
  },
  {
    "orden": 350,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-01",
    "carpeta": "Base de datos",
    "codigo_documento": "PRY-PRE-01-D0350",
    "tipo_documental": "Registro maestro de organizaciones",
    "aplicabilidad_catalogo": "Bases, catálogos y registros maestros del proyecto.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): documentación del censo, elegibilidad, medidas, implementación y resultados de seguimiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 2, 6 y 7 — gestión de información, línea base, implementación y seguimiento."
  },
  {
    "orden": 351,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-01",
    "carpeta": "Base de datos",
    "codigo_documento": "PRY-PRE-01-D0351",
    "tipo_documental": "Registro maestro de personas",
    "aplicabilidad_catalogo": "Bases, catálogos y registros maestros del proyecto.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): documentación del censo, elegibilidad, medidas, implementación y resultados de seguimiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 2, 6 y 7 — gestión de información, línea base, implementación y seguimiento."
  },
  {
    "orden": 352,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-01",
    "carpeta": "Base de datos",
    "codigo_documento": "PRY-PRE-01-D0352",
    "tipo_documental": "Registro maestro de predios",
    "aplicabilidad_catalogo": "Bases, catálogos y registros maestros del proyecto.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): documentación del censo, elegibilidad, medidas, implementación y resultados de seguimiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 2, 6 y 7 — gestión de información, línea base, implementación y seguimiento."
  },
  {
    "orden": 353,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-01",
    "carpeta": "Base de datos",
    "codigo_documento": "PRY-PRE-01-D0353",
    "tipo_documental": "Registro maestro de viviendas",
    "aplicabilidad_catalogo": "Bases, catálogos y registros maestros del proyecto.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): documentación del censo, elegibilidad, medidas, implementación y resultados de seguimiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 2, 6 y 7 — gestión de información, línea base, implementación y seguimiento."
  },
  {
    "orden": 354,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-01",
    "carpeta": "Base de datos",
    "codigo_documento": "PRY-PRE-01-D0354",
    "tipo_documental": "Respaldo autorizado de base de datos",
    "aplicabilidad_catalogo": "Bases, catálogos y registros maestros del proyecto.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): documentación del censo, elegibilidad, medidas, implementación y resultados de seguimiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 2, 6 y 7 — gestión de información, línea base, implementación y seguimiento."
  },
  {
    "orden": 355,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-02",
    "carpeta": "Estudios del PARRMS",
    "codigo_documento": "PRY-PRE-02-D0355",
    "tipo_documental": "Anexos de estudios",
    "aplicabilidad_catalogo": "Estudios y productos técnicos generales de la fase de preparación.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): planificación del reasentamiento, plan de acción, implementación, seguimiento y cierre.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): marco integral y Módulos 1–7."
  },
  {
    "orden": 356,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-02",
    "carpeta": "Estudios del PARRMS",
    "codigo_documento": "PRY-PRE-02-D0356",
    "tipo_documental": "Bases de apoyo de estudios",
    "aplicabilidad_catalogo": "Estudios y productos técnicos generales de la fase de preparación.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): planificación del reasentamiento, plan de acción, implementación, seguimiento y cierre.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): marco integral y Módulos 1–7."
  },
  {
    "orden": 357,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-02",
    "carpeta": "Estudios del PARRMS",
    "codigo_documento": "PRY-PRE-02-D0357",
    "tipo_documental": "Estudio de tenencia",
    "aplicabilidad_catalogo": "Estudios y productos técnicos generales de la fase de preparación.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): planificación del reasentamiento, plan de acción, implementación, seguimiento y cierre.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): marco integral y Módulos 1–7."
  },
  {
    "orden": 358,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-02",
    "carpeta": "Estudios del PARRMS",
    "codigo_documento": "PRY-PRE-02-D0358",
    "tipo_documental": "Informe de diagnóstico psicosocial",
    "aplicabilidad_catalogo": "Estudios y productos técnicos generales de la fase de preparación.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Sensitivo",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): planificación del reasentamiento, plan de acción, implementación, seguimiento y cierre.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): marco integral y Módulos 1–7."
  },
  {
    "orden": 359,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-02",
    "carpeta": "Estudios del PARRMS",
    "codigo_documento": "PRY-PRE-02-D0359",
    "tipo_documental": "Informe de levantamiento topográfico",
    "aplicabilidad_catalogo": "Estudios y productos técnicos generales de la fase de preparación.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): planificación del reasentamiento, plan de acción, implementación, seguimiento y cierre.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): marco integral y Módulos 1–7."
  },
  {
    "orden": 360,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-02",
    "carpeta": "Estudios del PARRMS",
    "codigo_documento": "PRY-PRE-02-D0360",
    "tipo_documental": "Línea Base Socioeconómica Detallada",
    "aplicabilidad_catalogo": "Estudios y productos técnicos generales de la fase de preparación.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Sensitivo",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): planificación del reasentamiento, plan de acción, implementación, seguimiento y cierre.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): marco integral y Módulos 1–7."
  },
  {
    "orden": 361,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-02",
    "carpeta": "Estudios del PARRMS",
    "codigo_documento": "PRY-PRE-02-D0361",
    "tipo_documental": "Mapas asociados a estudios",
    "aplicabilidad_catalogo": "Estudios y productos técnicos generales de la fase de preparación.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): planificación del reasentamiento, plan de acción, implementación, seguimiento y cierre.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): marco integral y Módulos 1–7."
  },
  {
    "orden": 362,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-02",
    "carpeta": "Estudios del PARRMS",
    "codigo_documento": "PRY-PRE-02-D0362",
    "tipo_documental": "Producto aprobado por ACP",
    "aplicabilidad_catalogo": "Estudios y productos técnicos generales de la fase de preparación.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): planificación del reasentamiento, plan de acción, implementación, seguimiento y cierre.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): marco integral y Módulos 1–7."
  },
  {
    "orden": 363,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-03",
    "carpeta": "Mecanismo CDQR",
    "codigo_documento": "PRY-PRE-03-D0363",
    "tipo_documental": "Acta relacionada con el caso",
    "aplicabilidad_catalogo": "Todos los casos y documentos de administración del mecanismo CDQR.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): mecanismo de quejas accesible, oportuno y apropiado para las personas afectadas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — diseño, registro, resolución y seguimiento del mecanismo de quejas."
  },
  {
    "orden": 364,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-03",
    "carpeta": "Mecanismo CDQR",
    "codigo_documento": "PRY-PRE-03-D0364",
    "tipo_documental": "Acuse de recibo",
    "aplicabilidad_catalogo": "Todos los casos y documentos de administración del mecanismo CDQR.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR + Catálogo legal PAC",
    "alias": "",
    "fuente_nd5": "ND5 (2012): mecanismo de quejas accesible, oportuno y apropiado para las personas afectadas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — diseño, registro, resolución y seguimiento del mecanismo de quejas."
  },
  {
    "orden": 365,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-03",
    "carpeta": "Mecanismo CDQR",
    "codigo_documento": "PRY-PRE-03-D0365",
    "tipo_documental": "Base de datos del mecanismo CDQR",
    "aplicabilidad_catalogo": "Todos los casos y documentos de administración del mecanismo CDQR.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): mecanismo de quejas accesible, oportuno y apropiado para las personas afectadas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — diseño, registro, resolución y seguimiento del mecanismo de quejas."
  },
  {
    "orden": 366,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-03",
    "carpeta": "Mecanismo CDQR",
    "codigo_documento": "PRY-PRE-03-D0366",
    "tipo_documental": "Documento de análisis o derivación del caso",
    "aplicabilidad_catalogo": "Todos los casos y documentos de administración del mecanismo CDQR.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "Documento de análisis o derivación",
    "fuente_nd5": "ND5 (2012): mecanismo de quejas accesible, oportuno y apropiado para las personas afectadas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — diseño, registro, resolución y seguimiento del mecanismo de quejas."
  },
  {
    "orden": 367,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-03",
    "carpeta": "Mecanismo CDQR",
    "codigo_documento": "PRY-PRE-03-D0367",
    "tipo_documental": "Documento de cierre del caso",
    "aplicabilidad_catalogo": "Todos los casos y documentos de administración del mecanismo CDQR.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): mecanismo de quejas accesible, oportuno y apropiado para las personas afectadas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — diseño, registro, resolución y seguimiento del mecanismo de quejas."
  },
  {
    "orden": 368,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-03",
    "carpeta": "Mecanismo CDQR",
    "codigo_documento": "PRY-PRE-03-D0368",
    "tipo_documental": "Formulario de recepción de caso",
    "aplicabilidad_catalogo": "Todos los casos y documentos de administración del mecanismo CDQR.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): mecanismo de quejas accesible, oportuno y apropiado para las personas afectadas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — diseño, registro, resolución y seguimiento del mecanismo de quejas."
  },
  {
    "orden": 369,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-03",
    "carpeta": "Mecanismo CDQR",
    "codigo_documento": "PRY-PRE-03-D0369",
    "tipo_documental": "Informe consolidado del mecanismo",
    "aplicabilidad_catalogo": "Todos los casos y documentos de administración del mecanismo CDQR.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): mecanismo de quejas accesible, oportuno y apropiado para las personas afectadas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — diseño, registro, resolución y seguimiento del mecanismo de quejas."
  },
  {
    "orden": 370,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-03",
    "carpeta": "Mecanismo CDQR",
    "codigo_documento": "PRY-PRE-03-D0370",
    "tipo_documental": "Registro general de consultas",
    "aplicabilidad_catalogo": "Todos los casos y documentos de administración del mecanismo CDQR.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): mecanismo de quejas accesible, oportuno y apropiado para las personas afectadas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — diseño, registro, resolución y seguimiento del mecanismo de quejas."
  },
  {
    "orden": 371,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-03",
    "carpeta": "Mecanismo CDQR",
    "codigo_documento": "PRY-PRE-03-D0371",
    "tipo_documental": "Registro general de denuncias",
    "aplicabilidad_catalogo": "Todos los casos y documentos de administración del mecanismo CDQR.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): mecanismo de quejas accesible, oportuno y apropiado para las personas afectadas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — diseño, registro, resolución y seguimiento del mecanismo de quejas."
  },
  {
    "orden": 372,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-03",
    "carpeta": "Mecanismo CDQR",
    "codigo_documento": "PRY-PRE-03-D0372",
    "tipo_documental": "Registro general de quejas",
    "aplicabilidad_catalogo": "Todos los casos y documentos de administración del mecanismo CDQR.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): mecanismo de quejas accesible, oportuno y apropiado para las personas afectadas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — diseño, registro, resolución y seguimiento del mecanismo de quejas."
  },
  {
    "orden": 373,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-03",
    "carpeta": "Mecanismo CDQR",
    "codigo_documento": "PRY-PRE-03-D0373",
    "tipo_documental": "Registro general de reclamos",
    "aplicabilidad_catalogo": "Todos los casos y documentos de administración del mecanismo CDQR.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): mecanismo de quejas accesible, oportuno y apropiado para las personas afectadas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — diseño, registro, resolución y seguimiento del mecanismo de quejas."
  },
  {
    "orden": 374,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-03",
    "carpeta": "Mecanismo CDQR",
    "codigo_documento": "PRY-PRE-03-D0374",
    "tipo_documental": "Resolución del caso",
    "aplicabilidad_catalogo": "Todos los casos y documentos de administración del mecanismo CDQR.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): mecanismo de quejas accesible, oportuno y apropiado para las personas afectadas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — diseño, registro, resolución y seguimiento del mecanismo de quejas."
  },
  {
    "orden": 375,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-03",
    "carpeta": "Mecanismo CDQR",
    "codigo_documento": "PRY-PRE-03-D0375",
    "tipo_documental": "Respuesta al solicitante",
    "aplicabilidad_catalogo": "Todos los casos y documentos de administración del mecanismo CDQR.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): mecanismo de quejas accesible, oportuno y apropiado para las personas afectadas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — diseño, registro, resolución y seguimiento del mecanismo de quejas."
  },
  {
    "orden": 376,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-04",
    "carpeta": "Predios, viviendas y hogares",
    "codigo_documento": "PRY-PRE-04-D0376",
    "tipo_documental": "Documento de corrección validada",
    "aplicabilidad_catalogo": "Relaciones técnicas y controles de consistencia entre unidades sociales, prediales y espaciales.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): documentación del censo, elegibilidad, medidas, implementación y resultados de seguimiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 2, 6 y 7 — gestión de información, línea base, implementación y seguimiento."
  },
  {
    "orden": 377,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-04",
    "carpeta": "Predios, viviendas y hogares",
    "codigo_documento": "PRY-PRE-04-D0377",
    "tipo_documental": "Informe de consistencia",
    "aplicabilidad_catalogo": "Relaciones técnicas y controles de consistencia entre unidades sociales, prediales y espaciales.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): documentación del censo, elegibilidad, medidas, implementación y resultados de seguimiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 2, 6 y 7 — gestión de información, línea base, implementación y seguimiento."
  },
  {
    "orden": 378,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-04",
    "carpeta": "Predios, viviendas y hogares",
    "codigo_documento": "PRY-PRE-04-D0378",
    "tipo_documental": "Informe de cruce geoespacial y censal",
    "aplicabilidad_catalogo": "Relaciones técnicas y controles de consistencia entre unidades sociales, prediales y espaciales.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): documentación del censo, elegibilidad, medidas, implementación y resultados de seguimiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 2, 6 y 7 — gestión de información, línea base, implementación y seguimiento."
  },
  {
    "orden": 379,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-04",
    "carpeta": "Predios, viviendas y hogares",
    "codigo_documento": "PRY-PRE-04-D0379",
    "tipo_documental": "Matriz de correspondencia de identificadores",
    "aplicabilidad_catalogo": "Relaciones técnicas y controles de consistencia entre unidades sociales, prediales y espaciales.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): documentación del censo, elegibilidad, medidas, implementación y resultados de seguimiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 2, 6 y 7 — gestión de información, línea base, implementación y seguimiento."
  },
  {
    "orden": 380,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-04",
    "carpeta": "Predios, viviendas y hogares",
    "codigo_documento": "PRY-PRE-04-D0380",
    "tipo_documental": "Registro de relación hogar-predio",
    "aplicabilidad_catalogo": "Relaciones técnicas y controles de consistencia entre unidades sociales, prediales y espaciales.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): documentación del censo, elegibilidad, medidas, implementación y resultados de seguimiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 2, 6 y 7 — gestión de información, línea base, implementación y seguimiento."
  },
  {
    "orden": 381,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-04",
    "carpeta": "Predios, viviendas y hogares",
    "codigo_documento": "PRY-PRE-04-D0381",
    "tipo_documental": "Registro de relación persona-hogar",
    "aplicabilidad_catalogo": "Relaciones técnicas y controles de consistencia entre unidades sociales, prediales y espaciales.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): documentación del censo, elegibilidad, medidas, implementación y resultados de seguimiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 2, 6 y 7 — gestión de información, línea base, implementación y seguimiento."
  },
  {
    "orden": 382,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-04",
    "carpeta": "Predios, viviendas y hogares",
    "codigo_documento": "PRY-PRE-04-D0382",
    "tipo_documental": "Registro de relación persona-predio",
    "aplicabilidad_catalogo": "Relaciones técnicas y controles de consistencia entre unidades sociales, prediales y espaciales.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): documentación del censo, elegibilidad, medidas, implementación y resultados de seguimiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 2, 6 y 7 — gestión de información, línea base, implementación y seguimiento."
  },
  {
    "orden": 383,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-04",
    "carpeta": "Predios, viviendas y hogares",
    "codigo_documento": "PRY-PRE-04-D0383",
    "tipo_documental": "Registro de relación predio-vivienda-hogar",
    "aplicabilidad_catalogo": "Relaciones técnicas y controles de consistencia entre unidades sociales, prediales y espaciales.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): documentación del censo, elegibilidad, medidas, implementación y resultados de seguimiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 2, 6 y 7 — gestión de información, línea base, implementación y seguimiento."
  },
  {
    "orden": 384,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-04",
    "carpeta": "Predios, viviendas y hogares",
    "codigo_documento": "PRY-PRE-04-D0384",
    "tipo_documental": "Registro técnico de hogares",
    "aplicabilidad_catalogo": "Relaciones técnicas y controles de consistencia entre unidades sociales, prediales y espaciales.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): documentación del censo, elegibilidad, medidas, implementación y resultados de seguimiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 2, 6 y 7 — gestión de información, línea base, implementación y seguimiento."
  },
  {
    "orden": 385,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-04",
    "carpeta": "Predios, viviendas y hogares",
    "codigo_documento": "PRY-PRE-04-D0385",
    "tipo_documental": "Reporte de duplicidades o inconsistencias",
    "aplicabilidad_catalogo": "Relaciones técnicas y controles de consistencia entre unidades sociales, prediales y espaciales.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): documentación del censo, elegibilidad, medidas, implementación y resultados de seguimiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 2, 6 y 7 — gestión de información, línea base, implementación y seguimiento."
  },
  {
    "orden": 386,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-04",
    "carpeta": "Predios, viviendas y hogares",
    "codigo_documento": "PRY-PRE-04-D0386",
    "tipo_documental": "Reporte de registros sin relación",
    "aplicabilidad_catalogo": "Relaciones técnicas y controles de consistencia entre unidades sociales, prediales y espaciales.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): documentación del censo, elegibilidad, medidas, implementación y resultados de seguimiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 2, 6 y 7 — gestión de información, línea base, implementación y seguimiento."
  },
  {
    "orden": 387,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-04",
    "carpeta": "Predios, viviendas y hogares",
    "codigo_documento": "PRY-PRE-04-D0387",
    "tipo_documental": "Versión consolidada de relaciones",
    "aplicabilidad_catalogo": "Relaciones técnicas y controles de consistencia entre unidades sociales, prediales y espaciales.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): documentación del censo, elegibilidad, medidas, implementación y resultados de seguimiento.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 2, 6 y 7 — gestión de información, línea base, implementación y seguimiento."
  },
  {
    "orden": 388,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-05",
    "carpeta": "Proceso del PARRMS",
    "codigo_documento": "PRY-PRE-05-D0388",
    "tipo_documental": "Archivo fotográfico del proceso",
    "aplicabilidad_catalogo": "Documentos transversales de planificación, participación y diseño del PARRMS.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): planificación del reasentamiento, plan de acción, implementación, seguimiento y cierre.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): marco integral y Módulos 1–7."
  },
  {
    "orden": 389,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-05",
    "carpeta": "Proceso del PARRMS",
    "codigo_documento": "PRY-PRE-05-D0389",
    "tipo_documental": "Base de actores clave",
    "aplicabilidad_catalogo": "Documentos transversales de planificación, participación y diseño del PARRMS.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): planificación del reasentamiento, plan de acción, implementación, seguimiento y cierre.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): marco integral y Módulos 1–7."
  },
  {
    "orden": 390,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-05",
    "carpeta": "Proceso del PARRMS",
    "codigo_documento": "PRY-PRE-05-D0390",
    "tipo_documental": "Cartografía del proceso",
    "aplicabilidad_catalogo": "Documentos transversales de planificación, participación y diseño del PARRMS.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): planificación del reasentamiento, plan de acción, implementación, seguimiento y cierre.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): marco integral y Módulos 1–7."
  },
  {
    "orden": 391,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-05",
    "carpeta": "Proceso del PARRMS",
    "codigo_documento": "PRY-PRE-05-D0391",
    "tipo_documental": "Diseño de vivienda",
    "aplicabilidad_catalogo": "Documentos transversales de planificación, participación y diseño del PARRMS.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): planificación del reasentamiento, plan de acción, implementación, seguimiento y cierre.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): marco integral y Módulos 1–7."
  },
  {
    "orden": 392,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-05",
    "carpeta": "Proceso del PARRMS",
    "codigo_documento": "PRY-PRE-05-D0392",
    "tipo_documental": "Documento de conformación de la plataforma de participación",
    "aplicabilidad_catalogo": "Documentos transversales de planificación, participación y diseño del PARRMS.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): planificación del reasentamiento, plan de acción, implementación, seguimiento y cierre.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): marco integral y Módulos 1–7."
  },
  {
    "orden": 393,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-05",
    "carpeta": "Proceso del PARRMS",
    "codigo_documento": "PRY-PRE-05-D0393",
    "tipo_documental": "Evidencia de actividad por zona o comunidad",
    "aplicabilidad_catalogo": "Documentos transversales de planificación, participación y diseño del PARRMS.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): planificación del reasentamiento, plan de acción, implementación, seguimiento y cierre.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): marco integral y Módulos 1–7."
  },
  {
    "orden": 394,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-05",
    "carpeta": "Proceso del PARRMS",
    "codigo_documento": "PRY-PRE-05-D0394",
    "tipo_documental": "Informe de participación",
    "aplicabilidad_catalogo": "Documentos transversales de planificación, participación y diseño del PARRMS.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): planificación del reasentamiento, plan de acción, implementación, seguimiento y cierre.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): marco integral y Módulos 1–7."
  },
  {
    "orden": 395,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-05",
    "carpeta": "Proceso del PARRMS",
    "codigo_documento": "PRY-PRE-05-D0395",
    "tipo_documental": "Informe, acta o minuta de mesa de concertación",
    "aplicabilidad_catalogo": "Documentos transversales de planificación, participación y diseño del PARRMS.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): planificación del reasentamiento, plan de acción, implementación, seguimiento y cierre.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): marco integral y Módulos 1–7."
  },
  {
    "orden": 396,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-05",
    "carpeta": "Proceso del PARRMS",
    "codigo_documento": "PRY-PRE-05-D0396",
    "tipo_documental": "Plan de Acción de Reasentamiento y Restablecimiento de Medios de Subsistencia",
    "aplicabilidad_catalogo": "Documentos transversales de planificación, participación y diseño del PARRMS.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): planificación del reasentamiento, plan de acción, implementación, seguimiento y cierre.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): marco integral y Módulos 1–7."
  },
  {
    "orden": 397,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-05",
    "carpeta": "Proceso del PARRMS",
    "codigo_documento": "PRY-PRE-05-D0397",
    "tipo_documental": "Presentación o material informativo",
    "aplicabilidad_catalogo": "Documentos transversales de planificación, participación y diseño del PARRMS.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): planificación del reasentamiento, plan de acción, implementación, seguimiento y cierre.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): marco integral y Módulos 1–7."
  },
  {
    "orden": 398,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-05",
    "carpeta": "Proceso del PARRMS",
    "codigo_documento": "PRY-PRE-05-D0398",
    "tipo_documental": "Registro fotográfico",
    "aplicabilidad_catalogo": "Documentos transversales de planificación, participación y diseño del PARRMS.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): planificación del reasentamiento, plan de acción, implementación, seguimiento y cierre.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): marco integral y Módulos 1–7."
  },
  {
    "orden": 399,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-05",
    "carpeta": "Proceso del PARRMS",
    "codigo_documento": "PRY-PRE-05-D0399",
    "tipo_documental": "Resultado o documento técnico de sitio de reasentamiento",
    "aplicabilidad_catalogo": "Documentos transversales de planificación, participación y diseño del PARRMS.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): planificación del reasentamiento, plan de acción, implementación, seguimiento y cierre.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): marco integral y Módulos 1–7."
  },
  {
    "orden": 400,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-05",
    "carpeta": "Proceso del PARRMS",
    "codigo_documento": "PRY-PRE-05-D0400",
    "tipo_documental": "Sistematización del proceso del PARRMS",
    "aplicabilidad_catalogo": "Documentos transversales de planificación, participación y diseño del PARRMS.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): planificación del reasentamiento, plan de acción, implementación, seguimiento y cierre.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): marco integral y Módulos 1–7."
  },
  {
    "orden": 401,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-06",
    "carpeta": "Proceso valuatorio",
    "codigo_documento": "PRY-PRE-06-D0401",
    "tipo_documental": "Base de resultados valuatorios",
    "aplicabilidad_catalogo": "Documentos consolidados y metodológicos del proceso valuatorio.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): compensación a costo de reposición y documentación de la valoración de tierras y activos.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 4 — valoración, costo de reposición, compensación y acuerdos."
  },
  {
    "orden": 402,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-06",
    "carpeta": "Proceso valuatorio",
    "codigo_documento": "PRY-PRE-06-D0402",
    "tipo_documental": "Informe consolidado de avalúos de mejoras o activos",
    "aplicabilidad_catalogo": "Documentos consolidados y metodológicos del proceso valuatorio.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): compensación a costo de reposición y documentación de la valoración de tierras y activos.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 4 — valoración, costo de reposición, compensación y acuerdos."
  },
  {
    "orden": 403,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-06",
    "carpeta": "Proceso valuatorio",
    "codigo_documento": "PRY-PRE-06-D0403",
    "tipo_documental": "Informe consolidado de avalúos de predios",
    "aplicabilidad_catalogo": "Documentos consolidados y metodológicos del proceso valuatorio.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): compensación a costo de reposición y documentación de la valoración de tierras y activos.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 4 — valoración, costo de reposición, compensación y acuerdos."
  },
  {
    "orden": 404,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-06",
    "carpeta": "Proceso valuatorio",
    "codigo_documento": "PRY-PRE-06-D0404",
    "tipo_documental": "Informe consolidado de avalúos de viviendas",
    "aplicabilidad_catalogo": "Documentos consolidados y metodológicos del proceso valuatorio.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): compensación a costo de reposición y documentación de la valoración de tierras y activos.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 4 — valoración, costo de reposición, compensación y acuerdos."
  },
  {
    "orden": 405,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-06",
    "carpeta": "Proceso valuatorio",
    "codigo_documento": "PRY-PRE-06-D0405",
    "tipo_documental": "Informe general de avalúos",
    "aplicabilidad_catalogo": "Documentos consolidados y metodológicos del proceso valuatorio.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): compensación a costo de reposición y documentación de la valoración de tierras y activos.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 4 — valoración, costo de reposición, compensación y acuerdos."
  },
  {
    "orden": 406,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-06",
    "carpeta": "Proceso valuatorio",
    "codigo_documento": "PRY-PRE-06-D0406",
    "tipo_documental": "Matriz de análisis valuatorio",
    "aplicabilidad_catalogo": "Documentos consolidados y metodológicos del proceso valuatorio.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): compensación a costo de reposición y documentación de la valoración de tierras y activos.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 4 — valoración, costo de reposición, compensación y acuerdos."
  },
  {
    "orden": 407,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-06",
    "carpeta": "Proceso valuatorio",
    "codigo_documento": "PRY-PRE-06-D0407",
    "tipo_documental": "Metodología y criterios técnicos de avalúos",
    "aplicabilidad_catalogo": "Documentos consolidados y metodológicos del proceso valuatorio.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): compensación a costo de reposición y documentación de la valoración de tierras y activos.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 4 — valoración, costo de reposición, compensación y acuerdos."
  },
  {
    "orden": 408,
    "nivel": "Proyecto",
    "fase": "Pre-reasentamiento",
    "codigo_carpeta": "PRY-PRE-06",
    "carpeta": "Proceso valuatorio",
    "codigo_documento": "PRY-PRE-06-D0408",
    "tipo_documental": "Registro fotográfico general",
    "aplicabilidad_catalogo": "Documentos consolidados y metodológicos del proceso valuatorio.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): compensación a costo de reposición y documentación de la valoración de tierras y activos.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 4 — valoración, costo de reposición, compensación y acuerdos."
  },
  {
    "orden": 409,
    "nivel": "Proyecto",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "PRY-DUR-01",
    "carpeta": "Documentos operativos",
    "codigo_documento": "PRY-DUR-01-D0409",
    "tipo_documental": "Acta o minuta de coordinación",
    "aplicabilidad_catalogo": "Documentos generales de implementación del reasentamiento.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): planificación del reasentamiento, plan de acción, implementación, seguimiento y cierre.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): marco integral y Módulos 1–7."
  },
  {
    "orden": 410,
    "nivel": "Proyecto",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "PRY-DUR-01",
    "carpeta": "Documentos operativos",
    "codigo_documento": "PRY-DUR-01-D0410",
    "tipo_documental": "Cronograma operativo",
    "aplicabilidad_catalogo": "Documentos generales de implementación del reasentamiento.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): planificación del reasentamiento, plan de acción, implementación, seguimiento y cierre.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): marco integral y Módulos 1–7."
  },
  {
    "orden": 411,
    "nivel": "Proyecto",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "PRY-DUR-01",
    "carpeta": "Documentos operativos",
    "codigo_documento": "PRY-DUR-01-D0411",
    "tipo_documental": "Evidencia fotográfica de actividades",
    "aplicabilidad_catalogo": "Documentos generales de implementación del reasentamiento.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): planificación del reasentamiento, plan de acción, implementación, seguimiento y cierre.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): marco integral y Módulos 1–7."
  },
  {
    "orden": 412,
    "nivel": "Proyecto",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "PRY-DUR-01",
    "carpeta": "Documentos operativos",
    "codigo_documento": "PRY-DUR-01-D0412",
    "tipo_documental": "Informe de avance",
    "aplicabilidad_catalogo": "Documentos generales de implementación del reasentamiento.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): planificación del reasentamiento, plan de acción, implementación, seguimiento y cierre.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): marco integral y Módulos 1–7."
  },
  {
    "orden": 413,
    "nivel": "Proyecto",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "PRY-DUR-01",
    "carpeta": "Documentos operativos",
    "codigo_documento": "PRY-DUR-01-D0413",
    "tipo_documental": "Informe de compensaciones",
    "aplicabilidad_catalogo": "Documentos generales de implementación del reasentamiento.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): planificación del reasentamiento, plan de acción, implementación, seguimiento y cierre.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): marco integral y Módulos 1–7."
  },
  {
    "orden": 414,
    "nivel": "Proyecto",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "PRY-DUR-01",
    "carpeta": "Documentos operativos",
    "codigo_documento": "PRY-DUR-01-D0414",
    "tipo_documental": "Informe de entrega",
    "aplicabilidad_catalogo": "Documentos generales de implementación del reasentamiento.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): planificación del reasentamiento, plan de acción, implementación, seguimiento y cierre.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): marco integral y Módulos 1–7."
  },
  {
    "orden": 415,
    "nivel": "Proyecto",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "PRY-DUR-01",
    "carpeta": "Documentos operativos",
    "codigo_documento": "PRY-DUR-01-D0415",
    "tipo_documental": "Informe de traslado",
    "aplicabilidad_catalogo": "Documentos generales de implementación del reasentamiento.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): planificación del reasentamiento, plan de acción, implementación, seguimiento y cierre.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): marco integral y Módulos 1–7."
  },
  {
    "orden": 416,
    "nivel": "Proyecto",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "PRY-DUR-01",
    "carpeta": "Documentos operativos",
    "codigo_documento": "PRY-DUR-01-D0416",
    "tipo_documental": "Matriz de seguimiento operativo",
    "aplicabilidad_catalogo": "Documentos generales de implementación del reasentamiento.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): planificación del reasentamiento, plan de acción, implementación, seguimiento y cierre.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): marco integral y Módulos 1–7."
  },
  {
    "orden": 417,
    "nivel": "Proyecto",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "PRY-DUR-01",
    "carpeta": "Documentos operativos",
    "codigo_documento": "PRY-DUR-01-D0417",
    "tipo_documental": "Plan operativo",
    "aplicabilidad_catalogo": "Documentos generales de implementación del reasentamiento.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): planificación del reasentamiento, plan de acción, implementación, seguimiento y cierre.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): marco integral y Módulos 1–7."
  },
  {
    "orden": 418,
    "nivel": "Proyecto",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "PRY-DUR-01",
    "carpeta": "Documentos operativos",
    "codigo_documento": "PRY-DUR-01-D0418",
    "tipo_documental": "Registro de actividades",
    "aplicabilidad_catalogo": "Documentos generales de implementación del reasentamiento.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): planificación del reasentamiento, plan de acción, implementación, seguimiento y cierre.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): marco integral y Módulos 1–7."
  },
  {
    "orden": 419,
    "nivel": "Proyecto",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "PRY-DUR-01",
    "carpeta": "Documentos operativos",
    "codigo_documento": "PRY-DUR-01-D0419",
    "tipo_documental": "Registro de incidencias",
    "aplicabilidad_catalogo": "Documentos generales de implementación del reasentamiento.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): planificación del reasentamiento, plan de acción, implementación, seguimiento y cierre.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): marco integral y Módulos 1–7."
  },
  {
    "orden": 420,
    "nivel": "Proyecto",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "PRY-DUR-01",
    "carpeta": "Documentos operativos",
    "codigo_documento": "PRY-DUR-01-D0420",
    "tipo_documental": "Reporte operativo",
    "aplicabilidad_catalogo": "Documentos generales de implementación del reasentamiento.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): planificación del reasentamiento, plan de acción, implementación, seguimiento y cierre.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): marco integral y Módulos 1–7."
  },
  {
    "orden": 421,
    "nivel": "Proyecto",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "PRY-DUR-02",
    "carpeta": "Informes de seguimiento",
    "codigo_documento": "PRY-DUR-02-D0421",
    "tipo_documental": "Informe de avance del reasentamiento",
    "aplicabilidad_catalogo": "Seguimiento consolidado del proyecto durante la implementación.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 422,
    "nivel": "Proyecto",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "PRY-DUR-02",
    "carpeta": "Informes de seguimiento",
    "codigo_documento": "PRY-DUR-02-D0422",
    "tipo_documental": "Informe de seguimiento de compensaciones",
    "aplicabilidad_catalogo": "Seguimiento consolidado del proyecto durante la implementación.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Confidencial",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 423,
    "nivel": "Proyecto",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "PRY-DUR-02",
    "carpeta": "Informes de seguimiento",
    "codigo_documento": "PRY-DUR-02-D0423",
    "tipo_documental": "Informe de seguimiento de medios de vida",
    "aplicabilidad_catalogo": "Seguimiento consolidado del proyecto durante la implementación.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 424,
    "nivel": "Proyecto",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "PRY-DUR-02",
    "carpeta": "Informes de seguimiento",
    "codigo_documento": "PRY-DUR-02-D0424",
    "tipo_documental": "Informe de seguimiento psicosocial",
    "aplicabilidad_catalogo": "Seguimiento consolidado del proyecto durante la implementación.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Sensitivo",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 425,
    "nivel": "Proyecto",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "PRY-DUR-02",
    "carpeta": "Informes de seguimiento",
    "codigo_documento": "PRY-DUR-02-D0425",
    "tipo_documental": "Informe de seguimiento social",
    "aplicabilidad_catalogo": "Seguimiento consolidado del proyecto durante la implementación.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 426,
    "nivel": "Proyecto",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "PRY-DUR-02",
    "carpeta": "Informes de seguimiento",
    "codigo_documento": "PRY-DUR-02-D0426",
    "tipo_documental": "Informe de seguimiento territorial",
    "aplicabilidad_catalogo": "Seguimiento consolidado del proyecto durante la implementación.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 427,
    "nivel": "Proyecto",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "PRY-DUR-02",
    "carpeta": "Informes de seguimiento",
    "codigo_documento": "PRY-DUR-02-D0427",
    "tipo_documental": "Informe mensual de seguimiento",
    "aplicabilidad_catalogo": "Seguimiento consolidado del proyecto durante la implementación.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 428,
    "nivel": "Proyecto",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "PRY-DUR-02",
    "carpeta": "Informes de seguimiento",
    "codigo_documento": "PRY-DUR-02-D0428",
    "tipo_documental": "Informe semestral de seguimiento",
    "aplicabilidad_catalogo": "Seguimiento consolidado del proyecto durante la implementación.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 429,
    "nivel": "Proyecto",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "PRY-DUR-02",
    "carpeta": "Informes de seguimiento",
    "codigo_documento": "PRY-DUR-02-D0429",
    "tipo_documental": "Informe trimestral de seguimiento",
    "aplicabilidad_catalogo": "Seguimiento consolidado del proyecto durante la implementación.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 430,
    "nivel": "Proyecto",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "PRY-DUR-02",
    "carpeta": "Informes de seguimiento",
    "codigo_documento": "PRY-DUR-02-D0430",
    "tipo_documental": "Matriz de indicadores",
    "aplicabilidad_catalogo": "Seguimiento consolidado del proyecto durante la implementación.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 431,
    "nivel": "Proyecto",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "PRY-DUR-02",
    "carpeta": "Informes de seguimiento",
    "codigo_documento": "PRY-DUR-02-D0431",
    "tipo_documental": "Reporte del tablero de control",
    "aplicabilidad_catalogo": "Seguimiento consolidado del proyecto durante la implementación.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 432,
    "nivel": "Proyecto",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "PRY-DUR-03",
    "carpeta": "Mecanismo CDQR",
    "codigo_documento": "PRY-DUR-03-D0432",
    "tipo_documental": "Base actualizada de casos",
    "aplicabilidad_catalogo": "Casos CDQR recibidos o gestionados durante la implementación.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): mecanismo de quejas accesible, oportuno y apropiado para las personas afectadas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — diseño, registro, resolución y seguimiento del mecanismo de quejas."
  },
  {
    "orden": 433,
    "nivel": "Proyecto",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "PRY-DUR-03",
    "carpeta": "Mecanismo CDQR",
    "codigo_documento": "PRY-DUR-03-D0433",
    "tipo_documental": "Informe periódico del mecanismo",
    "aplicabilidad_catalogo": "Casos CDQR recibidos o gestionados durante la implementación.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): mecanismo de quejas accesible, oportuno y apropiado para las personas afectadas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — diseño, registro, resolución y seguimiento del mecanismo de quejas."
  },
  {
    "orden": 434,
    "nivel": "Proyecto",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "PRY-DUR-03",
    "carpeta": "Mecanismo CDQR",
    "codigo_documento": "PRY-DUR-03-D0434",
    "tipo_documental": "Registro de nuevos casos",
    "aplicabilidad_catalogo": "Casos CDQR recibidos o gestionados durante la implementación.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): mecanismo de quejas accesible, oportuno y apropiado para las personas afectadas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — diseño, registro, resolución y seguimiento del mecanismo de quejas."
  },
  {
    "orden": 435,
    "nivel": "Proyecto",
    "fase": "Durante el reasentamiento",
    "codigo_carpeta": "PRY-DUR-03",
    "carpeta": "Mecanismo CDQR",
    "codigo_documento": "PRY-DUR-03-D0435",
    "tipo_documental": "Resolución",
    "aplicabilidad_catalogo": "Casos CDQR recibidos o gestionados durante la implementación.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): mecanismo de quejas accesible, oportuno y apropiado para las personas afectadas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulo 3 — diseño, registro, resolución y seguimiento del mecanismo de quejas."
  },
  {
    "orden": 436,
    "nivel": "Proyecto",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "PRY-POS-01",
    "carpeta": "Documentos de cierre",
    "codigo_documento": "PRY-POS-01-D0436",
    "tipo_documental": "Acta de cierre del proyecto",
    "aplicabilidad_catalogo": "Cierre, evaluación, auditoría y transferencia institucional del proyecto.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 437,
    "nivel": "Proyecto",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "PRY-POS-01",
    "carpeta": "Documentos de cierre",
    "codigo_documento": "PRY-POS-01-D0437",
    "tipo_documental": "Archivo fotográfico final",
    "aplicabilidad_catalogo": "Cierre, evaluación, auditoría y transferencia institucional del proyecto.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 438,
    "nivel": "Proyecto",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "PRY-POS-01",
    "carpeta": "Documentos de cierre",
    "codigo_documento": "PRY-POS-01-D0438",
    "tipo_documental": "Auditoría ex post",
    "aplicabilidad_catalogo": "Cierre, evaluación, auditoría y transferencia institucional del proyecto.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 439,
    "nivel": "Proyecto",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "PRY-POS-01",
    "carpeta": "Documentos de cierre",
    "codigo_documento": "PRY-POS-01-D0439",
    "tipo_documental": "Auditoría final",
    "aplicabilidad_catalogo": "Cierre, evaluación, auditoría y transferencia institucional del proyecto.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 440,
    "nivel": "Proyecto",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "PRY-POS-01",
    "carpeta": "Documentos de cierre",
    "codigo_documento": "PRY-POS-01-D0440",
    "tipo_documental": "Base maestra final",
    "aplicabilidad_catalogo": "Cierre, evaluación, auditoría y transferencia institucional del proyecto.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 441,
    "nivel": "Proyecto",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "PRY-POS-01",
    "carpeta": "Documentos de cierre",
    "codigo_documento": "PRY-POS-01-D0441",
    "tipo_documental": "Cartografía final",
    "aplicabilidad_catalogo": "Cierre, evaluación, auditoría y transferencia institucional del proyecto.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 442,
    "nivel": "Proyecto",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "PRY-POS-01",
    "carpeta": "Documentos de cierre",
    "codigo_documento": "PRY-POS-01-D0442",
    "tipo_documental": "Certificación de cierre",
    "aplicabilidad_catalogo": "Cierre, evaluación, auditoría y transferencia institucional del proyecto.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 443,
    "nivel": "Proyecto",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "PRY-POS-01",
    "carpeta": "Documentos de cierre",
    "codigo_documento": "PRY-POS-01-D0443",
    "tipo_documental": "Documento de transferencia a ACP",
    "aplicabilidad_catalogo": "Cierre, evaluación, auditoría y transferencia institucional del proyecto.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 444,
    "nivel": "Proyecto",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "PRY-POS-01",
    "carpeta": "Documentos de cierre",
    "codigo_documento": "PRY-POS-01-D0444",
    "tipo_documental": "Evaluación ex post",
    "aplicabilidad_catalogo": "Cierre, evaluación, auditoría y transferencia institucional del proyecto.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 445,
    "nivel": "Proyecto",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "PRY-POS-01",
    "carpeta": "Documentos de cierre",
    "codigo_documento": "PRY-POS-01-D0445",
    "tipo_documental": "Informe de cierre del PARRMS",
    "aplicabilidad_catalogo": "Cierre, evaluación, auditoría y transferencia institucional del proyecto.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 446,
    "nivel": "Proyecto",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "PRY-POS-01",
    "carpeta": "Documentos de cierre",
    "codigo_documento": "PRY-POS-01-D0446",
    "tipo_documental": "Informe de cumplimiento",
    "aplicabilidad_catalogo": "Cierre, evaluación, auditoría y transferencia institucional del proyecto.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 447,
    "nivel": "Proyecto",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "PRY-POS-01",
    "carpeta": "Documentos de cierre",
    "codigo_documento": "PRY-POS-01-D0447",
    "tipo_documental": "Informe de entrega documental",
    "aplicabilidad_catalogo": "Cierre, evaluación, auditoría y transferencia institucional del proyecto.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 448,
    "nivel": "Proyecto",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "PRY-POS-01",
    "carpeta": "Documentos de cierre",
    "codigo_documento": "PRY-POS-01-D0448",
    "tipo_documental": "Informe de evaluación final",
    "aplicabilidad_catalogo": "Cierre, evaluación, auditoría y transferencia institucional del proyecto.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 449,
    "nivel": "Proyecto",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "PRY-POS-01",
    "carpeta": "Documentos de cierre",
    "codigo_documento": "PRY-POS-01-D0449",
    "tipo_documental": "Informe final de indicadores",
    "aplicabilidad_catalogo": "Cierre, evaluación, auditoría y transferencia institucional del proyecto.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 450,
    "nivel": "Proyecto",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "PRY-POS-01",
    "carpeta": "Documentos de cierre",
    "codigo_documento": "PRY-POS-01-D0450",
    "tipo_documental": "Informe final de reasentamiento",
    "aplicabilidad_catalogo": "Cierre, evaluación, auditoría y transferencia institucional del proyecto.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  },
  {
    "orden": 451,
    "nivel": "Proyecto",
    "fase": "Post-reasentamiento",
    "codigo_carpeta": "PRY-POS-01",
    "carpeta": "Documentos de cierre",
    "codigo_documento": "PRY-POS-01-D0451",
    "tipo_documental": "Informe final de restablecimiento de medios de vida",
    "aplicabilidad_catalogo": "Cierre, evaluación, auditoría y transferencia institucional del proyecto.",
    "niveles_relacionados": "Todos los niveles",
    "llaves_relacion": "id_proyecto",
    "confidencialidad": "Uso interno",
    "activo": "Sí",
    "origen": "SIR",
    "alias": "",
    "fuente_nd5": "ND5 (2012): seguimiento, evaluación, auditoría de cierre y medidas correctivas.",
    "fuente_guia_ifc": "IFC Good Practice Handbook (2023): Módulos 6 y 7 — implementación, seguimiento, evaluación y auditoría de cierre."
  }
]


def catalogo_df() -> pd.DataFrame:
    """Devuelve únicamente los tipos documentales activos."""
    df = pd.DataFrame(CATALOGO_DOCUMENTAL)
    if df.empty:
        return df
    return df[df["activo"].astype(str).str.lower().eq("sí")].copy()


# ============================================================
# 3. DATOS MAESTROS SIMULADOS
# ============================================================

def crear_maestros_referencia() -> dict[str, pd.DataFrame]:
    """
    Simula las entidades que en producción serán consultadas desde
    los módulos maestros o desde una base de datos institucional.
    """
    lugares = pd.DataFrame([
        {"id_lugar_poblado": "LPO-001", "nombre": "Nueva Esperanza", "zona": "Zona 1"},
        {"id_lugar_poblado": "LPO-002", "nombre": "El Progreso", "zona": "Zona 1"},
        {"id_lugar_poblado": "LPO-003", "nombre": "Santa Rosa", "zona": "Zona 2"},
        {"id_lugar_poblado": "LPO-004", "nombre": "Los Pinos", "zona": "Zona 3"},
        {"id_lugar_poblado": "LPO-005", "nombre": "Río Claro", "zona": "Zona 3"},
    ])

    hogares = []
    personas = []
    personas_no_residentes = []
    predios = []
    viviendas = []
    activos = []

    nombres = [
        "María López", "Carlos Mendoza", "Rosa Martínez", "José Pérez",
        "Ana Rodríguez", "Luis García", "Elena Torres", "Miguel Castillo",
        "Carmen Díaz", "Roberto Herrera",
    ]

    for i, nombre in enumerate(nombres, start=1):
        id_hogar = f"HOG-{i:04d}"
        id_lugar = f"LPO-{((i - 1) % 5) + 1:03d}"
        id_predio = f"PRE-{i:04d}"
        id_vivienda = f"VIV-{i:04d}"

        hogares.append({
            "id_hogar": id_hogar,
            "nombre": nombre,
            "id_lugar_poblado": id_lugar,
            "codigo_campo": f"PAC-HOG-{i:03d}",
        })
        personas.append({
            "id_persona": f"PER-{i:04d}",
            "id_hogar": id_hogar,
            "nombre": nombre,
            "documento_identidad": f"8-{100+i}-{200+i}",
        })
        if i <= 5:
            personas.append({
                "id_persona": f"PER-{i+10:04d}",
                "id_hogar": id_hogar,
                "nombre": f"Integrante {i} {nombre.split()[-1]}",
                "documento_identidad": f"8-{300+i}-{400+i}",
            })

        predios.append({
            "id_predio": id_predio,
            "id_hogar": id_hogar,
            "id_lugar_poblado": id_lugar,
            "referencia": f"Predio de referencia {i}",
        })
        viviendas.append({
            "id_vivienda": id_vivienda,
            "id_predio": id_predio,
            "id_hogar": id_hogar,
            "referencia": f"Vivienda {i}",
        })
        activos.append({
            "id_activo": f"ACT-{i:04d}",
            "id_predio": id_predio,
            "id_hogar": id_hogar,
            "tipo_activo": "Mejora",
        })

    for i in range(1, 6):
        personas_no_residentes.append({
            "id_persona_no_residente": f"PNR-{i:04d}",
            "id_persona": f"PER-NR-{i:04d}",
            "nombre": f"Persona no residente {i}",
            "id_predio": f"PRE-{i:04d}",
            "id_lugar_poblado": f"LPO-{i:03d}",
        })

    organizaciones = pd.DataFrame([
        {
            "id_organizacion": "ORG-001",
            "nombre": "Comité Comunitario Nueva Esperanza",
            "tipo": "Comunitaria",
            "id_lugar_poblado": "LPO-001",
        },
        {
            "id_organizacion": "ORG-002",
            "nombre": "Asociación Productiva Río Claro",
            "tipo": "Productiva",
            "id_lugar_poblado": "LPO-005",
        },
    ])

    hogares_sin_censo = pd.DataFrame([
        {
            "id_registro_sin_censo": "HSC-001",
            "referencia": "Predio visitado sin ocupantes",
            "id_lugar_poblado": "LPO-002",
            "id_predio": "PRE-SC-001",
            "estado_identificacion": "Ausente",
        },
        {
            "id_registro_sin_censo": "HSC-002",
            "referencia": "Caso con rechazo al censo",
            "id_lugar_poblado": "LPO-004",
            "id_predio": "PRE-SC-002",
            "estado_identificacion": "Rechazo",
        },
    ])

    proyectos = pd.DataFrame([
        {
            "id_proyecto": "PRY-PARRMS-001",
            "nombre": "Plan de Reasentamiento y Restablecimiento de Medios de Subsistencia",
            "estado": "En ejecución",
        }
    ])

    return {
        "personas": pd.DataFrame(personas),
        "hogares": pd.DataFrame(hogares),
        "personas_no_residentes": pd.DataFrame(personas_no_residentes),
        "organizaciones": organizaciones,
        "lugares_poblados": lugares,
        "hogares_sin_censo": hogares_sin_censo,
        "proyectos": proyectos,
        "predios": pd.DataFrame(predios),
        "viviendas": pd.DataFrame(viviendas),
        "activos": pd.DataFrame(activos),
    }


# ============================================================
# 4. MODELO DE DATOS OPERATIVO
# ============================================================

COLUMNAS = {
    "expedientes": [
        "id_expediente", "nivel", "id_entidad_principal", "nombre_entidad",
        "fecha_apertura", "responsable_expediente", "estado_expediente",
        "porcentaje_completitud", "observaciones",
        "fecha_creacion", "fecha_actualizacion", "usuario_actualizacion",
    ],
    "documentos": [
        "id_documento", "id_serie_documental", "id_documento_padre",
        "tipo_registro", "es_version_vigente", "token_transaccion",
        "id_expediente_principal", "nivel_principal", "id_entidad_principal",
        "fase", "codigo_carpeta", "carpeta", "codigo_documento",
        "tipo_documental", "aplicabilidad", "justificacion_no_aplica",
        "confidencialidad", "nombre_archivo", "ruta_archivo",
        "hash_documento", "fecha_documento", "fecha_carga",
        "tiene_vigencia", "fecha_vencimiento", "estado_vigencia",
        "estado_carga", "usuario_carga", "usuario_revisor_asignado",
        "estado_revision", "confirmado", "version",
        "observaciones_carga",
        "fecha_creacion", "fecha_actualizacion", "usuario_actualizacion",
    ],
    "relaciones_documento": [
        "id_relacion", "id_documento", "id_serie_documental",
        "tipo_entidad", "id_entidad", "es_relacion_principal",
        "fecha_relacion", "usuario_relacion",
    ],
    "revisiones": [
        "id_revision", "id_documento", "usuario_revisor",
        "fecha_revision", "resultado_revision", "observaciones_revision",
        "requiere_subsanacion", "fecha_subsanacion",
        "fecha_creacion", "fecha_actualizacion",
    ],
    "checklist": [
        "id_checklist", "id_expediente", "nivel", "id_entidad_principal",
        "fase", "codigo_carpeta", "carpeta", "codigo_documento",
        "tipo_documental", "aplicabilidad", "justificacion_no_aplica",
        "id_documento_asociado", "estado_carga", "estado_revision",
        "estado_vigencia", "cumple", "fecha_actualizacion",
    ],
}


def df_vacio(nombre: str) -> pd.DataFrame:
    return pd.DataFrame(columns=COLUMNAS[nombre])


def asegurar_columnas(data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    salida = {}
    for nombre, columnas in COLUMNAS.items():
        df = data.get(nombre, df_vacio(nombre)).copy()
        for col in columnas:
            if col not in df.columns:
                df[col] = ""
        salida[nombre] = df[columnas]
    return salida


# ============================================================
# 5. MEMORIA, MIGRACIÓN Y PERSISTENCIA
# ============================================================

def serializar(valor: Any) -> Any:
    if isinstance(valor, (date, datetime)):
        return valor.isoformat()
    if isinstance(valor, float) and pd.isna(valor):
        return None
    return valor


def data_a_json(data: dict[str, pd.DataFrame]) -> dict[str, list[dict[str, Any]]]:
    return {
        nombre: [
            {col: serializar(row[col]) for col in df.columns}
            for _, row in df.iterrows()
        ]
        for nombre, df in data.items()
    }


def json_a_data(payload: dict[str, Any]) -> dict[str, pd.DataFrame]:
    data = {}
    for nombre, columnas in COLUMNAS.items():
        registros = payload.get(nombre, [])
        data[nombre] = (
            pd.DataFrame(registros, columns=columnas)
            if registros
            else df_vacio(nombre)
        )
    return asegurar_columnas(data)


def guardar_memoria() -> None:
    with ARCHIVO_MEMORIA.open("w", encoding="utf-8") as archivo:
        json.dump(
            data_a_json(st.session_state.data_m06),
            archivo,
            ensure_ascii=False,
            indent=2,
        )


def cargar_memoria() -> dict[str, pd.DataFrame]:
    if ARCHIVO_MEMORIA.exists():
        try:
            with ARCHIVO_MEMORIA.open("r", encoding="utf-8") as archivo:
                return json_a_data(json.load(archivo))
        except Exception as error:
            st.session_state["error_carga_memoria_m06"] = str(error)
    return asegurar_columnas({})


def inicializar_estado() -> None:
    if "maestros_m06" not in st.session_state:
        st.session_state.maestros_m06 = crear_maestros_referencia()
    if "data_m06" not in st.session_state:
        st.session_state.data_m06 = cargar_memoria()
    else:
        st.session_state.data_m06 = asegurar_columnas(st.session_state.data_m06)

    st.session_state.setdefault("usuario_actual", USUARIO_BETA)
    st.session_state.setdefault("pantalla_m06", "Índice")
    actualizar_estados_vigencia()


# ============================================================
# 6. UTILIDADES GENERALES
# ============================================================

def ahora() -> str:
    return datetime.now().isoformat(timespec="seconds")


def normalizar_bool(valor: Any) -> bool:
    if isinstance(valor, bool):
        return valor
    return str(valor).strip().lower() in ["true", "1", "sí", "si", "yes"]


def generar_id(prefijo: str) -> str:
    return f"{prefijo}-{uuid.uuid4().hex[:12].upper()}"


def upsert(tabla: str, registro: dict[str, Any], llave: str) -> str:
    df = st.session_state.data_m06[tabla].copy()
    valor = str(registro.get(llave, "")).strip()
    if not valor:
        raise ValueError(f"Falta la llave {llave}.")

    if df.empty or valor not in df[llave].astype(str).values:
        for col in COLUMNAS[tabla]:
            registro.setdefault(col, "")
        df = pd.concat(
            [df, pd.DataFrame([registro])[COLUMNAS[tabla]]],
            ignore_index=True,
        )
        accion = "creado"
    else:
        idx = df.index[df[llave].astype(str).eq(valor)][0]
        for col, val in registro.items():
            if col in df.columns:
                df.at[idx, col] = val
        accion = "actualizado"

    st.session_state.data_m06[tabla] = df
    guardar_memoria()
    return accion


def maestro(nombre: str) -> pd.DataFrame:
    return st.session_state.maestros_m06[nombre].copy()


def calcular_hash_referencia(nombre_archivo: str, ruta_archivo: str) -> str:
    """
    Hash funcional para la versión prototipo. En producción debe calcularse
    sobre los bytes del archivo almacenado en el repositorio.
    """
    base = f"{nombre_archivo.strip().lower()}|{ruta_archivo.strip().lower()}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def estado_vigencia_calculado(
    tiene_vigencia: str | bool,
    fecha_vencimiento: str | date | None,
) -> str:
    if not normalizar_bool(tiene_vigencia):
        return "No aplica"

    if not fecha_vencimiento:
        return "Vencido"

    try:
        vencimiento = (
            fecha_vencimiento
            if isinstance(fecha_vencimiento, date)
            else date.fromisoformat(str(fecha_vencimiento))
        )
    except ValueError:
        return "Vencido"

    hoy = date.today()
    if vencimiento < hoy:
        return "Vencido"
    if vencimiento <= hoy + timedelta(days=DIAS_ALERTA_VENCIMIENTO):
        return "Próximo a vencer"
    return "Vigente"


def actualizar_estados_vigencia() -> None:
    if "data_m06" not in st.session_state:
        return
    docs = st.session_state.data_m06["documentos"].copy()
    if docs.empty:
        return

    docs["estado_vigencia"] = docs.apply(
        lambda row: estado_vigencia_calculado(
            row.get("tiene_vigencia", False),
            row.get("fecha_vencimiento", ""),
        ),
        axis=1,
    )
    st.session_state.data_m06["documentos"] = docs


def validar_vigencia(
    tiene_vigencia: bool,
    fecha_documento: date,
    fecha_vencimiento: date | None,
) -> tuple[str, str]:
    if not tiene_vigencia:
        return "No aplica", "No aplica"

    if fecha_vencimiento is None:
        raise ValueError(
            "La fecha de vencimiento es obligatoria cuando el documento tiene vigencia."
        )
    if fecha_vencimiento < fecha_documento:
        raise ValueError(
            "La fecha de vencimiento no puede ser anterior a la fecha del documento."
        )
    return fecha_vencimiento.isoformat(), estado_vigencia_calculado(
        True, fecha_vencimiento
    )


# ============================================================
# 7. CONFIGURACIÓN DE NIVELES Y ENTIDADES
# ============================================================

CONFIG_NIVELES = {
    "Persona": {
        "tabla": "personas",
        "id": "id_persona",
        "nombre": "nombre",
    },
    "Hogar": {
        "tabla": "hogares",
        "id": "id_hogar",
        "nombre": "nombre",
    },
    "Persona no residente": {
        "tabla": "personas_no_residentes",
        "id": "id_persona_no_residente",
        "nombre": "nombre",
    },
    "Organización comunitaria o productiva": {
        "tabla": "organizaciones",
        "id": "id_organizacion",
        "nombre": "nombre",
    },
    "Lugar poblado": {
        "tabla": "lugares_poblados",
        "id": "id_lugar_poblado",
        "nombre": "nombre",
    },
    "Hogar sin censo": {
        "tabla": "hogares_sin_censo",
        "id": "id_registro_sin_censo",
        "nombre": "referencia",
    },
    "Proyecto": {
        "tabla": "proyectos",
        "id": "id_proyecto",
        "nombre": "nombre",
    },
}


def entidades_nivel(nivel: str) -> pd.DataFrame:
    config = CONFIG_NIVELES[nivel]
    return maestro(config["tabla"])


def obtener_entidad(nivel: str, id_entidad: str) -> dict[str, Any]:
    config = CONFIG_NIVELES[nivel]
    df = entidades_nivel(nivel)
    fila = df[df[config["id"]].astype(str).eq(str(id_entidad))]
    return fila.iloc[0].to_dict() if not fila.empty else {}


def etiqueta_entidad(nivel: str, fila: pd.Series | dict[str, Any]) -> str:
    config = CONFIG_NIVELES[nivel]
    return f"{fila.get(config['id'], '')} · {fila.get(config['nombre'], '')}"


def expediente_existente(nivel: str, id_entidad: str) -> dict[str, Any]:
    df = st.session_state.data_m06["expedientes"]
    if df.empty:
        return {}
    filas = df[
        df["nivel"].astype(str).eq(nivel)
        & df["id_entidad_principal"].astype(str).eq(str(id_entidad))
    ]
    return filas.iloc[0].to_dict() if not filas.empty else {}


def catalogo_nivel(nivel: str) -> pd.DataFrame:
    df = catalogo_df()
    return df[df["nivel"].astype(str).eq(nivel)].copy()


def fases_nivel(nivel: str) -> list[str]:
    df = catalogo_nivel(nivel)
    return list(dict.fromkeys(df["fase"].astype(str).tolist()))


def carpetas_nivel_fase(nivel: str, fase: str) -> pd.DataFrame:
    df = catalogo_nivel(nivel)
    sub = df[df["fase"].astype(str).eq(fase)].copy()
    return sub[["codigo_carpeta", "carpeta"]].drop_duplicates()


def tipos_por_carpeta(nivel: str, fase: str, codigo_carpeta: str) -> pd.DataFrame:
    df = catalogo_nivel(nivel)
    return df[
        df["fase"].astype(str).eq(fase)
        & df["codigo_carpeta"].astype(str).eq(str(codigo_carpeta))
    ].copy()


# ============================================================
# 8. EXPEDIENTES Y CHECKLIST
# ============================================================

def crear_o_actualizar_expediente(
    nivel: str,
    id_entidad: str,
    responsable: str,
    estado: str,
    observaciones: str,
) -> tuple[str, str]:
    entidad = obtener_entidad(nivel, id_entidad)
    if not entidad:
        raise ValueError("La entidad seleccionada no existe en los datos maestros.")

    existente = expediente_existente(nivel, id_entidad)
    id_expediente = existente.get("id_expediente") or generar_id("EXP")
    nombre = entidad.get(CONFIG_NIVELES[nivel]["nombre"], "")

    registro = {
        "id_expediente": id_expediente,
        "nivel": nivel,
        "id_entidad_principal": id_entidad,
        "nombre_entidad": nombre,
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
    crear_checklist_expediente(registro)
    recalcular_progreso_expediente(id_expediente)
    return accion, id_expediente


def crear_checklist_expediente(expediente: dict[str, Any]) -> None:
    checklist = st.session_state.data_m06["checklist"].copy()
    id_expediente = str(expediente.get("id_expediente", ""))
    nivel = str(expediente.get("nivel", ""))
    id_entidad = str(expediente.get("id_entidad_principal", ""))

    if not id_expediente or nivel not in NIVELES:
        return

    existentes = set()
    if not checklist.empty:
        existentes = set(
            checklist[
                checklist["id_expediente"].astype(str).eq(id_expediente)
            ]["codigo_documento"].astype(str)
        )

    nuevos = []
    for _, item in catalogo_nivel(nivel).iterrows():
        codigo = str(item["codigo_documento"])
        if codigo in existentes:
            continue

        nuevos.append({
            "id_checklist": generar_id("CHK"),
            "id_expediente": id_expediente,
            "nivel": nivel,
            "id_entidad_principal": id_entidad,
            "fase": item["fase"],
            "codigo_carpeta": item["codigo_carpeta"],
            "carpeta": item["carpeta"],
            "codigo_documento": codigo,
            "tipo_documental": item["tipo_documental"],
            "aplicabilidad": "Pendiente de determinar",
            "justificacion_no_aplica": "",
            "id_documento_asociado": "",
            "estado_carga": "No cargado",
            "estado_revision": "Pendiente de asignación",
            "estado_vigencia": "No aplica",
            "cumple": False,
            "fecha_actualizacion": ahora(),
        })

    if nuevos:
        checklist = pd.concat(
            [checklist, pd.DataFrame(nuevos)[COLUMNAS["checklist"]]],
            ignore_index=True,
        )
        st.session_state.data_m06["checklist"] = checklist
        guardar_memoria()


def sincronizar_checklist_documento(id_documento: str) -> None:
    docs = st.session_state.data_m06["documentos"].copy()
    fila = docs[docs["id_documento"].astype(str).eq(str(id_documento))]
    if fila.empty:
        return

    doc = fila.iloc[0].to_dict()
    id_exp = str(doc["id_expediente_principal"])
    codigo = str(doc["codigo_documento"])
    checklist = st.session_state.data_m06["checklist"].copy()
    mask = (
        checklist["id_expediente"].astype(str).eq(id_exp)
        & checklist["codigo_documento"].astype(str).eq(codigo)
    )
    if not mask.any():
        return

    grupo = docs[
        docs["id_expediente_principal"].astype(str).eq(id_exp)
        & docs["codigo_documento"].astype(str).eq(codigo)
    ].copy()
    grupo["_version"] = pd.to_numeric(grupo["version"], errors="coerce").fillna(1)

    vigentes = grupo[grupo["es_version_vigente"].apply(normalizar_bool)].copy()
    if vigentes.empty:
        vigentes = grupo.sort_values("_version", ascending=False).head(1)

    referencia = vigentes.sort_values("_version", ascending=False).iloc[0]
    estado_vigencia = estado_vigencia_calculado(
        referencia.get("tiene_vigencia", False),
        referencia.get("fecha_vencimiento", ""),
    )
    aprobado = (
        str(referencia.get("estado_revision", "")) == "Aprobado"
        and normalizar_bool(referencia.get("confirmado", False))
    )
    vigencia_valida = estado_vigencia in ["Vigente", "No aplica"]
    cumple = bool(aprobado and vigencia_valida)

    checklist.loc[mask, "aplicabilidad"] = "Aplica"
    checklist.loc[mask, "id_documento_asociado"] = referencia["id_documento"]
    checklist.loc[mask, "estado_carga"] = referencia.get("estado_carga", "")
    checklist.loc[mask, "estado_revision"] = referencia.get("estado_revision", "")
    checklist.loc[mask, "estado_vigencia"] = estado_vigencia
    checklist.loc[mask, "cumple"] = cumple
    checklist.loc[mask, "fecha_actualizacion"] = ahora()
    st.session_state.data_m06["checklist"] = checklist
    recalcular_progreso_expediente(id_exp)


def recalcular_progreso_expediente(id_expediente: str) -> None:
    checklist = st.session_state.data_m06["checklist"]
    sub = checklist[
        checklist["id_expediente"].astype(str).eq(str(id_expediente))
    ].copy()

    aplicables = sub[
        ~sub["aplicabilidad"].astype(str).isin(
            ["No aplica", "Pendiente de determinar"]
        )
    ]
    total = len(aplicables)
    cumplidos = (
        int(aplicables["cumple"].apply(normalizar_bool).sum())
        if total
        else 0
    )
    porcentaje = round(cumplidos / total * 100, 2) if total else 0.0

    expedientes = st.session_state.data_m06["expedientes"].copy()
    mask = expedientes["id_expediente"].astype(str).eq(str(id_expediente))
    if mask.any():
        expedientes.loc[mask, "porcentaje_completitud"] = porcentaje
        expedientes.loc[mask, "fecha_actualizacion"] = ahora()
        st.session_state.data_m06["expedientes"] = expedientes
    guardar_memoria()


def marcar_no_aplica(
    id_checklist: str,
    justificacion: str,
) -> None:
    if not justificacion.strip():
        raise ValueError("Debe registrar una justificación para marcar No aplica.")

    checklist = st.session_state.data_m06["checklist"].copy()
    mask = checklist["id_checklist"].astype(str).eq(str(id_checklist))
    if not mask.any():
        raise ValueError("El registro del checklist no existe.")

    checklist.loc[mask, "aplicabilidad"] = "No aplica"
    checklist.loc[mask, "justificacion_no_aplica"] = justificacion.strip()
    checklist.loc[mask, "estado_vigencia"] = "No aplica"
    checklist.loc[mask, "cumple"] = True
    checklist.loc[mask, "fecha_actualizacion"] = ahora()
    id_exp = checklist.loc[mask, "id_expediente"].iloc[0]
    st.session_state.data_m06["checklist"] = checklist
    recalcular_progreso_expediente(str(id_exp))


# ============================================================
# 9. DOCUMENTOS, RELACIONES Y VERSIONADO
# ============================================================

def validar_duplicidad_documento(
    hash_documento: str,
    id_entidad_principal: str,
    codigo_documento: str,
    fecha_documento: str,
) -> None:
    docs = st.session_state.data_m06["documentos"]
    if docs.empty:
        return

    duplicado = docs[
        docs["hash_documento"].astype(str).eq(hash_documento)
        & docs["id_entidad_principal"].astype(str).eq(id_entidad_principal)
        & docs["codigo_documento"].astype(str).eq(codigo_documento)
        & docs["fecha_documento"].astype(str).eq(fecha_documento)
    ]
    if not duplicado.empty:
        raise ValueError(
            "Ya existe una carga con el mismo archivo, tipo documental, entidad y fecha."
        )


def guardar_relaciones_documento(
    id_documento: str,
    id_serie: str,
    relaciones: list[dict[str, Any]],
) -> None:
    for relacion in relaciones:
        registro = {
            "id_relacion": generar_id("REL"),
            "id_documento": id_documento,
            "id_serie_documental": id_serie,
            "tipo_entidad": relacion["tipo_entidad"],
            "id_entidad": relacion["id_entidad"],
            "es_relacion_principal": bool(relacion.get("es_principal", False)),
            "fecha_relacion": ahora(),
            "usuario_relacion": st.session_state.usuario_actual,
        }
        upsert("relaciones_documento", registro, "id_relacion")


def guardar_documento(
    registro: dict[str, Any],
    relaciones: list[dict[str, Any]],
) -> str:
    if (
        not MODO_BETA_AUTORREVISION
        and registro["usuario_carga"] == registro["usuario_revisor_asignado"]
    ):
        raise ValueError(
            "El usuario que carga no puede revisar el mismo documento."
        )

    if not str(registro.get("nombre_archivo", "")).strip():
        raise ValueError("Capture el nombre o referencia del archivo.")
    if not str(registro.get("ruta_archivo", "")).strip():
        raise ValueError("Capture el vínculo o ruta del documento.")

    docs = st.session_state.data_m06["documentos"].copy()
    token = str(registro.get("token_transaccion", ""))
    if (
        token
        and not docs.empty
        and docs["token_transaccion"].astype(str).eq(token).any()
    ):
        raise ValueError("Esta acción de guardado ya fue procesada.")

    validar_duplicidad_documento(
        str(registro["hash_documento"]),
        str(registro["id_entidad_principal"]),
        str(registro["codigo_documento"]),
        str(registro["fecha_documento"]),
    )

    if str(registro.get("tipo_registro")) == "Nueva versión":
        serie = str(registro.get("id_serie_documental", ""))
        anteriores = docs[docs["id_serie_documental"].astype(str).eq(serie)]
        if anteriores.empty:
            raise ValueError(
                "No se encontró el documento base para crear la nueva versión."
            )
        docs.loc[
            docs["id_serie_documental"].astype(str).eq(serie),
            "es_version_vigente",
        ] = False

    registro["estado_revision"] = "Pendiente de revisión"
    registro["confirmado"] = False
    registro["es_version_vigente"] = True

    for col in COLUMNAS["documentos"]:
        registro.setdefault(col, "")

    if (
        not docs.empty
        and docs["id_documento"].astype(str).eq(str(registro["id_documento"])).any()
    ):
        raise ValueError("El identificador del documento ya existe.")

    docs = pd.concat(
        [docs, pd.DataFrame([registro])[COLUMNAS["documentos"]]],
        ignore_index=True,
    )
    st.session_state.data_m06["documentos"] = docs
    guardar_relaciones_documento(
        registro["id_documento"],
        registro["id_serie_documental"],
        relaciones,
    )
    guardar_memoria()
    sincronizar_checklist_documento(registro["id_documento"])
    return "creado"


def registrar_revision(
    id_documento: str,
    resultado: str,
    observaciones: str,
    requiere_subsanacion: bool,
) -> None:
    docs = st.session_state.data_m06["documentos"].copy()
    mask = docs["id_documento"].astype(str).eq(str(id_documento))
    if not mask.any():
        raise ValueError("El documento no existe.")

    doc = docs[mask].iloc[0].to_dict()
    usuario = st.session_state.usuario_actual

    if not MODO_BETA_AUTORREVISION:
        if doc.get("usuario_carga") == usuario:
            raise ValueError(
                "La persona que cargó el documento no puede revisarlo."
            )
        if doc.get("usuario_revisor_asignado") != usuario:
            raise ValueError(
                "El documento está asignado a otro responsable de revisión."
            )

    revision = {
        "id_revision": generar_id("REV"),
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
    docs.loc[mask, "estado_vigencia"] = docs.loc[mask].apply(
        lambda row: estado_vigencia_calculado(
            row.get("tiene_vigencia", False),
            row.get("fecha_vencimiento", ""),
        ),
        axis=1,
    )
    docs.loc[mask, "fecha_actualizacion"] = ahora()
    docs.loc[mask, "usuario_actualizacion"] = usuario
    st.session_state.data_m06["documentos"] = docs
    guardar_memoria()
    sincronizar_checklist_documento(id_documento)


# ============================================================
# 10. COMPONENTES DE INTERFAZ
# ============================================================

def aplicar_estilos() -> None:
    st.markdown(
        f"""
        <style>
            :root {{
                --sir-primary: {COLOR_PRIMARIO};
                --sir-accent: {COLOR_SECUNDARIO};
                --sir-coral: {COLOR_CORAL};
                --sir-soft: {COLOR_AZUL_CLARO};
                --sir-border: rgba(128,128,128,.25);
            }}
            .main-title {{
                font-size: clamp(1.5rem, 2.6vw, 2.35rem);
                font-weight: 950;
                color: var(--sir-primary);
                letter-spacing: -.035em;
            }}
            .sub-title {{
                opacity: .72;
                margin-bottom: 1rem;
            }}
            .sir-help {{
                border-left: 5px solid var(--sir-accent);
                padding: .85rem 1rem;
                border-radius: 14px;
                background: color-mix(
                    in srgb,
                    var(--secondary-background-color) 88%,
                    var(--sir-accent) 8%
                );
                margin-bottom: 1rem;
            }}
            .sir-card {{
                border: 1px solid var(--sir-border);
                border-radius: 16px;
                padding: 1rem;
                background: var(--secondary-background-color);
            }}
            div[data-testid="stMetric"] {{
                border: 1px solid var(--sir-border);
                border-radius: 16px;
                padding: .8rem;
                background: var(--secondary-background-color);
            }}
            .stButton > button,
            .stDownloadButton > button {{
                border-radius: 12px !important;
                font-weight: 800 !important;
                min-height: 2.6rem;
            }}
            @media (max-width: 720px) {{
                .main-title {{ font-size: 1.55rem; }}
                .sir-card {{ padding: .75rem; }}
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def encabezado() -> None:
    st.markdown(
        '<div class="main-title">M06 · Gestión Documental y Expedientes</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sub-title">'
        'Estructura integrada · Documento único · Versionado · Vigencia · Trazabilidad'
        '</div>',
        unsafe_allow_html=True,
    )


def selector_entidad(
    nivel: str,
    key_prefix: str,
    solo_con_expediente: bool = False,
) -> str:
    config = CONFIG_NIVELES[nivel]
    df = entidades_nivel(nivel)
    expedientes = st.session_state.data_m06["expedientes"]

    if solo_con_expediente:
        ids = expedientes[
            expedientes["nivel"].astype(str).eq(nivel)
        ]["id_entidad_principal"].astype(str).unique().tolist()
        df = df[df[config["id"]].astype(str).isin(ids)]

    if df.empty:
        st.warning("No hay registros disponibles para esta vista.")
        return ""

    opciones = df[config["id"]].astype(str).tolist()
    etiquetas = {
        str(row[config["id"]]): etiqueta_entidad(nivel, row)
        for _, row in df.iterrows()
    }
    return st.selectbox(
        "Entidad",
        opciones,
        format_func=lambda valor: etiquetas.get(valor, valor),
        key=f"{key_prefix}_{nivel}",
    )


def mostrar_contexto(nivel: str, id_entidad: str, expediente: dict[str, Any]) -> None:
    entidad = obtener_entidad(nivel, id_entidad)
    config = CONFIG_NIVELES[nivel]
    columnas = st.columns(4)
    columnas[0].info(f"**Expediente**\n\n{expediente.get('id_expediente', '')}")
    columnas[1].info(f"**Nivel**\n\n{nivel}")
    columnas[2].info(f"**ID entidad**\n\n{id_entidad}")
    columnas[3].info(
        f"**Referencia**\n\n{entidad.get(config['nombre'], '')}"
    )


def formulario_expediente(nivel: str, id_entidad: str) -> None:
    existente = expediente_existente(nivel, id_entidad)
    with st.form(f"form_expediente_{nivel}_{id_entidad}"):
        st.markdown("#### Expediente")
        if existente:
            st.success(f"Expediente existente: {existente['id_expediente']}")

        responsable = st.selectbox(
            "Responsable del expediente",
            USUARIOS,
            index=(
                USUARIOS.index(existente.get("responsable_expediente"))
                if existente.get("responsable_expediente") in USUARIOS
                else 0
            ),
        )
        estado = st.selectbox(
            "Estado del expediente",
            ESTADOS_EXPEDIENTE,
            index=(
                ESTADOS_EXPEDIENTE.index(existente.get("estado_expediente"))
                if existente.get("estado_expediente") in ESTADOS_EXPEDIENTE
                else 0
            ),
        )
        observaciones = st.text_area(
            "Observaciones",
            value=str(existente.get("observaciones", "")),
        )
        guardar = st.form_submit_button(
            "Actualizar expediente" if existente else "Crear expediente",
            type="primary",
            use_container_width=True,
        )

    if guardar:
        try:
            accion, id_exp = crear_o_actualizar_expediente(
                nivel,
                id_entidad,
                responsable,
                estado,
                observaciones,
            )
            st.success(f"Expediente {accion}: {id_exp}")
            st.rerun()
        except ValueError as error:
            st.error(str(error))


def selector_relaciones_adicionales(
    nivel_principal: str,
    id_principal: str,
    key_prefix: str,
) -> list[dict[str, Any]]:
    relaciones = [{
        "tipo_entidad": nivel_principal,
        "id_entidad": id_principal,
        "es_principal": True,
    }]

    with st.expander("Relacionar el documento con otras entidades", expanded=False):
        st.caption(
            "El archivo se guarda una sola vez. Estas relaciones permiten "
            "consultarlo desde otros expedientes sin duplicar la carga."
        )

        niveles_relacionables = [n for n in NIVELES if n != nivel_principal]
        seleccionados = st.multiselect(
            "Niveles relacionados",
            niveles_relacionables,
            key=f"{key_prefix}_niveles_relacionados",
        )

        for nivel in seleccionados:
            config = CONFIG_NIVELES[nivel]
            df = entidades_nivel(nivel)
            opciones = df[config["id"]].astype(str).tolist()
            etiquetas = {
                str(row[config["id"]]): etiqueta_entidad(nivel, row)
                for _, row in df.iterrows()
            }
            ids = st.multiselect(
                f"{nivel}",
                opciones,
                format_func=lambda valor, e=etiquetas: e.get(valor, valor),
                key=f"{key_prefix}_{nivel}_rel",
            )
            for id_entidad in ids:
                relaciones.append({
                    "tipo_entidad": nivel,
                    "id_entidad": id_entidad,
                    "es_principal": False,
                })

    return relaciones


def formulario_documento(
    nivel: str,
    id_entidad: str,
    expediente: dict[str, Any],
) -> None:
    id_exp = expediente["id_expediente"]
    docs = st.session_state.data_m06["documentos"].copy()

    fases = fases_nivel(nivel)
    if not fases:
        st.warning("El nivel seleccionado no tiene tipos documentales activos.")
        return

    fase = st.selectbox(
        "Fase",
        fases,
        key=f"fase_{nivel}_{id_exp}",
    )

    carpetas = carpetas_nivel_fase(nivel, fase)
    codigos_carpeta = carpetas["codigo_carpeta"].astype(str).tolist()
    etiquetas_carpeta = {
        str(row["codigo_carpeta"]): f"{row['codigo_carpeta']} · {row['carpeta']}"
        for _, row in carpetas.iterrows()
    }
    codigo_carpeta = st.selectbox(
        "Carpeta",
        codigos_carpeta,
        format_func=lambda valor: etiquetas_carpeta.get(valor, valor),
        key=f"carpeta_{nivel}_{id_exp}_{fase}",
    )

    opciones = tipos_por_carpeta(nivel, fase, codigo_carpeta)
    codigos_doc = opciones["codigo_documento"].astype(str).tolist()
    etiquetas_doc = {
        str(row["codigo_documento"]):
        f"{row['codigo_documento']} · {row['tipo_documental']}"
        for _, row in opciones.iterrows()
    }
    codigo_documento = st.selectbox(
        "Tipo documental",
        codigos_doc,
        format_func=lambda valor: etiquetas_doc.get(valor, valor),
        key=f"tipo_{nivel}_{id_exp}_{codigo_carpeta}",
    )
    item = opciones[
        opciones["codigo_documento"].astype(str).eq(codigo_documento)
    ].iloc[0]

    existentes = docs[
        docs["id_expediente_principal"].astype(str).eq(str(id_exp))
        & docs["codigo_documento"].astype(str).eq(codigo_documento)
    ].copy() if not docs.empty else docs

    modo = "Registrar documento nuevo"
    if not existentes.empty:
        modo = st.radio(
            "¿Qué deseas registrar?",
            ["Registrar documento nuevo", "Agregar nueva versión"],
            horizontal=True,
            key=f"modo_{id_exp}_{codigo_documento}",
        )

    serie_base = ""
    documento_padre = ""
    version = 1

    if modo == "Agregar nueva versión":
        series = (
            existentes.assign(
                _version=pd.to_numeric(
                    existentes["version"], errors="coerce"
                ).fillna(1)
            )
            .sort_values(["id_serie_documental", "_version"])
            .groupby("id_serie_documental", as_index=False)
            .tail(1)
        )
        opciones_series = series["id_serie_documental"].astype(str).tolist()
        etiquetas_series = {
            str(row["id_serie_documental"]):
            f"{row['nombre_archivo']} · v{int(row['_version'])}"
            for _, row in series.iterrows()
        }
        serie_base = st.selectbox(
            "Documento al que agregarás la nueva versión",
            opciones_series,
            format_func=lambda valor: etiquetas_series.get(valor, valor),
            key=f"serie_{id_exp}_{codigo_documento}",
        )
        base = existentes[
            existentes["id_serie_documental"].astype(str).eq(serie_base)
        ].copy()
        base["_version"] = pd.to_numeric(
            base["version"], errors="coerce"
        ).fillna(1)
        vigente = base.sort_values("_version", ascending=False).iloc[0]
        documento_padre = vigente["id_documento"]
        version = int(vigente["_version"]) + 1
        st.info(
            f"Se registrará la versión {version}. "
            "La versión anterior permanecerá en el histórico."
        )

    relaciones = selector_relaciones_adicionales(
        nivel,
        id_entidad,
        f"rel_{id_exp}_{codigo_documento}",
    )

    token_key = f"token_carga_{id_exp}"
    st.session_state.setdefault(token_key, 0)
    token = int(st.session_state[token_key])

    with st.form(
        f"form_documento_{nivel}_{id_exp}_{codigo_documento}_{token}"
    ):
        c1, c2 = st.columns(2)
        nombre_archivo = c1.text_input("Nombre o referencia del archivo")
        ruta_archivo = c2.text_input("Link o ruta del documento")

        c1, c2 = st.columns(2)
        fecha_documento = c1.date_input(
            "Fecha del documento",
            value=date.today(),
        )
        tiene_vigencia = c2.radio(
            "¿El documento tiene vigencia?",
            ["No", "Sí"],
            horizontal=True,
        )

        fecha_vencimiento = None
        if tiene_vigencia == "Sí":
            fecha_vencimiento = st.date_input(
                "Fecha de vencimiento",
                value=date.today() + timedelta(days=365),
                min_value=fecha_documento,
            )
        else:
            st.text_input(
                "Fecha de vencimiento",
                value="No aplica",
                disabled=True,
            )

        c1, c2 = st.columns(2)
        confidencialidad = c1.selectbox(
            "Confidencialidad",
            CONFIDENCIALIDADES,
            index=(
                CONFIDENCIALIDADES.index(item["confidencialidad"])
                if item["confidencialidad"] in CONFIDENCIALIDADES
                else 1
            ),
        )
        revisores = (
            [st.session_state.usuario_actual]
            if MODO_BETA_AUTORREVISION
            else [u for u in USUARIOS if u != st.session_state.usuario_actual]
        )
        revisor = c2.selectbox("Responsable de revisión", revisores)

        observaciones = st.text_area("Observaciones de carga")
        guardar = st.form_submit_button(
            "Registrar documento",
            type="primary",
            use_container_width=True,
        )

    if guardar:
        try:
            fecha_vencimiento_guardar, estado_vigencia = validar_vigencia(
                tiene_vigencia == "Sí",
                fecha_documento,
                fecha_vencimiento,
            )
            hash_documento = calcular_hash_referencia(
                nombre_archivo,
                ruta_archivo,
            )

            id_documento = generar_id("DOC")
            id_serie = serie_base or generar_id("SER")
            registro = {
                "id_documento": id_documento,
                "id_serie_documental": id_serie,
                "id_documento_padre": documento_padre,
                "tipo_registro": (
                    "Nueva versión"
                    if modo == "Agregar nueva versión"
                    else "Documento nuevo"
                ),
                "es_version_vigente": True,
                "token_transaccion": (
                    f"{id_exp}|{codigo_documento}|{token}|{uuid.uuid4().hex}"
                ),
                "id_expediente_principal": id_exp,
                "nivel_principal": nivel,
                "id_entidad_principal": id_entidad,
                "fase": fase,
                "codigo_carpeta": codigo_carpeta,
                "carpeta": item["carpeta"],
                "codigo_documento": codigo_documento,
                "tipo_documental": item["tipo_documental"],
                "aplicabilidad": "Aplica",
                "justificacion_no_aplica": "",
                "confidencialidad": confidencialidad,
                "nombre_archivo": nombre_archivo,
                "ruta_archivo": ruta_archivo,
                "hash_documento": hash_documento,
                "fecha_documento": fecha_documento.isoformat(),
                "fecha_carga": date.today().isoformat(),
                "tiene_vigencia": tiene_vigencia == "Sí",
                "fecha_vencimiento": fecha_vencimiento_guardar,
                "estado_vigencia": estado_vigencia,
                "estado_carga": "Cargado",
                "usuario_carga": st.session_state.usuario_actual,
                "usuario_revisor_asignado": revisor,
                "version": version,
                "observaciones_carga": observaciones,
                "fecha_creacion": ahora(),
                "fecha_actualizacion": ahora(),
                "usuario_actualizacion": st.session_state.usuario_actual,
            }

            guardar_documento(registro, relaciones)
            st.session_state[token_key] = token + 1
            st.success(
                f"Documento guardado una sola vez · "
                f"{registro['tipo_registro']} · versión {version}."
            )
            st.rerun()
        except ValueError as error:
            st.error(str(error))


def tabla_documentos(expediente: dict[str, Any]) -> None:
    actualizar_estados_vigencia()
    docs = st.session_state.data_m06["documentos"]
    sub = docs[
        docs["id_expediente_principal"].astype(str).eq(
            str(expediente["id_expediente"])
        )
    ].copy()

    st.markdown("#### Documentos registrados")
    if sub.empty:
        st.info("Todavía no hay documentos registrados.")
        return

    sub["version"] = pd.to_numeric(
        sub["version"], errors="coerce"
    ).fillna(1).astype(int)

    solo_vigentes = st.toggle(
        "Mostrar solo versiones vigentes",
        value=True,
        key=f"vigentes_{expediente['id_expediente']}",
    )
    vista = (
        sub[sub["es_version_vigente"].apply(normalizar_bool)].copy()
        if solo_vigentes
        else sub.copy()
    )

    columnas = [
        "id_documento", "id_serie_documental", "fase", "carpeta",
        "tipo_documental", "nombre_archivo", "version",
        "estado_revision", "tiene_vigencia", "fecha_vencimiento",
        "estado_vigencia", "confidencialidad", "ruta_archivo",
    ]
    st.dataframe(
        vista[columnas].sort_values(
            ["tipo_documental", "version"],
            ascending=[True, False],
        ),
        use_container_width=True,
        hide_index=True,
        column_config={
            "ruta_archivo": st.column_config.LinkColumn(
                "Documento",
                display_text="Abrir",
            ),
            "tiene_vigencia": st.column_config.CheckboxColumn(
                "Tiene vigencia"
            ),
        },
    )


def vista_historico(expediente: dict[str, Any]) -> None:
    actualizar_estados_vigencia()
    docs = st.session_state.data_m06["documentos"]
    revisiones = st.session_state.data_m06["revisiones"]
    relaciones = st.session_state.data_m06["relaciones_documento"]

    sub_docs = docs[
        docs["id_expediente_principal"].astype(str).eq(
            str(expediente["id_expediente"])
        )
    ].copy()

    if sub_docs.empty:
        st.info("El expediente todavía no tiene movimientos documentales.")
        return

    st.markdown("#### Histórico documental")
    columnas = [
        "id_documento", "id_serie_documental", "id_documento_padre",
        "tipo_registro", "es_version_vigente", "fase", "tipo_documental",
        "nombre_archivo", "version", "fecha_documento", "fecha_carga",
        "tiene_vigencia", "fecha_vencimiento", "estado_vigencia",
        "usuario_carga", "estado_revision", "ruta_archivo",
    ]
    st.dataframe(
        sub_docs[columnas].sort_values(
            ["tipo_documental", "version"],
            ascending=[True, False],
        ),
        use_container_width=True,
        hide_index=True,
        column_config={
            "ruta_archivo": st.column_config.LinkColumn(
                "Documento",
                display_text="Abrir",
            ),
        },
    )

    ids = sub_docs["id_documento"].astype(str).tolist()

    st.markdown("#### Relaciones del documento")
    sub_rel = relaciones[
        relaciones["id_documento"].astype(str).isin(ids)
    ].copy() if not relaciones.empty else relaciones
    if sub_rel.empty:
        st.info("No existen relaciones adicionales.")
    else:
        st.dataframe(sub_rel, use_container_width=True, hide_index=True)

    st.markdown("#### Histórico de revisiones")
    sub_rev = revisiones[
        revisiones["id_documento"].astype(str).isin(ids)
    ].copy() if not revisiones.empty else revisiones
    if sub_rev.empty:
        st.info("Todavía no se han registrado revisiones.")
    else:
        st.dataframe(
            sub_rev.sort_values("fecha_actualizacion", ascending=False),
            use_container_width=True,
            hide_index=True,
        )


def vista_checklist(expediente: dict[str, Any]) -> None:
    crear_checklist_expediente(expediente)
    id_exp = expediente["id_expediente"]

    docs = st.session_state.data_m06["documentos"]
    ids = docs[
        docs["id_expediente_principal"].astype(str).eq(str(id_exp))
    ]["id_documento"].astype(str).tolist() if not docs.empty else []
    for id_documento in ids:
        sincronizar_checklist_documento(id_documento)

    checklist = st.session_state.data_m06["checklist"]
    sub = checklist[
        checklist["id_expediente"].astype(str).eq(str(id_exp))
    ].copy()

    if sub.empty:
        st.warning("No fue posible generar el checklist.")
        return

    c1, c2, c3 = st.columns(3)
    fase_sel = c1.selectbox(
        "Fase",
        ["Todas"] + sorted(sub["fase"].dropna().astype(str).unique().tolist()),
    )
    carpeta_sel = c2.selectbox(
        "Carpeta",
        ["Todas"] + sorted(sub["carpeta"].dropna().astype(str).unique().tolist()),
    )
    vigencia_sel = c3.selectbox(
        "Vigencia",
        ["Todos"] + ESTADOS_VIGENCIA,
    )

    vista = sub.copy()
    if fase_sel != "Todas":
        vista = vista[vista["fase"].astype(str).eq(fase_sel)]
    if carpeta_sel != "Todas":
        vista = vista[vista["carpeta"].astype(str).eq(carpeta_sel)]
    if vigencia_sel != "Todos":
        vista = vista[vista["estado_vigencia"].astype(str).eq(vigencia_sel)]

    columnas = [
        "id_checklist", "fase", "carpeta", "codigo_documento",
        "tipo_documental", "aplicabilidad", "id_documento_asociado",
        "estado_carga", "estado_revision", "estado_vigencia", "cumple",
    ]
    st.dataframe(
        vista[columnas],
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("#### Configurar aplicabilidad")
    pendientes = sub[
        sub["aplicabilidad"].astype(str).eq("Pendiente de determinar")
    ]
    if pendientes.empty:
        st.info("No hay tipos documentales pendientes de clasificación.")
        return

    opciones = pendientes["id_checklist"].astype(str).tolist()
    etiquetas = {
        str(row["id_checklist"]):
        f"{row['fase']} · {row['carpeta']} · {row['tipo_documental']}"
        for _, row in pendientes.iterrows()
    }
    id_checklist = st.selectbox(
        "Tipo documental pendiente",
        opciones,
        format_func=lambda valor: etiquetas.get(valor, valor),
    )
    decision = st.radio(
        "Aplicabilidad",
        ["Aplica", "No aplica"],
        horizontal=True,
    )
    justificacion = st.text_area(
        "Justificación",
        disabled=decision != "No aplica",
    )
    if st.button("Guardar aplicabilidad", type="primary"):
        checklist_df = st.session_state.data_m06["checklist"].copy()
        mask = checklist_df["id_checklist"].astype(str).eq(id_checklist)
        if decision == "No aplica":
            try:
                marcar_no_aplica(id_checklist, justificacion)
                st.success("El documento fue marcado como No aplica.")
                st.rerun()
            except ValueError as error:
                st.error(str(error))
        else:
            checklist_df.loc[mask, "aplicabilidad"] = "Aplica"
            checklist_df.loc[mask, "justificacion_no_aplica"] = ""
            checklist_df.loc[mask, "cumple"] = False
            checklist_df.loc[mask, "fecha_actualizacion"] = ahora()
            st.session_state.data_m06["checklist"] = checklist_df
            recalcular_progreso_expediente(id_exp)
            st.success("El documento fue marcado como aplicable.")
            st.rerun()


# ============================================================
# 11. ÍNDICE Y REVISIÓN
# ============================================================

def construir_indice_documental() -> pd.DataFrame:
    actualizar_estados_vigencia()
    docs = st.session_state.data_m06["documentos"].copy()
    relaciones = st.session_state.data_m06["relaciones_documento"].copy()
    if docs.empty:
        return docs

    if relaciones.empty:
        docs["entidades_relacionadas"] = ""
        return docs

    resumen = (
        relaciones.assign(
            relacion=lambda df: (
                df["tipo_entidad"].astype(str)
                + ": "
                + df["id_entidad"].astype(str)
            )
        )
        .groupby("id_documento")["relacion"]
        .apply(lambda serie: " | ".join(dict.fromkeys(serie)))
        .reset_index(name="entidades_relacionadas")
    )
    return docs.merge(resumen, on="id_documento", how="left")


def pantalla_indice() -> None:
    st.markdown("### Índice documental")
    st.markdown(
        '<div class="sir-help">'
        'Consulta consolidada de documentos, versiones, vigencia y relaciones.'
        '</div>',
        unsafe_allow_html=True,
    )

    df = construir_indice_documental()
    if df.empty:
        st.info("Todavía no hay documentos registrados.")
        return

    c1, c2, c3, c4 = st.columns(4)
    texto = c1.text_input(
        "Buscar",
        placeholder="ID, archivo, entidad, carpeta...",
    )
    niveles = c2.multiselect(
        "Nivel",
        sorted(df["nivel_principal"].dropna().astype(str).unique()),
    )
    fases = c3.multiselect(
        "Fase",
        sorted(df["fase"].dropna().astype(str).unique()),
    )
    solo_vigentes_version = c4.toggle(
        "Solo versiones vigentes",
        value=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    carpetas = c1.multiselect(
        "Carpeta",
        sorted(df["carpeta"].dropna().astype(str).unique()),
    )
    tipos = c2.multiselect(
        "Tipo documental",
        sorted(df["tipo_documental"].dropna().astype(str).unique()),
    )
    revisiones = c3.multiselect(
        "Revisión",
        sorted(df["estado_revision"].dropna().astype(str).unique()),
    )
    vigencias = c4.multiselect(
        "Vigencia",
        ESTADOS_VIGENCIA,
    )

    vista = df.copy()
    filtros = [
        ("nivel_principal", niveles),
        ("fase", fases),
        ("carpeta", carpetas),
        ("tipo_documental", tipos),
        ("estado_revision", revisiones),
        ("estado_vigencia", vigencias),
    ]
    for campo, valores in filtros:
        if valores:
            vista = vista[vista[campo].astype(str).isin(valores)]

    if solo_vigentes_version:
        vista = vista[vista["es_version_vigente"].apply(normalizar_bool)]

    if texto.strip():
        consulta = texto.strip().lower()
        columnas_busqueda = [
            "id_documento", "id_serie_documental",
            "id_expediente_principal", "id_entidad_principal",
            "fase", "carpeta", "tipo_documental", "nombre_archivo",
            "entidades_relacionadas", "observaciones_carga",
        ]
        mascara = pd.Series(False, index=vista.index)
        for columna in columnas_busqueda:
            if columna in vista.columns:
                mascara |= (
                    vista[columna]
                    .fillna("")
                    .astype(str)
                    .str.lower()
                    .str.contains(consulta, regex=False)
                )
        vista = vista[mascara]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Resultados", len(vista))
    c2.metric(
        "Documentos únicos",
        vista["id_serie_documental"].nunique(),
    )
    c3.metric(
        "Vencidos",
        int(vista["estado_vigencia"].astype(str).eq("Vencido").sum()),
    )
    c4.metric(
        "Próximos a vencer",
        int(
            vista["estado_vigencia"]
            .astype(str)
            .eq("Próximo a vencer")
            .sum()
        ),
    )

    columnas = [
        "id_documento", "id_serie_documental", "version",
        "nivel_principal", "id_entidad_principal", "fase", "carpeta",
        "tipo_documental", "nombre_archivo", "fecha_documento",
        "fecha_vencimiento", "estado_vigencia", "estado_revision",
        "confidencialidad", "entidades_relacionadas", "ruta_archivo",
    ]
    st.dataframe(
        vista[columnas].sort_values(
            ["fecha_documento", "id_serie_documental", "version"],
            ascending=[False, True, False],
        ),
        use_container_width=True,
        hide_index=True,
        column_config={
            "ruta_archivo": st.column_config.LinkColumn(
                "Documento",
                display_text="Abrir",
            ),
        },
    )

    csv = vista[columnas].to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "Descargar resultados en CSV",
        csv,
        "indice_documental_m06_v8.csv",
        "text/csv",
        use_container_width=True,
    )


def bandeja_revision() -> None:
    actualizar_estados_vigencia()
    st.markdown("### Bandeja de revisión documental")
    usuario = st.session_state.usuario_actual
    docs = st.session_state.data_m06["documentos"]

    pendientes = docs[
        docs["usuario_revisor_asignado"].astype(str).eq(usuario)
        & docs["estado_revision"].astype(str).isin(
            ["Pendiente de revisión", "En revisión", "Observado"]
        )
    ].copy() if not docs.empty else docs

    if pendientes.empty:
        st.info("No tienes documentos pendientes de revisión.")
        return

    opciones = pendientes["id_documento"].astype(str).tolist()
    etiquetas = {
        str(row["id_documento"]):
        f"{row['tipo_documental']} · v{row['version']} · {row['estado_vigencia']}"
        for _, row in pendientes.iterrows()
    }
    id_documento = st.selectbox(
        "Documento asignado",
        opciones,
        format_func=lambda valor: etiquetas.get(valor, valor),
    )
    doc = pendientes[
        pendientes["id_documento"].astype(str).eq(id_documento)
    ].iloc[0].to_dict()

    c1, c2, c3 = st.columns(3)
    c1.info(f"**Nivel:** {doc['nivel_principal']}")
    c2.info(f"**Entidad:** {doc['id_entidad_principal']}")
    c3.info(f"**Vigencia:** {doc['estado_vigencia']}")

    st.write(
        f"**Documento:** {doc['tipo_documental']} · "
        f"**Versión:** {doc['version']}"
    )
    st.write(
        f"**Fecha de vencimiento:** "
        f"{doc.get('fecha_vencimiento', 'No aplica')}"
    )

    ruta = str(doc.get("ruta_archivo") or "")
    if ruta.startswith(("http://", "https://")):
        st.link_button("Abrir documento", ruta)
    elif ruta:
        st.code(ruta)

    with st.form(f"revision_{id_documento}"):
        resultado = st.selectbox(
            "Resultado",
            ["Aprobado", "Observado", "Rechazado"],
        )
        observaciones = st.text_area("Observaciones del revisor")
        requiere = st.checkbox("Requiere subsanación")
        enviar = st.form_submit_button(
            "Registrar revisión",
            type="primary",
            use_container_width=True,
        )

    if enviar:
        if resultado != "Aprobado" and not observaciones.strip():
            st.error(
                "Debe registrar observaciones cuando el documento no es aprobado."
            )
        else:
            try:
                registrar_revision(
                    id_documento,
                    resultado,
                    observaciones,
                    requiere,
                )
                st.success("Revisión registrada.")
                st.rerun()
            except ValueError as error:
                st.error(str(error))


# ============================================================
# 12. PANTALLAS POR NIVEL
# ============================================================

def metricas_generales() -> None:
    actualizar_estados_vigencia()
    expedientes = st.session_state.data_m06["expedientes"]
    docs = st.session_state.data_m06["documentos"]

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Expedientes", len(expedientes))
    c2.metric(
        "Documentos únicos",
        docs["id_serie_documental"].nunique() if not docs.empty else 0,
    )
    c3.metric(
        "Pendientes",
        int(
            docs["estado_revision"]
            .astype(str)
            .eq("Pendiente de revisión")
            .sum()
        ) if not docs.empty else 0,
    )
    c4.metric(
        "Vencidos",
        int(
            docs["estado_vigencia"].astype(str).eq("Vencido").sum()
        ) if not docs.empty else 0,
    )
    c5.metric(
        "Próximos a vencer",
        int(
            docs["estado_vigencia"]
            .astype(str)
            .eq("Próximo a vencer")
            .sum()
        ) if not docs.empty else 0,
    )


def pantalla_nivel(nivel: str) -> None:
    st.markdown(f"### {nivel}")
    st.markdown(
        '<div class="sir-help">'
        'Los datos de la entidad provienen de módulos maestros. '
        'El M06 crea y administra únicamente el expediente y sus documentos.'
        '</div>',
        unsafe_allow_html=True,
    )

    vistas = [
        "Resumen",
        "Expediente",
        "Agregar documentos",
        "Documentos",
        "Histórico",
        "Checklist y progreso",
    ]
    vista = st.radio(
        "Vista de trabajo",
        vistas,
        horizontal=True,
        key=f"vista_{nivel}",
    )

    id_entidad = selector_entidad(
        nivel,
        f"selector_{vista}",
        solo_con_expediente=vista != "Expediente",
    )
    if not id_entidad:
        return

    expediente = expediente_existente(nivel, id_entidad)

    if vista == "Expediente":
        formulario_expediente(nivel, id_entidad)
        return

    if not expediente:
        st.warning(
            "La entidad seleccionada no tiene expediente; "
            "primero debe crearlo."
        )
        return

    mostrar_contexto(nivel, id_entidad, expediente)

    if vista == "Resumen":
        crear_checklist_expediente(expediente)
        recalcular_progreso_expediente(expediente["id_expediente"])
        actualizado = expediente_existente(nivel, id_entidad)
        docs = st.session_state.data_m06["documentos"]
        sub = docs[
            docs["id_expediente_principal"].astype(str).eq(
                str(expediente["id_expediente"])
            )
        ]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Estado", actualizado.get("estado_expediente", ""))
        c2.metric("Cargas", len(sub))
        c3.metric(
            "Aprobadas",
            int(sub["estado_revision"].astype(str).eq("Aprobado").sum())
            if not sub.empty else 0,
        )
        c4.metric(
            "Vencidas",
            int(sub["estado_vigencia"].astype(str).eq("Vencido").sum())
            if not sub.empty else 0,
        )

        porcentaje = pd.to_numeric(
            actualizado.get("porcentaje_completitud", 0),
            errors="coerce",
        )
        porcentaje = 0 if pd.isna(porcentaje) else float(porcentaje)
        st.progress(
            min(max(porcentaje / 100, 0), 1),
            text=f"Completitud documental: {porcentaje:.1f}%",
        )

    elif vista == "Agregar documentos":
        formulario_documento(nivel, id_entidad, expediente)
    elif vista == "Documentos":
        tabla_documentos(expediente)
    elif vista == "Histórico":
        vista_historico(expediente)
    elif vista == "Checklist y progreso":
        vista_checklist(expediente)


def mostrar_sidebar() -> str:
    st.sidebar.title("M06 · Controles")

    usuarios_disponibles = (
        [USUARIO_BETA] + USUARIOS
        if MODO_BETA_AUTORREVISION
        else USUARIOS
    )
    st.session_state.usuario_actual = st.sidebar.selectbox(
        "Usuario activo",
        usuarios_disponibles,
        index=0,
        key="selector_usuario_m06",
    )

    st.sidebar.info(
        "Modo beta habilitado. En producción debe desactivarse "
        "la autorrevisión."
    )

    pantalla = st.sidebar.radio(
        "Pantalla",
        ["Índice"] + NIVELES + ["Bandeja de revisión"],
        key="pantalla_m06",
    )

    st.sidebar.markdown("---")
    if st.sidebar.button(
        "Guardar memoria local",
        use_container_width=True,
    ):
        guardar_memoria()
        st.sidebar.success("Memoria guardada.")

    confirmar = st.sidebar.checkbox("Confirmar reinicio total")
    if st.sidebar.button(
        "Reiniciar datos operativos",
        use_container_width=True,
        disabled=not confirmar,
    ):
        st.session_state.data_m06 = asegurar_columnas({})
        guardar_memoria()
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "Las entidades son referencias de otros módulos. "
        "Este módulo no crea personas, hogares, predios ni lugares poblados."
    )
    return pantalla


# ============================================================
# 13. MAIN
# ============================================================

def main() -> None:
    aplicar_estilos()
    inicializar_estado()
    encabezado()

    if st.session_state.get("error_carga_memoria_m06"):
        st.error(
            "No fue posible leer la memoria local: "
            f"{st.session_state['error_carga_memoria_m06']}"
        )

    pantalla = mostrar_sidebar()
    metricas_generales()
    st.markdown("---")

    if pantalla == "Índice":
        pantalla_indice()
    elif pantalla == "Bandeja de revisión":
        bandeja_revision()
    else:
        pantalla_nivel(pantalla)


if __name__ == "__main__":
    main()
