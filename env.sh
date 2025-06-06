#!/usr/bin/env bash
if [[ "$*" == *--dev* ]]; then
  echo "Configuring env in development mode"
  ENV_FILE="invenio_dev.env"
else
  echo "Configuring env in production mode"
  ENV_FILE="invenio_prod.env"
fi

{
    echo "# Secrets fetched from AWS Secrets Manager"
    aws secretsmanager get-secret-value --secret-id Invenio | \
      jq -r '.SecretString | fromjson | to_entries | .[] | .key + "=\"" + .value + "\""'
    echo ""
} > secrets.env

cat secrets.env ./env/invenio.env "./env/$ENV_FILE" > .env
rm secrets.env

echo "Environment set up using $ENV_FILE"
