# Configure SAML

NetBox charm SAML makes use of the saml-integrator. You can find
more information in [charmhub](https://charmhub.io/saml-integrator).

SAML is configured in NetBox using the library `python-social-core` with the SAMLAuth backend.

To configure it, you need to know the `entidy_id` and `metadata_url` of your IdP provider. 
`entity_id` must be a valir URI. It can be configured with the next commands:
```
juju deploy saml-integrator --channel latest/edge --config entity_id=<idp_entidy_id> --config metadata_url=<idp_metadata_url>
juju integrate saml-integrator netbox
```



For NetBox to work, you may need to customise some of the following configuration options:
 - `saml_sp_entity_id`: SAML SP entity id. This is mandatory, and should be a correct URL.
 - `saml_username`: SAML attribute used for both the social uid and the username (name_id by default).
 - `saml_email`: SAML attribute used for the email (optional).


NetBox configuration options for SAML can be configured like:
```
juju config netbox saml_sp_entity_id=<your_sp_entity_id_url> saml_username=<saml_attribute_for_uid_and_username>
```

