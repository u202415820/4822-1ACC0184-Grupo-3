# Piezas visuales que usan todas las pestañas: colores, estilo, tablas, leyendas y el dibujo del grafo.

import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network

import algoritmos as a

# ---------------------------------------------------------------- Colores (los mismos del Colab)
NARANJA = "#eb6834"   # proteína elegida, origen y dianas
AZUL = "#2a78d6"      # nivel 1 / intermedias
VERDE = "#1baf7a"     # nivel 2
MORADO = "#8e44ad"    # proteínas de resistencia (destino)
ROJO = "#c0392b"      # bloqueadas por un esquema
GRIS = "#9aa5b1"      # resto

ESTILO = """
<style>
html, body, .stApp, .stMarkdown, button, input, select, textarea, table { font-family: Arial, Helvetica, sans-serif; }
.block-container { padding-top: 0.8rem; padding-bottom: 1rem; max-width: 1500px; }
header[data-testid="stHeader"] { display: none; }
.barra { background: #1f2a37; color: #e4e9ee; padding: 12px 20px; border-radius: 4px; display: flex;
         justify-content: space-between; align-items: baseline; flex-wrap: wrap; gap: 8px; }
.barra b { font-size: 18px; letter-spacing: .02em; }
.barra span { color: #aab6c3; font-size: 13px; }
.cifras { display: flex; flex-wrap: wrap; gap: 26px; font-size: 13px; color: #3e4c59; padding: 8px 4px; }
.ph { font-size: 11px; font-weight: bold; letter-spacing: .08em; text-transform: uppercase; color: #52606d;
      border-bottom: 1px solid #cfd6dd; padding-bottom: 6px; margin-bottom: 8px; display: flex;
      justify-content: space-between; flex-wrap: wrap; gap: 6px; }
.ph i { font-style: normal; text-transform: none; letter-spacing: 0; }
.leyenda { display: flex; flex-wrap: wrap; gap: 16px; font-size: 12px; color: #3e4c59; padding-top: 6px; }
.punto { width: 12px; height: 12px; border-radius: 50%; display: inline-block; vertical-align: -1px; margin-right: 5px; }
.pill { display: inline-block; padding: 2px 9px; border-radius: 999px; color: #fff; font-size: 13px; margin: 2px 0; }
.chip { display: inline-block; padding: 3px 8px; border-radius: 3px; background: #fbe3e0; color: #9b2c1f;
        border: 1px solid #f0b4ab; font-size: 12px; margin: 0 4px 4px 0; }
.dato { font-size: 24px; font-weight: bold; color: #1f2933; }
.nota { font-size: 12px; color: #52606d; line-height: 1.45; }
.barra-h { height: 12px; background: #2a78d6; border-radius: 2px; display: inline-block; vertical-align: middle; }
table.t { border-collapse: collapse; width: 100%; font-size: 13px; background: #fff; }
table.t td, table.t th { padding: 6px 9px; border-bottom: 1px solid #e1e6eb; text-align: left; }
table.t th { font-size: 11px; color: #52606d; background: #eef1f4; }
table.t td.n, table.t th.n { text-align: right; font-variant-numeric: tabular-nums; }
.aviso { background: #fff7e0; border: 1px solid #e8cf8a; border-radius: 4px; padding: 9px 12px;
         font-size: 12.5px; color: #6b4e00; margin-top: 10px; }
</style>
"""


def aplicar_estilo():
  st.markdown(ESTILO, unsafe_allow_html=True)


def html(texto):
  st.markdown(texto, unsafe_allow_html=True)


def cabecera(titulo, detalle=""):
  html(f"<div class='ph'><span>{titulo}</span><i>{detalle}</i></div>")


def miles(n):
  return f"{n:,}".replace(",", " ")


def coma(x, d=3):
  return f"{x:.{d}f}".replace(".", ",")


