# ARCH — Documento de Arquitectura del Evaluador de Radioenlace LOS

**Versión:** 1.1  
**Referencias cruzadas:** PRD v1.0, MATHSPEC v1.1, IMPL v1.1

---

## 1. Decisiones arquitectónicas fundamentales

**Separación física-total entre motor de cálculo e interfaz visual.** Ningún módulo de `core/` importa matplotlib. Ningún módulo de `ui/` ejecuta física. Esta regla es absoluta y permite testear el motor de cálculo sin levantar ninguna figura.

**Arrays numpy como moneda de intercambio.** Todos los arrays internos están en SI (metros, Hz, vatios). Las conversiones de unidades ocurren exclusivamente en los adaptadores de entrada (widgets → params) y de salida (results → panel de texto). Nunca dentro del motor.

**Flujo unidireccional de datos.** Params → Motor → Profile → Visualización. No hay estado compartido entre capas. Cada recálculo produce un nuevo objeto `LinkProfile` inmutable.

**Parámetros inmutables.** `LinkParams` y `PowerBudgetParams` se declaran con `@dataclass(frozen=True)`. Los callbacks no modifican atributos directamente; crean una nueva instancia mediante `dataclasses.replace(...)`.

**Docstrings con referencia a ecuación.** Cada función del motor incluye en su docstring `Ref: EQ-XX` apuntando al número de ecuación en MATHSPEC. Esto es un requisito de trazabilidad (RNF-06 del PRD).

**Motor V1 acotado.** El pipeline principal implementa curvatura, LOS, Fresnel, difracción Knife-Edge y presupuesto de enlace. Multicamino y atenuación se mantienen como extensiones documentadas, pero no son importadas ni ejecutadas por `engine.py` en V1.

---

## 2. Stack tecnológico

| Componente | Tecnología | Versión mínima | Justificación |
|---|---|---:|---|
| Lenguaje | Python | 3.10 | `dataclasses`, `typing`, `match/case`, f-strings |
| Aritmética vectorial | numpy | 1.24 | Arrays, máscaras, operaciones elemento a elemento |
| Integrales de Fresnel | scipy | 1.10 | `scipy.special.fresnel`, EQ-15 |
| Visualización e interactividad | matplotlib | 3.7 | Figures, Axes, Slider, Button y widgets integrados |
| Datos tabulares | pandas | 2.0 | Lectura y validación de CSV |
| Descarga API secundaria | requests | 2.28 | HTTP a Open-Elevation |
| Pruebas | pytest | 7.0 | Ejecución automatizada de criterios F y P |
| Tipado y contratos | dataclasses + typing | stdlib | Contratos de interfaz entre módulos |

Sin frameworks web, servidores, bases de datos ni GUI nativa con Tkinter o Qt.

---

## 3. Estructura de carpetas

```text
radiolink/
│
├── main.py                         # Punto de entrada único
├── requirements.txt
├── README.md
├── AGENT_INSTRUCTIONS.md           # Instrucciones obligatorias para IA agéntica
│
├── config/
│   ├── __init__.py
│   ├── constants.py                # Constantes físicas universales
│   └── defaults.py                 # Valores por defecto de parámetros
│
├── core/                           # Motor de cálculo, sin imports de matplotlib
│   ├── __init__.py
│   ├── atmosphere.py               # EQ-01 a EQ-05: K, dN/dh, hER, z_eff
│   ├── geometry.py                 # EQ-06 a EQ-07: H_Tx, H_Rx, h_LOS
│   ├── fresnel_zones.py            # EQ-08 a EQ-12: r1, bandas, C_LOS, C_FFZ
│   ├── diffraction.py              # EQ-13 a EQ-18: v, F(v), Gd, Ld
│   ├── link_budget.py              # EQ-20 a EQ-24: Lfs, P_Rx, margen, A
│   ├── engine.py                   # Orquestador del pipeline V1
│   └── extensions/
│       ├── __init__.py
│       ├── multipath.py            # EQ-25 a EQ-27: H(f), nulos
│       └── attenuation.py          # EQ-28 a EQ-32: gases, lluvia
│
├── models/                         # Dataclasses, contratos de datos
│   ├── __init__.py
│   ├── params.py                   # LinkParams, PowerBudgetParams
│   ├── terrain.py                  # TerrainData
│   └── profile.py                  # LinkProfile, resultado del motor
│
├── data/
│   ├── __init__.py
│   ├── loader.py                   # Carga y validación de CSV local
│   ├── downloader.py               # Fuente secundaria: Open-Elevation
│   └── profiles/
│       ├── lima_atocongo.csv       # Caso geográfico de Lima
│       ├── validation_flat.csv     # Caso V-1: tierra plana
│       └── validation_edge.csv     # Caso V-2: borde en LOS
│
├── ui/
│   ├── __init__.py
│   ├── app.py                      # Controlador principal
│   ├── layout.py                   # Figure, Axes y regiones de widgets
│   ├── artists.py                  # Caché de Line2D, PolyCollection y Text
│   ├── callbacks.py                # Handlers de widgets
│   └── panels/
│       ├── __init__.py
│       ├── terrain_panel.py        # Perfil, LOS, Fresnel y obstáculo
│       ├── diffraction_panel.py    # Curva Gd(v)
│       └── results_panel.py        # Tabla de resultados
│
├── validation/
│   ├── __init__.py
│   └── cases.py                    # Generadores de TerrainData para V-1, V-2 y V-3
│
└── tests/
    ├── __init__.py
    ├── test_loader.py
    ├── test_atmosphere.py
    ├── test_geometry.py
    ├── test_fresnel_zones.py
    ├── test_diffraction.py
    ├── test_link_budget.py
    └── test_engine.py
```

