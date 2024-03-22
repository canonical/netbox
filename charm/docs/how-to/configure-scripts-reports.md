# Configure scripts and reports for high availability

For HA. can be "Git" or "Amazon S3".



With an admin user (can be created with `juju run netbox/0 create-super-user username=admin2 email=a@example.com`)
navigate to Operations -> Data Sources. Create one Git or "Amazon S3" one.


If s3 is not in AWS, the endpoint should be set like (this is limiting as there can only be one):
```
juju config netbox aws_endpoint_url=<aws_endpoint_url>
```

if using git, https://github.com/netbox-community/customizations.git is a good source fo examples...

In the data source, click on "Sync" (blue top right button). It should get to status "completed" and 
list the files found in the data source.



In Customization -> REPORTS & SCRIPTS.

Add a script or a report. The script or report has to be created from a previous Data Source.
"Auto sync enabled" should be clicked.

If there is more than one instance of NetBox, only after 5 minutes the script/report will work correctly.


