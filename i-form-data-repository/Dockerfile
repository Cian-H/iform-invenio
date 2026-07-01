# Dockerfile that builds a fully functional image of your app.
#
# This image installs all Python dependencies for your application. It's based
# on Almalinux (https://github.com/inveniosoftware/docker-invenio)
# and includes Pip, Pipenv, Node.js, NPM and some few standard libraries
# Invenio usually needs.
#
# Note: It is important to keep the commands in this file in sync with your
# bootstrap script located in ./scripts/bootstrap.

FROM registry.cern.ch/inveniosoftware/almalinux:1

ENV UV_PYTHON=3.12
ENV PIPENV_VENV_IN_PROJECT=1

COPY site ./site
COPY Pipfile Pipfile.lock ./
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
RUN uv python install ${UV_PYTHON} && \
    pipenv install --deploy --python $(uv python find ${UV_PYTHON}) && \
    pipenv run pip install "setuptools<70.0.0"

COPY ./docker/uwsgi/ ${INVENIO_INSTANCE_PATH}
COPY ./invenio.cfg ${INVENIO_INSTANCE_PATH}
COPY ./templates/ ${INVENIO_INSTANCE_PATH}/templates/
COPY ./app_data/ ${INVENIO_INSTANCE_PATH}/app_data/
COPY ./translations/ ${INVENIO_INSTANCE_PATH}/translations/
COPY ./ .

RUN curl -fsSL https://rpm.nodesource.com/setup_20.x | bash - && \
    dnf install -y nodejs

ARG INSTALL_LOCAL_WHEELS=false
COPY ./local_wheels/ ./local_wheels/
RUN if [ "$INSTALL_LOCAL_WHEELS" = "true" ]; then \
        if ls ./local_wheels/invenio_theme_iform*.whl ./local_wheels/invenio_config_iform*.whl 1> /dev/null 2>&1; then \
            pipenv run pip install --no-deps --force-reinstall ./local_wheels/invenio_theme_iform*.whl ./local_wheels/invenio_config_iform*.whl; \
        fi \
    fi

ENV WEBPACKEXT_PROJECT="invenio_assets.webpack:rspack_project"
RUN cp -r ./static/. ${INVENIO_INSTANCE_PATH}/static/ && \
    cp -r ./assets/. ${INVENIO_INSTANCE_PATH}/assets/ && \
    uv run invenio collect --verbose  && \
    npm config set legacy-peer-deps true && \
    uv run invenio webpack buildall

ENV PATH="/opt/invenio/src/.venv/bin:$PATH"