Los módulos `core/extensions/multipath.py` y `core/extensions/attenuation.py` se mantienen por trazabilidad con MATHSPEC, pero no son importados por `core/engine.py`, `ui/` ni `validation/` en V1.

---

## 4. Descripción de cada archivo

### `main.py`

Punto de entrada. Parsea argumentos de línea de comandos (`--source [local|api]`, `--profile <ruta_csv>`). Instancia `App` de `ui/app.py` y llama a `app.run()`. No contiene lógica de negocio.

```python
python main.py
python main.py --profile data/profiles/lima_atocongo.csv
python main.py --source api
```

La fuente API genera un CSV local y luego usa exactamente el mismo flujo de carga, cálculo y visualización que una fuente local.

---

### `config/constants.py`

```python
C_LIGHT = 3e8
R_EARTH = 6_371_000
R_EARTH_KM = 6_371.0
K_STANDARD = 4 / 3
G_STANDARD = -39.0
```

Unidades:

```text
C_LIGHT      [m/s]
R_EARTH      [m]
R_EARTH_KM   [km]
K_STANDARD   [-]
G_STANDARD   [N-units/km]
```

---

### `config/defaults.py`

```python
DEFAULT_FREQ_HZ = 7e9
DEFAULT_H_TX_M = 10.0
DEFAULT_H_RX_M = 10.0
DEFAULT_K = 4 / 3
DEFAULT_SPACING_M = 50.0
DEFAULT_PROFILE = "data/profiles/lima_atocongo.csv"
```

---

### `models/params.py`

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class LinkParams:
    f_hz: float
    h_tx_m: float
    h_rx_m: float
    K: float


@dataclass(frozen=True)
class PowerBudgetParams:
    p_tx_dbm: float
    g_tx_dbi: float
    g_rx_dbi: float
    l_cable_tx_db: float
    l_cable_rx_db: float
    sensitivity_dbm: float
    a_climate: float
    b_terrain: float
```

Unidades:

```text
LinkParams.f_hz       [Hz]
LinkParams.h_tx_m     [m]
LinkParams.h_rx_m     [m]
LinkParams.K          [-]

PowerBudgetParams.p_tx_dbm        [dBm]
PowerBudgetParams.g_tx_dbi        [dBi]
PowerBudgetParams.g_rx_dbi        [dBi]
PowerBudgetParams.l_cable_tx_db   [dB]
PowerBudgetParams.l_cable_rx_db   [dB]
PowerBudgetParams.sensitivity_dbm [dBm]
PowerBudgetParams.a_climate       [-]
PowerBudgetParams.b_terrain       [-]
```

Para actualizar parámetros se usa exclusivamente:

```python
from dataclasses import replace

