# IMPL — Plan de Implementación por Etapas

**Versión:** 1.1  
**Referencias cruzadas:** PRD v1.0, MATHSPEC v1.1, ARCH v1.1

---

## Protocolo de trabajo

**Regla de avance:** ninguna etapa comienza hasta que todos los criterios de aceptación de la etapa anterior estén implementados como pruebas `pytest`, ejecutados y aprobados mediante:

```bash
pytest -q
```

**Responsabilidades por etapa:**

| Actor | Tarea |
|---|---|
| IA agéntica | Implementa exclusivamente los módulos de la etapa actual, crea o actualiza los tests `pytest` correspondientes y ejecuta `pytest -q` |
| Oscar | Revisa resultados numéricos, verifica la presentación visual y resuelve discrepancias documentales o físicas |

**Criterios de aceptación:**

- **[F] Funcional:** el código se ejecuta sin error y produce la salida esperada.
- **[P] Físico:** el resultado numérico coincide con la predicción del MATHSPEC dentro de la tolerancia indicada.

Los criterios **[P]** son no negociables. Un resultado que compila, pero produce un valor físico incorrecto, es un fallo de etapa.

**Regla de contradicciones:** si durante una etapa hay conflicto entre MATHSPEC, ARCH, PRD o IMPL, la IA no debe inventar una interpretación. Debe detener la etapa y crear `CONTRADICTIONS.md` según `AGENT_INSTRUCTIONS.md`.

---

## Alcance por versión

### MVP obligatorio

Las etapas **0 a 8** constituyen el MVP obligatorio.

El MVP debe entregar:

- Carga reproducible de un perfil local CSV.
- Curvatura terrestre mediante factor \(K\).
- Línea de visión directa.
- Primera zona de Fresnel y despeje de 60%.
- Parámetro Fresnel-Kirchhoff \(v\).
- Difracción Knife-Edge de obstáculo único.
- Curva \(G_d(v)\).
- Perfil geográfico de Lima cargado localmente.
- Validaciones físicas automatizadas.
- Visualización estática e interactiva con sliders de frecuencia, \(K\), \(h_\mathrm{Tx}\) y \(h_\mathrm{Rx}\).

### Extensiones verificadas

Las etapas **9 a 11** son extensiones y solo comienzan cuando las etapas 0 a 8 estén completadas y `pytest -q` no presente fallos.

- Etapa 9: Diseño B.
- Etapa 10: Power budget y disponibilidad.
- Etapa 11: Descarga de perfil por API.

Los módulos `core/extensions/multipath.py` y `core/extensions/attenuation.py` no forman parte del pipeline V1 ni de estas etapas. Se conservan únicamente como extensiones futuras documentadas.

---

## Etapa 0 — Scaffolding del proyecto

### Objetivo

Crear la estructura completa del proyecto, los archivos de configuración, el documento de instrucciones para la IA y un punto de entrada importable. Al finalizar esta etapa, el proyecto puede instalarse y ejecutarse aunque aún no calcule un enlace.

### Módulos a generar

- Estructura de carpetas completa según ARCH §3.
- `requirements.txt`.
- `AGENT_INSTRUCTIONS.md`.
- `config/constants.py`.
- `config/defaults.py`.
- Todos los `__init__.py`.
- `main.py` como stub.
- Estructura inicial de `tests/`.

### Instrucción para la IA

> Genera la estructura de carpetas completa de `radiolink/` exactamente según ARCH §3. Crea `config/constants.py` con `C_LIGHT`, `R_EARTH`, `R_EARTH_KM`, `K_STANDARD` y `G_STANDARD`. Crea `config/defaults.py` con los valores de ARCH §4. Crea `requirements.txt` según ARCH §10, incluyendo pytest. Crea `AGENT_INSTRUCTIONS.md` exactamente según ARCH §11. Crea todos los `__init__.py` requeridos. Crea `main.py` como stub que importe `config.constants` y `config.defaults`, e imprima `RadioLink LOS v1.1` junto con las constantes. Crea `tests/test_scaffolding.py`.

### Tests de aceptación

Implementar en `tests/test_scaffolding.py`.

```python
def test_constants_exist():
    from config.constants import R_EARTH, K_STANDARD

    assert R_EARTH == 6_371_000
    assert abs(K_STANDARD - 4 / 3) < 1e-12


def test_main_importable():
    import main

    assert main is not None
```

**[F-0.1]** `pip install -r requirements.txt` completa sin errores.

**[F-0.2]** `python main.py` ejecuta sin `ImportError`.

**[F-0.3]** `pytest -q` ejecuta sin fallos.

**[P-0.1]** `R_EARTH == 6_371_000`.

**[P-0.2]** `K_STANDARD == 4/3`.

---

## Etapa 1 — Modelos de datos y carga de CSV

### Objetivo

Implementar los contratos de datos inmutables, el cargador de perfiles CSV y los datos de validación. Al finalizar esta etapa, el sistema puede cargar un perfil de terreno y acceder a sus arrays de forma segura.

