# Maintainer Mircea Mihalea <mircea at mihalea dot ro>
# Author Josh Walls <flib99>

pkgname=i3-workspace-names
_module='i3_workspace_names'
pkgver=0.5
pkgrel=1
pkgdesc="Dynamically rename i3wm workspaces depending on windows"
url="https://github.com/mihalea/i3-workspace-names"
depends=('python' 'python-i3ipc' 'python-enum-compat' 'python-requests')
makedepends=('python-setuptools')
license=('GPL')
arch=('any')
provides=('i3-workspace-names')
source=("git+https://github.com/mihalea/i3-workspace-names.git")
md5sums=('SKIP')

build() {
    cd "${pkgname}"
    python setup.py build
}

package() {
    depends+=()
    cd "${pkgname}"
    python setup.py install --root="${pkgdir}" --optimize=1 --skip-build
    install -D -m 0644 "config.example.json" "$pkgdir/usr/share/i3-workspace-names/config.example.json"
}
