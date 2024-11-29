<!-- This tutorial should be updated in the src-docs directory. -->

# Deploy the NetBox charm for the first time


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
- Juju 3 installed and bootstrapped to a MicroK8s controller. You can accomplish this process by using a Multipass VM as outlined in this guide: [Set up / Tear down your test environment](https://juju.is/docs/juju/set-up--tear-down-your-test-environment)
- Juju controller that can create a model of type kubernetes.
- Read/write access to a S3 compatible server with a bucket created.
- Configuration compatible with the traefik-k8s charms. In the case of MicroK8S this can be achieved with the metallb addon.

For more information about how to install Juju, see [Get started with Juju](https://juju.is/docs/olm/get-started-with-juju).


## Set up a Tutorial Model

To manage resources effectively and to separate this tutorial's workload from
your usual work, we create a new model using the following command.

```{literalinclude} code/getting-started/task.yaml
:language: bash
:start-after: [docs:juju-add-model]
:end-before: [docs:juju-add-model-end]
:dedent: 2
```

## Deploy NetBox

Deploy the NetBox charm, with all its mandatory requirements (PostgreSQL, Redis and S3)
and with the ingress.

### Deploy the NetBox charm

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


```{literalinclude} code/getting-started/task.yaml
:language: bash
:start-after: [docs:netbox-config-allowed-hosts]
:end-before: [docs:netbox-config-allowed-hosts-end]
:dedent: 2
```

### Deploy the Redis charm

NetBox requires Redis to work. You can deploy Redis with redis-k8s:
```{literalinclude} code/getting-started/task.yaml
:language: bash
:start-after: [docs:juju-deploy-redis]
:end-before: [docs:juju-deploy-redis-end]
:dedent: 2
```

Integrate redis-k8s with NetBox:
```{literalinclude} code/getting-started/task.yaml
:language: bash
:start-after: [docs:juju-integrate-redis-netbox]
:end-before: [docs:juju-integrate-redis-netbox-end]
:dedent: 2
```

### Deploy the PostgreSQL charm

NetBox requires PostgreSQL to work. Deploy PostgreSQL and integrate:
```{literalinclude} code/getting-started/task.yaml
:language: bash
:start-after: [docs:juju-netbox-postgresql]
:end-before: [docs:juju-netbox-postgresql-end]
:dedent: 2
```

### Deploy the s3-integrator charm

NetBox requires an S3 integration for the uploaded files. This is because
the NetBox charm is designed to work in a high availability (HA) configuration.
This allows uploaded images to be placed on an S3 compatible server instead of
the local filesystem.

Deploy the s3-integrator charm:
```{literalinclude} code/getting-started/task.yaml
:language: bash
:start-after: [docs:juju-deploy-s3]
:end-before: [docs:juju-deploy-s3-end]
:dedent: 2
```

Configure the s3-integrator charm with your S3 information, wait for the charm to update and provide the credentials:
```{literalinclude} code/getting-started/task.yaml
:language: bash
:start-after: [docs:juju-config-s3]
:end-before: [docs:juju-config-s3-end]
:dedent: 2
```

Once the s3-integrator charm has been deployed, integrate the charm with NetBox:
```{literalinclude} code/getting-started/task.yaml
:language: bash
:start-after: [docs:juju-netbox-s3]
:end-before: [docs:juju-netbox-s3-end]
:dedent: 2
```

See the [s3-integrator Charmhub page](https://charmhub.io/s3-integrator) for more information.

### Deploy the traefik-k8s charm

You need to enable MetalLb if using MicroK8s. See the [traefik-k8s charmhub page](https://charmhub.io/traefik-k8s) for more information.

With the next example, you can configure Traefik using path mode routing:
```{literalinclude} code/getting-started/task.yaml
:language: bash
:start-after: [docs:traefik]
:end-before: [docs:traefik-end]
:dedent: 2
```

If the host `netbox_hostname` can be resolved to the correct IP (the load balancer IP),
you should be able to browse NetBox in the URL http://netbox_hostname/netbox-tutorial-netbox

You can check the proxied endpoints with the command:
```{literalinclude} code/getting-started/task.yaml
:language: bash
:start-after: [docs:traefik-show-endpoints]
:end-at: [docs:traefik-show-endpoints-end]
:dedent: 2
```

## Create a super user
To be able to log in to NetBox, you can create a super user with the next command:
```{literalinclude} code/getting-started/task.yaml
:language: bash
:start-after: [docs:netbox-create-superuser]
:end-before: [docs:netbox-create-superuser-end]
:dedent: 2
```

Congratulations, With the username created and the password provided in the response, 
you have now full access to your own NetBox!

# Clean up the Environment

Well done! You've successfully completed the NetBox tutorial. To remove the
model environment you created during this tutorial, use the following command.

```{literalinclude} code/getting-started/task.yaml
:language: bash
:start-after: [docs:juju-destroy-model]
:end-before: [docs:juju-destroy-model-end]
:dedent: 2
```
