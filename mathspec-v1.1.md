## MATHSPEC — Especificación Matemática del Evaluador de Radioenlace LOS

**Versión:** 1.1
**Referencia cruzada:** PRD v1.0
**Fuente primaria:** Notas de clase y diapositivas del profesor Yarleque (TEL138), convenciones del curso

---

## 0. Convenciones globales

**Sistema de unidades del motor de cálculo:** SI puro (metros, Hz, vatios). Toda conversión se hace en los adaptadores de entrada/salida, nunca dentro del motor.

**Índice de ecuaciones:** cada función de cálculo en el código debe referenciar el número de ecuación de este documento en su docstring. Formato: `# EQ-XX`.

**Notación de signos para pérdidas:** el curso usa $G_d = 20\log_{10}|F(v)|$ como coeficiente de difracción (negativo para obstrucción). El power budget usa pérdida positiva $L_d = -G_d$. Ambas se definen formalmente en §6.

---

## 1. Parámetros del sistema y variables primarias

| Símbolo | Definición | Unidad SI | Restricción de dominio |
|---|---|---|---|
| $f$ | Frecuencia de operación | Hz | $10^8 \leq f \leq 10^{11}$ |
| $\lambda$ | Longitud de onda | m | $\lambda = c/f$, $c = 3\times10^8$ m/s |
| $d_T$ | Distancia total Tx–Rx (geodésica) | m | $d_T > 0$ |
| $d_{1,i}$ | Distancia desde Tx al punto $i$ del perfil | m | $0 \leq d_{1,i} \leq d_T$ |
| $d_{2,i}$ | Distancia desde punto $i$ al Rx | m | $d_{2,i} = d_T - d_{1,i}$ |
| $z_i$ | Elevación del terreno en el punto $i$ (MSL) | m | dato del DEM |
| $h_{Tx}$ | Altura de mástil en Tx | m | $h_{Tx} \geq 0$ |
| $h_{Rx}$ | Altura de mástil en Rx | m | $h_{Rx} \geq 0$ |
| $K$ | Factor de escala terrestre efectivo | adim. | $K > 0$; estándar $K = 4/3$ |
| $R$ | Radio medio de la Tierra | m | $R = 6{,}371{,}000$ m (fijo) |

---

## 2. Refracción atmosférica y factor K

### EQ-01 — Refractividad atmosférica

$$N = (n - 1) \times 10^6$$

donde $n$ es el índice de refracción del aire. $N$ es adimensional (N-units).

### EQ-02 — Gradiente de refractividad

$$G = \frac{dN}{dh} \quad \left[\frac{\text{N-units}}{\text{km}}\right]$$

Valor estándar de atmósfera normal: $G_0 = -39$ N-units/km.
Condición de conducto (ducting): $G < -157$ N-units/km.

### EQ-03 — Factor de escala terrestre K

$$K = \frac{1}{1 + R_{\text{km}} \cdot G \cdot 10^{-6}}$$

donde $R_{\text{km}} = 6371$ km y $G$ en N-units/km. Esta expresión se deriva de igualar la curvatura del rayo EM con la curvatura equivalente de la Tierra en el modelo de Tierra equivalente.

**Verificación:** con $G = -39$: $K = 1/(1 + 6371 \cdot (-39) \cdot 10^{-6}) = 1/(1 - 0.2485) = 1/0.7515 \approx 1.333 = 4/3$ ✓

**Implementación:** el usuario puede ingresar $G$ o $K$. La conversión inversa es:

$$G = \frac{(1/K - 1)}{R_{\text{km}} \cdot 10^{-6}} \quad \left[\frac{\text{N-units}}{\text{km}}\right]$$

---

## 3. Perfil efectivo por curvatura terrestre

### EQ-04 — Corrección de altura por curvatura terrestre

Para cada punto $i$ del perfil a distancias $d_{1,i}$ desde Tx y $d_{2,i}$ hasta Rx:

