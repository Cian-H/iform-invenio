#!/usr/bin/env bash

if [[ "$*" == *--dev* ]]; then
  ENV_FILE="invenio_dev.env"
else
  ENV_FILE="invenio.env"
fi

aws secretsmanager get-secret-value --secret-id Invenio | \
  jq -r '.SecretString | fromjson | to_entries | .[] | .key + "=\"" + .value + "\""' > secrets.env

cat "$ENV_FILE" secrets.env > .env

echo "Environment set up using $ENV_FILE"