new_params = replace(current_params, f_hz=7e9)
new_params = replace(current_params, K=1.0)
new_params = replace(current_params, h_tx_m=20.0)
```

Nunca se modifica directamente un atributo de `LinkParams` o `PowerBudgetParams`.

---

### `models/terrain.py`

```python
@dataclass
class TerrainData:
    d1_m: np.ndarray
    lat: np.ndarray
    lon: np.ndarray
    elevation_m: np.ndarray
    source: str

    @property
    def d_total_m(self) -> float:
        return float(self.d1_m[-1])

    @property
    def d2_m(self) -> np.ndarray:
        return self.d_total_m - self.d1_m

    @property
    def n_points(self) -> int:
        return len(self.d1_m)
```

`elevation_m` contiene exclusivamente elevación de terreno sobre el nivel medio del mar. Nunca contiene altura de antenas.

---

### `models/profile.py`

```python
@dataclass(frozen=True)
class LinkProfile:
    params: LinkParams
    terrain: TerrainData

    h_er_m: np.ndarray
    z_eff_m: np.ndarray
    h_los_m: np.ndarray

    r1_m: np.ndarray
    h_sup_m: np.ndarray
    h_inf_m: np.ndarray
    h_60pct_m: np.ndarray

    c_los_m: np.ndarray
    h_o_m: np.ndarray
    c_ffz_m: np.ndarray
    v: np.ndarray

    idx_critical: int
    v_critical: float
    g_d_db: float
    l_d_db: float
    l_fs_db: float

    p_rx_dbm: Optional[float]
    margin_db: Optional[float]
    availability_pct: Optional[float]
```

Descripción de arrays:

```text
h_er_m             Corrección por curvatura terrestre [m], EQ-04
z_eff_m            Elevación efectiva del terreno [m], EQ-05
h_los_m            Altura de la LOS [m], EQ-07

r1_m               Radio de la primera zona de Fresnel [m], EQ-08
h_sup_m    h_LOS + r1 [m], EQ-09
h_inf_m    h_LOS - r1 [m], EQ-09
h_60pct_m       h_LOS - 0.6 r1 [m], EQ-09

c_los_m            Despeje relativo a LOS [m], EQ-10
h_o_m              Altura de obstáculo sobre LOS [m], EQ-11
c_ffz_m            Despeje relativo al 60% de Fresnel [m], EQ-12
v                  Parámetro Fresnel-Kirchhoff [-], EQ-13
```

`z_eff_m` contiene únicamente terreno corregido por curvatura. Las alturas de antena se incorporan exclusivamente en `H_Tx` y `H_Rx` al calcular la LOS.

#### Invariantes de `LinkProfile`

Tras ejecutar exitosamente `core.engine.compute_link_profile(...)`, se deben cumplir estas postcondiciones:

```text
- Todos los arrays del perfil tienen longitud N = terrain.n_points.
- h_er_m == 0.0 y h_er_m[-1] == 0.0.
- z_eff_m == terrain.elevation_m + h_er_m, elemento a elemento.
- r1_m == 0.0 y r1_m[-1] == 0.0.
- v y v[-1] son np.nan.
- idx_critical pertenece al intervalo [1, N - 2].
- idx_critical == np.nanargmax(v).
- v_critical == v[idx_critical].
- g_d_db == diffraction_gain_db(v_critical).
- l_d_db == diffraction_loss_db(v_critical).
- l_d_db >= 0.0.
- l_fs_db > 0.0.
- Si p_rx_dbm no es None, margin_db == p_rx_dbm - sensitivity_dbm.
```

---

### `core/atmosphere.py`

```python
def k_from_gradient(dN_dh: float) -> float:
    """Ref: EQ-03. dN_dh [N-units/km]. Retorna K [-]."""


def gradient_from_k(K: float) -> float:
    """Ref: EQ-03. Inversa. Retorna dN/dh [N-units/km]."""


def earth_curvature_correction(
    d1_m: np.ndarray,
    d2_m: np.ndarray,
    K: float,
) -> np.ndarray:
    """Ref: EQ-04. Retorna h_ER_i [m]. Usa máscara en extremos."""


def effective_elevation(
    z_raw_m: np.ndarray,
    h_er_m: np.ndarray,
) -> np.ndarray:
    """Ref: EQ-05. Retorna z_eff_i [m]. No incorpora alturas de antena."""
```

---

### `core/geometry.py`

```python
def antenna_heights_msl(
    z_tx_m: float,
    h_tx_m: float,
    z_rx_m: float,
    h_rx_m: float,
) -> tuple[float, float]:
    """Ref: EQ-06. Retorna H_Tx y H_Rx [m MSL]."""