$$h_{ER,i} = \frac{d_{1,i} \cdot d_{2,i}}{2 \cdot K \cdot R}$$

con $d_{1,i}$, $d_{2,i}$, $R$ en metros y $h_{ER,i}$ resultante en metros.

**Forma numérica equivalente** (con distancias en km, resultado en metros):

$$h_{ER,i} = \frac{d_{1,i}[\text{km}] \cdot d_{2,i}[\text{km}]}{12.74 \cdot K} \quad [\text{m}]$$

La equivalencia se verifica: $2 \cdot (4/3) \cdot 6371 \cdot 10^{-3} = 16.989 \approx 12.74 \cdot (4/3)$. Ambas formas son correctas; el motor usa la forma SI (EQ-04).

### EQ-05 — Elevación efectiva del terreno

$$z_{eff,i} = z_i + h_{ER,i}$$

$h_{ER,i}$ es siempre positivo: el terreno "sube" efectivamente por la curvatura de la Tierra.

**Condición de borde:** en los extremos $i=0$ (Tx) y $i=N$ (Rx), $d_{1}=0$ o $d_{2}=0$, por lo que $h_{ER}=0$ y $z_{eff} = z$.

---

## 4. Línea de visión directa (LOS)

### EQ-06 — Altura de las fases de antena (MSL)

$$H_{Tx} = z_0 + h_{Tx}$$
$$H_{Rx} = z_N + h_{Rx}$$

donde $z_0$ y $z_N$ son las elevaciones del terreno en los extremos Tx y Rx respectivamente.

### EQ-07 — Altura de la LOS en el punto i

La LOS es la interpolación lineal entre $H_{Tx}$ y $H_{Rx}$ sobre el dominio de distancia:

$$h_{LOS,i} = H_{Tx} + (H_{Rx} - H_{Tx}) \cdot \frac{d_{1,i}}{d_T}$$

La LOS se calcula sobre las alturas de antena (MSL), no sobre el perfil efectivo. El perfil efectivo determina cuánto "sube" el terreno hacia esa LOS.

---

## 5. Zonas de Fresnel

### EQ-08 — Radio de la n-ésima zona de Fresnel

$$r_{n,i} = \sqrt{\frac{n \cdot \lambda \cdot d_{1,i} \cdot d_{2,i}}{d_{1,i} + d_{2,i}}}$$

con todas las magnitudes en metros. Para $n=1$:

$$r_{1,i} = \sqrt{\frac{\lambda \cdot d_{1,i} \cdot d_{2,i}}{d_{1,i} + d_{2,i}}} \quad [\text{m}]$$

**Forma numérica** con $f$ en GHz y distancias en km:

$$r_{1,i} = 17.3\sqrt{\frac{d_{1,i}[\text{km}] \cdot d_{2,i}[\text{km}]}{f[\text{GHz}] \cdot (d_{1,i}+d_{2,i})[\text{km}]}} \quad [\text{m}]$$

El factor 17.3 = $\sqrt{300}$ proviene de $\lambda = 0.3/f[\text{GHz}]$ metros.

**Condición de borde:** si $d_{1,i}=0$ o $d_{2,i}=0$, entonces $r_{1,i}=0$. Usar máscara de validez para evitar división por cero.

### EQ-09 — Bandas de Fresnel para visualización

$$h_{sup,i} = h_{LOS,i} + r_{1,i}$$
$$h_{inf,i} = h_{LOS,i} - r_{1,i}$$
$$h_{60\%,i} = h_{LOS,i} - 0.6 \cdot r_{1,i}$$

La línea $h_{60\%,i}$ representa el criterio práctico de diseño: el terreno no debe superar este umbral. Si lo supera, se incurre en pérdidas adicionales incluso si técnicamente hay LOS geométrica.

---

## 6. Despeje LOS y parámetro de Fresnel-Kirchhoff

### EQ-10 — Despeje relativo a la LOS

$$C_{LOS,i} = h_{LOS,i} - z_{eff,i}$$

