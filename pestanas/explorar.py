# Pestaña 1 · Explorar: la red alrededor de una proteína (BFS) o el esqueleto (MST, Kruskal),
# con la ficha de la proteína.

import time

import streamlit as st

import algoritmos as a
import datos as d
import fuentes as f
import interfaz as ui


def mostrar(red, umbral):
  grafo = red["grafo"]
  proteinas = d.proteinas_elegibles(grafo)
  desc = d.descripciones()
  izq, centro, der = st.columns([1.1, 3, 1.4], gap="small")

  # ---------------------------------------------------------------- Controles
  with izq:
    with st.container(border=True):
      ui.cabecera("Controles")
      p = st.selectbox("Proteína", proteinas, index=proteinas.index("rpoB") if "rpoB" in proteinas else 0,
                       help="Dianas de fármacos y proteínas de resistencia")
      vista = st.radio("Vista", ["Red completa (BFS)", "Esqueleto (MST, Kruskal)"])
      if vista.startswith("Red"):
        niveles = st.slider("Niveles alrededor de la proteína", 1, 2, 1)
      else:
        pasos = st.slider("Pasos dentro del árbol", 2, 12, 4)

  # ---------------------------------------------------------------- Grafo
  with centro:
    with st.container(border=True):
      inicio = time.perf_counter()
      if vista.startswith("Red"):
        path, nivel = a.bfs(grafo, p, max_nivel=niveles)
        t_bfs = time.perf_counter() - inicio
        aristas = []
        if niveles == 1:                       # todas las interacciones entre las vecinas
          for u in nivel:
            for v in grafo[u]:
              if v in nivel and u < v:
                aristas.append((u, v))
        else:                                  # con 2 niveles son demasiadas: solo el árbol del BFS
          for v in nivel:
            if path[v] != -1:
              aristas.append((path[v], v))
        colores = {v: (ui.AZUL if nivel[v] == 1 else ui.VERDE) for v in nivel}
        colores[p] = ui.NARANJA
        ui.cabecera(f"Entorno de {p} · nivel {niveles}", f"{ui.miles(len(nivel))} proteínas · {ui.miles(len(aristas))} interacciones")
        ui.dibujar(nivel.keys(), aristas, colores, {p})
        ui.leyenda([(ui.NARANJA, "Proteína elegida", "punto"), (ui.AZUL, "Nivel 1", "punto"), (ui.VERDE, "Nivel 2", "punto")])
      else:
        path, nivel = a.bfs(red["mst"], p, max_nivel=pasos)
        t_bfs = time.perf_counter() - inicio
        aristas = [(u, v) for u in nivel for v in red["mst"][u] if v in nivel and u < v]
        colores, etiquetas, tamanos = {}, {p}, {p: 24}
        for v in nivel:                        # como en la red completa: nivel 1 azul, nivel 2 verde
          if nivel[v] == 1:
            colores[v], tamanos[v] = ui.AZUL, 14
            etiquetas.add(v)                   # las vecinas directas en el árbol llevan su nombre
          elif nivel[v] == 2:
            colores[v], tamanos[v] = ui.VERDE, 9
        for lista in f.PROTEINAS.values():     # dianas de fármacos en naranja
          for x in lista:
            if x in nivel:
              colores[x] = ui.NARANJA
              etiquetas.add(x)
        for x in f.DESTINOS:                   # proteínas de resistencia en morado
          if x in nivel and colores.get(x) != ui.NARANJA:
            colores[x] = ui.MORADO
            etiquetas.add(x)
        colores[p] = ui.NARANJA
        ui.cabecera(f"Esqueleto alrededor de {p} · {pasos} pasos", f"{ui.miles(len(nivel))} proteínas")
        ui.dibujar(nivel.keys(), aristas, colores, etiquetas, tamanos)
        ui.leyenda([(ui.NARANJA, "Dianas de fármacos", "punto"), (ui.MORADO, "Proteínas de resistencia", "punto"),
                    (ui.AZUL, "A 1 paso en el árbol", "punto"), (ui.VERDE, "A 2 pasos", "punto"),
                    (ui.GRIS, "Más lejanas", "punto")])
      ui.html("<div class='nota'>Zoom con la rueda · arrastra los nodos · pasa el mouse sobre una interacción para ver su puntaje.</div>")

  # ---------------------------------------------------------------- Ficha de la proteína
  with der:
    with st.container(border=True):
      ui.cabecera("Ficha de la proteína")
      ui.html(f"<div class='dato'>{p}</div><div class='nota'>{desc.get(p, '')}</div>")
      m1, m2 = st.columns(2)
      m1.metric("Vecinas en la red", len(grafo[p]))
      m2.metric("Vecinas en el MST", len(red["mst"][p]))
      farmacos = d.farmacos_de(p)
      ui.html(f"<div class='nota'><b>Fármacos asociados (OMS, 2021):</b> {', '.join(farmacos) if farmacos else '—'}</div>")
      vecinas = sorted(grafo[p], key=lambda v: -a.peso[(p, v)])[:6]
      ui.html("<div style='height:8px'></div>")
      ui.tabla(["Vecinas más confiables", "Puntaje"], [[v, a.peso[(p, v)]] for v in vecinas], numericas=(1,))

  with st.expander("Algoritmo y costo", expanded=True):
    ui.tabla(["Algoritmo", "Complejidad", "Tiempo"], [
      ["BFS con profundidad limitada", "O(|V| + |E|)", ui.duracion(t_bfs)],
      ["Kruskal con unión por rango (al cargar)", "O(|E| log |E|)", ui.duracion(red["t_kruskal"])],
    ], numericas=(2,))
