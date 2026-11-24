# Navegacon-y--Mapeo--Autonomo
proyecto de SSR

Para ejecutar los nodos se lo hace desde el launch file usando el comando: ros2 launch agro_robot robot_agricola.launch.py.
Se estara ejecutando cada segundo un mensaje que indica que el robot se esta moviendo a cierta velocidad y cuantos metros ha recorrido.
Para simular una anomalia en un planta, se debe ejecutar el siguiente comando en otra terminal: ros2 topic pub --once /percepcion/anomalia std_msgs/msg/String "{data: 'Sigatoka negra en hilera 3'}". EL mensaje es un ejemplo y se puede modificar.

*Actualización*
Ahora los comandos para probar son:
1. En un terminal se ejecuta ros2 launch agro_robot robot_agricola.launch.py
2. En un segundo terminal se puede simular una anomalía con el siguiente comando de ejemplo: ros2 topic pub --once /percepcion/anomalia agro_robot_interfaces/msg/AnomaliaFoliar "{tipo_plaga: 'Sigatoka negra', confianza: 0.92, x: 12.5, y: 3.0, obstaculo_detectado: false}", donde se está accediendo a la mensajería AnomaliaFoliar y se puede modificar el tipo de plaga, el nivel confianza y la posición.
3. Para cambiar el terreno se puede llamar al servicio AjustarTerreno y ajustarlo entre las 3 opciones ("seco", "irregular", "lodo") con el siguiente comando: ros2 service call /traccion/ajustar_terreno agro_robot_interfaces/srv/AjustarTerreno "{tipo_terreno: 'lodo'}"
4. Para tener la lista completa de parámetros que se están ejecutando se puede usar el comando: ros2 param list /control_traccion o ros2 param list /percepcion
6. Si se quiere cambiar un parámetro en específico desde el terminar se lo puede hacer con el comando: ros2 param set /nodo parametro valor
