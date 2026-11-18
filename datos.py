# Cálculos que usan las pestañas. Llaman a algoritmos.py y guardan el resultado en caché
# para no repetirlos cada vez que el usuario toca un control.

import gzip
import time

import streamlit as st

import algoritmos as a
import fuentes as f


@st.cache_resource
def cargar_red(umbral):
  """Grafo, Kruskal y componentes: se calculan una sola vez por umbral."""
  grafo, peso = a.cargar(umbral)
  inicio = time.perf_counter()
  arbol = a.kruskal(grafo)
  t_kruskal = time.perf_counter() - inicio
  return {
    "grafo": grafo, "peso": peso, "labels": a.labels, "w2i": a.w2i,
    "arbol": arbol, "mst": a.lista_adyacencia(grafo, arbol), "t_kruskal": t_kruskal,
    "componentes": len(a.componentes_conexas(grafo, "bfs")),
  }


def activar(red):
  """algoritmos.py usa variables globales (peso, labels, w2i): las apuntamos a la red elegida."""
  a.grafo, a.peso, a.labels, a.w2i = red["grafo"], red["peso"], red["labels"], red["w2i"]


@st.cache_resource
def descripciones():
  """Primera frase de la descripción de cada proteína en STRING."""
  desc = {}
  with gzip.open(a.ARCHIVO_INFO, "rt", encoding="utf-8") as archivo:
    archivo.readline()
    for linea in archivo:
      datos = linea.rstrip("\n").split("\t")
      desc[datos[1]] = datos[3].split(";")[0]
  return desc


def proteinas_elegibles(grafo):
  """Dianas de fármacos y proteínas de resistencia que están en la red."""
  proteinas = set(f.DESTINOS)
  for lista in f.PROTEINAS.values():
    proteinas.update(lista)
  return sorted(p for p in proteinas if p in grafo)


def farmacos_de(proteina):
  return [nombre for nombre, genes in f.GENES_OMS.items() if proteina in genes]


def bloqueadas(esquema, s, t):
  """Proteínas de los fármacos del esquema, sin contar el origen ni el destino."""
  quitar = set()
  for farmaco in f.ESQUEMAS[esquema]:
    for p in f.PROTEINAS[farmaco]:
      quitar.add(p)
  quitar.discard(s)
  quitar.discard(t)
  return tuple(sorted(quitar))


@st.cache_data(show_spinner=False)
def calcular_rutas(umbral, s, t, L, conf_min, bloquear_directa, quitar):
  """UCS, alternativa, backtracking, Ford-Fulkerson y ruta en el MST para el par s -> t.
  quitar = proteínas bloqueadas (pestaña Tratamiento)."""
  red = cargar_red(umbral)
  activar(red)
  G = red["grafo"]
  if quitar:
    G = a.sin_proteinas(G, set(quitar))
  if bloquear_directa:
    G = a.sin_arista(G, s, t)

  inicio = time.perf_counter()
  ruta, conf = a.ucs(G, s, t)
  t_ucs = time.perf_counter() - inicio
  alternativa, conf_alt = a.ucs(a.sin_arista(G, s, t), s, t)

  # Poda previa: una interacción con puntaje/1000 < conf_min nunca puede estar en una ruta válida
  inicio = time.perf_counter()
  G_bt = {u: [v for v in G[u] if a.peso[(u, v)] / 1000 >= conf_min] for u in G}
  n_rutas, cuenta, llamadas = a.rutas_backtracking(G_bt, s, t, L, conf_min)
  t_bt = time.perf_counter() - inicio
  mejores = a.mejores_rutas(G_bt, s, t, L, conf_min, 6)

  inicio = time.perf_counter()
  flujo = a.FordFulkerson(G, s, t)
  t_ff = time.perf_counter() - inicio

  path, nivel = a.bfs(red["mst"], s)
  ruta_mst = a.reconstruir_ruta(path, t) if t in path else []

  return {
    "ruta": ruta, "conf": conf, "alternativa": alternativa, "conf_alt": conf_alt,
    "n_rutas": n_rutas, "intermedias": a.intermedias_frecuentes(cuenta, 8), "cuenta": cuenta,
    "llamadas": llamadas, "mejores": mejores, "flujo": flujo, "ruta_mst": ruta_mst,
    "t_ucs": t_ucs, "t_bt": t_bt, "t_ff": t_ff,
  }


def subgrafo_rutas(G, r, s, t, extra=()):
  """Proteínas y aristas a dibujar: origen, destino, rutas UCS y las intermedias más frecuentes."""
  nodos = {s, t}
  nodos.update(r["ruta"])
  nodos.update(r["alternativa"])
  for x, n in r["intermedias"]:
    nodos.add(x)
  nodos.update(extra)
  nodos = {u for u in nodos if u in G}
  aristas = []
  for u in nodos:
    for v in G[u]:
      if v in nodos and u < v:
        aristas.append((u, v))
  return nodos, aristas
