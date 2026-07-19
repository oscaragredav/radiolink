# PRD — Evaluador de Radioenlace LOS

**Versión:** 1.1  
**Proyecto:** Visualizador de enlace de microondas con curvatura terrestre, zonas de Fresnel y difracción Knife-Edge  
**Contexto académico:** Evaluación oral Examen 4 — Circuitos y Sistemas de Alta Frecuencia (TEL138)  
**Referencias cruzadas:** MATHSPEC v1.1, ARCH v1.1, IMPL v1.1

---

## 1. Propósito

Herramienta de escritorio en Python que, a partir de un perfil de elevación entre dos puntos, analiza un radioenlace LOS de microondas mediante corrección por curvatura terrestre, línea de visión, primera zona de Fresnel y difracción Knife-Edge de una arista dominante.

El sistema debe mostrar resultados geométricos y de difracción de manera reproducible. Cuando el power budget esté activo, debe mostrar por separado la potencia recibida, el margen respecto a sensibilidad y la disponibilidad calculada; no debe presentar ninguno de estos indicadores como una garantía absoluta de viabilidad operacional.

---

## 2. Usuario objetivo

El usuario es un operador técnico con conocimiento básico de propagación de radioenlaces. La interfaz prioriza trazabilidad de cálculos, visibilidad de parámetros y resultados intermedios por encima de simplificación para usuarios no técnicos.

---

## 3. Fuente de perfil

El sistema usa una fuente de perfil de elevación. La fuente no define un modo de cálculo físico distinto: una vez disponible el `TerrainData`, el pipeline físico es idéntico.

### RF-01 Perfil local

**RF-01.1** El sistema debe cargar un CSV local con las columnas:

```text
distance_m, latitude, longitude, elevation_m
```

**RF-01.2** El perfil local es la fuente principal para ejecución, validación y presentación oral. No requiere conexión a internet.

**RF-01.3** El sistema debe validar que:

- El CSV contenga al menos 50 puntos.
- `distance_m[0]` sea exactamente 0.0.
- `distance_m` sea estrictamente creciente.
- `elevation_m` no contenga valores nulos.

**RF-01.4** Si una validación falla, el sistema debe reportar un mensaje específico y detener la carga mediante una excepción de dominio.

**RF-01.5** El sistema debe reportar la fuente, número de puntos, distancia total y resolución efectiva del perfil cargado.

### RF-02 Perfil descargado por API

**RF-02.1** Como extensión opcional, el sistema puede generar un perfil a partir de coordenadas Tx y Rx usando Open-Elevation.

**RF-02.2** La descarga debe generar un CSV local reutilizable con nombre derivado de coordenadas y timestamp.

**RF-02.3** Tras descargar el perfil, el sistema debe cargarlo mediante el mismo validador y el mismo pipeline usados para un perfil local.

**RF-02.4** Una falla de red, timeout o respuesta inválida debe producir un error explícito y no debe afectar la operación con perfiles locales.

**RF-02.5** La fuente API no forma parte del MVP obligatorio ni debe requerirse durante la presentación oral.

---

## 4. Parámetros del enlace

### RF-03 Parámetros configurables

El sistema debe aceptar los siguientes parámetros:

| Parámetro | Símbolo | Unidad | Rango de interfaz | Valor por defecto |
|---|---|---:|---:|---:|
| Frecuencia | \(f\) | GHz | 0.1 a 30 | 7.0 |
| Altura de antena Tx | \(h_\mathrm{Tx}\) | m | 1 a 100 | 10 |
| Altura de antena Rx | \(h_\mathrm{Rx}\) | m | 1 a 100 | 10 |
| Factor de escala terrestre | \(K\) | adimensional | 0.5 a 5.0 | 1.333 |

**RF-03.1** Todos los cálculos internos deben convertir frecuencia a Hz y distancias a metros antes de entrar a `core/`.

**RF-03.2** El valor de \(K\) es la fuente de verdad del modelo atmosférico.

