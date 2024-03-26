# NetBox charm architecture

The NetBox charm initial version has been generated with the 
help of the paas-app-charmer project. The paas-app-charmer project provides many
of the functionalities needed by this charm like:
- PostgreSQL integration
- Django migrations
- Ingress integration
- COS (Prometheus metrics and Loki logs for gunicorn).

For the static assets, gunicorn is used with the help of the WhiteNoiseMiddleware.

There is only one container for each unit of NetBox, that runs the following
services managed by Pebble:
- django. Runs gunicorn.
- cron. Cron service that runs management commands for housekeeping and syncdatasource.
- statsd_exporter. To expose gunicorn metrics.

Besides the integrations provided directly by the paas-app-charmer toolchain, the next
integrations are implemented in NetBox:
- SAML integration.
- S3 integration.

Currently Redis is configured using environment variables. This will be updated
to a Redis integration.

The NetBox charm is designed for a fully high availability (HA) environment, and many
instances can be run for it. See [Configure Scripts and Reports for HA](../how-to/configure-scripts-reports.md)
for the requirements to use scripts and reports in this HA configuration.
