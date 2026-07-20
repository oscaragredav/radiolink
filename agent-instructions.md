# Instrucciones para IA agéntica

**Proyecto:** RadioLink LOS  
**Documentos de referencia:** MATHSPEC, ARCH, PRD, IMPL  
**Objetivo:** Implementar un evaluador de radioenlace LOS reproducible, físicamente trazable y validado mediante pruebas automatizadas.

---

## 1. Jerarquía documental

Los documentos del proyecto tienen autoridad distinta según el tipo de decisión.

| Prioridad | Documento | Autoridad |
|---:|---|---|
| 1 | `MATHSPEC.md` | Fórmulas, signos, unidades, convenciones físicas y resultados analíticos esperados |
| 2 | `architecture.md` | Estructura de carpetas, módulos, contratos de datos, dependencias y flujo de datos |
| 3 | `requirements.md` | Comportamiento observable, alcance, interfaz y restricciones funcionales |
| 4 | `implementation.md` | Orden de etapas, módulos a implementar y pruebas de aceptación |
| 5 | `AGENT_INSTRUCTIONS.md` | Reglas operativas para implementación, pruebas y resolución de contradicciones |

Reglas:

- Si existe conflicto entre una fórmula y un requisito funcional, prevalece `MATHSPEC.md`.
- Si existe conflicto entre organización de código y un detalle de interfaz, prevalece `architecture.md`.
- Si existe conflicto entre orden de tareas y arquitectura, se mantiene la arquitectura y se documenta el conflicto.
- Si no existe contradicción, se deben cumplir todos los documentos de forma consistente.

---

## 2. Regla de contradicciones

Si dos documentos se contradicen, la IA debe detener la implementación relacionada.

La IA no debe:

- Inventar una interpretación.
- Corregir silenciosamente un documento.
- Elegir una fórmula por conveniencia.
- Cambiar signos, unidades o tolerancias sin autorización.
- Agregar una solución “razonable” no definida por los documentos.

La IA debe crear o actualizar `CONTRADICTIONS.md` en la raíz del proyecto.

Formato obligatorio:

```md
# Contradicciones documentales

## C-001 — Título breve

**Estado:** Pendiente  
**Fecha:** YYYY-MM-DD  
**Documentos involucrados:**
- `archivo_a.md`, sección X
- `archivo_b.md`, sección Y

**Contradicción:**
Descripción concreta de los requisitos incompatibles.

**Impacto:**
Módulos, pruebas o resultados físicos potencialmente afectados.

**Resolución requerida:**
Pregunta concreta que debe responder el responsable del proyecto.

**Propuesta no aplicada:**
Posible alternativa técnica, marcada explícitamente como no implementada.
```

No continuar con los módulos afectados hasta que la contradicción sea resuelta.

---

## 3. Regla de avance

La implementación debe respetar estrictamente las etapas de `implementation.md`.

```text
Etapa 0 → Etapa 1 → Etapa 2 → ... → Etapa actual
```

No se puede iniciar una etapa nueva si la etapa anterior no cumple:

```bash
pytest -q
```

La salida esperada debe terminar sin fallos.

No se permite considerar “completa” una etapa solo porque:

- El código importa sin errores.
- La UI abre.
- La salida parece visualmente correcta.
- Un script manual imprime valores razonables.

Una etapa está completa únicamente cuando todas sus pruebas funcionales y físicas pasan.

---

## 4. Separación de capas

La arquitectura usa el flujo:

```text
Params → Core → LinkProfile → UI
```

Reglas obligatorias:

- `core/` no importa ningún módulo de `ui/`.
- `core/` no importa módulos de `data/`.
- `ui/` no recalcula curvatura, LOS, Fresnel, \(v\), \(G_d\), \(L_d\) ni power budget.
- `ui/` recibe objetos `LinkProfile` ya calculados.
- `ui/panels/` no importa funciones físicas individuales de `core/`.
- Solo `core/engine.py` orquesta el pipeline físico completo.
- `core/engine.py` no importa `core/extensions/` en V1.
- `main.py` no contiene lógica física ni validaciones de dominio.

