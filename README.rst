Orange Cloud python client
==========================
.. image:: https://img.shields.io/pypi/v/orangecloud-client.svg
    :target: https://pypi.python.org/pypi/orangecloud-client
.. image:: https://img.shields.io/github/license/antechrestos/orangecloud-client.svg
	:target: https://raw.githubusercontent.com/antechrestos/orangecloud-client/master/LICENSE

This library is a python implementation of the `orange cloud api <https://developer.orange.com/apis/cloud-france/api-reference>`_
It brings:

- an `api <#api>`_ to build other api around the orange cloud
- a `command line interface <#cli>`_ to directly interact with the cloud

Dependencies
------------
It is based on:

- `oauth2 client library <https://github.com/antechrestos/OAuth2Client>`_, itself based on `requests <https://pypi.python.org/pypi/requests>`_.
- `requests toolbelts <https://github.com/sigmavirus24/requests-toolbelt>`_


Installing
----------

From pip
~~~~~~~~
.. code-block:: bash

	$ pip install orangecloud-client

From sources
~~~~~~~~~~~~

To build the library run :

.. code-block:: bash

	$ python setup.py install

Run the OAuth Grant code process
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To start using it you must create a **developer** account on the
`orange partner platform <https://developer.orange.com/signin>`_.
Then create an application. But beware on one things: the **redirect url** must differ from any `localhost` or local url.
Since we want to trick it, do as follow:

- pick a domain name such `http://my-own-cloud.io:8080` (**do not use https as it cannot be handled later**)
- create the application
- map the **domain** `my-own-cloud.io` on `localhost` in your **host file** ( `/etc/hosts` for linux,
    `%systemroot%\\system32\\drivers\\etc\\` for windows)
- run the following code


.. code-block:: python

    # provide the client id and client secret got on your application page
    api_manager = ApiManager(client_id, client_secret)
    # in this example the redirect url  is http://myowncloud.io:8080 and /etc/hosts contains the line
    # 127.0.0.1       myowncloud.io
    redirect_uri = 'http://myowncloud.io:8080'
    url_to_open = api_manager.init_authorize_code_process(redirect_uri=redirect_uri, state='1234')
    print 'Open this URL: %s' % url_to_open
    code = api_manager.wait_and_terminate_authorize_code_process()
    api_manager.init_with_authorize_code(redirect_uri=redirect_uri, code=code)
    print 'refresh_token got %s' % api_manager.refresh_token

This will run a **local http server listening to your domain**, print an url to open. **Open it in your browser**,
log in using your cloud account, consent the access for your application.
You will be then redirected to your **local http server**. The code will be then extracted and exchanged for a token.
You can save your `refresh token`. Next time you can instantiate the `ApiManager` as follows:

.. code-block:: python

    api_manager = ApiManager(client_id, client_secret)
    api_manager.init_with_token(refresh_token)

You are now fully able to use the api.

API
---
The api brings the following *domains*.

Freeespace
~~~~~~~~~~
The only operation on this endpoint is the `get` one that returns the available free space.

Folders
~~~~~~~
This endpoint let you:

- `get` the information about a **folder** (*See the `documentation <https://developer.orange.com/apis/cloud-france/api-reference>`_ about the `query parameters`*)
- `create` a **folder** in the cloud
- `delete` a **folder** from the cloud
- `move` a **folder** from one **folder** to another
- `rename` a **folder**
- `copy` a **folder** in another **folder**

Files
~~~~~
This endpoint let you:

- `get` the information about a **file**.
- `delete` a **file** from the cloud
- `move` a **file** from one **folder** to another
- `rename` a **file**
- `copy` a **file** in another **folder**
- `upload` a **file** on the cloud
- `download` a **file** from the cloud

Command Line interface
----------------------
To run the client, enter the following command :

.. code-block:: bash

	$ orangecloud-client

At first execution, it will ask you ask.
Please note that your credentials won't be saved on your disk: only tokens will be kept for further use.
Please not that the command `shell` runs an interactive shell to interact with the cloud.
Other commands are single command and return after finished.

Issues and contributions
------------------------
Please submit issue/pull request.
