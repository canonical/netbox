<!-- This tutorial should be updated in the src-docs directory. -->

# Deploy the NetBox charm for the first time

## What you’ll do

- Deploy the NetBox charm.
- Integrate with Redis using the redis-k8s charm.
- Integrate with the PostgreSQL K8s charm.
- Integrate with S3 for storage.
- Expose the NetBox charm with Traefik k8s.
- Create a super user.

Through the process, you’ll verify the workload state, and log in to
your NetBox instance.

## Requirements

- Juju 3 installed and bootstrapped to a MicroK8s controller. You can accomplish this process by using a Multipass VM as outlined in this guide: [Set up / Tear down your test environment](https://juju.is/docs/juju/set-up--tear-down-your-test-environment)
- Juju controller that can create a model of type kubernetes.
- Read/write access to a S3 compatible server with a bucket created.
- Configuration compatible with the traefik-k8s charms. In the case of MicroK8S this can be achieved with the metallb addon.

For more information about how to install Juju, see [Get started with Juju](https://juju.is/docs/olm/get-started-with-juju).

## Set up a Tutorial Model

To manage resources effectively and to separate this tutorial’s workload from
your usual work, we create a new model using the following command.

```bash
juju add-model netbox-tutorial
```

## Deploy NetBox

Deploy the NetBox charm, with all its mandatory requirements (PostgreSQL, Redis and S3)
and with the ingress.

### Deploy the NetBox charm

```bash
juju deploy netbox
```

At this point NetBox should be blocked as there is no S3 integration for
storage, Redis or PostgreSQL.

Set the allowed hosts. In this example every host is allowed. For a production environment
only the used hosts should be allowed.

```bash
juju config netbox django-allowed-hosts='*'
```

### Deploy the Redis charm

NetBox requires Redis to work. You can deploy Redis with redis-k8s:

```bash
juju deploy redis-k8s --channel=latest/edge
```

Integrate redis-k8s with NetBox:

```bash
juju integrate redis-k8s netbox
```

### Deploy the PostgreSQL charm

NetBox requires PostgreSQL to work. Deploy PostgreSQL and integrate:

```bash
juju deploy postgresql-k8s --channel 14/stable --trust
juju integrate postgresql-k8s netbox
```

### Deploy the s3-integrator charm

NetBox requires an S3 integration for the uploaded files. This is because
the NetBox charm is designed to work in a high availability (HA) configuration.
This allows uploaded images to be placed on an S3 compatible server instead of
the local filesystem.

Deploy the s3-integrator charm:

```bash
juju deploy s3-integrator --channel edge
```

Configure the s3-integrator charm with your S3 information, wait for the charm to update and provide the credentials:

```bash
juju config s3-integrator endpoint="${AWS_ENDPOINT_URL}" bucket="${AWS_BUCKET}" path=/ region="${AWS_REGION}" s3-uri-style="${AWS_URI_STYLE}"
juju wait-for application s3-integrator --query='name=="s3-integrator" && (status=="active" || status=="blocked")'
juju run s3-integrator/leader sync-s3-credentials access-key="${AWS_ACCESS_KEY_ID}" secret-key="${AWS_SECRET_ACCESS_KEY}"
```

Once the s3-integrator charm has been deployed, integrate the charm with NetBox:

```bash
juju integrate s3-integrator netbox
```

See the [s3-integrator Charmhub page](https://charmhub.io/s3-integrator) for more information.

### Deploy the traefik-k8s charm

You need to enable MetalLb if using MicroK8s. See the [traefik-k8s charmhub page](https://charmhub.io/traefik-k8s) for more information.

With the next example, you can configure Traefik using path mode routing:

```bash
juju deploy traefik-k8s --channel edge --trust
juju config traefik-k8s external_hostname=${EXTERNAL_HOSTNAME}
juju config traefik-k8s routing_mode=${ROUTING_MODE}
juju integrate traefik-k8s netbox
```

If the host `netbox_hostname` can be resolved to the correct IP (the load balancer IP),
you should be able to browse NetBox in the URL http://netbox_hostname/netbox-tutorial-netbox

You can check the proxied endpoints with the command:

```bash
juju run traefik-k8s/0 show-proxied-endpoints --format=yaml
# [docs:traefik-show-endpoints-end]
```

## Create a super user

To be able to log in to NetBox, you can create a super user with the next command:

```bash
juju run netbox/0 create-superuser username=admin email=admin@example.com
```

Congratulations! Your username has been created, and the password provided in the response
gives you full access to your NetBox. Simply visit http://netbox_hostname/netbox-tutorial-netbox
and log in using your username and password.

# Clean up the Environment

Well done! You’ve successfully completed the NetBox tutorial. To remove the
model environment you created during this tutorial, use the following command.

```bash
juju destroy-model netbox-tutorial
```