### Módulos a generar

- `models/params.py`.
- `models/terrain.py`.
- `models/profile.py`.
- `data/loader.py`.
- `data/profiles/validation_flat.csv`.
- `data/profiles/validation_edge.csv`.
- `tests/test_loader.py`.
- `tests/test_models.py`.

### Reglas de implementación

- `LinkParams` y `PowerBudgetParams` usan `@dataclass(frozen=True)`.
- `TerrainData` puede ser `@dataclass(frozen=True)`.
- `LinkProfile` usa `@dataclass(frozen=True)`.
- `LinkProfile` no usa campos `Optional` para arrays físicos obligatorios.
- `validation_flat.csv` debe contener 201 puntos desde 0 m hasta 10 000 m, con espaciamiento de 50 m y elevación cero.
- `validation_edge.csv` debe contener la misma grilla de distancias, inicialmente con elevación cero; su pico se define completamente en la etapa 2.

### Instrucción para la IA

> Implementa `models/params.py`, `models/terrain.py`, `models/profile.py` y `data/loader.py` según ARCH §4. `LinkParams` y `PowerBudgetParams` deben ser frozen dataclasses. `TerrainData` debe incluir `d_total_m`, `d2_m` y `n_points`. `LinkProfile` debe incluir todos los campos definidos en ARCH §4, incluyendo `h_sup_m`, `h_inf_m` y `h_60pct_m`. Implementa `load_terrain_csv` y `save_terrain_csv`. `load_terrain_csv` debe validar las condiciones de ARCH §8 y lanzar `TerrainLoadError` con mensaje descriptivo. Genera `validation_flat.csv` y una versión inicial de `validation_edge.csv` con la grilla requerida. Crea tests pytest para cada criterio.

### Tests de aceptación

Implementar en `tests/test_loader.py` y `tests/test_models.py`.

```python
from dataclasses import FrozenInstanceError

import pandas as pd
import pytest

from data.loader import TerrainLoadError, load_terrain_csv
from models.params import LinkParams


def test_load_validation_flat():
    terrain = load_terrain_csv("data/profiles/validation_flat.csv")

    assert terrain.n_points == 201
    assert terrain.d_total_m == 10_000.0
    assert terrain.d2_m == 10_000.0
    assert terrain.d2_m[-1] == 0.0


def test_d2_m_at_center():
    terrain = load_terrain_csv("data/profiles/validation_flat.csv")

    assert abs(terrain.d2_m - 5_000.0) < 1e-12


def test_invalid_non_monotonic_csv_raises(tmp_path):
    bad_path = tmp_path / "bad.csv"

    pd.DataFrame(
        {
            "distance_m": [0.0, 100.0, 50.0],
            "latitude": [0.0, 0.0, 0.0],
            "longitude": [0.0, 0.0, 0.0],
            "elevation_m": [0.0, 0.0, 0.0],
        }
    ).to_csv(bad_path, index=False)

    with pytest.raises(TerrainLoadError):
        load_terrain_csv(str(bad_path))


def test_link_params_are_immutable():
    params = LinkParams(
        f_hz=7e9,
        h_tx_m=10.0,
        h_rx_m=10.0,
        K=4 / 3,
    )

    with pytest.raises(FrozenInstanceError):
        params.K = 1.0
```

**[F-1.1]** `validation_flat.csv` se carga correctamente.

**[F-1.2]** Un CSV no monótono lanza `TerrainLoadError`.

**[F-1.3]** `LinkParams` no permite mutación directa.

**[P-1.1]** `d2_m[100] == 5_000.0` m.

---

## Etapa 2 — Atmósfera y geometría

### Objetivo

Implementar la corrección por curvatura terrestre, la elevación efectiva, las alturas absolutas de antena y la LOS. También se genera de forma definitiva el caso V-2 de borde exactamente sobre la LOS.

### Módulos a generar

- `core/atmosphere.py`.
- `core/geometry.py`.
- `validation/cases.py`, versión inicial.
- Actualización final de `data/profiles/validation_edge.csv`.
- `tests/test_atmosphere.py`.
- `tests/test_geometry.py`.

### Regla importante

`z_eff_m` representa únicamente terreno corregido por curvatura:

\[
z_{\mathrm{eff}} = z_{\mathrm{raw}} + h_{\mathrm{ER}}
\]

Las alturas de antena no se suman dentro de `z_eff_m`. Solo se usan para construir:

\[
H_{\mathrm{Tx}} = z_{\mathrm{Tx}} + h_{\mathrm{Tx}}
\]

\[
H_{\mathrm{Rx}} = z_{\mathrm{Rx}} + h_{\mathrm{Rx}}
\]

### Instrucción para la IA

