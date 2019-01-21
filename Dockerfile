FROM registry.fedoraproject.org/fedora:28

ENV LANG=en_US.UTF-8 \
    HOME=/root

# Install requirements
COPY requirements.sh requirements.txt /tmp/ucho/
RUN bash /tmp/ucho/requirements.sh && \
    pip3 install -r /tmp/ucho/requirements.txt

# Install
COPY ./ /tmp/ucho/
WORKDIR ${HOME}
RUN cd /tmp/ucho && pip3 install .
CMD listen.py
