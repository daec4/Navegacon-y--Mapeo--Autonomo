import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from rcl_interfaces.msg import SetParametersResult
from geometry_msgs.msg import Twist
from std_msgs.msg import String
from agro_robot_interfaces.msg import AnomaliaFoliar
from agro_robot_interfaces.srv import AjustarTerreno

FRECUENCIA_CMD = 10.0      # Hz

# Factor que se aplica a la velocidad de crucero según el terreno
FACTOR_TERRENO = {
    'seco': 1.0,
    'irregular': 0.7,
    'lodo': 0.5,
}

class ControlTraccionNode(Node):
    def __init__(self):
        super().__init__('control_traccion')

        self.declare_parameters('', [
            # Dimensiones físicas (m)
            ('wheel_radius', 0.15),
            ('wheel_base', 0.65),
            ('track_width', 0.55),
            # Límites cinemáticos
            ('max_linear_vel', 1.0),
            ('max_angular_vel', 1.2),
            ('max_linear_accel', 0.5),
            ('max_angular_accel', 0.8),
            ('velocidad_crucero', 0.5),
            ('tiempo_inspeccion', 5),
            # Terreno
            ('tipo_terreno', 'seco'),
            # Parametros por defecto del control PID
            ('kp_linear', 1.2), ('ki_linear', 0.05), ('kd_linear', 0.1),
            ('kp_angular', 1.8), ('ki_angular', 0.02), ('kd_angular', 0.15),
        ])
        self.add_on_set_parameters_callback(self.validar_parametros)

        self.create_subscription(AnomaliaFoliar, '/percepcion/anomalia', self.cb_anomalia, 10)
        self.pub_cmd = self.create_publisher(Twist, '/traccion/cmd_vel', 10)
        self.pub_estado = self.create_publisher(String, '/traccion/estado', 10)
        self.create_service(AjustarTerreno, '/traccion/ajustar_terreno', self.cb_ajustar_terreno)

        self.segundos_detenido = 0
        self.detenido = False
        self.anomalia = ''
        self.recorrido = 0.0            # m
        self.v_actual = 0.0             # m/s

        self.create_timer(1.0 / FRECUENCIA_CMD, self.cb_motores)
        self.create_timer(1.0, self.cb_estado)
        self.get_logger().info(
            f'Control de tracción listo | terreno "{self.p("tipo_terreno")}" | '
            f'velocidad objetivo {self.velocidad_objetivo():.2f} m/s')

    def p(self, nombre):
        return self.get_parameter(nombre).value

    def velocidad_objetivo(self):
        v = self.p('velocidad_crucero') * FACTOR_TERRENO.get(self.p('tipo_terreno'), 1.0)
        return min(v, self.p('max_linear_vel'))

    def validar_parametros(self, params):
        for prm in params:
            if prm.name == 'tipo_terreno' and prm.value not in FACTOR_TERRENO:
                return SetParametersResult(
                    successful=False, reason=f'Terreno inválido. Use: {list(FACTOR_TERRENO)}')
            if prm.name in ('velocidad_crucero', 'max_linear_vel', 'max_linear_accel',
                            'tiempo_inspeccion') and prm.value <= 0:
                return SetParametersResult(successful=False, reason=f'{prm.name} debe ser > 0')
        for prm in params:
            self.get_logger().info(f'Parámetro actualizado: {prm.name} = {prm.value}')
        return SetParametersResult(successful=True)

    def cb_ajustar_terreno(self, request, response):
        terreno = request.tipo_terreno.strip().lower()
        if terreno not in FACTOR_TERRENO:
            response.exito = False
            response.mensaje = f'Terreno "{request.tipo_terreno}" no válido. Use: seco, lodo o irregular'
            self.get_logger().error(response.mensaje)
            return response

        self.set_parameters([Parameter('tipo_terreno', Parameter.Type.STRING, terreno)])
        response.exito = True
        response.mensaje = (f'Terreno cambiado a "{terreno}": velocidad '
                            f'{self.velocidad_objetivo():.2f} m/s')
        self.get_logger().info(response.mensaje)
        return response

    def cb_anomalia(self, msg: AnomaliaFoliar):
        if msg.obstaculo_detectado:
            self.anomalia = f'OBSTÁCULO en ({msg.x:.1f}, {msg.y:.1f})'
        else:
            self.anomalia = (f'{msg.tipo_plaga} ({msg.confianza * 100:.0f} %) '
                             f'en ({msg.x:.1f}, {msg.y:.1f})')
        self.detenido = True
        self.segundos_detenido = int(self.p('tiempo_inspeccion'))
        self.get_logger().warn(f'Deteniendo por: {self.anomalia}')

    def cb_motores(self):
        dt = 1.0 / FRECUENCIA_CMD
        v_obj = 0.0 if self.detenido else self.velocidad_objetivo()

        # Rampa de aceleración limitada por max_linear_accel
        dv_max = self.p('max_linear_accel') * dt
        self.v_actual += max(-dv_max, min(dv_max, v_obj - self.v_actual))
        if self.detenido:
            self.v_actual = 0.0          # frenado inmediato al detectar una anomalía

        cmd = Twist()
        cmd.linear.x = self.v_actual
        self.pub_cmd.publish(cmd)
        self.recorrido += self.v_actual * dt

    def cb_estado(self):
        if self.segundos_detenido > 0:
            texto = (f'DETENIDO por {self.anomalia} | '
                     f'reanuda en {self.segundos_detenido} s')
            self.segundos_detenido -= 1
        else:
            if self.detenido:
                self.detenido = False
                self.get_logger().info('Inspección terminada: reanudando movimiento')
            texto = (f'AVANZANDO a {self.v_actual:.2f} m/s | terreno {self.p("tipo_terreno")} | '
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