Convención de signo:
- $C_{LOS,i} > 0$: terreno por debajo de la LOS — hay despeje.
- $C_{LOS,i} = 0$: borde del terreno exactamente en la LOS.
- $C_{LOS,i} < 0$: terreno por encima de la LOS — hay obstrucción.

### EQ-11 — Altura del obstáculo sobre la LOS

$$h_{O,i} = -C_{LOS,i} = z_{eff,i} - h_{LOS,i}$$

- $h_{O,i} > 0$: obstrucción (el terreno supera la LOS).
- $h_{O,i} \leq 0$: despeje (el terreno está por debajo de la LOS).

Esta es la magnitud que entra al cálculo de $v$.

### EQ-12 — Despeje relativo al 60% de la primera zona de Fresnel

$$C_{FFZ,i} = C_{LOS,i} - 0.6 \cdot r_{1,i}$$

Si $C_{FFZ,i} < 0$: el obstáculo penetra el 60% de la primera zona → se introducen pérdidas adicionales aunque $C_{LOS,i} > 0$ (hay LOS geométrica pero con degradación por difracción).

### EQ-13 — Parámetro de Fresnel-Kirchhoff

$$v_i = h_{O,i} \cdot \sqrt{\frac{2(d_{1,i} + d_{2,i})}{\lambda \cdot d_{1,i} \cdot d_{2,i}}}$$

equivalentemente, usando EQ-08:

$$v_i = \frac{h_{O,i} \cdot \sqrt{2}}{r_{1,i}}$$

Convención de signo (consistente con EQ-11 y las diapositivas del profesor):
- $v > 0$: obstrucción sobre la LOS.
- $v = 0$: borde exactamente en la LOS.
- $v < 0$: despeje por debajo de la LOS.

**Condición de borde:** en $d_{1,i}=0$ o $d_{2,i}=0$, $v_i = \text{NaN}$. Estos puntos se excluyen de toda búsqueda de máximo.

### EQ-14 — Identificación del obstáculo crítico

$$i^* = \arg\max_{i \in \mathcal{V}} v_i$$

donde $\mathcal{V} = \{i : d_{1,i} > 0 \text{ y } d_{2,i} > 0\}$ (puntos interiores válidos).

El obstáculo crítico no es necesariamente el de mayor altura absoluta ni el de mayor $h_{O,i}$: el parámetro $v$ incorpora también la posición relativa en el trayecto y la frecuencia.

---

## 7. Pérdida por difracción Knife-Edge

### EQ-15 — Integrales de Fresnel

$$C(x) = \int_0^x \cos\!\left(\frac{\pi t^2}{2}\right) dt, \qquad S(x) = \int_0^x \sin\!\left(\frac{\pi t^2}{2}\right) dt$$

**Implementación:** `scipy.special.fresnel(x)` devuelve la tupla `(S(x), C(x))` en ese orden. Asignar correctamente:

```python
S_v, C_v = scipy.special.fresnel(v)
```

Valores asintóticos: $C(\pm\infty) = S(\pm\infty) = \pm 1/2$.

### EQ-16 — Función de difracción compleja F(v)

$$F(v) = \frac{1+j}{2} \left[\left(\frac{1}{2} - C(v)\right) - j\left(\frac{1}{2} - S(v)\right)\right]$$

Esta es la integral de Fresnel-Kirchhoff evaluada desde $v$ hasta $+\infty$, derivada del principio de Huygens.

**Verificación para v = 0:**
$F(0) = \frac{1+j}{2}(0.5 - j \cdot 0.5) = \frac{(1+j)(1-j)}{4} = \frac{2}{4} = 0.5$, entonces $|F(0)| = 0.5$ ✓

### EQ-17 — Coeficiente de difracción (convención del profesor)

$$G_d \,[\text{dB}] = 20\log_{10}|F(v)|$$

- Para $v \to -\infty$ (despeje total): $|F| \to 1$, $G_d \to 0$ dB.
- Para $v = 0$: $G_d = 20\log_{10}(0.5) = -6.02$ dB.
- Para $v > 0$ creciente: $G_d$ decrece (mayor pérdida).

