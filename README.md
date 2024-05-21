# ft_transcendence

├── django
│   ├── app
│   │   ├── accounts
│   │   ├── chat
│   │   ├── ft_transcendence
│   │   ├── manage.py
│   │   ├── pong
│   │   ├── relations
│   │   ├── requirements.txt
│   │   ├── static
│   │   ├── templates
│   │   └── user
│   ├── Dockerfile
│   └── tools
│       ├── script.sh
│       └── wait-for-it.sh
├── docker-compose.yml
├── Makefile
├── README.md
└── requirements
    ├── elk
    │   ├── elksetup.sh
    │   ├── filebeat.yml
    │   ├── kibanasetup.sh
    │   └── logstash.conf
    ├── grafana
    │   ├── dashboard
    │   └── datasource
    ├── locust-tasks
    │   ├── locustfile.py
    │   └── __pycache__
    ├── nginx
    │   ├── dockerfile
    │   ├── nginx.conf
    │   └── tools
    └── prometheus
        ├── alert_rules.yaml
        └── prometheus.yaml