> Implementa `core/atmosphere.py` con `k_from_gradient`, `gradient_from_k`, `earth_curvature_correction` y `effective_elevation`, según ARCH §4 y MATHSPEC. Implementa `core/geometry.py` con `antenna_heights_msl` y `los_height`. Todas las funciones operan en SI. Cada función física incluye `Ref: EQ-XX` en su docstring. Implementa los tests pytest descritos. Define `case_edge_on_los()` de manera reproducible: el perfil contiene un pico en `d1=4_000 m`, con `d_total=10_000 m`, `h_tx=10 m`, `h_rx=10 m`, terreno base cero y `K=1e12` para anular curvatura. La elevación del pico debe ser exactamente 10 m, pues la LOS es horizontal a 10 m.

### Tests de aceptación

Implementar en `tests/test_atmosphere.py` y `tests/test_geometry.py`.

```python
import numpy as np

from config.constants import K_STANDARD
from core.atmosphere import (
    earth_curvature_correction,
    effective_elevation,
    gradient_from_k,
    k_from_gradient,
)
from core.geometry import antenna_heights_msl, los_height


def test_standard_k_from_gradient():
    K = k_from_gradient(-39.0)

    assert abs(K - 4 / 3) < 0.001


def test_gradient_from_standard_k():
    gradient = gradient_from_k(4 / 3)

    assert abs(gradient - (-39.0)) < 0.01


def test_earth_curvature_professor_example():
    d1_m = np.array([8_000.0])
    d2_m = np.array([12_000.0])

    h_er_m = earth_curvature_correction(d1_m, d2_m, 1.33)

    assert abs(h_er_m - 5.666) < 0.05


def test_earth_curvature_is_zero_at_endpoints():
    d1_m = np.array([0.0, 5_000.0, 10_000.0])
    d2_m = np.array([10_000.0, 5_000.0, 0.0])

    h_er_m = earth_curvature_correction(d1_m, d2_m, K_STANDARD)

    assert h_er_m == 0.0
    assert h_er_m[-1] == 0.0


def test_effective_elevation_does_not_include_antennas():
    z_raw_m = np.array([100.0, 120.0, 100.0])
    h_er_m = np.array([0.0, 5.0, 0.0])

    z_eff_m = effective_elevation(z_raw_m, h_er_m)

    assert np.allclose(z_eff_m, np.array([100.0, 125.0, 100.0]))


def test_los_is_horizontal_for_equal_endpoint_heights():
    H_tx_m, H_rx_m = antenna_heights_msl(
        z_tx_m=0.0,
        h_tx_m=10.0,
        z_rx_m=0.0,
        h_rx_m=10.0,
    )

    d1_m = np.linspace(0.0, 10_000.0, 201)
    h_los_m = los_height(H_tx_m, H_rx_m, d1_m, 10_000.0)

    assert np.allclose(h_los_m, 10.0)


def test_los_professor_example():
    H_tx_m, H_rx_m = antenna_heights_msl(
        z_tx_m=0.0,
        h_tx_m=110.0,
        z_rx_m=0.0,
        h_rx_m=150.0,
    )

    h_los_m = los_height(
        H_tx_m,
        H_rx_m,
        np.array([8_000.0]),
        20_000.0,
    )

    assert abs(h_los_m - 126.0) < 0.1
```

**[P-2.1]** \(K(-39)=4/3\) dentro de 0.001.

**[P-2.2]** La inversión \(K \rightarrow dN/dh\) devuelve −39 N-units/km.

**[P-2.3]** Para el ejemplo del profesor, \(h_{\mathrm{ER}}=5.666\pm0.05\) m.

**[P-2.4]** La curvatura en los extremos es cero.

**[P-2.5]** Antenas de igual altura sobre terreno plano generan LOS horizontal.

**[P-2.6]** La LOS del ejemplo del profesor vale \(126.0\pm0.1\) m.

---

## Etapa 3 — Zonas de Fresnel y despeje

### Objetivo

Implementar el radio de Fresnel, bandas superior e inferior, umbral de 60%, despeje LOS, altura de obstáculo y despeje de Fresnel.

### Módulos a generar

- `core/fresnel_zones.py`.
- `tests/test_fresnel_zones.py`.

### Instrucción para la IA

> Implementa `core/fresnel_zones.py` según ARCH §4. `fresnel_radius_n` debe devolver 0.0 en extremos. `fresnel_bands` debe devolver `h_sup_m`, `h_inf_m` y `h_60pct_m`. No se permite calcular bandas de Fresnel en `ui/`; solo `core` puede hacerlo. Implementa las pruebas pytest.

### Tests de aceptación

Implementar en `tests/test_fresnel_zones.py`.

