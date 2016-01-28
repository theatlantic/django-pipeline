import glob
import os
import distutils.spawn


def local_path(path):
    return os.path.join(os.path.dirname(__file__), path)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'TEST_NAME': ':memory:'
    }
}

DEBUG = False

SITE_ID = 1

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.auth',
    'django.contrib.admin',
    'pipeline',
    'tests.tests'
]

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware'
)

ROOT_URLCONF = 'tests.urls'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware'
)

MEDIA_URL = '/media/'

MEDIA_ROOT = local_path('media')

STATICFILES_STORAGE = 'pipeline.storage.PipelineStorage'
STATIC_ROOT = local_path('static/')
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    ('pipeline', local_path('assets/')),
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'pipeline.finders.PipelineFinder',
)

SECRET_KEY = "django-pipeline"

PIPELINE = {
    'PIPELINE_ENABLED': True,
    'JS_COMPRESSOR': None,
    'CSS_COMPRESSOR': None,
    'STYLESHEETS': {
        'screen': {
            'source_filenames': (
                'pipeline/css/first.css',
                'pipeline/css/second.css',
                'pipeline/css/urls.css'
            ),
            'output_filename': 'screen.css'
        }
    },
    'JAVASCRIPT': {
        'scripts': {
            'source_filenames': (
                'pipeline/js/first.js',
                'pipeline/js/second.js',
                'pipeline/js/application.js',
                'pipeline/templates/**/*.jst'
            ),
            'output_filename': 'scripts.js'
        },
        'scripts_async': {
            'source_filenames': (
                'pipeline/js/first.js',
                'pipeline/js/second.js',
                'pipeline/js/application.js',
                'pipeline/templates/**/*.jst'
            ),
            'output_filename': 'scripts_async.js',
            'extra_context': {
                'async': True,
            }
        },
        'scripts_defer': {
            'source_filenames': (
                'pipeline/js/first.js',
                'pipeline/js/second.js',
                'pipeline/js/application.js',
                'pipeline/templates/**/*.jst'
            ),
            'output_filename': 'scripts_defer.js',
            'extra_context': {
                'defer': True,
            }
        },
        'scripts_async_defer': {
            'source_filenames': (
                'pipeline/js/first.js',
                'pipeline/js/second.js',
                'pipeline/js/application.js',
                'pipeline/templates/**/*.jst'
            ),
            'output_filename': 'scripts_async_defer.js',
            'extra_context': {
                'async': True,
                'defer': True,
            }
        }
    }
}

NODE_MODULES_PATH = local_path('node_modules')
NODE_BIN_PATH = os.path.join(NODE_MODULES_PATH, '.bin')
NODE_EXE_PATH = distutils.spawn.find_executable('node')
JAVA_EXE_PATH = distutils.spawn.find_executable('java')
CSSTIDY_EXE_PATH = distutils.spawn.find_executable('csstidy')
HAS_NODE = os.path.exists(NODE_BIN_PATH) and NODE_EXE_PATH
HAS_JAVA = bool(JAVA_EXE_PATH)
HAS_CSSTIDY = bool(CSSTIDY_EXE_PATH)

if HAS_NODE:
    def node_exe_path(command):
        exe_ext = '.cmd' if os.name == 'nt' else ''
        return os.path.join(NODE_BIN_PATH, "%s%s" % (command, exe_ext))

    PIPELINE.update({
        'SASS_BINARY': node_exe_path('node-sass'),
        'COFFEE_SCRIPT_BINARY': node_exe_path('coffee'),
        'COFFEE_SCRIPT_ARGUMENTS': ['--no-header'],
        'LESS_BINARY': node_exe_path('lessc'),
        'BABEL_BINARY': node_exe_path('babel'),
        'BABEL_ARGUMENTS': ['--presets', 'es2015'],
        'STYLUS_BINARY': node_exe_path('stylus'),
        'LIVE_SCRIPT_BINARY': node_exe_path('lsc'),
        'LIVE_SCRIPT_ARGUMENTS': ['--no-header'],
        'YUGLIFY_BINARY': node_exe_path('yuglify'),
        'UGLIFYJS_BINARY': node_exe_path('uglifyjs'),
        'CSSMIN_BINARY': node_exe_path('cssmin'),
    })

if HAS_NODE and HAS_JAVA:
    PIPELINE.update({
        'CLOSURE_BINARY': [
            JAVA_EXE_PATH, '-jar',
            os.path.join(NODE_MODULES_PATH, 'google-closure-compiler', 'compiler.jar')],
        'YUI_BINARY': [
            JAVA_EXE_PATH, '-jar',
            glob.glob(os.path.join(NODE_MODULES_PATH, 'yuicompressor', 'build', '*.jar'))[0]]
    })

if HAS_CSSTIDY:
    PIPELINE.update({'CSSTIDY_BINARY': CSSTIDY_EXE_PATH})

TEMPLATE_DIRS = (
    local_path('templates'),
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': TEMPLATE_DIRS,
    },
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'APP_DIRS': True,
        'DIRS': TEMPLATE_DIRS,
        'OPTIONS': {
            'extensions': ['pipeline.jinja2.PipelineExtension']
        }
    }
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'pipeline.templatetags.pipeline': {
            'handlers': ['console'],
            'level': 'ERROR',
        },
    },
}