$G_d$ es negativo o cero. No es una ganancia en sentido convencional sino el nivel relativo al espacio libre.

### EQ-18 — Pérdida por difracción (convención del *power budget*)

$$L_d \,[\text{dB}] =
\max\!\left(0,\,-20\log_{10}|F(v)|\right)$$

$$L_d \geq 0$$

$L_d$ es, por construcción, una pérdida no negativa. Para valores muy negativos de $v$ (despeje amplio), la evaluación numérica de las integrales de Fresnel (espiral de Euler) puede producir $|F(v)|$ ligeramente mayor que $1$ debido a oscilaciones numéricas. Sin el truncamiento, ello implicaría

$$G_d > 0\ \text{dB},$$

lo cual es físicamente imposible para un obstáculo *knife-edge*. El operador

$$
\max(0,\cdot)
$$

elimina este artefacto numérico sin introducir ningún umbral empírico sobre $v$.

$L_d$ se suma como pérdida adicional en **EQ-22**.

**Esta es la magnitud que entra al presupuesto de enlace.** $G_d$ se usa solo para la curva del panel de visualización.

### EQ-19 — Aproximaciones empíricas de Lee (solo referencia, no usar en el motor)

$$G_d[\text{dB}] \approx \begin{cases} 0 & v \leq -1 \\ 20\log(0.5 - 0.62v) & -1 \leq v \leq 0 \\ 20\log(0.5\,e^{-0.95v}) & 0 \leq v \leq 1 \\ 20\log\!\left(0.4 - \sqrt{0.1184-(0.38-0.1v)^2}\right) & 1 \leq v \leq 2.4 \\ 20\log(0.225/v) & v > 2.4 \end{cases}$$

Estas aproximaciones son útiles para cálculo manual rápido pero no se implementan en el motor. El motor usa EQ-16 y EQ-17 exclusivamente mediante `scipy.special.fresnel`.

---

## 8. Pérdida en espacio libre (Friis)

### EQ-20 — Pérdida en espacio libre (forma fundamental)

$$L_{fs} = \left(\frac{\lambda}{4\pi d_T}\right)^2$$

En unidades lineales (adimensional, $< 1$).

### EQ-21 — Pérdida en espacio libre en dB

$$L_{fs}[\text{dB}] = 20\log_{10}\!\left(\frac{4\pi d_T}{\lambda}\right) = 20\log_{10}(4\pi) + 20\log_{10}(d_T) - 20\log_{10}(\lambda)$$

**Forma numérica** con $f$ en GHz y $d_T$ en km:

$$L_{fs}[\text{dB}] = 92.45 + 20\log_{10}(f[\text{GHz}]) + 20\log_{10}(d_T[\text{km}])$$

El motor calcula siempre con SI (EQ-21 en forma fundamental), pero reporta el resultado numérico en dB.

---

## 9. Presupuesto de enlace completo

### EQ-22 — Potencia recibida

$$P_{Rx}[\text{dBm}] = P_{Tx}[\text{dBm}] + G_{Tx}[\text{dBi}] - L_{c,Tx}[\text{dB}] - L_{fs}[\text{dB}] - L_d[\text{dB}] + G_{Rx}[\text{dBi}] - L_{c,Rx}[\text{dB}]$$

donde $L_{c,Tx}$ y $L_{c,Rx}$ son las pérdidas de cable/feeder en cada extremo.

### EQ-23 — Margen de enlace (Fade Margin)

$$F[\text{dB}] = P_{Rx}[\text{dBm}] - S[\text{dBm}]$$

donde $S$ es la sensibilidad del receptor. El enlace es viable si $F > 0$ dB.

---

## 10. Disponibilidad del enlace

### EQ-24 — Disponibilidad sin diversidad espacial

$$A = \left(1 - a \cdot b \cdot 10.42 \times 10^{-6} \cdot f[\text{GHz}] \cdot d_T[\text{km}]^3 \cdot 10^{-F/10}\right) \times 100\%$$

