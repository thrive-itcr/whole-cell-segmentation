# Whole Cell Segmentation

_Copyright (c) General Electric Company, 2017.  All rights reserved._

To build the container:

```sh
$ docker build -t thriveitcr/whole-cell-segmentation --build-arg http_proxy=$http_proxy --build-arg https_proxy=$https_proxy --build-arg no_proxy=$no_proxy .
```

To add it to the docker-compose file:
```sh
  whole-cell-segmentation:
    image: thriveitcr/whole-cell-segmentation:latest
    ports:
    - 7106
    environment:
      MSG_SYSTEM: amqp
      SERVICE_NAME: whole-cell-segmentation--v1_0_0
      SERVICE_TAGS: analytic
 ```