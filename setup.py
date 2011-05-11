from setuptools import setup

version = '1.15'

long_description = '\n\n'.join([
    open('README.txt').read(),
    open('TODO.txt').read(),
    open('CREDITS.txt').read(),
    open('CHANGES.txt').read(),
    ])

install_requires = [
    'Django',
    'django-staticfiles',
    'django-extensions',
    'lizard-ui',
    'lizard-map >= 1.68',
    'django-nose',
    'django-treebeard',
    'nens',
    'shapely',
    'south',
    ],

tests_require = [
    ]

setup(name='lizard-shape',
      version=version,
      description="Provides storage and visualization for shapefiles and his files",
      long_description=long_description,
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Programming Language :: Python',
                   'Framework :: Django',
                   ],
      keywords=[],
      author='Jack Ha',
      author_email='jack.ha@nelen-schuurmans.nl',
      url='http://www.nelen-schuurmans.nl/lizard/',
      license='GPL',
      packages=['lizard_shape'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      tests_require=tests_require,
      extras_require = {'test': tests_require},
      entry_points={
          'console_scripts': [
            ],
          'lizard_map.adapter_class': [
            'adapter_shapefile = lizard_shape.layers:AdapterShapefile',
            ],
          },
      )
