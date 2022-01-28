#/bin/sh

if [ ! -f /etc/nginx/ssl/fullchain.pem ]; then
	openssl req -newkey rsa:2048 -nodes -keyout /etc/nginx/ssl/privkey.pem -x509 -days 365 -out /etc/nginx/ssl/fullchain.pem -subj "/C=US/ST=EXAMPLE/L=EXAMPLE/O=EXAMPLE/OU=/CN=EXAMPLE/emailAddress=example@example.org"
fi


