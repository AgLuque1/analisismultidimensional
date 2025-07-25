#!/bin/bash
mkdir -p /data/db

mongod --logpath /var/log/mongod.log --logappend --bind_ip_all &
sleep 5

# Importamos datos a mongo
mongoimport --db EjemploVentas --collection meta --file /data/mongo-init/meta.json --jsonArray
mongoimport --db EjemploVentas --collection data --file /data/mongo-init/data.json --jsonArray
mongoimport --db MetaInformation --collection data --file /data/mongo-init/metainformation_data.json --jsonArray

# Aplicamos migraciones de Django
python bigdatamed-main/manage.py makemigrations dashboard --noinput
python bigdatamed-main/manage.py migrate --noinput

echo "Migraciones hechas"
echo "Recopilando archivos estáticos"
python bigdatamed-main/manage.py collectstatic --noinput

# Creamos superusuario si no existe
python bigdatamed-main/manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "admin@example.com", "adminpass")
EOF



# Lanzamos bigdatamed Django en background
python bigdatamed-main/manage.py runserver 0.0.0.0:8000 &

# Lanzamos API_CLOUDS
cd /bigdatamed/API_CLOUDS
flask run --host 0.0.0.0 --port 5000
