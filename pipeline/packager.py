from __future__ import unicode_literals
import os.path

from django.contrib.staticfiles.storage import staticfiles_storage
from django.contrib.staticfiles.finders import find
from django.core.files.base import ContentFile
from django.utils.encoding import smart_bytes

from pipeline.compilers import Compiler
from pipeline.compressors import Compressor
from pipeline.conf import settings
from pipeline.exceptions import PackageNotFound
from pipeline.glob import glob
from pipeline.signals import css_compressed, js_compressed


class Package(object):
    def __init__(self, config):
        self.config = config
        self._sources = []

    @property
    def sources(self):
        if not self._sources:
            paths = []
            for pattern in self.config.get('source_filenames', []):
                for path in glob(pattern):
                    if path not in paths and find(path):
                        paths.append(str(path))
            self._sources = paths
        return self._sources

    @property
    def paths(self):
        return [path for path in self.sources
                if not path.endswith(settings.TEMPLATE_EXT)]

    @property
    def templates(self):
        return [path for path in self.sources
                if path.endswith(settings.TEMPLATE_EXT)]

    @property
    def output_filename(self):
        return self.config.get('output_filename')

    @property
    def extra_context(self):
        return self.config.get('extra_context', {})

    @property
    def template_name(self):
        return self.config.get('template_name')

    @property
    def variant(self):
        return self.config.get('variant')

    @property
    def manifest(self):
        return self.config.get('manifest', True)


class Packager(object):
    def __init__(self, storage=None, verbose=False, css_packages=None, js_packages=None):
        if storage is None:
            storage = staticfiles_storage
        self.storage = storage
        self.verbose = verbose
        self.compressor = Compressor(storage=storage, verbose=verbose)
        self.compiler = Compiler(storage=storage, verbose=verbose)
        if css_packages is None:
            css_packages = settings.STYLESHEETS
        if js_packages is None:
            js_packages = settings.JAVASCRIPT
        self.packages = {
            'css': self.create_packages(css_packages),
            'js': self.create_packages(js_packages),
        }

    def package_for(self, kind, package_name):
        try:
            return self.packages[kind][package_name]
        except KeyError:
            raise PackageNotFound(
                "No corresponding package for %s package name : %s" % (
                    kind, package_name
                )
            )

    def individual_url(self, filename):
        return self.storage.url(filename)

    def pack_stylesheets(self, package, **kwargs):
        return self.pack(package, self.compressor.compress_css, css_compressed,
                         compress_type='css',
                         output_filename=package.output_filename,
                         variant=package.variant, **kwargs)

    def compile(self, paths, force=False):
        return self.compiler.compile(paths, force=force)

    def pack(self, package, compress, signal, compress_type, **kwargs):
        output_filename = package.output_filename
        if self.verbose:
            print("Saving: %s" % output_filename)
        paths = self.compile(package.paths, force=True)
        content, source_map = compress(paths, **kwargs)
        if source_map is not None:
            source_map_output_filename = output_filename + '.map'
            if self.verbose:
                print("Saving: %s" % source_map_output_filename)
            self.save_file(source_map_output_filename, source_map)
            source_map_comment = "sourceMappingURL=%s" % (
                os.path.basename(staticfiles_storage.url(source_map_output_filename)))
            if compress_type == 'js':
                content += "\n//# %s" % source_map_comment
            else:
                content += "\n/*# %s */" % source_map_comment
            yield source_map_output_filename
        self.save_file(output_filename, content)
        signal.send(sender=self, package=package, **kwargs)
        yield output_filename

    def pack_javascripts(self, package, **kwargs):
        return self.pack(package, self.compressor.compress_js, js_compressed,
                         compress_type='js', templates=package.templates, **kwargs)

    def pack_templates(self, package):
        return self.compressor.compile_templates(package.templates)

    def save_file(self, path, content):
        return self.storage.save(path, ContentFile(smart_bytes(content)))

    def create_packages(self, config):
        packages = {}
        if not config:
            return packages
        for name in config:
            packages[name] = Package(config[name])
        return packages
