from setuptools import setup, find_packages
from akoteka.setup.setup import getSetupIni

sp=getSetupIni()

setup(
      name=sp['name'],
      version=sp['version'],
      description='Videoteka',
      long_description="Helps to manage your media contents",	#=open('README.md', encoding="utf-8").read(),
      url='http://github.com/dallaszkorben/akoteka',
      author='dallaszkorben',
      author_email='dallaszkorben@gmail.com',
      license='MIT',
      classifiers =[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
      ],
      packages = find_packages(),
      setup_requires=[ "pyqt5", "pyqt5-sip", "numpy", "pyttsx3", 'configparser', 'psutil'],
      install_requires=["pyqt5", 'pyqt5-sip', 'numpy','pyttsx3', 'configparser', 'psutil'],
      entry_points = {
        'console_scripts': [
		'akoteka=akoteka.gui.main_window:main',
		'inihealthcheck=akoteka.health_check:main'
		]
      },
      package_data={
        'cardholder': ['img/*.gif'],
        'akoteka': ['gui/img/*.png'],
        'akoteka': ['setup/setup.ini'],
        'akoteka': ['dict/*.properties']
      },
      include_package_data = True,
      zip_safe=False)