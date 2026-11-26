import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy
from sensor_msgs.msg import Image
from agro_robot_interfaces.msg import AnomaliaFoliar

FRECUENCIA_HZ = 15.0
ANCHO, ALTO = 160, 120


class PercepcionNode(Node):
    def __init__(self):
        super().__init__('percepcion')

        qos_imagen = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
            durability=DurabilityPolicy.VOLATILE,
        )

        self.pub_imagen = self.create_publisher(Image, '/percepcion/imagen', qos_imagen)
        self.pub_anomalia = self.create_publisher(AnomaliaFoliar, '/percepcion/anomalia', 10)

        self.pixeles = bytes([40, 140, 40]) * (ANCHO * ALTO)
        self.create_timer(1.0 / FRECUENCIA_HZ, self.cb_camara)
        self.get_logger().info(f'Percepción publicando imágenes a {FRECUENCIA_HZ:.0f} Hz (Best-Effort)')

    def cb_camara(self):
        msg = Image()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'camara'
        msg.height, msg.width = ALTO, ANCHO
        msg.encoding = 'rgb8'
        msg.step = ANCHO * 3
        msg.data = self.pixeles
        self.pub_imagen.publish(msg)

    def reportar_anomalia(self, tipo_plaga, confianza, x, y, obstaculo=False):
        msg = AnomaliaFoliar()
        msg.tipo_plaga = tipo_plaga
        msg.confianza = float(confianza)
        msg.x, msg.y = float(x), float(y)
        msg.obstaculo_detectado = obstaculo
        self.pub_anomalia.publish(msg)
        self.get_logger().warn(f'Anomalía detectada: {tipo_plaga} ({confianza * 100:.0f} %) en ({x}, {y})')


def main(args=None):
    rclpy.init(args=args)
    nodo = PercepcionNode()
    try:
        rclpy.spin(nodo)
    except KeyboardInterrupt:
        pass
    finally:
        nodo.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
