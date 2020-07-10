Pipeline
========

.. image:: https://secure.travis-ci.org/jazzband/django-pipeline.png
    :alt: Build Status
    :target: http://travis-ci.org/jazzband/django-pipeline

.. image:: https://jazzband.co/static/img/badge.svg
   :alt: Jazzband
   :target: https://jazzband.co/

Pipeline is an asset packaging library for Django, providing both CSS and
JavaScript concatenation and compression, built-in JavaScript template support,
and optional data-URI image and font embedding.

Testing
-------

::

    pyenv 3.7.3 2.7.18
    python3 -m venv venv
    . venv/bin/activate
    npm install
    python -m pip install tox
    tox

If you don't have the Java runtime installed, you will receive a nasty message::

    No Java runtime present, requesting install.

And you will be presented a system dialog to "No Java runtime present, requesting install."

If you would rather not do this, you enable an environment variable to skip tests
requiring the Java runtime like this::

    PIPELINE_SKIP_JAVA=1 tox

Or, just export so you don't have to add that before each tox invocation::

    export PIPELINE_SKIP_JAVA=1
    tox -e py37-django20


Installation
------------

To install it, simply: ::

    pip install django-pipeline


Documentation
-------------

For documentation, usage, and examples, see :
https://django-pipeline.readthedocs.io