```python
import numpy as np

from config.constants import C_LIGHT
from core.fresnel_zones import (
    ffz_clearance,
    fresnel_bands,
    fresnel_radius_n,
    los_clearance,
    obstacle_height,
)


def test_fresnel_radius_professor_example():
    lam_m = C_LIGHT / 900e6
    d1_m = np.array([8_000.0])
    d2_m = np.array([12_000.0])

    r1_m = fresnel_radius_n(1, lam_m, d1_m, d2_m)

    assert abs(r1_m - 39.986) < 0.05


def test_fresnel_radius_maximum_at_center():
    lam_m = C_LIGHT / 900e6
    d1_m = np.array([4_900.0, 5_000.0, 5_100.0])
    d2_m = 10_000.0 - d1_m

    r1_m = fresnel_radius_n(1, lam_m, d1_m, d2_m)

    assert r1_m >= r1_m[1]
    assert r1_m >= r1_m[2][1]


def test_fresnel_radius_zero_at_endpoints():
    lam_m = C_LIGHT / 900e6
    d1_m = np.array([0.0, 5_000.0, 10_000.0])
    d2_m = 10_000.0 - d1_m

    r1_m = fresnel_radius_n(1, lam_m, d1_m, d2_m)

    assert r1_m == 0.0
    assert r1_m[-1] == 0.0


def test_los_clearance_professor_example():
    h_los_m = np.array([126.0])
    z_eff_m = np.array([125.666])

    c_los_m = los_clearance(h_los_m, z_eff_m)

    assert abs(c_los_m - 0.334) < 0.05


def test_ffz_clearance_professor_example():
    c_los_m = np.array([0.334])
    r1_m = np.array([39.986])

    c_ffz_m = ffz_clearance(c_los_m, r1_m)

    assert abs(c_ffz_m - (-23.657)) < 0.1


def test_obstacle_height_sign():
    c_los_m = np.array([0.334])

    h_o_m = obstacle_height(c_los_m)

    assert abs(h_o_m - (-0.334)) < 0.01


def test_fresnel_bands():
    h_los_m = np.array([100.0])
    r1_m = np.array([20.0])

    upper_m, lower_m, clearance_60_m = fresnel_bands(h_los_m, r1_m)

    assert upper_m == 120.0
    assert lower_m == 80.0
    assert clearance_60_m == 88.0
```

**[P-3.1]** \(r_1=39.986\pm0.05\) m para el ejemplo del profesor.

**[P-3.2]** El radio de Fresnel es máximo en el centro de un trayecto simétrico.

**[P-3.3]** \(C_{\mathrm{LOS}}=0.334\pm0.05\) m.

**[P-3.4]** \(C_{\mathrm{FFZ}}=-23.657\pm0.1\) m.

**[P-3.5]** El radio Fresnel es cero en Tx y Rx.

---

## Etapa 4 — Motor de difracción

### Objetivo

Implementar el parámetro Fresnel-Kirchhoff, la función de difracción exacta, el coeficiente \(G_d\), la pérdida adicional \(L_d\) y la selección del obstáculo crítico.

Esta es la etapa físicamente más crítica del proyecto.

### Módulos a generar

- `core/diffraction.py`.
- `tests/test_diffraction.py`.

### Regla de pérdida

La función exacta produce:

\[
G_d(v)=20\log_{10}|F(v)|
\]

La pérdida adicional para presupuesto de enlace es:

\[
L_d(v)=\max(0,-G_d(v))
\]

No se usa umbral empírico adicional. La curva visual representa \(G_d(v)\), mientras que el power budget usa \(L_d(v)\).

### Instrucción para la IA

> Implementa `core/diffraction.py` según ARCH §4 y MATHSPEC. `fresnel_kirchhoff_parameter` debe retornar `np.nan` en extremos. `critical_obstacle_index` debe usar `np.nanargmax(v)`. `diffraction_function` debe usar `scipy.special.fresnel(v)`, recordando que SciPy retorna `(S, C)`. `diffraction_gain_db` devuelve el valor exacto de EQ-17. `diffraction_loss_db` devuelve `max(0.0, -diffraction_gain_db(v))`. `diffraction_curve` representa `G_d(v)`, no la pérdida truncada. Implementa todos los tests pytest.

### Tests de aceptación

Implementar en `tests/test_diffraction.py`.

