# Algoritmos del proyecto, copiados del Colab (notebooks/TB2_Grupo3_Caso3.ipynb).
# La lógica es la misma, solo cambia cómo se leen los archivos.

import gzip
import heapq
import math
import os
import sys

sys.setrecursionlimit(10000)

# Ruta a la carpeta data/ sin importar desde dónde se ejecute
CARPETA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
ARCHIVO_INFO = os.path.join(CARPETA, "83332.protein.info.v12.5.txt.gz")
ARCHIVO_LINKS = os.path.join(CARPETA, "83332.protein.links.v12.5.txt.gz")

# Se llenan con cargar()
nombre = {}   # nombre["83332.Rv0667"] = "rpoB"
grafo = {}    # grafo["rpoB"] = ["rpoC", "rpoA", ...]
peso = {}     # peso[("rpoB", "rpoC")] = 999
labels = []   # labels[i] = nombre de la proteína i (para UFDS)
w2i = {}      # w2i["rpoB"] = número de rpoB


def leer_nombres():
  nombres = {}
  with gzip.open(ARCHIVO_INFO, "rt", encoding="utf-8") as f:
    f.readline()  # títulos
    for linea in f:
      datos = linea.split("\t")
      nombres[datos[0]] = datos[1]
  return nombres


def construir_grafo(umbral):
  grafo = {}
  peso = {}
  with gzip.open(ARCHIVO_LINKS, "rt", encoding="utf-8") as f:
    f.readline()  # cabecera
    for linea in f:
      p1, p2, puntaje = linea.split()
      puntaje = int(puntaje)
      if puntaje >= umbral:
        u = nombre[p1]
        v = nombre[p2]
        if u not in grafo:
          grafo[u] = []
        grafo[u].append(v)
        peso[(u, v)] = puntaje
  return grafo, peso


def cargar(umbral=700):
  """Lee los archivos y deja listos grafo, peso, labels y w2i."""
  global nombre, grafo, peso, labels, w2i
  nombre = leer_nombres()
  grafo, peso = construir_grafo(umbral)
  labels = list(grafo.keys())
  w2i = {}
  for i, u in enumerate(labels):
    w2i[u] = i
  return grafo, peso

# El archivo trae cada par 2 veces (A-B y B-A), por eso dividimos entre 2 (siempre sera no dirigido)
def contar_aristas(grafo):
  total = 0
  for u in grafo:
    total += len(grafo[u])
  return total // 2

# nivel[v] = a cuántos pasos está v desde s
# max_nivel = hasta qué profundidad buscamos (profundidad limitada)
def bfs(G, s, max_nivel=None):
  visited = {s: True}
  path = {s: -1}
  nivel = {s: 0}
  queue = [s]

  while queue:
    u = queue.pop(0)  # sacamos el primero de la cola (FIFO)
    if nivel[u] == max_nivel:
      continue        # no seguimos más allá del nivel máximo
    for v in G[u]:
      if v not in visited:
        visited[v] = True
        path[v] = u
        nivel[v] = nivel[u] + 1
        queue.append(v)
  return path, nivel

def dfs(G, s):
  path = {s: -1}
  visited = {}

  def _dfs(u):
    visited[u] = True
    for v in G[u]:
      if v not in visited:
        path[v] = u
        _dfs(v)

  _dfs(s)
  return path

# Lanzamos un recorrido desde cada nodo que aún no se visitó, todo lo que alcanza ese recorrido es una componente
def componentes_conexas(G, recorrido):
  componentes = []
  visto = {}
  for s in G:
    if s not in visto:
      if recorrido == "bfs":
        path, nivel = bfs(G, s)
      else:
        path = dfs(G, s)
      componente = list(path.keys())  # todos los nodos alcanzados desde s
      for v in componente:
        visto[v] = True
      componentes.append(componente)
  return componentes


def tamanio_mayor(componentes):
  mayor = 0
  for c in componentes:
    if len(c) > mayor:
      mayor = len(c)
  return mayor

# Quick-Union
def find(s, a):
  i = a
  while s[i] != i:          # sube hasta la raíz
    i = s[i]
  return i

def union(s, a, b):
  pa = find(s, a)
  pb = find(s, b)
  s[pa] = pb                # solo cambia un padre

def costo(u, v):
  return -math.log(peso[(u, v)] / 1000)

def reconstruir_ruta(path, t):
  ruta = []
  v = t
  while v != -1:
    ruta.append(v)
    v = path[v]
  ruta.reverse()
  return ruta