**RF-03.3** El gradiente de refractividad \(dN/dh\) se deriva de \(K\) mediante la relación definida en MATHSPEC.

**RF-03.4** La interfaz debe mostrar \(dN/dh\) como valor de solo lectura junto al control de \(K\). El usuario no ingresa directamente \(dN/dh\).

**RF-03.5** El rango de \(K\) se ofrece para exploración académica y sensibilidad del modelo. Valores extremos dentro del rango no representan necesariamente condiciones atmosféricas típicas.

**RF-03.6** Cambiar frecuencia, \(K\), \(h_\mathrm{Tx}\) o \(h_\mathrm{Rx}\) debe recalcular automáticamente el perfil completo y actualizar la visualización.

---

## 5. Perfil efectivo y LOS

### RF-04 Curvatura terrestre

**RF-04.1** Para cada punto interno del perfil, el sistema debe calcular la corrección por curvatura terrestre conforme a MATHSPEC.

**RF-04.2** El cálculo de curvatura se aplica solamente donde:

\[
d_{1,i}>0
\quad\text{y}\quad
d_{2,i}>0
\]

**RF-04.3** En Tx y Rx, la corrección por curvatura debe ser exactamente 0 m.

**RF-04.4** La elevación efectiva se define como:

\[
z_{\mathrm{eff},i}
=
z_{\mathrm{raw},i}
+
h_{\mathrm{ER},i}
\]

**RF-04.5** `z_eff_m` representa exclusivamente elevación de terreno corregida por curvatura. No incluye altura de antenas en ningún punto, incluidos Tx y Rx.

**RF-04.6** El sistema debe conservar el perfil crudo y el perfil efectivo para visualización.

### RF-05 Línea de visión directa

**RF-05.1** La altura absoluta de la antena Tx se define separadamente como:

\[
H_{\mathrm{Tx}}
=
z_{\mathrm{eff,Tx}}
+
h_\mathrm{Tx}
\]

**RF-05.2** La altura absoluta de la antena Rx se define separadamente como:

\[
H_{\mathrm{Rx}}
=
z_{\mathrm{eff,Rx}}
+
h_\mathrm{Rx}
\]

**RF-05.3** La LOS debe ser la recta entre:

```text
(0, H_Tx)
(d_total, H_Rx)
```

**RF-05.4** El sistema debe calcular `h_los_m` en cada punto del perfil conforme a la ecuación de interpolación lineal definida en MATHSPEC.

---

## 6. Zonas de Fresnel

### RF-06 Primera zona de Fresnel

**RF-06.1** El sistema debe calcular el radio de la primera zona de Fresnel `r1_m` en todos los puntos del perfil.

**RF-06.2** En los extremos, donde \(d_1=0\) o \(d_2=0\), el radio de Fresnel debe ser exactamente 0 m.

**RF-06.3** El motor debe calcular y almacenar en `LinkProfile`:

```text
h_sup_m = h_los_m + r1_m
h_inf_m = h_los_m - r1_m
h_inf_mh_60pct_m = h_los_m - 0.6 * r1_m
```

**RF-06.4** La interfaz debe representar las bandas usando exclusivamente los arrays entregados por `LinkProfile`. La interfaz no debe recalcular zonas de Fresnel.

**RF-06.5** El sistema debe calcular el despeje relativo a la LOS:

\[
C_{\mathrm{LOS},i}
=
h_{\mathrm{LOS},i}
-
z_{\mathrm{eff},i}
\]

**RF-06.6** El sistema debe calcular el despeje relativo al 60% de Fresnel:

\[
C_{\mathrm{FFZ},i}
=
C_{\mathrm{LOS},i}
-
0.6r_{1,i}
\]

---

## 7. Parámetro de difracción

### RF-07 Parámetro Fresnel-Kirchhoff

**RF-07.1** El sistema debe calcular el parámetro \(v_i\) en los puntos internos del perfil conforme a MATHSPEC.

**RF-07.2** La convención de signos es obligatoria:

