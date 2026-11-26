# Navegación y Mapeo Autónomo para Control de Plagas en Plantaciones de Banano y Cacao

Proyecto de SSR en **ROS 2 Jazzy**. Arquitectura de software de un robot móvil terrestre que recorre hileras de una plantación, detecta anomalías foliares y ajusta su tracción al terreno.

## Contenido

| Paquete | Descripción |
|---|---|
| `agro_robot` | Nodos `percepcion` y `control_traccion`, launch y parámetros (`config/robot_params.yaml`) |
| `agro_robot_interfaces` | Mensaje `AnomaliaFoliar`, servicio `AjustarTerreno` y acción `NavegarPlantacion` |

## Requisitos

- Ubuntu 24.04
- ROS 2 Jazzy Desktop ([guía de instalación](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html))
- Git, colcon y rosdep:

```bash
sudo apt update
sudo apt install git python3-colcon-common-extensions python3-rosdep
sudo rosdep init        # solo la primera vez; si dice que ya existe, ignorar
rosdep update
```

## Instalación

**1. Clonar el repositorio.** La raíz del repositorio es el workspace.

```bash
cd ~
git clone https://github.com/daec4/Navegacon-y--Mapeo--Autonomo.git ws_Proyecto
cd ~/ws_Proyecto
```

**2. Instalar dependencias:**

```bash
source /opt/ros/jazzy/setup.bash
rosdep install --from-paths src --ignore-src -y
```

**3. Compilar:**

```bash
colcon build
source install/setup.bash
```

Debe terminar con `Summary: 2 packages finished`.

> En **cada terminal nueva** hay que ejecutar:
> ```bash
> source /opt/ros/jazzy/setup.bash
> source ~/ws_Proyecto/install/setup.bash
> ```

## Ejecución

**Terminal 1 – lanzar los nodos:**

```bash
ros2 launch agro_robot robot_agricola.launch.py
```

Cada segundo se muestra el estado del robot:

```
AVANZANDO a 0.50 m/s | terreno seco | recorrido 3.0 m
```

## Pruebas (Terminal 2)

**Simular una anomalía foliar:** el robot se detiene durante `tiempo_inspeccion` segundos y luego reanuda.

```bash
ros2 topic pub --once /percepcion/anomalia agro_robot_interfaces/msg/AnomaliaFoliar "{tipo_plaga: 'Sigatoka negra', confianza: 0.92, x: 12.5, y: 3.0, obstaculo_detectado: false}"
```

**Simular un obstáculo:**

```bash
ros2 topic pub --once /percepcion/anomalia agro_robot_interfaces/msg/AnomaliaFoliar "{tipo_plaga: '', confianza: 1.0, x: 14.0, y: 3.0, obstaculo_detectado: true}"
```

**Servicio – cambiar el tipo de terreno** (`seco`, `irregular`, `lodo`):

```bash
ros2 service call /traccion/ajustar_terreno agro_robot_interfaces/srv/AjustarTerreno "{tipo_terreno: 'lodo'}"
```

| Terreno | Factor sobre la velocidad de crucero |
|---|---|
| seco | 100 % |
| irregular | 70 % |
| lodo | 50 % |

**Parámetros:**

```bash
ros2 param list /control_traccion
ros2 param get  /control_traccion tipo_terreno
ros2 param set  /control_traccion velocidad_crucero 0.8
ros2 param set  /control_traccion tiempo_inspeccion 3
```

**Inspeccionar nodos y tópicos:**

```bash
ros2 node list
ros2 topic list
ros2 topic echo /traccion/estado
ros2 topic echo /traccion/cmd_vel
ros2 topic hz   /percepcion/imagen --qos-reliability best_effort    # ~15 Hz
ros2 topic info /percepcion/imagen --verbose                        # QoS BEST_EFFORT
rqt_graph
```


## Autores

Juan Cruz · Daniel Espinoza · Byron Ortega — ESPOL
