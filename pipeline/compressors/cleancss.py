from __future__ import unicode_literals

import codecs
import json
import os
import logging

from django.conf import settings as django_settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.exceptions import SuspiciousFileOperation

from pipeline.conf import settings
from pipeline.compressors import SubProcessCompressor
from pipeline.utils import source_map_re, relurl


logger = logging.getLogger('pipeline')


class CleanCSSCompressor(SubProcessCompressor):

    def compress_css(self, css):
        args = [settings.CLEANCSS_BINARY, settings.CLEANCSS_ARGUMENTS]
        return self.execute_command(args, css)

    def compress_css_with_source_map(self, paths, output_filename):
        output_path = staticfiles_storage.path(output_filename)
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        args = [settings.CLEANCSS_BINARY]
        args += ['--source-map']
        if settings.CLEANCSS_ARGUMENTS:
            args += [settings.CLEANCSS_ARGUMENTS]
        else:
            # At present, without these arguments, cleancss does not
            # generate accurate source maps
            args += [
                '--skip-advanced', '--skip-media-merging',
                '--skip-restructuring', '--skip-shorthand-compacting',
                '--keep-line-breaks']
        args += ['--output', output_path]
        args += [staticfiles_storage.path(p) for p in paths]

        self.execute_command(args, cwd=output_dir)

        source_map_file = "%s.map" % output_path

        with codecs.open(output_path, encoding='utf-8') as f:
            css = f.read()
        with codecs.open(source_map_file, encoding='utf-8') as f:
            source_map = f.read()

        # Strip out existing source map comment (it will be re-added with packaging)
        css = source_map_re.sub('', css)

        output_url = "%s/%s" % (
            staticfiles_storage.url(os.path.dirname(output_filename)),
            os.path.basename(output_path))

        # Grab urls from staticfiles storage (in case filenames are hashed)
        source_map_data = json.loads(source_map)
        for i, source in enumerate(source_map_data['sources']):
            source_abs_path = os.path.abspath(os.path.join(output_dir, source))
            source_rel_path = os.path.relpath(
                source_abs_path, staticfiles_storage.base_location)
            source_url = None
            try:
                source_url = staticfiles_storage.url(source_rel_path)
            except SuspiciousFileOperation:
                for static_dir in django_settings.STATICFILES_DIRS:
                    if not isinstance(static_dir, tuple):
                        continue
                    prefix, path = static_dir
                    if not source_abs_path.startswith(path):
                        continue
                    source_rel_path = os.path.relpath(source_abs_path, path)
                    source_url = staticfiles_storage.url(
                        os.path.join(prefix, source_rel_path))
                if not source_url:
                    logger.exception("Could not relativize source map file")
                    continue
            source_map_data['sources'][i] = relurl(source_url, output_url)
        source_map = json.dumps(source_map_data)

        return css, source_map