```text
v > 0: obstáculo sobre la LOS
v = 0: borde exactamente en la LOS
v < 0: despeje bajo la LOS
```

**RF-07.3** En los extremos Tx y Rx, `v` debe ser `NaN`.

**RF-07.4** El sistema debe almacenar el array completo `v` dentro de `LinkProfile`.

### RF-08 Obstáculo crítico

**RF-08.1** El obstáculo crítico se define mediante:

\[
\mathrm{idx\_critical}
=
\operatorname{nanargmax}(v)
\]

**RF-08.2** El índice crítico debe pertenecer al intervalo:

```text
1 <= idx_critical <= N - 2
```

**RF-08.3** El sistema debe reportar para el punto crítico:

- Distancia desde Tx.
- Distancia hacia Rx.
- Elevación efectiva.
- Altura de la LOS.
- Radio Fresnel 1.
- Despeje respecto a LOS.
- Despeje respecto al 60% de Fresnel.
- Valor \(v_\mathrm{critical}\).
- Coeficiente de difracción \(G_d\).
- Pérdida adicional de difracción \(L_d\).

---

## 8. Difracción Knife-Edge

### RF-09 Modelo de difracción

**RF-09.1** El sistema debe usar exclusivamente la solución exacta de integrales de Fresnel mediante `scipy.special.fresnel`.

**RF-09.2** El sistema no debe usar la aproximación polinomial de ITU-R P.526.

**RF-09.3** El coeficiente de difracción debe calcularse como:

\[
G_d
=
20\log_{10}|F(v)|
\]

**RF-09.4** La pérdida adicional de difracción debe calcularse como:

\[
L_d
=
\max(0,-G_d)
\]

**RF-09.5** La pérdida adicional \(L_d\) debe ser siempre mayor o igual a 0 dB.

**RF-09.6** El panel de difracción debe representar \(G_d(v)\), la curva exacta de Fresnel, y no la pérdida truncada \(L_d(v)\).

**RF-09.7** El power budget, cuando esté activo, debe usar \(L_d\) como pérdida adicional.

**RF-09.8** El panel de resultados debe declarar:

```text
Modelo: Knife-Edge de obstáculo único.
La pérdida adicional se limita a Ld >= 0 dB para el presupuesto de enlace.
Terreno redondeado, múltiples crestas y mecanismos atmosféricos requieren modelos adicionales.
```

---

## 9. Casos de validación

### RF-10 Casos integrados

El sistema debe incluir tres casos de validación precargados.

### RF-10.1 Caso V-1: tierra plana

El caso V-1 debe usar exactamente:

| Parámetro | Valor |
|---|---:|
| Distancia total | 10 000 m |
| Número de puntos | 201 |
| Espaciamiento | 50 m |
| Elevación del terreno | 0 m |
| Frecuencia | 7 GHz |
| \(K\) | \(10^{12}\) |
| \(h_\mathrm{Tx}\) | 14.64 m |
| \(h_\mathrm{Rx}\) | 14.64 m |

El resultado esperado es:

```text
v_critical = -2.00 ± 0.03
L_d = 0.00 dB
```

### RF-10.2 Caso V-2: borde sobre LOS

El caso V-2 debe usar exactamente:

| Parámetro | Valor |
|---|---:|
| Distancia total | 10 000 m |
| Número de puntos | 201 |
| Pico | d1 = 4 000 m |
| Terreno base | 0 m |
| Elevación del pico | 10 m |
| Frecuencia | 7 GHz |
| \(K\) | \(10^{12}\) |
| \(h_\mathrm{Tx}\) | 10 m |
| \(h_\mathrm{Rx}\) | 10 m |

El resultado esperado es:

```text
h_o = 0 m
v_critical = 0.00 ± 0.05
G_d = -6.0206 ± 0.01 dB
L_d = 6.0206 ± 0.01 dB
```

### RF-10.3 Caso V-3: Lima

El caso V-3 debe cargar un CSV local de un trayecto real en Lima.