```python
import numpy as np
from scipy.special import fresnel as scipy_fresnel

from config.constants import C_LIGHT
from core.diffraction import (
    critical_obstacle_index,
    diffraction_function,
    diffraction_gain_db,
    diffraction_loss_db,
    fresnel_kirchhoff_parameter,
)


def test_diffraction_exact_value_at_v_zero():
    F0 = diffraction_function(0.0)
    g_d_db = diffraction_gain_db(0.0)
    l_d_db = diffraction_loss_db(0.0)

    assert abs(abs(F0) - 0.5) < 1e-6
    assert abs(g_d_db - (-6.0206)) < 0.01
    assert abs(l_d_db - 6.0206) < 0.01


def test_diffraction_function_matches_manual_construction_at_zero():
    S0, C0 = scipy_fresnel(0.0)

    F0_manual = (1.0 + 1.0j) / 2.0 * (
        (0.5 - C0) - 1.0j * (0.5 - S0)
    )

    assert abs(abs(F0_manual) - 0.5) < 1e-10


def test_v_sign_convention():
    lam_m = C_LIGHT / 7e9
    d1_m = np.array([np.nan, 4_000.0, np.nan])
    d2_m = np.array([np.nan, 6_000.0, np.nan])

    h_o_obstructed_m = np.array([np.nan, 50.0, np.nan])
    h_o_clear_m = np.array([np.nan, -20.0, np.nan])

    v_obstructed = fresnel_kirchhoff_parameter(
        h_o_obstructed_m,
        lam_m,
        d1_m,
        d2_m,
    )

    v_clear = fresnel_kirchhoff_parameter(
        h_o_clear_m,
        lam_m,
        d1_m,
        d2_m,
    )

    assert v_obstructed > 0.0[1]
    assert v_clear < 0.0[1]


def test_v_is_nan_at_endpoints():
    lam_m = C_LIGHT / 7e9
    d1_m = np.array([0.0, 4_000.0, 10_000.0])
    d2_m = np.array([10_000.0, 6_000.0, 0.0])
    h_o_m = np.array([0.0, 50.0, 0.0])

    v = fresnel_kirchhoff_parameter(h_o_m, lam_m, d1_m, d2_m)

    assert np.isnan(v)
    assert np.isnan(v[-1])


def test_critical_obstacle_is_selected_by_v():
    lam_m = C_LIGHT / 7e9
    d1_m = np.array([np.nan, 1_000.0, 5_000.0, np.nan])
    d2_m = np.array([np.nan, 9_000.0, 5_000.0, np.nan])
    h_o_m = np.array([np.nan, 100.0, 50.0, np.nan])

    v = fresnel_kirchhoff_parameter(h_o_m, lam_m, d1_m, d2_m)

    assert critical_obstacle_index(v) == np.nanargmax(v)


def test_diffraction_loss_is_never_negative():
    for value in np.linspace(-10.0, 10.0, 200):
        assert diffraction_loss_db(float(value)) >= 0.0
```

**[P-4.1]** Para \(v=0\): \(|F|=0.5\), \(G_d=-6.0206\) dB y \(L_d=6.0206\) dB.

**[P-4.2]** El signo de \(v\) sigue la convención: obstrucción positiva, despeje negativo.

**[P-4.3]** Los extremos producen `np.nan` en \(v\).

**[P-4.4]** El obstáculo crítico se selecciona por máximo \(v\), no por máxima altura absoluta.

**[P-4.5]** \(L_d\) nunca es negativa.

---

## Etapa 5 — Presupuesto de enlace

### Objetivo

Implementar pérdida de espacio libre, potencia recibida, margen y disponibilidad.

### Módulos a generar

- `core/link_budget.py`.
- `tests/test_link_budget.py`.

### Instrucción para la IA

> Implementa `core/link_budget.py` según ARCH §4. `free_space_loss_db` usa la forma SI de Friis. `received_power_dbm` resta `l_d_db` como pérdida adicional. `link_margin_db` aplica EQ-23. `link_availability` aplica EQ-24. Implementa los tests pytest.

### Tests de aceptación

Implementar en `tests/test_link_budget.py`.

```python
import numpy as np

from config.constants import C_LIGHT
from core.link_budget import (
    free_space_loss_db,
    link_availability,
    link_margin_db,
    received_power_dbm,
)
from models.params import LinkParams, PowerBudgetParams


def build_params():
    return LinkParams(
        f_hz=7e9,
        h_tx_m=10.0,
        h_rx_m=10.0,
        K=4 / 3,
    )


def build_power_budget_params():
    return PowerBudgetParams(
        p_tx_dbm=40.0,
        g_tx_dbi=30.0,
        g_rx_dbi=30.0,
        l_cable_tx_db=1.0,
        l_cable_rx_db=1.0,
        sensitivity_dbm=-80.0,
        a_climate=0.5,
        b_terrain=1.0,
    )


def test_free_space_loss_professor_example():
    lam_m = C_LIGHT / 900e6
    expected_db = 20.0 * np.log10(4.0 * np.pi * 6_000.0 / lam_m)

    result_db = free_space_loss_db(6_000.0, 900e6)

    assert abs(result_db - expected_db) < 0.01


def test_free_space_loss_matches_ghz_km_expression():
    result_db = free_space_loss_db(6_000.0, 900e6)
    expected_db = 92.45 + 20.0 * np.log10(0.9) + 20.0 * np.log10(6.0)

    assert abs(result_db - expected_db) < 0.1


def test_received_power_without_diffraction_matches_manual_budget():
    params = build_params()
    pb = build_power_budget_params()

    l_fs_db = free_space_loss_db(20_000.0, 7e9)
    p_rx_dbm = received_power_dbm(params, pb, l_fs_db, 0.0)

    expected_dbm = 40.0 + 30.0 - 1.0 - l_fs_db + 30.0 - 1.0

    assert abs(p_rx_dbm - expected_dbm) < 0.01


def test_diffraction_loss_reduces_received_power_exactly():
    params = build_params()
    pb = build_power_budget_params()
    l_fs_db = free_space_loss_db(20_000.0, 7e9)

    p_rx_without_ld = received_power_dbm(params, pb, l_fs_db, 0.0)
    p_rx_with_ld = received_power_dbm(params, pb, l_fs_db, 10.0)

    assert abs((p_rx_without_ld - p_rx_with_ld) - 10.0) < 0.01


def test_link_margin():
    assert link_margin_db(-70.0, -80.0) == 10.0


def test_availability_increases_with_margin():
    a_20 = link_availability(20.0, 7.0, 20.0, 0.5, 1.0)
    a_30 = link_availability(30.0, 7.0, 20.0, 0.5, 1.0)

    assert a_30 > a_20
```

