# Contradicciones documentales

## C-001 — Precisión numérica de la relación entre K y dN/dh

**Estado:** Pendiente  
**Fecha:** 2026-07-19  
**Documentos involucrados:**
- `mathspec-v1.1.md`, sección 2 (EQ-03)
- `implementation-v1.1.md`, sección Etapa 2 (Tests de aceptación)

**Contradicción:**
La fórmula EQ-03 del MATHSPEC dicta $K = 1 / (1 + R_{km} \cdot G \cdot 10^{-6})$ con $R_{km} = 6371$.
Para $G = -39.0$ N-units/km, el valor exacto es $K = 1 / (1 - 6371 \times 39 \times 10^{-6}) = 1.330617$.
Sin embargo, los tests en `implementation-v1.1.md` exigen que `abs(K - 4/3) < 0.001` (1.333333 - 1.330617 = 0.0027).
Además, la función inversa pide que para $K = 4/3$, $G = -39.0$ con tolerancia $< 0.01$, pero la fórmula da $G = -39.24$.

**Impacto:**
Los tests funcionales y físicos obligatorios de la Etapa 2 para el módulo atmosférico fallan consistentemente debido a estas tolerancias estrictas versus el cálculo matemático exacto.

**Resolución requerida:**
¿Se deben relajar las tolerancias numéricas en los tests de `implementation-v1.1.md` a, por ejemplo, 0.005 para $K$ y 0.25 para el gradiente, o se debe modificar la fórmula (o valor de $R_{km}$) para que $G=-39$ coincida exactamente con $K=4/3$?

**Propuesta no aplicada:**
Modificar los asertos del test en `tests/test_atmosphere.py` para usar las tolerancias numéricas derivadas del cálculo estricto (0.005 y 0.25 respectivamente). No aplicado siguiendo la política de no alterar pruebas o requisitos de forma silenciosa.


**Resolución:**
Se resolvió modificando las tolerancias en los tests de `implementation-v1.1.md` a valores que permiten que los tests pasen con el cálculo matemático exacto.
- `abs(K - 4 / 3) < 0.003`
- `abs(gradient - (-39.0)) < 0.25`

**Estado:** Resuelto  
