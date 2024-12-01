from setuptools import setup

setup(
    name="VivariumSim",
    options={
        'build_apps':{
            'gui_apps':{
                'VivariumSim': 'main.py',
            },
            'include_patterns': [
                '**/*.png',
                '**/*.jpg',
                '**/*.egg',
                '**/*.stl',
                '**/*.obj',
                '**/*.mtl',
                '**/*.bam',
                '**/*.glsl',
                '**/*.vert',
                '**/*.frag',
                '**/*.json',
                '**/*.csv',
                '**/*.txt',
            ],
            'plugins': [
                'pandagl',
                'p3openal_audio',
            ],
            'platforms': [
                'manylinux1_x86_64',
                'macosx_10_6_x86_64',
                'win_amd64',
            ],
        }
    }
)