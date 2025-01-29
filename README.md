# AM-D-Model Data Repository

Welcome to the modified InvenioRDM instance for the AM-D-Model data repository.
This instance has been modified specifically for production ready, containerized
deployment in an amazon AWS EC2 instance behind a reverse proxy. This allows it
to be incorporated as part of a larger research project's website.

## Getting started

Run the following commands in order to start the InvenioRDM instance:

```console
invenio-cli containers build
./prepare-env.sh
docker compose -f docker-compose.full.yml up -d
rm .env # Cleanup for security reasons
```

## Overview

Following is an overview of the files and folders in this instance:

| Name | Description |
|---|---|
| ``Dockerfile`` | Dockerfile used to build your application image. |
| ``Pipfile`` | Python requirements installed via [pipenv](https://pipenv.pypa.io) |
| ``Pipfile.lock`` | Locked requirements (generated on first install). |
| ``app_data`` | Application data such as vocabularies. |
| ``assets`` | Web assets (CSS, JavaScript, LESS, JSX templates) used in the Webpack build. |
| ``docker`` | Example configuration for NGINX and uWSGI. |
| ``docker-compose.full.yml`` | Example of a full infrastructure stack. |
| ``docker-compose.yml`` | Backend services needed for local development. |
| ``docker-services.yml`` | Common services for the Docker Compose files. |
| ``invenio.cfg`` | The Invenio application configuration. |
| ``logs`` | Log files. |
| ``prepare_env.sh`` | Creation of a .env file containing required secrets from AWS |
| ``static`` | Static files that need to be served as-is (e.g. images). |
| ``templates`` | Folder for your Jinja templates. |
| ``.invenio`` | Common file used by Invenio-CLI to be version controlled. |
| ``.invenio.private`` | Private file used by Invenio-CLI *not* to be version controlled. |

## Documentation

To learn how to configure, customize, deploy and much more, visit
the [InvenioRDM Documentation](https://inveniordm.docs.cern.ch/).
