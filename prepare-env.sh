#!/usr/bin/env bash
aws secretsmanager get-secret-value --secret-id Invenio | \
  jq -r '.SecretString | fromjson | to_entries | .[] | .key + "=\"" + .value + "\""' > secrets.env
cat am-d-model.env secrets.env > .env
