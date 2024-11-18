# start datastream service
docker-compose -f data/docker-compose.yml up &
# start grafana
docker-compose -f grafana/docker-compose.yml up &
# wait until log-net network is created
sleep 5
# start logging service
docker-compose -f logging/docker-compose.yml up