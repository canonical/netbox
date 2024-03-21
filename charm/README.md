[![CharmHub Badge](https://charmhub.io/netbox/badge.svg)](https://charmhub.io/netbox)
[![Publish to edge](https://github.com/canonical/netbox/actions/workflows/publish_charm.yaml/badge.svg)](https://github.com/canonical/netbox/actions/workflows/publish_charm.yaml)
[![Promote charm](https://github.com/canonical/netbox/actions/workflows/promote_charm.yaml/badge.svg)](https://github.com/canonical/netbox/actions/workflows/promote_charm.yaml)
[![Discourse Status](https://img.shields.io/discourse/status?server=https%3A%2F%2Fdiscourse.charmhub.io&style=flat&label=CharmHub%20Discourse)](https://discourse.charmhub.io)


<!--
Avoid using this README file for information that is maintained or published elsewhere, e.g.:

* metadata.yaml > published on Charmhub
* documentation > published on (or linked to from) Charmhub
* detailed contribution guide > documentation or CONTRIBUTING.md

Use links instead.
-->

# NetBox charm operator

A Juju charm deploying and managing NetBox on Kubernetes.

NetBox is the go-to solution for modeling and documenting network
infrastructure for thousands of organizations worldwide. As a
successor to legacy IPAM and DCIM applications, NetBox provides a
cohesive, extensive, and accessible data model for all things
networked.


This charm simplifies initial deployment and "day N" operations of
NetBox on Kubernetes, such as integration with SSO, access to S3 for
file storage and more. It allows for deployment on many
different Kubernetes platforms, from MicroK8s to Charmed Kubernetes to
public cloud Kubernetes offerings.

As such, the charm makes it easy for those looking to take control of
their own NetBox server whilst keeping operations simple, and gives them
the freedom to deploy on the Kubernetes platform of their choice.

For DevOps or SRE teams this charm will make operating NetBox simple
and straightforward through Juju's clean interface. It will allow easy
deployment into multiple environments for testing of changes.

## Other resources

<!-- If your charm is documented somewhere else other than Charmhub, provide a link separately. -->

- [Netbox upstream repository](https://github.com/netbox-community/netbox)

* [Get support](https://discourse.charmhub.io/)

* [Join our online chat](https://matrix.to/#/#charmhub-charmdev:ubuntu.com)

* [Contribute](https://charmhub.io/netbox/docs/contributing)

* [Getting Started](https://charmhub.io/netbox/docs/getting-started)

- See the [Juju SDK documentation](https://juju.is/docs/sdk) for more information about developing and improving charms.

---
