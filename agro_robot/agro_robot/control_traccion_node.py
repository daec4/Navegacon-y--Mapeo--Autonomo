"""
Nodo de control de tracción.

SUSCRIBE
  /percepcion/anomalia   std_msgs/String       al recibir una anomalía, el robot se detiene
PUBLICA
  /traccion/cmd_vel      geometry_msgs/Twist   velocidad enviada a los motores (10 Hz)
  /traccion/estado       std_msgs/String       estado del robot, una vez por segundo

Comportamiento: avanza por la hilera a velocidad constante. Si llega una
anomalía, se detiene TIEMPO_INSPECCION segundos y luego reanuda solo.
"""
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String

VELOCIDAD_CRUCERO = 0.5    # m/s
TIEMPO_INSPECCION = 5      # s detenido por cada anomalía
FRECUENCIA_CMD = 10.0      # Hz


class ControlTraccionNode(Node):
    def __init__(self):
        super().__init__('control_traccion')

        # Suscriptor
        self.create_subscription(String, '/percepcion/anomalia', self.cb_anomalia, 10)

        # Publicadores
        self.pub_cmd = self.create_publisher(Twist, '/traccion/cmd_vel', 10)
        self.pub_estado = self.create_publisher(String, '/traccion/estado', 10)

        self.segundos_detenido = 0      
        self.anomalia = ''
        self.recorrido = 0.0       
        self.detenido = False    

        self.create_timer(1.0 / FRECUENCIA_CMD, self.cb_motores)
        self.create_timer(1.0, self.cb_estado)
        self.get_logger().info('Control de tracción listo: robot en movimiento')

    def cb_anomalia(self, msg: String):
        self.anomalia = msg.data
        self.detenido = True
        self.segundos_detenido = TIEMPO_INSPECCION
        self.get_logger().warn(f'Deteniendo por anomalía: {msg.data}')

    def cb_motores(self):
        cmd = Twist()
        if not self.detenido:
            cmd.linear.x = VELOCIDAD_CRUCERO
            self.recorrido += VELOCIDAD_CRUCERO / FRECUENCIA_CMD
        self.pub_cmd.publish(cmd)

    def cb_estado(self):
        if self.segundos_detenido > 0:
            texto = (f'DETENIDO por anomalía "{self.anomalia}" | '
                    f'reanuda en {self.segundos_detenido} s')
            self.segundos_detenido -= 1
        else:
            if self.detenido:
                self.detenido = False
                self.get_logger().info('Inspección terminada: reanudando movimiento')
            texto = (f'AVANZANDO a {VELOCIDAD_CRUCERO:.1f} m/s | '
                    f'recorrido {self.recorrido:.1f} m')
        self.pub_estado.publish(String(data=texto))
        self.get_logger().info(texto)

def main(args=None):
    rclpy.init(args=args)
    nodo = ControlTraccionNode()
    try:
        rclpy.spin(nodo)
    except KeyboardInterrupt:
        pass
    finally:
        nodo.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
