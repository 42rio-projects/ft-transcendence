#!/bin/bash
# setup.sh

curl --fail -X POST "kibana:5601/api/data_views/data_view" -H 'kbn-xsrf: true' -H 'Content-Type: application/json' --user elastic:memude  -d'
{
  "data_view": {
     "title": "django",
     "name": "django"
  }
}
'

curl --fail -X POST "kibana:5601/api/data_views/data_view" -H 'kbn-xsrf: true' -H 'Content-Type: application/json' --user elastic:memude  -d'
{
  "data_view": {
     "title": "adminer",
     "name": "adminer"
  }
}
'

curl --fail -X POST "kibana:5601/api/data_views/data_view" -H 'kbn-xsrf: true' -H 'Content-Type: application/json' --user elastic:memude  -d'
{
  "data_view": {
     "title": "elasticsearch",
     "name": "elasticsearch"
  }
}
'