No se exige un valor universal fijo para \(v_\mathrm{critical}\) o \(L_d\), porque dependen del CSV de perfil suministrado. El sistema debe cumplir las invariantes del motor, calcular correctamente \(L_\mathrm{fs}\) y producir resultados reproducibles usando el mismo archivo y parámetros.

---

## 10. Visualización

### RF-11 Panel de perfil

**RF-11.1** La figura debe mostrar:

- Perfil de terreno crudo en gris.
- Perfil efectivo en negro.
- LOS del Diseño A en rojo.
- Banda completa de Fresnel 1 en azul semitransparente.
- Umbral de 60% de Fresnel en azul discontinuo.
- Marcador del obstáculo crítico.
- Mástiles Tx y Rx.
- Anotación con distancia, \(v\) y \(L_d\).

**RF-11.2** El eje X debe ser distancia desde Tx en km.

**RF-11.3** El eje Y debe ser elevación en m.s.n.m.

**RF-11.4** El toggle de terreno crudo/efectivo debe cambiar únicamente la visualización; no debe modificar el cálculo físico.

### RF-12 Panel de difracción

**RF-12.1** El panel debe mostrar la curva exacta \(G_d(v)\) para:

\[
-3 \leq v \leq 3
\]

**RF-12.2** El eje X debe representar \(v\).

**RF-12.3** El eje Y debe representar \(G_d\) en dB.

**RF-12.4** Debe existir una línea vertical en \(v=0\) etiquetada como borde en LOS.

**RF-12.5** El punto de operación debe usar:

```text
x = v_critical
y = g_d_db
```

### RF-13 Panel de resultados

**RF-13.1** El panel debe mostrar:

```text
d_total
f
K
d1_critical
d2_critical
v_critical
G_d
L_d
L_fs
```

**RF-13.2** Si el power budget está activo, también debe mostrar:

```text
P_Rx
Margen
Disponibilidad
```

**RF-13.3** Los resultados de margen y disponibilidad deben mostrarse como indicadores distintos.

---

## 11. Diseño B

### RF-14 Comparación de diseños

Esta funcionalidad es una extensión, no un requisito del MVP.

**RF-14.1** El sistema puede permitir un Diseño B con alturas `h_tx_b` y `h_rx_b` sin modificar Diseño A.

**RF-14.2** Diseño B debe reutilizar el mismo perfil de terreno, frecuencia y \(K\) de Diseño A, salvo que una futura versión declare explícitamente más parámetros comparables.

**RF-14.3** Si Diseño B está activo, la interfaz debe mostrar LOS, banda Fresnel y punto de operación para ambos diseños.

**RF-14.4** Si los parámetros de A y B son idénticos, todos los resultados físicos deben ser idénticos.

**RF-14.5** La interfaz puede mostrar cuál diseño tiene menor \(L_d\), pero no debe usar esa comparación como garantía de disponibilidad operacional.

---

## 12. Power budget

### RF-15 Presupuesto de enlace

Esta funcionalidad es una extensión activable.

**RF-15.1** El sistema puede aceptar:

```text
P_Tx
G_Tx
G_Rx
L_cable_Tx
L_cable_Rx
Sensibilidad
a_climate
b_terrain
```

**RF-15.2** Si está activo, el sistema debe calcular:

\[
P_\mathrm{Rx}
=
P_\mathrm{Tx}
+
G_\mathrm{Tx}
+
G_\mathrm{Rx}
-
L_{\mathrm{cable,Tx}}
-
L_{\mathrm{cable,Rx}}
-
L_\mathrm{fs}
-
L_d
\]

**RF-15.3** El margen debe calcularse como:

\[
M
=
P_\mathrm{Rx}
-
\mathrm{Sensibilidad}
\]

**RF-15.4** El sistema debe mostrar el margen como:

```text
Margen sobre sensibilidad: X dB
```

**RF-15.5** Si el margen es negativo, el sistema debe indicar déficit respecto a sensibilidad.

