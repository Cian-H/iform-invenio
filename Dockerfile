FROM ghcr.io/front-matter/invenio-rdm-starter:latest

RUN /opt/invenio/.venv/bin/python -m ensurepip
RUN /opt/invenio/.venv/bin/python -m pip install invenio-theme-tugraz invenio-records-lom
RUN /opt/invenio/.venv/bin/python -m pip uninstall -y pip
RUN invenio collect
RUN apt install -y npm
RUN invenio webpack buildall
RUN apt remove -y npm
