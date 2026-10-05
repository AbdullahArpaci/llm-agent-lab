from setuptools import find_packages, setup
import os
from glob import glob
package_name = 'swarm_talk'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share',package_name,'launch'), glob("launch/*")),
        (os.path.join('share',package_name,'config'), glob("config/*"))
    ],

    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='abdullah',
    maintainer_email='arpaciabdullah5151@gmail.com',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            "drone_adapter = swarm_talk.drone_adapter:main",
            "swarm_manager = swarm_talk.swarm_manager:main"
        ],
    },
)


