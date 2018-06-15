pkgbase=('i3-workspace-names')
pkgname=('i3-workspace-names')
_module='i3-workspace-names'
pkgver='0.2'
pkgrel=1
pkgdesc="Dynamically rename i3wm workspaces depending on windows"
url="https://gitlab.com/flib99/i3-workspace-names"
depends=('python')
makedepends=('python-setuptools')
license=('GPL')
arch=('any')
source=("https://files.pythonhosted.org/packages/source/i/i3-workspace-names/i3-workspace-names-${pkgver}.tar.gz")
md5sums=('SKIP')

build() {
    cd "${srcdir}/${_module}-${pkgver}"
    python setup.py build
}

package() {
    depends+=()
    cd "${srcdir}/${_module}-${pkgver}"
    python setup.py install --root="${pkgdir}" --optimize=1 --skip-build
}
