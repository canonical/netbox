# Configure scripts and reports for high availability

NetBox charm is designed with high availability (HA) in mind. As there is no support
for a shared filesystem, this implies that reports and scripts should not be uploaded as file uploads,
as they will not work correctly with multiple instances and there is risk of data loss.

To use scripts and reports, it is necessary to configure a Data Source, this can be of type 
"Git" or "Amazon S3". The git repository https://github.com/netbox-community/customizations.git is
a good source of examples of both scripts and reports.

For S3 data sources, if the S3 server used is a compatible S3 server, the juju configuration
option `aws_endpoint_url` should be set to the url of the S3 server, as NetBox by default only
allows using Amazon S3. This option limit the S3 compatible servers to just one possible 
S3 server. For example, if you use minio in the url `https://minio.example.com`, you
should run `juju config netbox aws_endpoint_url=https://minio.example.com`.

Once a data source for "Git" or "Amazon S3" is configured (menu Operations -> Data Sources),
it should be synced (blue button in the top right of the data source screen).

Once a data source is created and synced, scripts and reports can be created from the 
data source (menu Customization -> reports & scripts). For that, the file in the data
source should be selected, and the checkbox "Auto sync enabled" should be clicked. 

After a few minutes, the script or report will be synchronised over all instances of NetBox and
will be usable.


See this video for more information [NetBox Custom Scripts and Reports, plus Remote Data Sources
](https://www.youtube.com/watch?v=jxsFwyMk18k).