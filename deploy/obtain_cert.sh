#!/usr/bin/env bash
# Obtain TLS cert with Certbot + nginx
set -euo pipefail
DOMAIN=${1:-your-domain.example.com}
SITE_CONF=/etc/nginx/sites-available/game_module
if [ ! -f "$SITE_CONF" ]; then
  echo "please install deploy/nginx_gm_full.conf to $SITE_CONF and update server_name"
  exit 2
fi
sudo ln -sf /etc/nginx/sites-available/game_module /etc/nginx/sites-enabled/game_module
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d "$DOMAIN"
sudo nginx -t && sudo systemctl reload nginx

echo "Obtained certificate for $DOMAIN"