**RF-15.6** Si el margen es positivo, el sistema puede indicar margen positivo respecto a sensibilidad.

**RF-15.7** La disponibilidad se muestra separadamente y no reemplaza el análisis de margen.

---

## 13. Requisitos no funcionales

### RNF-01 Operación offline

El flujo principal con CSV local no debe realizar llamadas de red.

### RNF-02 Reproducibilidad

Dados el mismo CSV y los mismos parámetros, el sistema debe producir los mismos valores numéricos.

### RNF-03 Tiempo de respuesta

Para perfiles de hasta 500 puntos, un recálculo debe completar en menos de 2 segundos en una laptop estándar.

### RNF-04 Entorno

```text
Python >= 3.10
numpy
scipy
matplotlib
pandas
pytest
requests, solo para fuente API opcional
```

### RNF-05 Ejecución

El proyecto debe ejecutarse desde la raíz mediante:

```bash
pip install -r requirements.txt
python main.py
pytest -q
```

### RNF-06 Trazabilidad

Toda función física del motor debe contener una referencia `Ref: EQ-XX` a MATHSPEC.

### RNF-07 Separación de capas

- `core/` no importa módulos de `ui/`.
- `ui/` no recalcula física.
- `ui/` representa únicamente los resultados de `LinkProfile`.
- El motor no importa módulos de descarga ni extensiones físicas en V1.

### RNF-08 Inmutabilidad

`LinkParams`, `PowerBudgetParams` y `LinkProfile` deben ser dataclasses inmutables.

Las actualizaciones de parámetros deben usar:

```python
dataclasses.replace(...)
```

### RNF-09 Pruebas automatizadas

Todo criterio funcional o físico definido en IMPL debe existir como prueba automatizada dentro de `tests/`.

---

## 14. Limitaciones declaradas

### LIM-01 Difracción

El modelo representa un único obstáculo dominante Knife-Edge.

No incluye métodos de múltiples obstáculos como Epstein-Peterson o Deygout.

### LIM-02 Terreno

La calidad del resultado depende de la resolución y exactitud del DEM de origen. El sistema no inventa detalle topográfico no presente en el CSV.

### LIM-03 Atmósfera

El factor \(K\) se considera uniforme a lo largo del trayecto. No se modelan gradientes locales de refractividad, ducting ni variaciones verticales complejas.

### LIM-04 Extensiones atmosféricas

Multicamino, lluvia, absorción por gases y vapor de agua no participan en el pipeline V1.

Pueden conservarse como módulos futuros documentados, pero no deben modificar cálculos, resultados ni UI del MVP.

### LIM-05 Geometría

No se modelan obstáculos redondeados, smooth-earth diffraction ni superficies irregulares complejas.

---

## 15. Fuera de alcance

- Aplicación web.
- Servidor local.
- Bases de datos.
- GUI nativa con Tkinter o Qt.
- Mapas interactivos.
- Exportación de reportes PDF.
- Modelos de múltiples obstáculos.
- Ducting atmosférico completo.
- Integración de multicamino y atenuación en el MVP.
- Garantía de disponibilidad operacional real.

---

## 16. Criterios globales de aceptación

El proyecto se considera conforme con este PRD cuando:

- Carga un CSV local válido sin conexión a internet.
- Calcula curvatura, LOS, Fresnel, \(v\), \(G_d\) y \(L_d\).
- V-1 produce \(v_\mathrm{critical}=-2.00\pm0.03\) y \(L_d=0\) dB.
- V-2 produce \(v_\mathrm{critical}=0\pm0.05\) y \(L_d=6.0206\pm0.01\) dB.
- V-3 produce resultados reproducibles e invariantes válidas.
- Cambiar \(K\) modifica el perfil efectivo y el resultado crítico.
- La UI muestra bandas Fresnel calculadas por el motor, sin recalcularlas.
- La UI muestra la curva exacta \(G_d(v)\), no la pérdida truncada.
- `pytest -q` termina sin fallos.
- El MVP no depende de internet.
