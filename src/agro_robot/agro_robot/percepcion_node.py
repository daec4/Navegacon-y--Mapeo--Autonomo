"""
Nodo de percepción visual.

PUBLICA
  /percepcion/imagen     sensor_msgs/Image   QoS Best-Effort, 15 Hz (flujo de cámara)
  /percepcion/anomalia   std_msgs/String     descripción de la anomalía foliar detectada

Para probar, la anomalía se publica directamente desde la terminal en
/percepcion/anomalia. Si más adelante hay un detector, este nodo la publicará
llamando a `reportar_anomalia()`.
"""
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy
from sensor_msgs.msg import Image
from std_msgs.msg import String

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

        # Publicadores
        self.pub_imagen = self.create_publisher(Image, '/percepcion/imagen', qos_imagen)
        self.pub_anomalia = self.create_publisher(String, '/percepcion/anomalia', 10)

        # Imagen de relleno
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

    def reportar_anomalia(self, descripcion):
        self.pub_anomalia.publish(String(data=descripcion))
        self.get_logger().warn(f'Anomalía detectada: {descripcion}')


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
