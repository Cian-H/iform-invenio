FROM ghcr.io/front-matter/invenio-rdm-starter:v12.0.18.0

RUN /opt/invenio/.venv/bin/python -m ensurepip
RUN /opt/invenio/.venv/bin/python -m pip install --upgrade pip
RUN /opt/invenio/.venv/bin/python -m pip install invenio-theme-iform==2025.6.3
RUN apt update -y && apt upgrade -y
RUN apt install -y npm
RUN invenio collect --verbose
RUN invenio webpack buildall
# RUN apt remove -y npm && apt autoremove -y
RUN ls -la /opt/invenio/var/instance/static/ || echo "Static directory not found"
