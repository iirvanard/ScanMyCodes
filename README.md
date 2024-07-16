
## Deployment

start redis manually
```bash
  redis-server
```


run postgresql
```bash
  - 
```

install python packages
```bash
  pip install -r requirements.txt
```
start celery worker
```bash
  celery -A app:celery worker -l info
```

run debug locally 
```bash
  flask run --debug
```

## Build css using npx
to build css 
```bash
  npx tailwindcss -i ./static/src/main.css -o ./static/css/main.css --watch 
```

## Docker
to build docker image 

```bash
docker compose build --no-cache
```
to run docker container 

```bash
docker compose -f ./production.yml up -d
```

