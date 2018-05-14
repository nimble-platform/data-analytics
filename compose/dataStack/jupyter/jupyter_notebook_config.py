# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

from jupyter_core.paths import jupyter_data_dir
import subprocess
import os
import errno
import stat

c = get_config()
c.NotebookApp.ip = '*'
c.NotebookApp.port = 8888
c.NotebookApp.open_browser = False
#c.NotebookApp.password = '' # 'sha1:bcd259ccf...<your hashed password here>'
c.NotebookApp.token = '30bbf31e2c867cd06f7ed80306e2abcb9768dba6'  # enables login without any security layers


# run behind an apache2 proxy, tutorial:
# https://linode.com/docs/applications/big-data/install-a-jupyter-notebook-server-on-a-linode-behind-an-apache-reverse-proxy/https://linode.com/docs/applications/big-data/install-a-jupyter-notebook-server-on-a-linode-behind-an-apache-reverse-proxy/

c.NotebookApp.allow_origin = 'http://127.0.0.1:8888/jupyter'
c.NotebookApp.base_url = '/jupyter'  # OK
#c.NotebookApp.certfile = '/absolute/path/to/mycert.pem'
#c.NotebookApp.ip = '�localhost' # geht ned, il060 a ned
#c.NotebookApp.keyfile = '/absolute/path/to/mykey.key'
#c.NotebookApp.open_browser = False
#c.NotebookApp.password = 'sha1:30bbf31e2c867cd06f7ed80306e2abcb9768dba6'  # enables login without any security layers, doesn't work
c.NotebookApp.trust_xheaders = True # doesn't work


