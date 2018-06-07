from setuptools import setup, find_packages

setup(
    name='diffcalc',
    version='2.1',
    
    description='A diffraction condition calculator for X-ray or neutron diffractometer control.',
    long_description=open('README.rst').read(),
    url='https://github.com/DiamondLightSource/diffcalc',
    
    author='Rob Walton',
    author_email='rob.walton@diamond.ac.uk',
    
    license='GNU',
    
    packages=find_packages(exclude=['docs']),
    
    install_requires=[         
        'numpy',
        'ipython',
        'pytest',
        'pytest-xdist',
        'nose'
    ],

    entry_points={
        'console_scripts': [
            'diffcalc=diffcmd.diffcalc_launcher:main',
        ],
    },
)