Parámetros:

| Parámetro | Descripción | Rango | Valor asumible |
|---|---|---|---|
| $a$ | Factor de clima | 0.25–1.0 | 1 (clima húmedo) |
| $b$ | Factor de terreno | 0.25–4.0 | 4 (terreno llano/agua) |
| $f$ | Frecuencia | GHz | — |
| $d_T$ | Distancia | km | — |
| $F$ | Fade margin | dB (de EQ-23) | — |

La outage probability es $P_{out} = 1 - A/100$.

---

## 11. Función de transferencia del canal multicamino

### EQ-25 — Modelo de dos trayectos

$$H(\omega) = 1 + \Gamma \cdot e^{-j\omega \Delta\tau}$$

donde $\Gamma$ es el coeficiente de reflexión del trayecto secundario (típicamente $|\Gamma| \leq 1$) y $\Delta\tau$ es la diferencia de retardo entre el trayecto directo y el reflejado.

### EQ-26 — Módulo cuadrado de la función de transferencia

$$|H(f)|^2 = |1 + \Gamma e^{-j2\pi f \Delta\tau}|^2 = 1 + |\Gamma|^2 + 2|\Gamma|\cos(2\pi f \Delta\tau)$$

Los nulos (fading selectivo) ocurren cuando $2\pi f \Delta\tau = \pi + 2k\pi$, es decir:

$$f_{nulo,k} = \frac{2k+1}{2\Delta\tau}, \qquad k = 0, 1, 2, \ldots$$

### EQ-27 — Separación entre nulos consecutivos

$$\Delta f = \frac{1}{\Delta\tau}$$

Esta es la frecuencia de coherencia del canal. Para $\Delta\tau$ entre 10 y 80 ns:

$$\Delta f \in \left[\frac{1}{80\times10^{-9}},\, \frac{1}{10\times10^{-9}}\right] = [12.5\text{ MHz},\, 100\text{ MHz}]$$

---

## 12. Atenuación atmosférica por gases

### EQ-28 — Atenuación específica por oxígeno

$$a_O = \begin{cases} 0.001\!\left[0.00719 + \dfrac{6.09}{f^2+0.227} + \dfrac{4.81}{(f-57)^2+1.50}\right]f^2 & f < 57\text{ GHz} \\[6pt] a_O(57) + 1.5(f-57) & f \geq 57\text{ GHz} \end{cases}$$

con $f$ en GHz y $a_O$ en dB/km.

### EQ-29 — Atenuación específica por vapor de agua

$$a_W = 0.0001\left[0.050 + 0.0021\rho + \frac{3.6}{(f-22.2)^2+8.5} + \frac{10.6}{(f-183.3)^2+9.0}\right]$$

con $f$ en GHz, $\rho$ en g/m³ (típicamente 7.5 g/m³ a nivel del mar) y $a_W$ en dB/km.

### EQ-30 — Atenuación total por gases

$$A_a[\text{dB}] = (a_O + a_W) \cdot d_T[\text{km}]$$

**Nota de aplicabilidad:** para $f < 10$ GHz, $a_O$ y $a_W$ son del orden de $10^{-2}$ dB/km o menores. Para enlaces típicos de backhaul de microondas ($f \leq 15$ GHz, $d_T \leq 50$ km), $A_a < 1$ dB y puede omitirse en el presupuesto básico.

---

## 13. Atenuación por lluvia

### EQ-31 — Atenuación específica por lluvia

$$a_r = k \cdot R_{\text{rain}}^\alpha \quad [\text{dB/km}]$$

donde $R_{\text{rain}}$ es la intensidad de lluvia en mm/h, y $k$, $\alpha$ son constantes que dependen de la frecuencia y la polarización (tabla ITU-R).

### EQ-32 — Atenuación total por lluvia

$$A_r[\text{dB}] = a_r \cdot L_{r,eff}$$

