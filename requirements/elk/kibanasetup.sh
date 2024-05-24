#!/bin/bash
# kibanasetup.sh

# Array com os nomes dos data views
names=("django" "pgadmin" "elasticsearch" "grafana" "postgres" "cadvisor" "filebeat" "kibana" "logstash" "prometheus" "redis" "nginx" "alertmanager" "node_exporter")
senha=${KIBANA_PASSWORD}

for name in "${names[@]}"; do
  # Criação de dataview via API
  curl_response=$(curl --silent --fail -X POST "http://kibana:5601/api/data_views/data_view" \
                     -H 'kbn-xsrf: true' -H 'Content-Type: application/json' \
                     --user "elastic:$senha" \
                     -d "{ \"data_view\": { \"title\": \"$name\", \"name\": \"$name\" } }" 2>&1)

  if [ $? -eq 0 ]; then
    echo "Data view \"$name\" created successfully."
  else
    echo "Failed to create data view \"$name\". Response: $curl_response"
    continue
  fi
done

echo "Waiting for 30 seconds..."
sleep 30

for name in "${names[@]}"; do
  # Attach index to ILM policy
curl_response=$(curl -k --silent --fail -X PUT "https://elasticsearch:9200/$name/_settings?pretty" --user "elastic:$senha"  -H 'Content-Type: application/json' -d '{
  "index": {
    "lifecycle": {
      "name": "kibana-event-log-policy"
    }
  }
}' 2>&1)

if [ $? -eq 0 ]; then
  echo "Política ILM \"kibana-event-log-policy\" anexada com sucesso a index $name ."
else
  echo "Falha ao anexar a política ILM ao índice $name Resposta: $curl_response"
  continue
fi
done