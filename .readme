# RadioLink LOS

Proyecto para analizar un radioenlace usando un perfil de terreno. La interfaz muestra la línea de vista, la zona de Fresnel, la difracción y algunos resultados del enlace.

## Ejecución

Se recomienda usar el entorno virtual del proyecto:

```bash
source venv/bin/activate
python main.py
```

También se puede indicar otro perfil CSV:

```bash
python main.py --profile data/profiles/validation_flat.csv
```

Los perfiles de ejemplo están en `data/profiles/`.

## Interfaz

La aplicación permite cambiar frecuencia, factor K y alturas de antena. También se pueden activar Diseño B, Budget Px y Obstáculo Móvil al mismo tiempo. El obstáculo móvil usa un terreno sintético y tiene sliders para la distancia y la altura.

## Pruebas

Para ejecutar las pruebas:

```bash
pytest -q
```

El proyecto usa Python, NumPy y Matplotlib. Las dependencias están en `requirements.txt`.
