# -*- coding: utf-8 -*-

import sys
import os
import urllib.parse

import requests
from deconstrst.builder import DeconstJSONBuilder
from sphinx.application import Sphinx
from sphinx.builders import BUILTIN_BUILDERS


def build(srcdir, destdir):
    """
    Invoke Sphinx with locked arguments to generate JSON content.
    """

    # I am a terrible person
    BUILTIN_BUILDERS['deconst'] = DeconstJSONBuilder

    doctreedir = os.path.join(destdir, '.doctrees')

    app = Sphinx(srcdir=srcdir, confdir=srcdir, outdir=destdir,
                 doctreedir=doctreedir, buildername="deconst",
                 confoverrides={}, status=sys.stdout, warning=sys.stderr,
                 freshenv=True, warningiserror=False, tags=[], verbosity=0,
                 parallel=1)
    app.build(True, [])

    return app.statuscode


def submit(destdir, content_store_url, content_id_base):
    """
    Submit the generated json files to the content store API.
    """

    headers = {
        "Content-Type": "application/json"
    }

    for dirpath, dirnames, filenames in os.walk(destdir):
        for name in filenames:
            fullpath = os.path.join(dirpath, name)
            base, ext = os.path.splitext(name)

            if os.path.isfile(fullpath) and ext == ".json":
                relpath = os.path.relpath(fullpath, destdir)

                if base == "index":
                    full_suffix = dirpath
                else:
                    full_suffix = os.path.join(dirpath, base)

                content_suffix = os.path.relpath(full_suffix, destdir)

                content_id = content_id_base + content_suffix
                content_id = content_id.rstrip("/.")

                print(
                    "submitting [{}] as [{}] ... ".format(relpath, content_id),
                    end=''
                )

                url = content_store_url + "content/" + \
                    urllib.parse.quote(content_id, safe='')

                with open(fullpath, "rb") as inf:
                    response = requests.put(url, data=inf, headers=headers)
                    response.raise_for_status()

                print("success")

    print("All generated content submitted to the content store.")

    return 0
