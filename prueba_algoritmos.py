# Prueba para verificar que algoritmos.py da los mismos resultados que el Notebook del Colab.
import algoritmos as a

grafo, peso = a.cargar(700)
print("Nodos:", len(grafo), "| Aristas:", a.contar_aristas(grafo))
print("Componentes:", len(a.componentes_conexas(grafo, "bfs")))

ruta, conf = a.ucs(grafo, "rpoB", "katG")
print("UCS:", " - ".join(ruta), round(conf, 3))

ruta, conf = a.ucs(a.sin_arista(grafo, "rpoB", "katG"), "rpoB", "katG")
print("UCS sin arista:", " - ".join(ruta), round(conf, 3))

rutas, cuenta, llamadas = a.rutas_backtracking(grafo, "rpoB", "katG", 3, 0.9)
print("Backtracking:", rutas, "rutas |", a.intermedias_frecuentes(cuenta, 3))

print("Ford-Fulkerson:", a.FordFulkerson(grafo, "rpoB", "katG"))
print("Kruskal:", len(a.kruskal(grafo)), "aristas")