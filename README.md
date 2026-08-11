# Research Project Website

This repository contains the source code for I-Form's custom Invenio instance

## Deployment

This project is deployed using an automated Python CLI. All commands should be
run from the repository root via `uv`.

### 1. Initial Server Setup (Bootstrap)

On the deployment server, first generate the `.env` configuration file:

```sh
uv run cli bootstrap server
mv .env.template .env
```
Populate the `.env` file with the specific configuration. (S3 credentials will
be fetched dynamically via AWS environment variables or Bitwarden during
deployment).

### 2. Pushing Updates

Before deploying, it is required to merge the local `main` branch into `prod`
and push it to the remote server. This can be done automatically from the local
machine:

```sh
uv run cli deploy merge-and-push-prod
```

### 3. First-Time Deployment

On the deployment server, spin up the infrastructure and initialize the
databases and indices for the first time by running:

```sh
uv run cli deploy prod-deploy
```

### 4. Updating an Existing Deployment

For future code updates, pull and deploy the latest changes with automatic
healthcheck rollbacks using:

```sh
uv run cli deploy prod-update --auto-rollback
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file
for details.