def duracion(segundos):
  if segundos < 1:
    return coma(segundos * 1000, 2) + " ms"
  return coma(segundos, 2) + " s"


def tabla(columnas, filas, numericas=()):
  """Tabla HTML simple. numericas = índices de las columnas alineadas a la derecha."""
  cab = "".join(f"<th class='{'n' if i in numericas else ''}'>{c}</th>" for i, c in enumerate(columnas))
  cuerpo = ""
  for fila in filas:
    cuerpo += "<tr>" + "".join(f"<td class='{'n' if i in numericas else ''}'>{c}</td>" for i, c in enumerate(fila)) + "</tr>"
  html(f"<table class='t'><thead><tr>{cab}</tr></thead><tbody>{cuerpo}</tbody></table>")


def leyenda(items):
  """items: lista de (color, texto, forma) con forma 'punto', 'linea' o 'guion'."""
  partes = []
  for color, texto, forma in items:
    if forma == "punto":
      partes.append(f"<span><span class='punto' style='background:{color}'></span>{texto}</span>")
    elif forma == "linea":
      partes.append(f"<span><span style='display:inline-block;width:22px;height:4px;background:{color};vertical-align:3px;margin-right:5px'></span>{texto}</span>")
    else:
      partes.append(f"<span><span style='display:inline-block;width:22px;border-top:2px dashed {color};vertical-align:3px;margin-right:5px'></span>{texto}</span>")
  html("<div class='leyenda'>" + "".join(partes) + "</div>")


def pills(ruta, s, t):
  partes = []
  for p in ruta:
    color = NARANJA if p == s else MORADO if p == t else AZUL
    partes.append(f"<span class='pill' style='background:{color}'>{p}</span>")
  return " → ".join(partes)


# ---------------------------------------------------------------- Dibujo interactivo (pyvis)
def dibujar(nodos, aristas, colores, etiquetas, tamanos=None, estilos=None, alto=520):
  """nodos: proteínas · aristas: pares (u, v) · colores/tamanos: por proteína ·
  etiquetas: proteínas que muestran su nombre · estilos: por arista {color, width, dashes}."""
  tamanos = tamanos or {}
  estilos = estilos or {}
  net = Network(height=f"{alto}px", width="100%", bgcolor="#ffffff", cdn_resources="in_line")
  for u in nodos:
    net.add_node(u, label=u if u in etiquetas else " ", title=u, color=colores.get(u, GRIS),
                 size=tamanos.get(u, 16 if u in etiquetas else 6),
                 font={"face": "Arial", "size": 14, "color": "#1f2933"})
  for u, v in aristas:
    e = estilos.get((u, v)) or estilos.get((v, u)) or {}
    net.add_edge(u, v, title=f"{u} – {v}: {a.peso[(u, v)]}", color=e.get("color", "#c3cad3"),
                 width=e.get("width", 1), dashes=e.get("dashes", False))
  net.set_options("""
  { "physics": {"solver": "forceAtlas2Based", "stabilization": {"iterations": 300}},
    "edges": {"smooth": false},
    "interaction": {"hover": true, "tooltipDelay": 80} }
  """)
  pagina = net.generate_html()
  # 1) Cuando termina de acomodarse, se apaga la física: el grafo deja de moverse.
  # 2) Las pestañas ocultas dibujan el grafo con ancho 0: al mostrarse, se vuelve a centrar.
  pagina = pagina.replace("</body>", """
<script>
function centrar() { if (typeof network !== "undefined") { network.redraw(); network.fit(); } }
function congelar() { if (typeof network !== "undefined") { network.setOptions({ physics: false }); centrar(); } }
if (typeof network !== "undefined") { network.once("stabilizationIterationsDone", congelar); }
setTimeout(congelar, 3000);
window.addEventListener("resize", centrar);
</script>
</body>""")
  if hasattr(st, "iframe"):
    st.iframe(pagina, height=alto + 20)
  else:
    components.html(pagina, height=alto + 20)
