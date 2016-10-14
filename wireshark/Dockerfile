FROM ubuntu:xenial

ENV MAKEFLAGS=-j4

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    build-essential \
    git \
    python \
    libtool-bin \
    pkg-config \
    bison \
    flex \
    libglib2.0-dev \
    qtbase5-dev \
    qttools5-dev-tools \
    autoconf \
    libpcap-dev \
    libgcrypt-dev \
    python-serial \
    python-twisted \
    wget \
    python3-dev

WORKDIR /usr/src
RUN git clone -v --depth 1 --branch master-2.2 https://github.com/wireshark/wireshark.git
WORKDIR /usr/src/wireshark
RUN git checkout master-2.2
ADD plugins /usr/src/wireshark/plugins
#RUN ./autogen.sh
#RUN ./configure --prefix=/usr
#RUN make

WORKDIR /tmp
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3 get-pip.py
RUN pip3 install twisted pyserial urwid
