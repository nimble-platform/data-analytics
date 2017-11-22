# download redis
FROM redis:4.0.2-alpine
#FROM redis:3.2.11-alpine

COPY sysctl.conf /etc/sysctl.conf

CMD ["redis-server", "--appendonly", "yes"]
