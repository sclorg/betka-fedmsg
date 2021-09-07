# Ucho -TESTS

[![Docker Repository on Quay](https://quay.io/repository/rhscl/betka-fedmsg/status "Docker Repository on Quay")](https://quay.io/repository/rhscl/betka-fedmsg)

Ucho can transfer Fedora Messaging events to celery tasks.

## Configuration

If you are interested in specific Fedora Messaging topic,
add it to data/configuration/fedmsg-celerize-map.yaml.

## tl;dr Just tell me how to start this

- [1. terminal] go to cloned [frambo](https://github.com/user-cont/frambo) directory and run `make redis-start`
- [2. terminal] in `ucho/` run `make fedmsg-start`

## Start Ucho in container

Set up configuration details for your redis for celery by setting env variables `REDIS_BROKER` and `REDIS_BACKEND` in docker run.
By default it expects a redis running on `localhost`.
To start one, go to cloned [frambo](https://github.com/user-cont/frambo) directory and run `make redis-start`.

You can lunch it with fedmsg:

```
make fedmsg-start
```

## Install Ucho locally

Install required packages and get cerificates

```
./requirements.sh
```

Create virtualenv:

```
virtualenv ucho
```

Activate it by sourcing the activation file:

```
source ./ucho/bin/activate
```

Run command in your virtual env:

```
pip3 install -r requirements.txt
```

Listen on fedmsg:

```
TASK='fedmsg' DEPLOYMENT=dev listen.py
```
