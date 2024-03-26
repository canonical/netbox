# How to contribute

## Overview

This document explains the processes and practices recommended for contributing
enhancements to the NetBox operator.

- Generally, before developing enhancements to this charm, you should consider
[opening an issue](https://github.com/canonical/netbox/issues)
explaining your use case.
- If you would like to chat with us about your use-cases or proposed
implementation, you can reach us at [Canonical Mattermost public channel](https://chat.charmhub.io/charmhub/channels/charm-dev)
or [Discourse](https://discourse.charmhub.io/).
- Familiarising yourself with the [Charmed Operator Framework](https://juju.is/docs/sdk)
library will help you a lot when working on new features or bug fixes.
- All enhancements require review before being merged. Code review typically
examines
  - code quality
  - test coverage
  - user experience for Juju operators of this charm.
- Please help us out in ensuring easy to review branches by rebasing your pull
request branch onto the `main` branch. This also avoids merge commits and
creates a linear Git commit history.
- Please generate src documentation for every commit. See the section below for
more details.

## Developing

The code for this charm can be downloaded as follows:

```
git clone https://github.com/canonical/netbox
```

You can use the environments created by `tox` for development:

```shell
tox --notest -e unit
source .tox/unit/bin/activate
```

### Testing

Note that the [NetBox](../rockcraft.yaml) image needs to be built and pushed to microk8s
for the tests to run. They should be tagged as `localhost:32000/netbox:latest` so that
Kubernetes knows how to pull them from the MicroK8s repository. Note that the MicroK8s 
registry needs to be enabled using `microk8s enable registry`. More details regarding 
the OCI images below. The following commands can then be used to run the tests:

* `tox`: Runs all of the basic checks (`lint`, `unit`, `static`, and `coverage-report`).
* `tox -e fmt`: Runs formatting using `black` and `isort`.
* `tox -e lint`: Runs a range of static code analysis to check the code.
* `tox -e static`: Runs other checks such as `bandit` for security issues.
* `tox -e unit`: Runs the unit tests.
* `tox -e integration`: Runs the integration tests.

### Generating src docs for every commit

Run the following command:

```bash
echo -e "tox -e src-docs\ngit add charm/src-docs\n" >> .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## Build charm

Build the charm in this git repository using:

```shell
pushd charm && charmcraft pack && popd
```
For the integration tests (and also to deploy the charm locally), the netbox
image is required in the microk8s registry. To enable it:

    microk8s enable registry

The following commands import the images in the Docker daemon and push them into
the registry:

    cd [project_dir] && rockcraft pack
    skopeo --insecure-policy copy --dest-tls-verify=false oci-archive:netbox_0.1_amd64.rock docker://localhost:32000/netbox:latest

### Deploy

```bash
# Create a model
juju add-model netbox-dev
# Enable DEBUG logging
juju model-config logging-config="<root>=INFO;unit=DEBUG"
# Deploy the charm (assuming you're on amd64)
juju deploy ./charm/netbox_ubuntu-22.04-amd64.charm \
  --resource django-app-image=localhost:32000/netbox:latest
```

### Configure NetBox

NetBox required a Redis server to work correctly. This can
be set using configuration options, like:

```bash
juju config netbox redis_hostname=<redis_hostname>
```

NetBox is built using Django. It is necessary to set the
allowed hosts for it to work. For development (not recommended
for production environments), you can allow all hosts using
the configuration option `django_allowed_hosts` like:

```bash
juju config django_allowed_hosts='*'
```

The NetBox charm requires a postgresql_client interface to work.
Thanks to Juju, this can be easily configured with:
```bash
juju deploy postgresql-k8s --channel 14/stable --trust
juju wait-for application postgresql-k8s
juju integrate postgresql-k8s netbox
```

## Canonical Contributor Agreement

Canonical welcomes contributions to the NetBox Operator. Please check out our [contributor agreement](https://ubuntu.com/legal/contributors) if you're interested in contributing to the solution.