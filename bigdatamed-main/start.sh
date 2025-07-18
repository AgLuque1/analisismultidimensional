#!/bin/sh

app_supervisor=bigdatamed

# python3 manage.py createsuperuser

/usr/bin/supervisord

supervisorctl restart $app_supervisor

service nginx start