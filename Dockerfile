FROM ghcr.io/front-matter/invenio-rdm-starter:latest

ARG WHEEL

RUN /opt/invenio/.venv/bin/python -m ensurepip
RUN /opt/invenio/.venv/bin/python -m pip install --upgrade pip
RUN /opt/invenio/.venv/bin/python -m pip install invenio-theme-iform==2025.5.20
RUN /opt/invenio/.venv/bin/python -m pip uninstall -y pip
RUN invenio collect
RUN apt install -y npm
RUN invenio webpack buildall
RUN apt remove -y npm
