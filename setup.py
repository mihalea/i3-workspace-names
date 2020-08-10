from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('README.md') as f:
    long_description = f.read()

setup(name='i3-workspace-names',
      version='0.5',
      description='Dynamically rename i3wm workspaces depending on windows',
      long_description=long_description,
      url='https://gitlab.com/mihalea/i3-workspace-names',
      author='Mircea Mihalea',
      author_email='mircea@mihalea.ro',
      license='GPL',
      zip_safe=False,
      install_requires=requirements,
      py_modules=['i3_workspace_names'],
      entry_points={
          'console_scripts': [
              'i3-workspace-names=i3_workspace_names:main'
          ]
      })