**[P-5.1]** La forma SI de \(L_\mathrm{fs}\) coincide con el ejemplo del profesor.

**[P-5.2]** La forma SI y la forma GHz/km difieren menos de 0.1 dB.

**[P-5.3]** Agregar \(L_d=10\) dB reduce \(P_\mathrm{Rx}\) exactamente en 10 dB.

**[P-5.4]** La disponibilidad aumenta cuando aumenta el margen.

---

## Etapa 6 — Motor orquestador e integración

### Objetivo

Implementar el motor completo, poblar todos los campos de `LinkProfile`, verificar invariantes y validar los tres casos integrados.

### Módulos a generar

- `core/engine.py`.
- `validation/cases.py`.
- `tests/test_engine.py`.

### Instrucción para la IA

> Implementa `compute_link_profile` exactamente según el pipeline de ARCH §4 y §6. Debe poblar todos los campos de `LinkProfile`, incluyendo las tres bandas de Fresnel. Antes de retornar, debe verificar las invariantes de ARCH §4. Implementa `case_flat_earth`, `case_edge_on_los` y `case_lima`. Los casos V-1 y V-2 deben ser deterministas, sin red. `case_lima` debe cargar el CSV local. No usar `copy.copy`; cualquier modificación de parámetros en tests usa `dataclasses.replace`.

### Definición obligatoria del Caso V-1

```text
d_total_m = 10_000 m
n_points = 201
distance spacing = 50 m
terreno = 0 m
f_hz = 7e9 Hz
K = 1e12
h_tx_m = 14.64 m
h_rx_m = 14.64 m
```

El punto central está en \(d_1=d_2=5\,000\) m.

El valor esperado es:

```text
v_critical ≈ -2.00
L_d = 0.00 dB
```

La tolerancia permitida para \(v_\mathrm{critical}\) es 0.03 debido al redondeo de altura de antena.

### Definición obligatoria del Caso V-2

```text
d_total_m = 10_000 m
n_points = 201
d1_peak_m = 4_000 m
d2_peak_m = 6_000 m
terreno base = 0 m
elevación del pico = 10 m
f_hz = 7e9 Hz
K = 1e12
h_tx_m = 10 m
h_rx_m = 10 m
```

Resultado esperado:

```text
h_o = 0
v_critical = 0
G_d = -6.0206 dB
L_d = 6.0206 dB
```

### Tests de aceptación

Implementar en `tests/test_engine.py`.

```python
from dataclasses import replace

import numpy as np

from core.diffraction import diffraction_gain_db, diffraction_loss_db
from core.engine import compute_link_profile
from core.link_budget import free_space_loss_db
from validation.cases import case_edge_on_los, case_flat_earth, case_lima


def assert_profile_invariants(profile):
    terrain = profile.terrain
    n = terrain.n_points

    arrays = [
        profile.h_er_m,
        profile.z_eff_m,
        profile.h_los_m,
        profile.r1_m,
        profile.h_sup_m,
        profile.h_inf_m,
        profile.h_60pct_m,
        profile.c_los_m,
        profile.h_o_m,
        profile.c_ffz_m,
        profile.v,
    ]

    assert all(len(array) == n for array in arrays)

    assert profile.h_er_m == 0.0
    assert profile.h_er_m[-1] == 0.0

    assert np.allclose(
        profile.z_eff_m,
        terrain.elevation_m + profile.h_er_m,
    )

    assert profile.r1_m == 0.0
    assert profile.r1_m[-1] == 0.0

    assert np.isnan(profile.v)
    assert np.isnan(profile.v[-1])

    assert 1 <= profile.idx_critical <= n - 2
    assert profile.idx_critical == np.nanargmax(profile.v)
    assert profile.v_critical == profile.v[profile.idx_critical]

    assert abs(
        profile.g_d_db - diffraction_gain_db(profile.v_critical)
    ) < 1e-12

    assert abs(
        profile.l_d_db - diffraction_loss_db(profile.v_critical)
    ) < 1e-12

    assert profile.l_d_db >= 0.0
    assert profile.l_fs_db > 0.0


def test_case_v1_flat_earth():
    terrain, params = case_flat_earth()
    profile = compute_link_profile(params, terrain)

    assert_profile_invariants(profile)
    assert abs(profile.v_critical - (-2.0)) < 0.03
    assert profile.l_d_db == 0.0


def test_case_v2_edge_on_los():
    terrain, params = case_edge_on_los()
    profile = compute_link_profile(params, terrain)

    assert_profile_invariants(profile)
    assert abs(profile.v_critical) < 0.05
    assert abs(profile.g_d_db - (-6.0206)) < 0.01
    assert abs(profile.l_d_db - 6.0206) < 0.01


def test_case_v3_lima_internal_consistency():
    terrain, params = case_lima()
    profile = compute_link_profile(params, terrain)

    assert_profile_invariants(profile)

    expected_lfs_db = free_space_loss_db(
        terrain.d_total_m,
        params.f_hz,
    )

    assert abs(profile.l_fs_db - expected_lfs_db) < 0.01


def test_k_changes_result_for_lima():
    terrain, params = case_lima()

    profile_k1 = compute_link_profile(
        replace(params, K=1.0),
        terrain,
    )

    profile_kstandard = compute_link_profile(
        replace(params, K=4 / 3),
        terrain,
    )

    assert not np.allclose(
        profile_k1.h_er_m,
        profile_kstandard.h_er_m,
    )

    assert profile_k1.v_critical != profile_kstandard.v_critical
```