La UI puede modificar estado visual, pero no debe modificar resultados físicos ya calculados.

---

## 5. Inmutabilidad de parámetros

Los siguientes dataclasses son inmutables:

```python
LinkParams
PowerBudgetParams
LinkProfile
```

Se deben declarar con:

```python
@dataclass(frozen=True)
```

Está prohibido modificar sus atributos directamente:

```python
params.K = 1.0
params.f_hz = 14e9
params.h_tx_m = 20.0
```

Para modificar parámetros se usa exclusivamente:

```python
from dataclasses import replace

new_params = replace(params, K=1.0)
new_params = replace(params, f_hz=14e9)
new_params = replace(params, h_tx_m=20.0)
```

No usar:

```python
copy.copy(params)
copy.deepcopy(params)
```

seguido de asignación de atributos.

---

## 6. Unidades y nomenclatura

Dentro de `core/`, todas las variables físicas deben usar unidades SI.

Convenciones obligatorias:

```python
d1_m
d2_m
d_total_m
f_hz
f_ghz
lam_m
h_er_m
z_eff_m
h_los_m
r1_m
h_sup_m
h_inf_m
h_60pct_m
c_los_m
h_o_m
c_ffz_m
g_d_db
l_d_db
l_fs_db
p_rx_dbm
margin_db
availability_pct
```

No usar nombres ambiguos:

```python
d1
d2
f
lam
h
loss
gain
result
value
```

Las conversiones de GHz a Hz, km a m y otras conversiones de presentación solo pueden ocurrir:

- En adaptadores de entrada de UI.
- En adaptadores de salida de UI.
- En carga o serialización de archivos cuando el formato lo requiera.

Nunca dentro de ecuaciones físicas del motor.

---

## 7. Convenciones físicas obligatorias

### Curvatura y terreno efectivo

```text
z_eff_m = elevation_m + h_er_m
```

`z_eff_m` contiene únicamente el terreno corregido por curvatura.

Nunca incluir alturas de antena en `z_eff_m`.

Las alturas absolutas de antenas se calculan separadamente:

```text
H_Tx = z_eff_m + h_tx_m
H_Rx = z_eff_m[-1] + h_rx_m
```

### Extremos del perfil

En Tx y Rx:

```text
h_er_m = 0
h_er_m[-1] = 0

r1_m = 0
r1_m[-1] = 0

v = NaN
v[-1] = NaN
```

No usar división por cero ni `try/except` para manejar extremos. Usar máscaras booleanas de NumPy.

Ejemplo obligatorio:

```python
valid = (d1_m > 0.0) & (d2_m > 0.0)

v = np.full_like(d1_m, np.nan, dtype=float)

v[valid] = h_o_m[valid] * np.sqrt(
    2.0 * d_total_m /
    (lam_m * d1_m[valid] * d2_m[valid])
)
```

### Zonas de Fresnel

Las bandas se calculan exclusivamente en `core/fresnel_zones.py`:

```text
h_sup_m = h_los_m + r1_m
h_inf_m = h_los_m - r1_m
h_60pct_m = h_los_m - 0.6 * r1_m
```

Los tres arrays deben formar parte de `LinkProfile`.

La UI debe leer estos arrays; no debe recalcularlos.

### Obstáculo crítico

El índice crítico siempre se obtiene mediante:

```python
idx_critical = np.nanargmax(v)
```

Nunca usar:

```python
np.argmax(h_o_m)
np.argmax(elevation_m)
np.argmax(z_eff_m)
```

El obstáculo crítico es el punto con máximo \(v\), no necesariamente el punto más alto.

### Difracción

La convención de signo es obligatoria:

```text
v > 0: obstrucción sobre LOS
v = 0: borde en LOS
v < 0: despeje bajo LOS
```

El coeficiente exacto se calcula como:

```text
G_d = 20 log10(|F(v)|)
```

La pérdida adicional usada en el presupuesto de enlace es:

```text
L_d = max(0.0, -G_d)
```