donde $L_{r,eff}$ es la longitud efectiva del trayecto a través de la celda de lluvia (en km).

---

## 14. Casos de validación numérica

Estos son los casos que el motor debe reproducir exactamente para validar la implementación. Son los referenciados en RF-12 del PRD.

### Caso V-1 — Despeje total (tierra plana)

**Entrada:** perfil plano $z_i = 0$ m para todo $i$, $h_{Tx} = h_{Rx} = 50$ m, $d_T = 10{,}000$ m, $f = 7$ GHz, $K = 4/3$.

**Resultado esperado:** $h_{ER,i} = 0$ para todo $i$ (perfil plano no tiene corrección por curvatura relativa), $v_i < 0$ para todo $i$, $L_d = 0$ dB.

### Caso V-2 — Obstáculo exactamente en la LOS

**Entrada:** perfil con un único pico de altura $h_{O,i^*} = 0$ (borde exactamente en LOS, $C_{LOS,i^*} = 0$), con $d_{1,i^*}$ y $d_{2,i^*}$ arbitrarios pero positivos.

**Resultado esperado por EQ-16 y EQ-17:**
- $v_{i^*} = 0$
- $|F(0)| = 0.5$ (de EQ-16)
- $G_d = 20\log_{10}(0.5) = -6.02$ dB
- $L_d = 6.02$ dB

Este es el valor de referencia fundamental: cuando el obstáculo roza exactamente la LOS, la pérdida adicional es 6 dB (la potencia llega a la mitad de la de espacio libre). La tolerancia de implementación aceptable es $\pm 0.1$ dB.

### Caso V-3 — Verificación de K

**Entrada:** misma geometría, variar $K$ de 1.0 a 4/3.

**Resultado esperado:** $h_{ER,i}$ aumenta al disminuir $K$ (para $K=1$ la corrección es máxima, la Tierra "sube" más), lo que aumenta $h_{O,i^*}$ y por tanto $v_{i^*}$ y $L_d$.

---

## 15. Resumen de decisiones de diseño matemático

Estas son las decisiones donde existía ambigüedad y se tomó una posición explícita:

**D-01:** El motor usa integrales exactas de Fresnel (EQ-15, EQ-16), no las aproximaciones de Lee (EQ-19) ni las de ITU-R P.526. Razón: el curso deriva y evalúa la integral exacta; las aproximaciones son para cálculo manual.

**D-02:** El obstáculo crítico se selecciona por $\max(v_i)$, no por $\max(h_{O,i})$. Razón: $v$ incorpora frecuencia y posición relativa en el trayecto (EQ-14).

**D-03:** $v > 0$ indica obstrucción, $v < 0$ indica despeje. Esta convención coincide con las diapositivas del profesor (figuras (a), (b), (c) del modelo knife-edge).

**D-04:** $L_d = -20\log_{10}|F(v)|$ es siempre positivo y se resta en EQ-22. $G_d = 20\log_{10}|F(v)|$ es siempre negativo o cero y se usa solo en la curva de visualización.

**D-05:** $h_{ER}$ se añade al terreno, no se resta de la LOS. Ambas son matemáticamente equivalentes, pero sumar al terreno mantiene la LOS como referencia fija y hace la visualización más intuitiva.

**D-06:** La LOS se calcula entre las alturas absolutas MSL de las antenas ($H_{Tx}$, $H_{Rx}$), no entre las alturas de terreno. El mástil es parte de la geometría del enlace desde el principio.

**D-07:** $L_d$ se trunca a cero mediante $\max(0,\cdot)$ en **EQ-18**, no mediante un umbral de $v$. No existe en este modelo ningún valor $v_{\text{clear}}$ por debajo del cual $L_d$ se declare cero por convención: la integral exacta con truncamiento es la única regla. En particular, el umbral $v \leq -0.78$ de la aproximación **ITU-R P.526** no se usa, ya que pertenece a la fórmula empírica de Lee (EQ-19), que está explícitamente descartada del motor.