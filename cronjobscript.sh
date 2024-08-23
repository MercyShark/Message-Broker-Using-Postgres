# host.docker.internal is a special DNS name which resolves to the internal IP address used by the host. If ur postgres is running on the host machine, then you can use host.docker.internal to connect to the host machine from the container.
export DB_HOST="host.docker.internal" 
export DB_PORT="5432"
export DB_NAME="message_broker"
export DB_USER="<your-username>"
export DB_PASSWORD="<your-password>"
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "
UPDATE message_broker
SET picked_at = NULL
WHERE deleted_at IS NULL
  AND picked_at IS NOT NULL
  AND picked_at < NOW() - INTERVAL '10 minutes';
"




