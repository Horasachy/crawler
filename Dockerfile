FROM ubuntu:20.04 as build-target
ENV LC_ALL C
ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN true

RUN apt-get -qqy update
RUN apt-get -qqy --no-install-recommends install \
  wget \
  firefox \
  x11vnc \
  xvfb \
  xfonts-100dpi \
  xfonts-75dpi \
  xfonts-scalable \
  xfonts-cyrillic \
  python3 \
  python3-pip \
  python3.8-dev \
  python3-venv \
  python3-setuptools \
  python3-wheel \
  build-essential \
  curl \
  firefox \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/*
ENV DISPLAY=:99
CMD ["Xvfb", ":99", "-screen", "0", "1366x768x16"]

RUN mkdir /crawler \
    /crawler/crawler-data \
    /crawler/crawler-data/logs \
    /crawler/crawler-data/eggs \
    /crawler/crawler-data/items \
    /crawler/crawler-data/dbs
WORKDIR /crawler
ENV PATH="~/.local/bin:$PATH"
EXPOSE 5000 6800 8050

ADD requirements.txt /crawler
RUN pip3 install -r requirements.txt
ADD ./docker/scrapyd.conf /etc/scrapyd/
ADD ./docker/scrapydweb_settings_v10.py /crawler/
ADD ./docker/geckodriver /crawler/
ADD ./docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
RUN chmod +x geckodriver
COPY buc_crawler /crawler/buc_crawler

ENTRYPOINT ["/entrypoint.sh"]