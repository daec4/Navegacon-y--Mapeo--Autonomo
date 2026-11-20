# Navegacon-y--Mapeo--Autonomo
proyecto de SSR

Para ejecutar los nodos se lo hace desde el launch file usando el comando: ros2 launch agro_robot robot_agricola.launch.py.
Se estara ejecutando cada segundo un mensaje que indica que el robot se esta moviendo a cierta velocidad y cuantos metros ha recorrido.
Para simular una anomalia en un planta, se debe ejecutar el siguiente comando en otra terminal: ros2 topic pub --once /percepcion/prueba std_msgs/msg/String "{data: 'Sigatoka negra en hilera 3'}". EL mensaje es un ejemplo y se puede modificar.
