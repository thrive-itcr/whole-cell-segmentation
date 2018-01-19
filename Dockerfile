# Copyright (c) General Electric Company, 2017.  All rights reserved.

FROM rt106/rt106-algorithm-sdk

USER root

RUN  apt-get -y update \
     && apt-get -y install libgtk2.0-0 \
     && apt-get -y install libsm6 \
     && pip install numpy opencv-python

ADD rt106SpecificAdaptorCode.py        /rt106/rt106SpecificAdaptorCode.py
ADD rt106SpecificAdaptorDefinitions.json       /rt106/rt106SpecificAdaptorDefinitions.json
ADD entrypoint.sh                            /rt106/entrypoint.sh
ADD WholeCellSeg.py                          /rt106/WholeCellSeg.py
ADD rt106-wavelet-nuclei-segmentation.tar.gz /rt106

RUN mkdir -p /rt106/input && mkdir -p /rt106/output
RUN chmod a+x /rt106/entrypoint.sh
WORKDIR /rt106

RUN chown -R rt106:rt106 /rt106
USER rt106:rt106

CMD ["/rt106/entrypoint.sh"]
