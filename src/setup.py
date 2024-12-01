from setuptools import setup

setup(
    name="VivariumSim",
    options={
        'bam-model-extensions':[
                '.obj'
        ],
        
        'build_apps':{
            'gui_apps':{
                'VivariumSim': 'main.py',
            },
            
            # Set up output logging, important for GUI apps!
            'log_filename': '$USER_APPDATA/VivariumSim/output.log',
            'log_append': True,
            
            
            
            'include_patterns': [
                'assets/**/*.png',
                'assets/**/*.jpg',
                'assets/**/*.stl',
                'assets/**/*.obj',
                'assets/**/*.vert',
                'assets/**/*.frag',
                '/**/*.prc'
            ],
            'plugins': [
                'pandagl',
                'p3openal_audio',
                'p3assimp',
                'p3ptloader'
            ],
            'platforms': [
                'manylinux1_x86_64',
                'macosx_10_6_x86_64',
                'win_amd64',
            ],
        },
    
    }
)