Desarrollo:
# docker-compose.override.yml para desarrollo
services:
  proyectos_app:
    environment:
      - FLASK_ENV=development
      - FLASK_DEBUG=1
    volumes:
      - .:/app
    ports:
      - "5001:5000"

## ------------------------------------------------------------------- ##
## ------------------------------------------------------------------- ##

Producción:
# docker-compose.prod.yml para producción
services:
  proyectos_app:
    environment:
      - FLASK_ENV=production
    deploy:
      resources:
        limits:
          cpus: '0.50'
          memory: 512M
    restart: unless-stopped