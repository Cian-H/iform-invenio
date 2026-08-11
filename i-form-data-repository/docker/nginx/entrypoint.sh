#!/bin/sh

# Check if Let's Encrypt live certificates exist
if [ -d "/etc/letsencrypt/live" ] && [ "$(ls -A /etc/letsencrypt/live)" ]; then
    # Certs exist, find the first domain folder (ignoring README)
    DOMAIN=$(find /etc/letsencrypt/live -mindepth 1 -maxdepth 1 -type d | head -n 1 | xargs basename)
    echo "Using Let's Encrypt certificates for $DOMAIN"
    ln -sf /etc/letsencrypt/live/$DOMAIN/fullchain.pem /etc/ssl/certs/invenio.crt
    ln -sf /etc/letsencrypt/live/$DOMAIN/privkey.pem /etc/ssl/private/invenio.key
else
    # Fallback to test certs
    echo "Using fallback test certificates"
    cp /etc/ssl/certs/test.crt /etc/ssl/certs/invenio.crt
    cp /etc/ssl/private/test.key /etc/ssl/private/invenio.key
fi

# Execute the default CMD (nginx)
exec "$@"
