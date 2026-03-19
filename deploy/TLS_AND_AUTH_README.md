Production deployment notes

1) TLS via Nginx + Certbot

- Install nginx and certbot on your server.
- Place the example site config `nginx_gm_example.conf` in `/etc/nginx/sites-available/` and symlink to `sites-enabled`.
- Update `server_name` with your domain and reload nginx.
- Obtain certificates with Certbot and configure the nginx site to listen on 443.

Example commands:

```bash
sudo cp deploy/nginx_gm_example.conf /etc/nginx/sites-available/game_module
sudo ln -s /etc/nginx/sites-available/game_module /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d your-domain.example.com
```

2) API key & firewall

- Set the environment variable `GAME_MODULE_API_KEY` to a strong secret on the server.
- Ensure the FastAPI instance binds to localhost only (127.0.0.1) and let nginx proxy from public interface. This prevents direct external access.

3) Running the server (systemd)

Create a systemd service, for example `/etc/systemd/system/game_module.service`:

```
[Unit]
Description=Game Module API
After=network.target

[Service]
User=gameuser
Group=gameuser
WorkingDirectory=/path/to/your/project
Environment="GAME_MODULE_API_KEY=your-secret"
Environment="GM_MAX_REQUEST_SIZE=4194304"
ExecStart=/path/to/venv/bin/uvicorn game_module.http_api:app --host 127.0.0.1 --port 8000 --workers 2
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now game_module
```

4) TLS alternatives

- You can also run `uvicorn` directly with TLS, but using nginx as a reverse proxy is recommended for stability and easier certificate management.

5) Monitoring and limits

- Nginx `client_max_body_size` and the ASGI `BodySizeLimiter` protect your app from large uploads.
- The `GM_SIM_TIMEOUT` environment variable sets a per-simulation timeout to prevent long-running tasks from blocking the server.

6) Security reminder

- Keep your system updated and restrict access to the server. Rotate API keys periodically. Consider using mTLS or OAuth for stronger security if needed.
