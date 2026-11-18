# Pestaña 3 · Tratamiento: se bloquean las proteínas de un esquema de la NTS N° 221
# y se comparan las rutas entre dos proteínas antes y después.

import streamlit as st

import datos as d
import fuentes as f
import interfaz as ui


def mostrar(red, umbral):
  grafo = red["grafo"]
  proteinas = d.proteinas_elegibles(grafo)
  izq, centro, der = st.columns([1.1, 3, 1.4], gap="small")

  # ---------------------------------------------------------------- Controles
  with izq:
    with st.container(border=True):
      ui.cabecera("Simulación")
      esquema = st.radio("Esquema (NTS N° 221, Tabla N° 10)", list(f.ESQUEMAS), index=3)
      ui.html("<div class='nota'>Solo esquemas de la norma: no se pueden armar combinaciones libres.</div>")
      c1, c2 = st.columns(2)
      s = c1.selectbox("Origen", proteinas, index=proteinas.index("rpoB") if "rpoB" in proteinas else 0, key="trat_s")
      destinos = [p for p in proteinas if p != s]
      t = c2.selectbox("Destino", destinos, index=destinos.index("katG") if "katG" in destinos else 0, key="trat_t")
      quitar = d.bloqueadas(esquema, s, t)
      ui.html("<b style='font-size:12px'>Proteínas bloqueadas</b><br>" +
              "".join(f"<span class='chip'>{p}</span>" for p in quitar))

  with st.spinner("Simulando..."):
    antes = d.calcular_rutas(umbral, s, t, 3, 0.90, False, ())
    despues = d.calcular_rutas(umbral, s, t, 3, 0.90, False, quitar)

  # ---------------------------------------------------------------- Grafo y comparación de esquemas
  with centro:
    with st.container(border=True):
      ui.cabecera(f"{s} → {t} con el esquema {esquema.split(':')[0]}",
                  f"{antes['n_rutas']} → {despues['n_rutas']} rutas · L ≤ 3 · confianza ≥ 0,90")
      nodos, aristas = d.subgrafo_rutas(grafo, antes, s, t, [p for p in quitar if p in antes["cuenta"]])
      colores = {x: ui.AZUL for x in nodos}  # todas las intermedias en azul (también las de la alternativa)
      for p in quitar:
        colores[p] = ui.ROJO
      colores[s], colores[t] = ui.NARANJA, ui.MORADO
      estilos = {}
      for u, v in aristas:                     # aristas que tocan una proteína bloqueada
        if u in quitar or v in quitar:
          estilos[(u, v)] = {"color": "#e8a59b", "dashes": True}
      for u, v in zip(despues["ruta"], despues["ruta"][1:]):
        estilos[(u, v)] = {"color": ui.NARANJA, "width": 5}
      maximo = max(antes["cuenta"].values(), default=1)
      tamanos = {x: 8 + 22 * despues["cuenta"].get(x, 0) / maximo for x in nodos}
      for p in quitar:
        tamanos[p] = 14
      tamanos[s], tamanos[t] = 22, 20
      ui.dibujar(nodos, aristas, colores, set(nodos), tamanos, estilos)
      ui.leyenda([(ui.ROJO, "Bloqueada por el esquema", "punto"), ("#e8a59b", "Ruta que desaparece", "guion"),
                  (ui.NARANJA, "Ruta UCS después del bloqueo", "linea")])

    with st.container(border=True):
      ui.cabecera(f"Todos los esquemas para {s} → {t}")
      filas = [["Sin tratamiento", "—", antes["n_rutas"], antes["flujo"]]]
      for nombre in f.ESQUEMAS:
        q = d.bloqueadas(nombre, s, t)
        r = d.calcular_rutas(umbral, s, t, 3, 0.90, False, q)
        ini, fin = ("<b>", "</b>") if nombre == esquema else ("", "")
        filas.append([f"{ini}{nombre.split(':')[0]}{fin}", ", ".join(q), f"{ini}{r['n_rutas']}{fin}", f"{ini}{r['flujo']}{fin}"])
      ui.tabla(["Esquema", "Proteínas bloqueadas", "Rutas", "Caminos indep."], filas, numericas=(2, 3))

  # ---------------------------------------------------------------- Antes y después
  with der:
    with st.container(border=True):
      ui.cabecera("Antes y después")
      x0 = antes["intermedias"][0][0] if antes["intermedias"] else None
      filas = [
        ["Ruta UCS", ui.coma(antes["conf"]), ui.coma(despues["conf"])],
        ["Rutas alternativas", antes["n_rutas"], despues["n_rutas"]],
        ["Caminos independientes", antes["flujo"], despues["flujo"]],
      ]
      if x0:
        filas.append([f"Rutas con {x0}", antes["cuenta"].get(x0, 0), despues["cuenta"].get(x0, 0)])
      ui.tabla(["", "Antes", "Después"], filas, numericas=(1, 2))
      st.divider()
      igual = antes["ruta"] == despues["ruta"]
      texto = (f"La ruta más confiable {'no cambia' if igual else 'cambia a ' + ' → '.join(despues['ruta'])}. "
               f"El esquema elimina {antes['n_rutas'] - despues['n_rutas']} de {antes['n_rutas']} rutas alternativas.")
      if x0 and x0 not in quitar:
        texto += (f" <b>{x0}</b> sigue en {despues['cuenta'].get(x0, 0)} de las {despues['n_rutas']} restantes: "
                  "ningún fármaco del esquema la bloquea.")
      ui.html(f"<b style='font-size:13px'>Qué muestra</b><div class='nota'>{texto}</div>")
      st.divider()
      ui.html("<div class='nota'>Es una hipótesis computacional sobre la red, no una predicción clínica. "
              "El origen y el destino nunca se bloquean.</div>")

  with st.expander("Algoritmo y costo", expanded=True):
    ui.tabla(["Paso", "Complejidad"], [
      ["Quitar las proteínas del esquema (sin_proteinas)", "O(|V| + |E|)"],
      ["UCS, backtracking y Ford-Fulkerson, antes y después", "Las de cada algoritmo"],
    ])
