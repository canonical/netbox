# Testing NetBox

We recommend the [Getting Started Tutorial](./getting-started.md) to get familiarised with NetBox in a Juju deployment.

However, if your goal is to test NetBox locally in the easiest
possible way (not recommended for a production environment), then this
is your tutorial.

## Install Multipass

You need to install Multipass. With Multipass you will create a Ubuntu
VMs with NetBox installed.


Multipass can be easily installed in Linux, Windows and macOS. See
https://multipass.run/install for more instructions.

## Launch NetBox with a Multipass instance.


Launch a VM named `netbox` with Multipass, using the cloud init configuration that will installed NetBox. This
process will take about 20 minutes, depending on your computer and internet connection. Run the next command
to install NetBox:
```
multipass launch --cloud-init https://raw.githubusercontent.com/canonical/netbox/main/charm/cloudinit-juju-3.1.yaml --timeout 1800 --name netbox --memory 4G --cpus 3 --disk 30G 22.04
```

After the VM is started and running, you can access Netbox using the URL that you will
get with the next command:
```
multipass exec netbox -- juju run traefik-k8s/0 show-proxied-endpoints --format=yaml
```

You can create an admin user with the next command:
```
multipass exec netbox -- juju run netbox/leader create-superuser username=admin email=netbox@example.com
```

Once you are finished, you can delete the netbox VM with the next command:
```
multipass delete netbox --purge
```

## Troubleshooting
```
multipass exec netbox -- tail -f /var/log/cloud-init-output.log
```