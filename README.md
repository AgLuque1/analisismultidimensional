# Instalación del entorno

Para instalar y levantar el entorno del proyecto, es necesario tener previamente instalados **docker** y **docker-compose** en el sistema. 
Si no están instalados, se instalan de la siguiente forma:
`sudo apt install docker`
`sudo apt install docker-compose`

Se recomienda ejecutar antes `sudo apt-get update` para actualizar los paquetes.

Tener en cuenta que hay que tener el servicio de docker levantado (`sudo systemctl start docker`) Una vez cumplido este requisito, se debe clonar el repositorio con `git clone`, acceder al directorio del proyecto clonado, y ejecutar el siguiente comando:

```bash
sudo docker-compose up --build