def ucs(G, s, t):
  dist = {s: 0}
  path = {s: -1}
  visited = {}
  cola = [(0, s)]                 # cola de prioridad: (costo, proteína)

  while cola:
    c, u = heapq.heappop(cola)    # sale la de menor costo
    if u in visited:
      continue
    visited[u] = True
    if u == t:
      break
    for v in G[u]:
      nuevo = c + costo(u, v)
      if v not in dist or nuevo < dist[v]:
        dist[v] = nuevo
        path[v] = u
        heapq.heappush(cola, (nuevo, v))

  if t not in dist:  # s y t están en componentes distintas
    return [], 0.0
  
  ruta = reconstruir_ruta(path, t)
  confianza = math.exp(-dist[t])  # de costo a confianza
  return ruta, confianza

def sin_arista(G, s, t):
  G2 = {}
  for u in G:
    G2[u] = []
    for v in G[u]:
      if not ((u == s and v == t) or (u == t and v == s)):
        G2[u].append(v)
  return G2

def rutas_backtracking(G, s, t, L, conf_min):
  cuenta = {}                 # cuántas rutas pasan por cada proteína intermedia
  ruta = [s]
  en_ruta = {s: True}         # control de ciclos: una proteína no se repite en la ruta
  total = {"rutas": 0, "llamadas": 0}

  def bt(u, conf):
    total["llamadas"] += 1
    if u == t:
      total["rutas"] += 1
      for x in ruta[1:-1]:    # contamos al vuelo, sin guardar la ruta
        if x not in cuenta:
          cuenta[x] = 0
        cuenta[x] += 1
      return
    if len(ruta) - 1 == L:    # poda: máximo L pasos (la recursión nunca pasa de L)
      return
    for v in G[u]:
      if v in en_ruta:
        continue
      nueva = conf * peso[(u, v)] / 1000
      if nueva < conf_min:    # poda: confianza mínima
        continue
      ruta.append(v)
      en_ruta[v] = True
      bt(v, nueva)
      ruta.pop()              # retroceder
      del en_ruta[v]

  bt(s, 1.0)
  return total["rutas"], cuenta, total["llamadas"]


def intermedias_frecuentes(cuenta, k):
  orden = []
  for n in range(max(cuenta.values(), default=0), 0, -1):
    for x in cuenta:
      if cuenta[x] == n:
        orden.append((x, n))
  return orden[:k]

def BFS(cap, G, s, t, parent):
  visited = {s: True}
  queue = [s]
  while queue:
    u = queue.pop(0)
    for v in G[u]:
      if v not in visited and cap[(u, v)] > 0:
        visited[v] = True
        parent[v] = u
        queue.append(v)
  return t in visited


def FordFulkerson(G, source, sink):
  cap = {}
  for u in G:
    for v in G[u]:
      cap[(u, v)] = 1
  parent = {}
  max_flow = 0

  while BFS(cap, G, source, sink, parent):
    path_flow = float("Inf")
    s = sink
    while s != source:
      path_flow = min(path_flow, cap[(parent[s], s)])
      s = parent[s]
    max_flow += path_flow

    v = sink
    while v != source:
      u = parent[v]
      cap[(u, v)] -= path_flow
      cap[(v, u)] += path_flow
      v = parent[v]
    parent = {}
  return max_flow

# Unión por rango (como applyUnion en clase): el árbol más bajo se cuelga del más alto
def union_rango(parent, rank, x, y):
  if rank[x] < rank[y]:
    parent[x] = y
  elif rank[x] > rank[y]:
    parent[y] = x
  else:
    parent[y] = x
    rank[x] += 1


def kruskal(G, rango=True):
  # 1. Cada arista una sola vez, con su costo
  aristas_costo = []
  for u in G:
    for v in G[u]:
      if u < v:
        aristas_costo.append((costo(u, v), u, v))
  aristas_costo.sort()            # de menor a mayor costo = de la más confiable a la menos

  # 2. Cada proteína empieza sola en su conjunto
  parent = [i for i in range(len(labels))]
  rank = [0 for i in range(len(labels))]

  # 3. Tomamos la arista solo si une dos conjuntos distintos (si no, formaría un ciclo)
  arbol = []
  for c, u, v in aristas_costo:
    x = find(parent, w2i[u])
    y = find(parent, w2i[v])
    if x != y:
      arbol.append((u, v))
      if rango:
        union_rango(parent, rank, x, y)
      else:
        parent[x] = y             # Quick-Union simple de la sección 15
  return arbol

def lista_adyacencia(G, arbol):
  """El MST como lista de adyacencia"""
  mst = {}
  for u in G:
    mst[u] = []
  for u, v in arbol:
    mst[u].append(v)
    mst[v].append(u)
  return mst


def sin_proteinas(G, quitar):
  """Copia del grafo sin las proteínas de la lista quitar"""
  G2 = {}
  for u in G:
    if u in quitar:
      continue
    G2[u] = []
    for v in G[u]:
      if v not in quitar:
        G2[u].append(v)
  return G2