**[P-6.1]** V-1 produce \(v_\mathrm{critical}=-2.00\pm0.03\) y \(L_d=0\) dB.

**[P-6.2]** V-2 produce \(v_\mathrm{critical}=0\pm0.05\) y \(L_d=6.0206\pm0.01\) dB.

**[P-6.3]** V-3 cumple todas las invariantes y calcula \(L_\mathrm{fs}\) idéntico a su forma analítica.

**[P-6.4]** Cambiar \(K\) modifica el perfil efectivo y el valor crítico del trayecto de Lima.

---

## Etapa 7 — Visualización estática

### Objetivo

Implementar la figura completa, sin widgets, usando exclusivamente datos de `LinkProfile`.

### Módulos a generar

- `ui/layout.py`.
- `ui/artists.py`.
- `ui/panels/terrain_panel.py`.
- `ui/panels/diffraction_panel.py`.
- `ui/panels/results_panel.py`.
- `ui/app.py`, versión estática.
- `tests/test_ui_static.py`.

### Instrucción para la IA

> Implementa la visualización estática según ARCH §7. La figura debe medir 14×10 pulgadas. `ui/artists.py` crea los artistas una única vez. `terrain_panel.py` representa terreno crudo, terreno efectivo, LOS, bandas Fresnel, umbral del 60%, mástiles y obstáculo crítico usando únicamente `LinkProfile`. `diffraction_panel.py` grafica `G_d(v)` para 500 puntos en el rango [−3, 3]. `results_panel.py` muestra valores numéricos. No usar `ax.clear()` en los paneles de terreno o difracción. La UI no puede recalcular física.

### Tests de aceptación

Implementar pruebas básicas sin abrir interfaz bloqueante, usando backend `Agg`.

```python
import matplotlib

matplotlib.use("Agg")


def test_static_app_can_be_created():
    from ui.app import App
    from validation.cases import case_lima

    terrain, _ = case_lima()
    app = App(terrain)

    assert app is not None
```

**[F-7.1]** La aplicación estática se crea sin errores de Matplotlib.

**[F-7.2]** La figura incluye tres paneles: perfil, curva de difracción y resultados.

**[F-7.3]** La banda Fresnel se construye desde `profile.h_sup_m` y `profile.h_inf_m`.

**[F-7.4]** El marcador de obstáculo usa `profile.idx_critical`.

**[F-7.5]** El panel de difracción marca \((v_\mathrm{critical}, G_d)\).

**[F-7.6]** Ningún módulo de `ui/` importa funciones físicas individuales desde `core/`; la UI trabaja con `LinkProfile`.

---

## Etapa 8 — Widgets interactivos

### Objetivo

Agregar sliders de frecuencia, \(K\), altura Tx y altura Rx. El usuario debe poder explorar cambios de diseño sin modificar directamente dataclasses inmutables.

### Módulos a generar

- `ui/callbacks.py`.
- Actualización de `ui/app.py`.
- Actualización de `ui/layout.py`.
- `tests/test_callbacks.py`.

### Instrucción para la IA

> Implementa sliders para frecuencia, K, hTx y hRx. Cada callback debe usar `dataclasses.replace` sobre `app.params_a` y luego llamar `app._recompute()`. No se permite mutación directa. El slider de K actualiza un campo de solo lectura con el gradiente equivalente `dN/dh`. El toggle de terreno crudo/efectivo solo modifica visibilidad; no recalcula física. Los botones de casos cargan un `TerrainData` y un `LinkParams` de `validation.cases`, y luego recalculan.

### Tests de aceptación

```python
from dataclasses import replace

from validation.cases import case_flat_earth


def test_replace_creates_new_params_without_mutating_original():
    _, params = case_flat_earth()

    new_params = replace(params, f_hz=14e9)

    assert params.f_hz == 7e9
    assert new_params.f_hz == 14e9
    assert params is not new_params
```

**[F-8.1]** Cambiar frecuencia de 7 GHz a 14 GHz estrecha visualmente la banda Fresnel.

**[F-8.2]** Cambiar \(K\) modifica el perfil efectivo y el resultado crítico.

