# Datos clínicos de fuentes oficiales.
#   - Genes de resistencia: catálogo de mutaciones de la OMS (2021), Tabla 6, p. 63 -> Anexo 28 del informe.
#   - Esquemas: NTS N° 221-MINSA/DGIESP-2024, Tabla N° 10, pp. 35-36 -> Anexo 31 del informe.
# Solo se usan proteínas que existen en el grafo (con su nombre en STRING).

AVISO = ("Herramienta académica de exploración. No es una recomendación clínica. "
         "Los tratamientos se rigen por la NTS N° 221-MINSA/DGIESP-2024.")

# Fármaco -> proteínas que representa en el grafo (última columna del Anexo 31).
# La primera de cada lista es el origen de las búsquedas en la pestaña Buscar.
PROTEINAS = {
  "Rifampicina (R)": ["rpoB"],
  "Isoniazida (H)": ["katG", "inhA"],
  "Etambutol (E)": ["embB"],
  "Pirazinamida (Z)": ["pncA"],
  "Levofloxacino (Lfx)": ["gyrA"],
  "Moxifloxacino (Mfx)": ["gyrA"],
  "Bedaquilina (Bdq)": ["atpE"],
  "Pretomanid (Pa)": ["ddn"],
  "Delamanid (Dlm)": ["ddn"],
  "Linezolid (Lzd)": ["rplC"],
  "Clofazimina (Cfz)": ["mmpR5"],
  "Amikacina (Am)": ["eis"],
  "Etionamida (Eto)": ["ethA"],
}

# Fármaco -> todos los genes de resistencia que están en el grafo (Anexo 28). Solo se muestran como información.
GENES_OMS = {
  "Rifampicina (R)": ["rpoB", "rpoA", "rpoC"],
  "Isoniazida (H)": ["ahpC", "inhA", "katG"],
  "Etambutol (E)": ["embA", "embB", "embC"],
  "Pirazinamida (Z)": ["pncA", "clpC1", "panD"],
  "Levofloxacino (Lfx)": ["gyrA", "gyrB"],
  "Moxifloxacino (Mfx)": ["gyrA", "gyrB"],
  "Bedaquilina (Bdq)": ["atpE", "pepQ", "mmpR5", "mmpL5", "mmpS5"],
  "Pretomanid (Pa)": ["ddn", "fgd1", "fbiA", "fbiB", "fbiC", "fbiD"],
  "Delamanid (Dlm)": ["ddn", "fgd1", "fbiA", "fbiB", "fbiC", "fbiD"],
  "Linezolid (Lzd)": ["rplC"],
  "Clofazimina (Cfz)": ["pepQ", "mmpR5", "mmpL5", "mmpS5"],
  "Amikacina (Am)": ["eis", "whiB7"],
  "Etionamida (Eto)": ["ethA", "inhA"],
}

# Proteínas asociadas a resistencia que se usan como destino
# (OMS, 2021: rpoA y rpoC para rifampicina; ahpC, katG e inhA para isoniazida)
DESTINOS = ["rpoA", "rpoC", "ahpC", "katG", "inhA", "rpoB"]

# Esquemas de la Tabla N° 10 de la NTS 221 -> fármacos que los componen.
# Cicloserina (Cs) no tiene genes en el catálogo, por eso no aparece en BLCC.
ESQUEMAS = {
  "Sensible: 2(H-R-Z-E)/4(H-R)": ["Isoniazida (H)", "Rifampicina (R)", "Pirazinamida (Z)", "Etambutol (E)"],
  "TB-Hr: 6(R-E-Z-Lfx)": ["Rifampicina (R)", "Etambutol (E)", "Pirazinamida (Z)", "Levofloxacino (Lfx)"],
  "BPaLM: 6(Bdq-Pa-Lzd-Mfx)": ["Bedaquilina (Bdq)", "Pretomanid (Pa)", "Linezolid (Lzd)", "Moxifloxacino (Mfx)"],
  "BLC: 9(Bdq-Lzd-Cfz-Lfx-Z)": ["Bedaquilina (Bdq)", "Linezolid (Lzd)", "Clofazimina (Cfz)", "Levofloxacino (Lfx)", "Pirazinamida (Z)"],
  "BPaL: 6(Bdq-Pa-Lzd)": ["Bedaquilina (Bdq)", "Pretomanid (Pa)", "Linezolid (Lzd)"],
  "BLCC: 6(Bdq-Lzd-Cfz-Cs-Z)": ["Bedaquilina (Bdq)", "Linezolid (Lzd)", "Clofazimina (Cfz)", "Pirazinamida (Z)"],
}