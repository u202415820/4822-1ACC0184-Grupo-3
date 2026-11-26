# Pestaña 2 · Rutas: de la diana de un fármaco a una proteína de resistencia.
# UCS (mejor ruta y alternativa), backtracking (rutas e intermedias), Ford-Fulkerson y la ruta en el MST.

import streamlit as st

import algoritmos as a
import datos as d
import fuentes as f
import interfaz as ui


def mostrar(red, umbral):
  grafo = red["grafo"]
  izq, centro, der = st.columns([1.1, 3, 1.4], gap="small")

  # ---------------------------------------------------------------- Controles
  with izq:
    with st.container(border=True):
      ui.cabecera("Búsqueda")
      farmaco = st.selectbox("Fármaco (origen)", list(f.PROTEINAS),
                             format_func=lambda x: f"{x} → {f.PROTEINAS[x][0]}")
      s = f.PROTEINAS[farmaco][0]
      destinos = [p for p in f.DESTINOS if p != s and p in grafo]
      t = st.selectbox("Proteína de resistencia (destino)", destinos,
                       index=destinos.index("katG") if "katG" in destinos else 0)
      L = st.slider("Longitud máxima L", 1, 4, 3, help="Con L = 4 el backtracking puede tardar varios segundos")
      conf_min = st.slider("Confianza mínima de la ruta", 0.80, 1.00, 0.90, 0.01,
                           help="El umbral filtra cada interacción por separado. Este valor filtra la ruta completa: "
                                "su confianza es el producto de los puntajes de sus interacciones "
                                "(por ejemplo, 0,75 × 0,75 × 0,75 = 0,42). Las rutas por debajo se descartan.")
      ui.html("<div class='nota'>Confianza de una ruta = producto de los puntajes de sus interacciones / 1000.</div>")
      bloquear = st.checkbox("Bloquear la interacción directa")

  if s not in grafo or t not in grafo:
    st.warning("Con este umbral, el origen o el destino no está en la red.")
    return

  with st.spinner("Buscando rutas..."):
    r = d.calcular_rutas(umbral, s, t, L, conf_min, bloquear, ())

  # ---------------------------------------------------------------- Grafo y tabla de rutas
  with centro:
    with st.container(border=True):
      ui.cabecera(f"Rutas de {s} a {t}", f"{r['n_rutas']} rutas · L ≤ {L} · confianza ≥ {ui.coma(conf_min, 2)}")
      if not r["ruta"]:
        st.info("No hay ninguna ruta entre estas proteínas.")
      else:
        G_dib = a.sin_arista(grafo, s, t) if bloquear else grafo
        nodos, aristas = d.subgrafo_rutas(G_dib, r, s, t)
        maximo = max([n for x, n in r["intermedias"]], default=1)
        tamanos = {x: 8 + 22 * r["cuenta"].get(x, 0) / maximo for x in nodos}   # tamaño = n.º de rutas
        tamanos[s], tamanos[t] = 22, 20
        colores = {x: ui.AZUL for x in nodos}  # todas las intermedias en azul (también las de la alternativa)
        colores[s], colores[t] = ui.NARANJA, ui.MORADO
        estilos = {}
        for u, v in zip(r["alternativa"], r["alternativa"][1:]):
          estilos[(u, v)] = {"color": ui.NARANJA, "width": 2, "dashes": True}
        for u, v in zip(r["ruta"], r["ruta"][1:]):
          estilos[(u, v)] = {"color": ui.NARANJA, "width": 5}
        ui.dibujar(nodos, aristas, colores, set(nodos), tamanos, estilos)
        ui.leyenda([(ui.NARANJA, "Origen (diana)", "punto"), (ui.MORADO, "Destino (resistencia)", "punto"),
                    (ui.NARANJA, "Ruta UCS", "linea"), (ui.NARANJA, "Alternativa si se bloquea", "guion"),
                    (ui.AZUL, "Intermedias (tamaño = n.º de rutas)", "punto")])

    with st.container(border=True):
      ui.cabecera(f"Rutas encontradas (backtracking) · las {len(r['mejores'])} más confiables de {r['n_rutas']}")
      ui.tabla(["#", "Ruta", "Interacciones", "Confianza"],
               [[i + 1, " – ".join(ruta), len(ruta) - 1, ui.coma(c)] for i, (ruta, c) in enumerate(r["mejores"])],
               numericas=(0, 2, 3))

  # ---------------------------------------------------------------- Resultados
  with der:
    with st.container(border=True):
      ui.cabecera("Resultados")
      m1, m2 = st.columns(2)
      m1.metric("Rutas encontradas", r["n_rutas"], help=f"Backtracking: rutas de hasta {L} interacciones "
                f"con confianza ≥ {ui.coma(conf_min, 2)}")
      m2.metric("Caminos independientes", r["flujo"], help="Ford-Fulkerson: rutas que no comparten interacciones")
      st.divider()
      ui.html("<b style='font-size:13px'>Intermedias más frecuentes</b>")
      if r["intermedias"]:
        maximo = r["intermedias"][0][1]
        filas = ""
        for x, n in r["intermedias"][:5]:
          filas += (f"<div style='display:flex;align-items:center;gap:8px;font-size:12.5px;margin:3px 0'>"
                    f"<span style='width:52px'>{x}</span><span class='barra-h' style='width:{max(6, 150 * n / maximo):.0f}px'></span>{n}</div>")
        ui.html(filas)
        x0, n0 = r["intermedias"][0]
        ui.html(f"<div class='nota'><b>{x0}</b> está en {n0} de {r['n_rutas']} rutas: proteína candidata para investigación.</div>")
      else:
        ui.html("<div class='nota'>No hay rutas con intermedias para estos parámetros.</div>")
      st.divider()
      if r["ruta"]:
        ui.html(f"<b style='font-size:13px'>Ruta más confiable (UCS)</b><br>{ui.pills(r['ruta'], s, t)}"
                f"<div class='nota'>confianza {ui.coma(r['conf'])} · {len(r['ruta']) - 1} interacción(es)</div>")
        if r["alternativa"]:
          ui.html(f"<div class='nota' style='margin-top:6px'>Si se bloquea: <b>{' → '.join(r['alternativa'])}</b> · {ui.coma(r['conf_alt'])}</div>")
      st.divider()
      if r["ruta_mst"]:
        texto = " → ".join(r["ruta_mst"]) if len(r["ruta_mst"]) <= 6 else " → ".join(r["ruta_mst"][:3]) + " → … → " + t
        ui.html(f"<b style='font-size:13px'>La misma conexión en el esqueleto (MST)</b>"
                f"<div class='nota'>{texto} · <b>{len(r['ruta_mst']) - 1} pasos</b>. "
                "El árbol conserva un solo camino: sirve para ver la red, no para buscar rutas.</div>")
      st.divider()
      ui.html(f"<div class='nota'>Caminos independientes: grados {s} {len(grafo[s])} · {t} {len(grafo[t])}. "
              "El flujo nunca supera el grado menor.</div>")

  with st.expander("Algoritmo y costo", expanded=True):
    ui.tabla(["Algoritmo", "Complejidad", "Llamadas", "Tiempo"], [
      ["UCS (costo −ln(puntaje/1000))", "O((|V| + |E|) log |V|)", "–", ui.duracion(r["t_ucs"])],
      ["Backtracking con poda", "O(Δ^L)", ui.miles(r["llamadas"]), ui.duracion(r["t_bt"])],
      ["Ford-Fulkerson", "O(f · (|V| + |E|))", "–", ui.duracion(r["t_ff"])],
    ], numericas=(2, 3))
