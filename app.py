# Red TB: punto de entrada de la app. Ejecutar con:  streamlit run app.py
# Cada pestaña está en su propio archivo dentro de pestanas/.

import streamlit as st

st.set_page_config(page_title="Red TB", layout="wide", initial_sidebar_state="collapsed")

import algoritmos as a
import datos as d
import fuentes as f
import interfaz as ui
from pestanas import explorar, rutas, tratamiento

ui.aplicar_estilo()

# ---------------------------------------------------------------- Barra superior
ui.html("<div class='barra'><div><b>Red TB</b> &nbsp; <span>Explorador de la red de proteínas de "
        "<i>M. tuberculosis</i> H37Rv</span></div><span>STRING v12.5 · Grupo 3 · Complejidad Algorítmica</span></div>")

col_cifras, col_umbral = st.columns([5, 1], vertical_alignment="center")
umbral = col_umbral.selectbox("Umbral de confianza", [700, 900, 400], label_visibility="collapsed",
                              format_func=lambda u: f"Umbral {u}" + (" (proyecto)" if u == 700 else ""))
red = d.cargar_red(umbral)
d.activar(red)
grafo = red["grafo"]
col_cifras.markdown(
  f"<div class='cifras'><span><b>{ui.miles(len(grafo))}</b> proteínas</span>"
  f"<span><b>{ui.miles(a.contar_aristas(grafo))}</b> interacciones</span>"
  f"<span><b>{red['componentes']}</b> componentes conexas</span>"
  f"<span><b>{ui.miles(len(red['arbol']))}</b> interacciones en el MST</span></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------- Pestañas
tab_explorar, tab_rutas, tab_tratamiento = st.tabs(["Explorar", "Rutas", "Tratamiento"])
with tab_explorar:
  explorar.mostrar(red, umbral)
with tab_rutas:
  rutas.mostrar(red, umbral)
with tab_tratamiento:
  tratamiento.mostrar(red, umbral)

ui.html(f"<div class='aviso'>{f.AVISO}</div>")
