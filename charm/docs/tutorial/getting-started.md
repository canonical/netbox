# Getting Started

## What you’ll do
- Deploy the NetBox charm.
- Use an external Redis server
- Integrate with the PostgreSQL K8s charm.
- Integrate with S3 for storage.
- Expose NetBox charm with Traefik k8s.
- Create a super user.

Through the process, you'll verify the workload state, and log in to
your NetBox instance.

## Requirements
- Juju 3 installed.
- Juju controller that can create a model of type kubernetes.
- Read/write access to a S3 compatible server with a bucket created.

For more information about how to install Juju, see [Get started with Juju](https://juju.is/docs/olm/get-started-with-juju).


## Setting up a Tutorial Model

To manage resources effectively and to separate this tutorial's workload from
your usual work, we recommend creating a new model using the following command.

```
juju add-model netbox-tutorial
```

## Deploy the NetBox charm

Deploy NetBox charm, with all requirements (PostgreSQL, redis and S3).

### Deploy the charms:
```
juju deploy netbox
```

At this point netbox should be blocked as there it no S3 integration for
storage, Redis nor PostgreSQL.

Set the allowed hosts. In this example every host is allowed. For a production environment
only the used hosts should be allowed.
```
juju config nebox django_allowed_hosts='*'
```


### Redis

NetBox requires Redis to work. Currently you can configure Redis with 
configuration options (to be changed to an integration).

Deploy redis-k8s:
```
juju deploy redis-k8s --channel=latest/edge
```

To get the admin_password:
```
juju run redis-k8s/0 get-initial-admin-password
```

Configure NetBox:
```
juju config netbox redis_hostname=redis-k8s-0.redis-k8s-endpoints redis_password=<admin_password>
```


### Deploy Postgresql

juju deploy postgresql-k8s --channel 14/stable --trust
juju integrate postgresql-k8s netbox


### Deploy s3-integrator
juju deploy s3-integrator --channel edge
juju config s3-integrator endpoint="<aws_endpoing_url>" bucket=<bucket_name> path=<path_in_bucket> region=<region> s3-uri-style=<path_or_host>
juju wait-for application s3-integrator --query='name=="s3-integrator" && (status=="active" || status=="blocked")'
juju run s3-integrator/leader sync-s3-credentials access-key=${AWS_ACCESS_KEY_ID} secret-key=${AWS_SECRET_ACCESS_KEY}
juju integrate s3-integrator netbox


### Deploy traefik-k8s 

You need to enable MetalLb if using MicroK8s. See for more information: https://charmhub.io/traefik-k8s

Example for path mode:

juju deploy traefik-k8s --channel edge --trust
juju config traefik-k8s external_hostname=<netbox_hostname>
juju config traefik-k8s routing_mode=path
juju integrate traefik-k8s netbox
juju run traefik-k8s/0 show-proxied-endpoints --format=yaml


If the host  netbox_hostname can be resolved to the correct IP (the load balancer IP), 
you should be able to browse NetBox in the url

http://netbox_hostname/netbox-tutorial-netbox
(run `juju run traefik-k8s/0 show-proxied-endpoints --format=yaml` to check traefik proxied endpoint)

To create a superuser:
juju run netbox/0 create-super-user username=<admin_username> email=<admin_email>


