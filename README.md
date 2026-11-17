# Red TB: explorador de la red de proteínas de la tuberculosis

Aplicativo del curso **Complejidad Algorítmica (1ACC0184)**, UPC 2026-20, Grupo 3, Caso 3: análisis de redes biológicas.

Mapa interactivo de las proteínas de *Mycobacterium tuberculosis* H37Rv construido con datos de STRING v12.5 (3 802 proteínas y 28 739 interacciones con confianza ≥ 700). Permite:

- **Ver** la red, su esqueleto de máxima confianza (MST) y el entorno de una diana.
- **Buscar** la ruta más confiable entre una diana y una proteína de resistencia, las rutas alternativas y las proteínas intermedias más frecuentes.
- **Simular** el bloqueo de las dianas de un esquema de tratamiento de la NTS N° 221-MINSA/DGIESP-2024.

> Herramienta académica de exploración. No es una recomendación clínica. Los tratamientos se rigen por la NTS N° 221-MINSA/DGIESP-2024.

## Algoritmos

| Técnica | Uso |
|---|---|
| BFS / DFS | Componentes conexas y entorno de las dianas |
| UFDS (Quick-Find, Quick-Union) | Componentes conexas; base de Kruskal |
| Kruskal (MST) | Esqueleto de la red para el mapa |
| UCS | Ruta de mayor confianza (costo −ln(puntaje/1000)) |
| Backtracking | Rutas alternativas de hasta L pasos |
| Ford-Fulkerson | Número de rutas independientes |

## Cómo ejecutarlo

Requiere Python 3.11 o superior.

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows  (Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt
streamlit run app.py
```

La app se abre en el navegador en `http://localhost:8501`.

## Uso de la app

| Pestaña | Qué hace el usuario | Qué muestra | Algoritmos |
|---|---|---|---|
| **Explorar** | Elige una proteína y la vista | Su entorno por niveles o el esqueleto de la red, y la ficha de la proteína | BFS, Kruskal |
| **Rutas** | Elige un fármaco y una proteína de resistencia | La ruta más confiable, la alternativa si se bloquea, las rutas de hasta L pasos, las intermedias más frecuentes y los caminos independientes | UCS, backtracking, Ford-Fulkerson |
| **Tratamiento** | Elige un esquema de la NTS N° 221 y un par de proteínas | Las proteínas bloqueadas y cuántas rutas quedan antes y después, para todos los esquemas | UCS, backtracking, Ford-Fulkerson |

Cada pestaña incluye el recuadro **Algoritmo y costo**, con la complejidad y el tiempo medido de cada algoritmo.

## Estructura del proyecto

```
app.py                  Punto de entrada: arma la página y llama a cada pestaña
algoritmos.py           Algoritmos del Colab (BFS, DFS, UFDS, UCS, backtracking, Ford-Fulkerson, Kruskal)
fuentes.py              Fármacos, genes y esquemas (OMS, 2021; NTS N° 221-MINSA/DGIESP-2024)
datos.py                Carga de la red y cálculos con caché
interfaz.py             Colores, estilo, tablas y dibujo del grafo (pyvis)
pestanas/               Una pestaña por archivo: explorar.py, rutas.py, tratamiento.py
data/                   Archivos de STRING v12.5 comprimidos
notebooks/              Cuaderno de Colab con el análisis del informe
prueba_algoritmos.py    Comprueba que algoritmos.py da los mismos resultados que el Colab
.streamlit/config.toml  Tema de la app
```

## Datos

- STRING v12.5, organismo 83332 (*M. tuberculosis* H37Rv): https://string-db.org
- Catálogo de mutaciones de la OMS (2021) y NTS N° 221-MINSA/DGIESP-2024 para fármacos y esquemas.

## Integrantes

| Código | Nombre |
|---|---|
| u202413533 | Mijail Alexander Matihues Quevedo |
| u20241b451 | Alexandra Yamile Meza Soza |
| u202415820 | Leonardo Moises Cabrera Novoa |
