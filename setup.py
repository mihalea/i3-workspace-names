from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(name='i3-workspace-names',
      version='0.1',
      description='Dynamically rename i3wm workspaces depending on windows',
      url='https://gitlab.com/flib99/i3-workspace-names',
      author='Josh Walls',
      author_email='me@joshwalls.co.uk',
      license='MIT',
      zip_safe=False,
      install_requires=requirements,
      scripts=['i3-workspace-names'])
