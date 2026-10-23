from setuptools import find_packages, setup

package_name = 'lab1_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='beshr',
    maintainer_email='mariambeshr05@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'go_to_pose_server = lab1_control.go_to_pose_server:main',
            'reset_server = lab1_control.reset_server:main',
            'square_server = lab1_control.square_server:main',
        ],
    },
)
