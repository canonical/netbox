# Getting Started

## What you’ll do
- Deploy the NetBox charm.
- Integrate with Redis using the redis-k8s charm.
- Integrate with the PostgreSQL K8s charm.
- Integrate with S3 for storage.
- Expose the NetBox charm with Traefik k8s.
- Create a super user.

Through the process, you'll verify the workload state, and log in to
your NetBox instance.

## Requirements
- Juju 3 installed.
- Juju controller that can create a model of type kubernetes.
- Read/write access to a S3 compatible server with a bucket created.
- Configuration compatible with the traefik-k8s charms. In the case of MicroK8S this can be achieved with the metallb addon.

For more information about how to install Juju, see [Get started with Juju](https://juju.is/docs/olm/get-started-with-juju).


## Setting up a Tutorial Model

To manage resources effectively and to separate this tutorial's workload from
your usual work, we recommend creating a new model using the following command.

```{literalinclude} code/getting-started/task.yaml
:language: bash
:start-after: [docs:juju-add-model]
:end-before: [docs:juju-add-model-end]
:dedent: 2
```

## Deploy the NetBox charm

Deploy the NetBox charm, with all its mandatory requirements (PostgreSQL, Redis and S3).

### Deploy the charms:

```{literalinclude} code/getting-started/task.yaml
:language: bash
:start-after: [docs:juju-deploy-netbox]
:end-before: [docs:juju-deploy-netbox-end]
:dedent: 2
```

At this point NetBox should be blocked as there is no S3 integration for
storage, Redis or PostgreSQL.

Set the allowed hosts. In this example every host is allowed. For a production environment
only the used hosts should be allowed.

### Deploy the charms:

```{literalinclude} code/getting-started/task.yaml
:language: bash
:start-after: [docs:netbox-config-allowed-hosts]
:end-before: [docs:netbox-config-allowed-hosts-end]
:dedent: 2
```

### Redis

NetBox requires Redis to work. You can deploy Redis with redis-k8s:
```{literalinclude} code/getting-started/task.yaml
:language: bash
:start-after: [docs:juju-deploy-redis]
:end-before: [docs:juju-deploy-redis-end]
:dedent: 2
```

Integrate redis-k8s with NetBox with:
```{literalinclude} code/getting-started/task.yaml
:language: bash
:start-after: [docs:juju-integrate-redis-netbox]
:end-before: [docs:juju-integrate-redis-netbox-end]
:dedent: 2
```

### Deploy PostgreSQL

NetBox requires PostgreSQL to work. Deploy and integrate with:
```{literalinclude} code/getting-started/task.yaml
:language: bash
:start-after: [docs:juju-netbox-postgresql]
:end-before: [docs:juju-netbox-postgresql-end]
:dedent: 2
```

### Deploy s3-integrator

NetBox requires an S3 integration for the uploaded files. This is because
the NetBox charm is designed to work in a high availability (HA) configuration.
This allows uploaded images to be placed on an S3 compatible server instead of
the local filesystem.

You can configure it with:
```{literalinclude} code/getting-started/task.yaml
:language: bash
:start-after: [docs:juju-netbox-s3]
:end-before: [docs:juju-netbox-s3-end]
:dedent: 2
```

See the [s3-integrator charmhub page](https://charmhub.io/s3-integrator) for more information.

### Deploy traefik-k8s 

You need to enable MetalLb if using MicroK8s. See the [traefik-k8s charmhub page](https://charmhub.io/traefik-k8s) for more information.

With the next example, you can configure Traefik using path mode routing:
```{literalinclude} code/getting-started/task.yaml
:language: bash
:start-after: [docs:traefik]
:end-before: [docs:traefik-end]
:dedent: 2
```

If the host `netbox_hostname` can be resolved to the correct IP (the load balancer IP),
you should be able to browse NetBox in the url http://netbox_hostname/netbox-tutorial-netbox

You can check the proxied endpoints with the command:
```{literalinclude} code/getting-started/task.yaml
:language: bash
:start-after: [docs:traefik-show-endpoints]
:end-at: [docs:traefik-show-endpoints-end]
:dedent: 2
```

## Create superuser
To be able to login to NetBox, you can create a super user with the next command:
```{literalinclude} code/getting-started/task.yaml
:language: bash
:start-after: [docs:netbox-create-superuser]
:end-before: [docs:netbox-create-superuser-end]
:dedent: 2
```

Congratulations, With the username created and the password provided in the response, 
you have now full access to your own NetBox!

