from setuptools import setup

setup(
    name='pylps',
    version='0.0.1',
    description='LPS in python',
    entry_points={
        'console_scripts': [
            'pylps=pylps_helper.command_line:main'
        ]
    },
)

# setup(
#     name='pylps_helper',
#     version='0.0.1',
#     description='pylps helper',
#     entry_points={
#         'console_scripts': [
#             'pylps=pylps_helper.command_line:main'
#         ]
#     },
# )
