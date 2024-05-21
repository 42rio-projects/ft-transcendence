#!/bin/sh

CERT_DIR="/etc/nginx/ssl"

mkdir -p "$CERT_DIR"

if [ -f "$CERT_DIR/server.crt" ] && [ -f "$CERT_DIR/server.key" ]; then
  echo "Certificates already exist in $CERT_DIR. Skipping generation."
else
  openssl genrsa -out "$CERT_DIR/server.key" 2048
  openssl req -new -key "$CERT_DIR/server.key" -out "$CERT_DIR/server.csr" -subj "/C=$COUNTRY/ST=$STATE/L=$LOCALITY/O=$ORGANIZATION/OU=$OUNITY/CN=$DOMAIN_NAME"
  openssl x509 -req -in "$CERT_DIR/server.csr" -signkey "$CERT_DIR/server.key" -out "$CERT_DIR/server.crt" -days 365
  echo "Certificates generated in $CERT_DIR!"
fi

nginx -g "daemon off;"