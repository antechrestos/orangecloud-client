# Orange Cloud Client


## *Description*

This library is a python implementation of the [orange cloud api](https://developer.orange.com/apis/cloud-france/api-reference). It brings:

- an [api](#api) to build other api around the orange cloud
- a `cli` to directly interact with the cloud (**yet to develop**)

## *Dependencies*
It is based on:

- [oauth2 client library](https://github.com/antechrestos/OAuth2Client), itself based on r[requests] (https://pypi.python.org/pypi/requests)
- [requests toolbelts](https://github.com/sigmavirus24/requests-toolbelt)

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




