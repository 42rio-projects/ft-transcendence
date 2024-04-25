#!/bin/bash
# kibanasetup.sh

names=("django" "adminer" "elasticsearch" "grafana" "postgres" "cadvisor" "filebeat" "kibana" "logstash" "prometheus" "redis")

for name in "${names[@]}"; do
  # Request para criação de dataview via API
  curl_response=$(curl --fail -X POST "kibana:5601/api/data_views/data_view" \
                     -H 'kbn-xsrf: true' -H 'Content-Type: application/json' \
                     --user elastic:memude \
                     -d "{ \"data_view\": { \"title\": \"$name\", \"name\": \"$name\" } }" 2>&1)

  # Checando o status code da requisição
  curl_status_code=$(echo "$curl_response" | grep 'HTTP' | awk '{print $2}')

  if [ "$curl_status_code" -eq 0 ]; then
    echo "Data view \"$name\" created successfully."
  else
    echo "Failed to create data view \"$name\". Status code: $curl_status_code."
    continue
  fi
done
