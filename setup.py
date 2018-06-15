from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('README.md') as f:
    long_description = f.read()

setup(name='i3-workspace-names',
      version='0.2',
      description='Dynamically rename i3wm workspaces depending on windows',
      long_description=long_description,
      url='https://gitlab.com/flib99/i3-workspace-names',
      author='Josh Walls',
      author_email='me@joshwalls.co.uk',
      license='GPL',
      zip_safe=False,
      install_requires=requirements,
      scripts=['i3-workspace-names'])