Reglas:

- La curva del panel de difracción representa `G_d(v)`.
- El punto de operación del panel usa `(v_critical, g_d_db)`.
- El power budget usa `l_d_db`.
- `l_d_db` siempre debe cumplir `l_d_db >= 0.0`.
- No usar aproximación polinomial ITU-R P.526.
- No añadir un umbral empírico adicional.
- Usar `scipy.special.fresnel(v)`, recordando que retorna `(S, C)`.

---

## 8. Pipeline obligatorio

`core.engine.compute_link_profile(...)` ejecuta el pipeline en este orden:

```text
1.  atmosphere.earth_curvature_correction → h_er_m
2.  atmosphere.effective_elevation → z_eff_m
3.  geometry.antenna_heights_msl → H_Tx, H_Rx
4.  geometry.los_height → h_los_m
5.  fresnel_zones.fresnel_radius_n → r1_m
6.  fresnel_zones.fresnel_bands → h_sup_m, h_inf_m, h_60pct_m
7.  fresnel_zones.los_clearance → c_los_m
8.  fresnel_zones.obstacle_height → h_o_m
9.  fresnel_zones.ffz_clearance → c_ffz_m
10. diffraction.fresnel_kirchhoff_parameter → v
11. diffraction.critical_obstacle_index → idx_critical
12. diffraction.diffraction_gain_db → g_d_db
13. diffraction.diffraction_loss_db → l_d_db
14. link_budget.free_space_loss_db → l_fs_db
15. Si existen PowerBudgetParams:
    - received_power_dbm → p_rx_dbm
    - link_margin_db → margin_db
    - link_availability → availability_pct
16. Verificar invariantes de LinkProfile
17. Retornar un nuevo LinkProfile inmutable
```

No se puede cambiar el orden sin actualizar y aprobar los documentos de arquitectura y especificación matemática.

---

## 9. Invariantes de `LinkProfile`

Antes de retornar un `LinkProfile`, `compute_link_profile(...)` debe verificar:

```python
N = terrain.n_points

assert len(profile.h_er_m) == N
assert len(profile.z_eff_m) == N
assert len(profile.h_los_m) == N
assert len(profile.r1_m) == N
assert len(profile.h_sup_m) == N
assert len(profile.h_inf_m) == N
assert len(profile.h_60pct_m) == N
assert len(profile.c_los_m) == N
assert len(profile.h_o_m) == N
assert len(profile.c_ffz_m) == N
assert len(profile.v) == N

assert profile.h_er_m == 0.0
assert profile.h_er_m[-1] == 0.0

assert profile.r1_m == 0.0
assert profile.r1_m[-1] == 0.0

assert np.isnan(profile.v)
assert np.isnan(profile.v[-1])

assert 1 <= profile.idx_critical <= N - 2
assert profile.idx_critical == np.nanargmax(profile.v)
assert profile.v_critical == profile.v[profile.idx_critical]

assert profile.l_d_db >= 0.0
assert profile.l_fs_db > 0.0
```

Cuando el power budget está activo:

```python
assert profile.margin_db == (
    profile.p_rx_dbm - pb_params.sensitivity_dbm
)
```

---

## 10. Pruebas automatizadas

Cada criterio `[F]` o `[P]` definido en `implementation.md` debe existir como prueba automatizada dentro de `tests/`.

Estructura esperada:

```text
tests/
├── test_scaffolding.py
├── test_models.py
├── test_loader.py
├── test_atmosphere.py
├── test_geometry.py
├── test_fresnel_zones.py
├── test_diffraction.py
├── test_link_budget.py
├── test_engine.py
├── test_ui_static.py
└── test_callbacks.py
```

Reglas:

