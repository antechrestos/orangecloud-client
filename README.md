# Orange Cloud Client


## *Description*

This library is a python implementation of the [orange cloud api](https://developer.orange.com/apis/cloud-france/api-reference). It brings:

- an [api](#api) to build other api around the orange cloud
- a `cli` to directly interact with the cloud (**yet to develop**)

## *Dependencies*
It is based on:

- [oauth2 client library](https://github.com/antechrestos/OAuth2Client), itself based on r[requests] (https://pypi.python.org/pypi/requests)
- [requests toolbelts](https://github.com/sigmavirus24/requests-toolbelt)

## Installation
To start using it you must create a **developer** account on the [orange partner platform](https://developer.orange.com/signin). Then create an application. But beware on one things: the redirect url must defer from any `localhost`or local url. Since we want to trick it, do as follow:

- pick a domain name such `http://myowncloud.io:8080` (**do not use https as it cannot be handled later**)
- create the application
- map the **domain** `myowncloud.io` on `localhost` in your `host file` (`/etc/hosts` for linux, `%systemroot%\system32\drivers\etc\` for windows)
- run the following code

```python
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
```
    
This will open a light http server listening to your domain, print an url to open. Open it, log in using your cloud account, consent the access for your application. You will be then redirected to your local http server. The code will be then extracted and exchanged for a token. You can save your `refresh token`. Next time you can instanciate the `ApiManager` as follows:
    
```python
api_manager = ApiManager(client_id, client_secret)
api_manager.init_with_token(refresh_token)
```

You are now fully able to use the api.

## *api*
The api brings the following *domains*.

#### Freespace
The only operation on this endpoint is the `get`one that returns the available free space.

#### Folders
This endpoint let you:

- `get` the informations about a **folder** (*See the [documentation](https://developer.orange.com/apis/cloud-france/api-reference) about the `query parameters`*)
- `create` a **folder** in the cloud
- `delete`a **folder** from the cloud
- `move` a **folder** from one **folder** to another
- `rename` a **folder**
- `copy` a **folder** in another **folder**

#### Files
This endpoint let you:

- `get` the informations about a **file**.
- `delete` a **file** from the cloud
- `move` a **file** from one **folder** to another
- `rename` a **file**
- `copy` a **file** in another **folder**
- `upload` a **file** on the cloud
- `download` a **file** from the cloud




