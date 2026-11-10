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

```bash
pip install -r requirements.txt
streamlit run app.py
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