- Cada prueba debe tener nombre `test_*`.
- Cada prueba valida una propiedad física o funcional concreta.
- No se aceptan scripts manuales como reemplazo de tests.
- Las pruebas no deben depender de conexión a internet.
- Las pruebas de descarga API deben usar mocks.
- Las pruebas de UI deben usar backend no interactivo, por ejemplo `matplotlib.use("Agg")`.
- La IA debe ejecutar `pytest -q` después de cada etapa.
- Si una prueba física falla, no se debe ajustar arbitrariamente la tolerancia para volverla verde.
- **Formato de aserciones para depuración:** En la parte de los `assert` se deben colocar variables intermedias de manera que al hacer debug se pueda inspeccionar qué valor se está evaluando. Por ejemplo, en vez de:
  ```python
  assert abs(abs(F0) - 0.5) < 1e-6
  ```
  Se debe escribir:
  ```python
  error = abs(abs(F0) - 0.5)
  tolerance = 1e-6
  assert error < tolerance
  ```

---

## 11. Casos físicos obligatorios

### Caso V-1: tierra plana

```text
d_total_m = 10_000
n_points = 201
elevation_m = 0
f_hz = 7e9
K = 1e12
h_tx_m = 14.64
h_rx_m = 14.64
```

Resultado esperado:

```text
v_critical = -2.00 ± 0.03
l_d_db = 0.00
```

### Caso V-2: borde en LOS

```text
d_total_m = 10_000
n_points = 201
d1_peak_m = 4_000
d2_peak_m = 6_000
terrain_base_m = 0
peak_elevation_m = 10
f_hz = 7e9
K = 1e12
h_tx_m = 10
h_rx_m = 10
```

Resultado esperado:

```text
h_o_m[idx_critical] = 0
v_critical = 0.00 ± 0.05
g_d_db = -6.0206 ± 0.01 dB
l_d_db = 6.0206 ± 0.01 dB
```

### Caso V-3: Lima

```text
- Carga exclusivamente un CSV local.
- Debe cumplir las invariantes de LinkProfile.
- Debe ser reproducible con el mismo CSV y parámetros.
- l_fs_db debe coincidir con la forma analítica de espacio libre.
```

---

## 12. Reglas de interfaz

La UI solo representa estado y resultados ya calculados.

Reglas:

- Los callbacks crean nuevos `LinkParams` mediante `dataclasses.replace`.
- Cada callback llama a `app._recompute()`.
- `app._recompute()` llama a `core.engine.compute_link_profile(...)`.
- Los paneles reciben `LinkProfile`.
- Los artistas de Matplotlib se crean una única vez.
- Las actualizaciones usan `.set_data()`, `.set_xdata()`, `.set_ydata()` o `.set_xy()`.
- No usar `ax.clear()` dentro del ciclo de actualización.
- El redibujado final usa una sola llamada a `fig.canvas.draw_idle()`.

El toggle de terreno crudo/efectivo:

- Solo modifica visibilidad.
- No recalcula física.
- No modifica `TerrainData`.
- No modifica `LinkProfile`.

---

## 13. Dependencias y alcance

Dependencias autorizadas:

```text
numpy
scipy
matplotlib
pandas
requests
pytest
```

No agregar nuevas dependencias sin autorización explícita.

No implementar en el MVP:

```text
- Aplicación web
- Servidores
- Base de datos
- Tkinter o Qt
- Mapas interactivos
- Exportación PDF
- Obstáculos múltiples
- Ducting atmosférico completo
- Multicamino integrado al engine
- Atenuación por lluvia, gases o vapor integrada al engine
```

`core/extensions/multipath.py` y `core/extensions/attenuation.py` pueden existir por trazabilidad con MATHSPEC, pero:

```text
- No se importan desde core/engine.py en V1.
- No modifican LinkProfile en V1.
- No afectan UI en V1.
- No participan en tests del MVP.
```

---

## 14. Entregable de cada etapa

Al finalizar una etapa, la IA debe entregar:

1. Archivos nuevos o modificados de esa etapa.
2. Tests `pytest` nuevos o actualizados.
3. Resultado de `pytest -q`.
4. Lista breve de decisiones aplicadas.
5. Lista de problemas pendientes, si existen.
6. `CONTRADICTIONS.md`, si se detectó una contradicción documental.

La IA no debe pasar a una etapa posterior hasta que los tests de la etapa actual pasen.