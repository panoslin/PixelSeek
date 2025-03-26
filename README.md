# For development:
```bash
docker compose --env-file .env up -d
```

# For production:
```bash
docker compose --env-file .env.prod up -d
```

# Down
```bash
# Stop containers, remove images, and remove volumes
docker compose down --rmi all -v
```