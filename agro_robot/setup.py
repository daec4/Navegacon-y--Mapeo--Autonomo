from glob import glob
from setuptools import setup

package_name = 'agro_robot'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Juan Cruz, Daniel Espinoza, Byron Ortega',
    maintainer_email='juancruz@espol.edu.ec, daescarr@espol.edu.ec, byalort@espol.edu.ec',
    description='Robot móvil para control de plagas en banano y cacao',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'percepcion = agro_robot.percepcion_node:main',
            'control_traccion = agro_robot.control_traccion_node:main',
        ],
    },
)