def los_height(
    H_tx_m: float,
    H_rx_m: float,
    d1_m: np.ndarray,
    d_total_m: float,
) -> np.ndarray:
    """Ref: EQ-07. Retorna h_LOS_i [m MSL]."""
```

---

### `core/fresnel_zones.py`

```python
def fresnel_radius_n(
    n: int,
    lam_m: float,
    d1_m: np.ndarray,
    d2_m: np.ndarray,
) -> np.ndarray:
    """Ref: EQ-08. Retorna radio de zona Fresnel [m]. r=0 en extremos."""


def fresnel_bands(
    h_los_m: np.ndarray,
    r1_m: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Ref: EQ-09. Retorna h_sup_m, h_inf_m y h_60pct_m."""


def los_clearance(
    h_los_m: np.ndarray,
    z_eff_m: np.ndarray,
) -> np.ndarray:
    """Ref: EQ-10. C_LOS = h_LOS - z_eff. Positivo significa despeje."""


def obstacle_height(c_los_m: np.ndarray) -> np.ndarray:
    """Ref: EQ-11. h_O = -C_LOS. Positivo significa obstrucción."""


def ffz_clearance(
    c_los_m: np.ndarray,
    r1_m: np.ndarray,
) -> np.ndarray:
    """Ref: EQ-12. C_FFZ = C_LOS - 0.6*r1."""
```

---

### `core/diffraction.py`

```python
def fresnel_kirchhoff_parameter(
    h_o_m: np.ndarray,
    lam_m: float,
    d1_m: np.ndarray,
    d2_m: np.ndarray,
) -> np.ndarray:
    """
    Ref: EQ-13.

    v_i = h_O_i * sqrt(2*(d1_i+d2_i)/(lambda*d1_i*d2_i))

    Retorna np.nan donde d1_i == 0 o d2_i == 0.
    Convención: v > 0 indica obstrucción; v < 0 indica despeje.
    """


def critical_obstacle_index(v: np.ndarray) -> int:
    """Ref: EQ-14. Retorna np.nanargmax(v)."""


def diffraction_function(v: float) -> complex:
    """
    Ref: EQ-16.

    F(v) = (1+j)/2 * [(0.5-C(v)) - j*(0.5-S(v))]

    Usa scipy.special.fresnel(v), que retorna (S, C).
    """


def diffraction_gain_db(v: float) -> float:
    """
    Ref: EQ-17.

    G_d = 20 log10(|F(v)|).

    Representa el coeficiente exacto de difracción calculado a partir
    de las integrales de Fresnel. Puede ser negativo, cero o levemente
    positivo debido al comportamiento oscilatorio de la solución exacta.
    """


def diffraction_loss_db(v: float) -> float:
    """
    Ref: EQ-18.

    L_d = max(0.0, -G_d).

    Retorna la pérdida adicional de difracción usada en el presupuesto
    de enlace. Nunca acredita ganancia de difracción respecto al espacio
    libre y siempre cumple L_d >= 0.
    """


def diffraction_curve(v_range: np.ndarray) -> np.ndarray:
    """
    Calcula G_d(v) para un array de valores v.

    Se usa para visualizar el coeficiente exacto G_d(v), no la pérdida
    truncada L_d(v).
    """
```

---

### `core/link_budget.py`

```python
def free_space_loss_db(d_total_m: float, f_hz: float) -> float:
    """Ref: EQ-21. L_fs = 20 log10(4*pi*d/lambda). Retorna [dB]."""


def received_power_dbm(
    params: LinkParams,
    pb: PowerBudgetParams,
    l_fs_db: float,
    l_d_db: float,
) -> float:
    """
    Ref: EQ-22.

    P_Rx = P_Tx + G_Tx - L_cTx - L_fs - L_d + G_Rx - L_cRx.
    """


def link_margin_db(
    p_rx_dbm: float,
    sensitivity_dbm: float,
) -> float:
    """Ref: EQ-23. Margen = P_Rx - sensibilidad."""


def link_availability(
    margin_db: float,
    f_ghz: float,
    d_km: float,
    a: float,
    b: float,
) -> float:
    """Ref: EQ-24. Retorna disponibilidad [%]."""
```

---

### `core/extensions/multipath.py`

```python
def channel_transfer_function(
    f_hz: np.ndarray,
    delta_tau_s: float,
    gamma: complex = 1.0,
) -> np.ndarray:
    """Ref: EQ-25. H(f) = 1 + gamma*exp(-j*2*pi*f*delta_tau)."""


def null_separation_hz(delta_tau_s: float) -> float:
    """Ref: EQ-27. Delta_f = 1/delta_tau."""
```

Este módulo no forma parte del pipeline V1.

---

### `core/extensions/attenuation.py`

```python
def oxygen_attenuation_db_per_km(f_ghz: float) -> float:
    """Ref: EQ-28. Atenuación por oxígeno [dB/km]."""


def water_vapor_attenuation_db_per_km(
    f_ghz: float,
    rho_g_per_m3: float = 7.5,
) -> float:
    """Ref: EQ-29. Atenuación por vapor de agua [dB/km]."""


def rain_attenuation_db_per_km(
    f_ghz: float,
    rain_rate_mm_per_hr: float,
    k: float,
    alpha: float,
) -> float:
    """Ref: EQ-31. a_r = k*R^alpha [dB/km]."""


def total_gas_attenuation_db(
    f_ghz: float,
    d_km: float,
    rho_g_per_m3: float = 7.5,
) -> float:
    """Ref: EQ-30. A_a = (a_O + a_W)*d [dB]."""
```

Este módulo no forma parte del pipeline V1.

---

### `core/engine.py`

`compute_link_profile(...)` es la única función del motor que usa la interfaz.

```python
def compute_link_profile(
    params: LinkParams,
    terrain: TerrainData,
    pb_params: Optional[PowerBudgetParams] = None,
) -> LinkProfile:
    """
    Ejecuta el pipeline V1:

    1.  atmosphere.earth_curvature_correction -> h_er_m
    2.  atmosphere.effective_elevation -> z_eff_m
    3.  geometry.antenna_heights_msl -> H_Tx, H_Rx
    4.  geometry.los_height -> h_los_m
    5.  fresnel_zones.fresnel_radius_n -> r1_m
    6.  fresnel_zones.fresnel_bands ->
        h_sup_m, h_inf_m, h_60pct_m
    7.  fresnel_zones.los_clearance -> c_los_m
    8.  fresnel_zones.obstacle_height -> h_o_m
    9.  fresnel_zones.ffz_clearance -> c_ffz_m
    10. diffraction.fresnel_kirchhoff_parameter -> v
    11. diffraction.critical_obstacle_index -> idx_critical
    12. diffraction.diffraction_gain_db(v_critical) -> g_d_db
    13. diffraction.diffraction_loss_db(v_critical) -> l_d_db
    14. link_budget.free_space_loss_db -> l_fs_db
    15. Si pb_params no es None:
        link_budget.received_power_dbm -> p_rx_dbm
        link_budget.link_margin_db -> margin_db
        link_budget.link_availability -> availability_pct
    16. Verifica invariantes de LinkProfile.

    No importa ni ejecuta core.extensions en V1.
    """
```

---

### `data/loader.py`

```python
def load_terrain_csv(filepath: str) -> TerrainData:
    """
    Lee un CSV con columnas:
    distance_m, latitude, longitude, elevation_m.

    Valida:
    - Mínimo 50 puntos.
    - distance_m monótonamente estrictamente creciente.
    - Sin NaN en elevation_m.
    - distance_m == 0.0.

    Lanza TerrainLoadError con mensaje específico si falla.
    """


def save_terrain_csv(
    terrain: TerrainData,
    filepath: str,
) -> None:
    """Serializa TerrainData al formato CSV estándar."""
```

---

### `data/downloader.py`

```python
def download_elevation_profile(
    lat_tx: float,
    lon_tx: float,
    lat_rx: float,
    lon_rx: float,
    spacing_m: float = 50.0,
    save_path: Optional[str] = None,
) -> TerrainData:
    """
    Fuente secundaria de perfil.

    Genera puntos entre Tx y Rx, consulta Open-Elevation, guarda el CSV
    si save_path fue definido y retorna TerrainData.

    El resultado debe poder guardarse y reutilizarse en modo local.
    """


def geodesic_points(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
    n_points: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Retorna d1_m, lat_array y lon_array.

    Para trayectos menores de 15 km se permite interpolación lineal de
    latitud/longitud como aproximación documentada.
    """
```

---

### `ui/app.py`

```python
class App:
    terrain: TerrainData
    params_a: LinkParams
    params_b: Optional[LinkParams]
    pb_params: Optional[PowerBudgetParams]

    profile_a: LinkProfile
    profile_b: Optional[LinkProfile]

    design_b_active: bool
    show_raw_terrain: bool

    def __init__(self, terrain: TerrainData): ...
    def run(self) -> None: ...
    def _recompute(self) -> None: ...
    def _on_param_change(self) -> None: ...
```

La aplicación puede mantener estado de UI, pero cada recalculo debe crear nuevos objetos inmutables `LinkParams` y `LinkProfile`.

---

### `ui/layout.py`

```python
def build_layout() -> dict[str, plt.Axes]:
    """
    Retorna Axes para:

    terrain
    diffraction
    results
    sl_freq
    sl_k
    sl_htx
    sl_hrx
    btn_b
    btn_raw
    btn_case
    """
```

---

### `ui/artists.py`

```python
@dataclass
class TerrainArtists:
    raw_terrain: plt.Line2D
    eff_terrain: plt.Line2D

    los_a: plt.Line2D
    los_b: Optional[plt.Line2D]

    fresnel_band_a: PolyCollection
    fresnel_band_b: Optional[PolyCollection]

    fresnel_60_a: plt.Line2D
    fresnel_60_b: Optional[plt.Line2D]

    obstacle_marker_a: plt.Line2D
    obstacle_marker_b: Optional[plt.Line2D]

    obstacle_annot: plt.Annotation
    tx_mast: plt.Line2D
    rx_mast: plt.Line2D


@dataclass
class DiffractionArtists:
    curve: plt.Line2D
    operating_pt_a: plt.Line2D
    operating_pt_b: Optional[plt.Line2D]
    vline_zero: plt.Line2D
```

Los artistas se crean una sola vez. Las actualizaciones usan `.set_data()` o `.set_xy()`. No se crean nuevos artistas durante cada recálculo.

---

### `ui/callbacks.py`

Los callbacks crean nuevas instancias de parámetros mediante `dataclasses.replace`.

```python
def make_freq_callback(app: App) -> Callable:
    """Crea callback de frecuencia y usa replace(app.params_a, f_hz=...)."""


def make_k_callback(app: App) -> Callable:
    """Crea callback de K y muestra dN/dh derivado en modo lectura."""


def make_htx_callback(app: App) -> Callable:
    """Crea callback de altura Tx mediante dataclasses.replace."""


def make_hrx_callback(app: App) -> Callable:
    """Crea callback de altura Rx mediante dataclasses.replace."""


def make_toggle_b_callback(app: App) -> Callable: ...
def make_toggle_raw_callback(app: App) -> Callable: ...
def make_validation_callback(app: App, case_id: str) -> Callable: ...
```

No se permiten asignaciones directas como:

```python
app.params_a.K = new_k
app.params_a.f_hz = new_f_hz
```

---

### `ui/panels/terrain_panel.py`

```python
def update_terrain_panel(
    artists: TerrainArtists,
    profile_a: LinkProfile,
    profile_b: Optional[LinkProfile],
    show_raw: bool,
) -> None:
    """
    Actualiza terreno, LOS, Fresnel, umbral 60%, mástiles y obstáculo crítico.

    La función usa únicamente datos presentes en LinkProfile.
    No recalcula curvatura, Fresnel, v ni Ld.
    """
```

---

### `ui/panels/diffraction_panel.py`

```python
def update_diffraction_panel(
    artists: DiffractionArtists,
    profile_a: LinkProfile,
    profile_b: Optional[LinkProfile],
) -> None:
    """
    Grafica G_d(v) para v en [-3, 3].

    Marca el punto de operación de cada diseño usando:
    x = v_critical
    y = g_d_db
    """
```

---

### `ui/panels/results_panel.py`

```python
def update_results_panel(
    ax: plt.Axes,
    profile_a: LinkProfile,
    profile_b: Optional[LinkProfile],
) -> None:
    """
    Muestra:

    d_total, f, K, d1_critical, d2_critical, v_critical,
    G_d, L_d, L_fs y, si corresponde, P_Rx, margen y disponibilidad.
    """
```

---

### `validation/cases.py`

```python
def case_flat_earth() -> tuple[TerrainData, LinkParams]:
    """
    Caso V-1: perfil plano de 10 km.

    Parámetros fijos:
    - d_total = 10_000 m
    - n_points = 201
    - terreno = 0 m
    - f = 7 GHz
    - K = 1e12, para anular curvatura numéricamente
    - h_Tx = h_Rx = 14.64 m

    Resultado esperado:
    - La muestra central está en d1 = 5_000 m.
    - v_critical aproximadamente -2.00.
    - L_d = 0.00 dB.
    """


def case_edge_on_los(
    d1_m: float = 4_000,
    d2_m: float = 6_000,
    f_hz: float = 7e9,
) -> tuple[TerrainData, LinkParams]:
    """
    Caso V-2.

    Genera un perfil con una única cresta cuya cima toca exactamente la LOS.

    Resultado esperado:
    - h_O = 0
    - v = 0
    - |F(0)| = 0.5
    - G_d = -6.0206 dB
    - L_d = 6.0206 dB
    """


def case_lima() -> tuple[TerrainData, LinkParams]:
    """Caso V-3: carga data/profiles/lima_atocongo.csv."""
```

---

## 5. Interfaces entre módulos

Regla de dependencias:

```text
config/       <- importado por todos
models/       <- importado por core/, data/, ui/ y validation/
core/         <- importado por ui/ y validation/
data/         <- importado por ui/ y validation/
validation/   <- importado por ui/
ui/           <- importado únicamente por main.py
```

Está prohibido:

```text
- core/ importando de ui/
- core/ importando de data/
- core/engine.py importando de core/extensions/ en V1
- ui/panels/ importando directamente módulos físicos de core/
- ui/ recalculando Fresnel, v, Gd o Ld
```

La UI recibe un `LinkProfile` completo y solo representa datos ya calculados.

---

## 6. Flujo de datos end-to-end

```text
Usuario mueve slider de frecuencia
          |
          v
callbacks.make_freq_callback()
          |
          v
app.params_a = dataclasses.replace(
    app.params_a,
    f_hz=nuevo_valor_hz,
)
          |
          v
app._recompute()
          |
          v
engine.compute_link_profile(params_a, terrain, pb_params)
          |
          +--> atmosphere.earth_curvature_correction -> h_er_m
          +--> atmosphere.effective_elevation -> z_eff_m
          +--> geometry.antenna_heights_msl -> H_Tx, H_Rx
          +--> geometry.los_height -> h_los_m
          +--> fresnel_zones.fresnel_radius_n -> r1_m
          +--> fresnel_zones.fresnel_bands ->
          |    h_sup_m, h_inf_m, h_60pct_m
          +--> fresnel_zones.los_clearance -> c_los_m
          +--> fresnel_zones.obstacle_height -> h_o_m
          +--> fresnel_zones.ffz_clearance -> c_ffz_m
          +--> diffraction.fresnel_kirchhoff_parameter -> v
          +--> diffraction.critical_obstacle_index -> idx_critical
          +--> diffraction.diffraction_gain_db -> g_d_db
          +--> diffraction.diffraction_loss_db -> l_d_db
          +--> link_budget.free_space_loss_db -> l_fs_db
          +--> [si pb] received_power, margin, availability
          +--> verifica invariantes de LinkProfile
          |
          v
app.profile_a = nuevo_profile
          |
          +--> terrain_panel.update_terrain_panel(...)
          +--> diffraction_panel.update_diffraction_panel(...)
          +--> results_panel.update_results_panel(...)
          |
          v
fig.canvas.draw_idle()
```

El redibujado ocurre una sola vez al final de la actualización.

---

## 7. Layout de la figura matplotlib

```text
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   PANEL TERRAIN                                        │
│   Terreno + perfil efectivo + LOS + Fresnel + obstáculo│
│                                                         │
├───────────────────────────┬─────────────────────────────┤
│                           │                             │
│   PANEL DIFRACCIÓN        │   PANEL RESULTADOS          │
│   Curva Gd(v) vs v        │   Tabla numérica            │
│                           │                             │
├───────────────────────────┴─────────────────────────────┤
│ Slider frecuencia                                        │
│ Slider K                                                 │
│ Slider hTx                                               │
│ Slider hRx                                               │
├─────────────────────────────────────────────────────────┤
│ Botón Diseño B | Terreno crudo/efectivo | Casos V-1/V-2/V-3 │
└─────────────────────────────────────────────────────────┘
```

Tamaño:

```text
14 × 10 pulgadas
140 dpi
1960 × 1400 px
```

Paleta:

| Elemento | Diseño A | Diseño B |
|---|---|---|
| LOS | `#E63946` | `#2DC653` |
| Banda Fresnel | `#4895EF`, alpha 0.15 | `#2DC653`, alpha 0.10 |
| Línea 60% Fresnel | `#4895EF`, discontinua | `#2DC653`, discontinua |
| Obstáculo crítico | `#F4A261` | `#E9C46A` |

Elementos fijos:

| Elemento | Color | Estilo |
|---|---|---|
| Perfil crudo | `#AAAAAA` | Línea continua delgada |
| Perfil efectivo | `#333333` | Relleno hasta eje X |
| Mástiles Tx/Rx | `#333333` | Segmentos verticales |
| Curva Gd(v) | `#555555` | Línea continua |
| Línea v = 0 | `#CC0000` | Línea discontinua |

---

## 8. Formato del CSV de perfil de terreno

```csv
distance_m,latitude,longitude,elevation_m
0.0,-12.1234,-76.9876,245.3
50.0,-12.1238,-76.9871,247.1
```

Restricciones:

```text
- distance_m debe ser exactamente 0.0.
- distance_m debe ser estrictamente creciente.
- elevation_m no puede contener NaN.
- El archivo debe contener como mínimo 50 filas.
- latitude y longitude se conservan para trazabilidad, pero no se validan
  geométricamente contra distance_m.
```

---

## 9. Convenciones de código

Variables físicas en `core/` usan nombres con unidades:

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
```

Nunca usar nombres ambiguos como:

```python
d1
f
lambda
h
```

Máscaras para extremos:

```python
valid = (d1_m > 0.0) & (d2_m > 0.0)

v = np.full_like(d1_m, np.nan, dtype=float)

v[valid] = h_o_m[valid] * np.sqrt(
    2.0 * d_total_m /
    (lam_m * d1_m[valid] * d2_m[valid])
)
```

Nunca manejar división por cero de arrays con `try/except`.

Las actualizaciones de Matplotlib usan:

```python
line.set_data(...)
collection.set_verts(...)
collection.set_xy(...)
```

No usar `ax.clear()` durante el loop de actualización de datos.

Docstring mínimo:

```python
def function_name(...) -> ReturnType:
    """
    Descripción breve.

    Ref: EQ-XX (MATHSPEC v1.1).

    Args:
        variable [unidad]: descripción.

    Returns:
        resultado [unidad].
    """
```

---

## 10. `requirements.txt`

```text
numpy>=1.24
scipy>=1.10
matplotlib>=3.7
pandas>=2.0
requests>=2.28
pytest>=7.0
```

---

## 11. `AGENT_INSTRUCTIONS.md`

El repositorio debe incluir un archivo `AGENT_INSTRUCTIONS.md` con el siguiente contenido mínimo:

```md
# Instrucciones para IA agéntica

## Jerarquía documental

1. MATHSPEC: autoridad única para fórmulas, signos, unidades y convenciones.
2. ARCH: autoridad para módulos, contratos, dependencias y flujo de datos.
3. PRD: autoridad para comportamiento observable, alcance e interfaz.
4. IMPL: autoridad para orden de implementación y pruebas de aceptación.

## Regla de contradicciones

Si dos documentos se contradicen, detener la implementación.

No inventar interpretaciones ni aplicar cambios silenciosos.

Crear CONTRADICTIONS.md con:

- Archivos y secciones en conflicto
- Descripción concreta de la contradicción
- Riesgo técnico o físico
- Propuesta de resolución
- Pregunta concreta para el responsable del proyecto

## Reglas de implementación

- Implementar una etapa a la vez.
- Ejecutar pytest -q antes de pasar a la siguiente etapa.
- No implementar UI hasta que el motor core esté validado.
- No modificar ni simplificar fórmulas del MATHSPEC.
- Mantener unidades SI dentro de core.
- No agregar dependencias no especificadas.
- No agregar modelos físicos no especificados.
- No importar core/extensions desde engine.py en V1.
- El flujo principal debe funcionar sin conexión a internet.
- La UI no debe recalcular física.
- LinkParams y PowerBudgetParams son inmutables.
- Usar dataclasses.replace para producir nuevas variantes de parámetros.

## Pruebas

Cada criterio funcional F y físico P definido en IMPL debe implementarse
como test automatizado pytest dentro de tests/.

Los scripts manuales son solo apoyo didáctico; no reemplazan pytest.
```
