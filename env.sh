#!/usr/bin/env bash
if [[ "$*" == *--dev* ]]; then
  echo "Configuring env in development mode"
  ENV_FILE="invenio_dev.env"
else
  echo "Configuring env in production mode"
  ENV_FILE="invenio_prod.env"
fi

aws secretsmanager get-secret-value --secret-id Invenio | \
  jq -r '.SecretString | fromjson | to_entries | .[] | .key + "=\"" + .value + "\""' > secrets.env

cat ./env/invenio.env "./env/$ENV_FILE" secrets.env > .env

echo "Environment set up using $ENV_FILE"