**[F-8.3]** El valor de \(dN/dh\) se actualiza automáticamente al modificar \(K\).

**[F-8.4]** El toggle de terreno crudo/efectivo no altera `LinkProfile`.

**[P-8.1]** Al cargar V-2 desde la interfaz, el resultado mostrado es \(L_d=6.0206\pm0.01\) dB.

---

# Extensiones posteriores

Las etapas siguientes no son requisito para el MVP.

---

## Etapa 9 — Diseño B y comparación

### Objetivo

Comparar dos conjuntos de alturas de antena sobre el mismo trayecto.

### Módulos a modificar

- `ui/app.py`.
- `ui/layout.py`.
- `ui/artists.py`.
- `ui/callbacks.py`.
- `ui/panels/terrain_panel.py`.
- `ui/panels/diffraction_panel.py`.
- `ui/panels/results_panel.py`.
- Tests correspondientes.

### Instrucción para la IA

> Agrega Diseño B sin modificar Diseño A. `params_b` debe ser otro `LinkParams` inmutable. Cuando Diseño B esté activo, se calcula un segundo `LinkProfile`. La UI debe mostrar ambas LOS, ambas bandas Fresnel y ambos puntos de operación. Si los parámetros son idénticos, los resultados deben ser numéricamente idénticos.

### Tests de aceptación

**[F-9.1]** Diseño A y B muestran LOS diferenciadas.

**[P-9.1]** Si `params_b == params_a`, entonces:

```text
v_critical_A == v_critical_B
G_d_A == G_d_B
L_d_A == L_d_B
```

con tolerancia menor a \(10^{-12}\).

**[P-9.2]** Elevar una antena en Diseño B reduce \(v_\mathrm{critical}\) y no aumenta \(L_d\) cuando el obstáculo dominante permanece único.

---

## Etapa 10 — Power budget y disponibilidad

### Objetivo

Activar el presupuesto de enlace usando \(L_d\) como pérdida adicional.

### Módulos a modificar

- `ui/app.py`.
- `ui/panels/results_panel.py`.
- Tests de integración de power budget.

### Instrucción para la IA

> Agrega campos opcionales para `PowerBudgetParams`. Cuando se active, `compute_link_profile` recibe esos parámetros. La interfaz muestra `L_fs`, `L_d`, `P_Rx`, margen y disponibilidad. No usar la palabra “viable” como garantía absoluta; mostrar por separado “margen respecto a sensibilidad” y “disponibilidad calculada”.

### Tests de aceptación

**[P-10.1]** Con \(L_d=0\), \(P_\mathrm{Rx}\) coincide con Friis.

**[P-10.2]** Para el mismo enlace:

\[
P_{\mathrm{Rx},B}-P_{\mathrm{Rx},A}
=
L_{d,A}-L_{d,B}
\]

con tolerancia menor a 0.01 dB.

**[P-10.3]** Una reducción de 10 dB en margen reduce la disponibilidad conforme a EQ-24.

---

## Etapa 11 — Descarga API

### Objetivo

Implementar una fuente secundaria de perfiles mediante Open-Elevation.

### Módulos a generar

- `data/downloader.py`.
- `tests/test_downloader.py`, usando mocks para no depender de red.

### Instrucción para la IA

> Implementa `download_elevation_profile`. Debe generar puntos, consultar la API, validar respuesta, construir `TerrainData` y guardar un CSV reutilizable. La prueba automatizada debe usar mocks de requests; no depender de la red pública. El uso real de red se valida manualmente antes de la presentación, nunca como condición de `pytest`.

### Tests de aceptación

**[F-11.1]** Un response mock válido produce `TerrainData` válido.

**[F-11.2]** Un timeout o respuesta inválida genera `DownloadError`.

**[F-11.3]** El CSV generado puede cargarse mediante `load_terrain_csv`.

---

## Resumen de etapas

| Etapa | Estado | Módulos principales | Criterio físico principal |
|---|---|---|---|
| 0 | MVP | Configuración, estructura, instrucciones IA | \(K_\mathrm{standard}=4/3\) |
| 1 | MVP | Models y loader CSV | `d2_m` correcto |
| 2 | MVP | Curvatura y geometría | \(h_\mathrm{ER}=5.666\) m |
| 3 | MVP | Fresnel y despeje | \(r_1=39.986\) m |
| 4 | MVP | Difracción | \(L_d(v=0)=6.0206\) dB |
| 5 | MVP | Power budget core | \(L_d\) reduce \(P_\mathrm{Rx}\) exactamente |
| 6 | MVP | Engine e integración | V-1 y V-2 reproducibles |
| 7 | MVP | UI estática | Perfil y curva correctos |
| 8 | MVP | UI interactiva | Recalculo correcto con sliders |
| 9 | Extensión | Diseño B | A = B si parámetros iguales |
| 10 | Extensión | Power budget UI | Diferencia de potencia igual a diferencia de \(L_d\) |
| 11 | Extensión | Descarga API | CSV descargado válido |
