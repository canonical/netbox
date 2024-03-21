A Juju charm deploying and managing
[NetBox](https://github.com/netbox-community/netbox/) on
Kubernetes. NetBox is the go-to solution for modeling and documenting network
infrastructure for thousands of organizations worldwide.

This charm simplifies initial deployment and "day N" operations of
NetBox on Kubernetes, such as integration with SSO, access to S3 for
file storage and more. It allows for deployment on many
different Kubernetes platforms, from [MicroK8s](https://microk8s.io)
to [Charmed Kubernetes](https://ubuntu.com/kubernetes) to public cloud
Kubernetes offerings.

As such, the charm makes it easy for those looking to take control of
their own NetBox server whilst keeping operations simple, and gives them
the freedom to deploy on the Kubernetes platform of their choice.

For DevOps or SRE teams this charm will make operating NetBox simple
and straightforward through Juju's clean interface. It will allow easy
deployment into multiple environments for testing of changes.


## Limitations

TODO Talk about limitations with scripts/reports and redirect to the
how-to for scripts/reports.

## Other resources

- [Netbox upstream repository](https://github.com/netbox-community/netbox)
* [Get support](https://discourse.charmhub.io/)
* [Join our online chat](https://matrix.to/#/#charmhub-charmdev:ubuntu.com)
* [Contribute](https://charmhub.io/netbox/docs/contributing)
* [Getting Started](https://charmhub.io/netbox/docs/getting-started)
* [Juju SDK documentation](https://juju.is/docs/sdk) for more information about developing and improving charms.

## Contributing to this documentation

Documentation is an important part of this project, and we take the
same open-source approach to the documentation as the code. As such,
we welcome community contributions, suggestions and constructive
feedback on our documentation. Our documentation is hosted on the
[Charmhub forum](https://discourse.charmhub.io/) to enable easy
collaboration. Please use the “Help us improve this documentation”
links on each documentation page to either directly change something
you see that’s wrong, or ask a question, or make a suggestion about a
potential change via the comments section.

If there’s a particular area of documentation that you’d like to see that’s
missing, please [file a bug](https://github.com/canonical/netbox/issues).

# Contents

1. [Tutorial](tutorial)
  1. [Getting Started](tutorial/getting-started.md)
1. [How to](how-to)
  1. [Contribute](how-to/contribute.md)
  2. [Configure SAML](how-to/configure-saml.md)
  3. [Configure Data Sources for HA](how-to/configure-datasources.md)
1. [Reference](reference)
  1. [Actions](reference/actions.md)
  2. [Integrations](reference/integrations.md)
1. [Explanation](explanation)
  1. [Charm architecture](explanation/charm-architecture.md)
