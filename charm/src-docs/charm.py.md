<!-- markdownlint-disable -->

<a href="../../charm/src/charm.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `charm.py`
Django Charm entrypoint. 

**Global Variables**
---------------
- **CRON_EVERY_5_MINUTES**
- **CRON_AT_MIDNIGHT**


---

## <kbd>class</kbd> `DjangoCharm`
Django Charm service. 

<a href="../../charm/src/charm.py#L35"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `__init__`

```python
__init__(*args: Any) → None
```

Initialize the instance. 



**Args:**
 
 - <b>`args`</b>:  passthrough to CharmBase. 


---

#### <kbd>property</kbd> app

Application that this unit is part of. 

---

#### <kbd>property</kbd> charm_dir

Root directory of the charm as it is running. 

---

#### <kbd>property</kbd> config

A mapping containing the charm's config and current values. 

---

#### <kbd>property</kbd> meta

Metadata of this charm. 

---

#### <kbd>property</kbd> model

Shortcut for more simple access the model. 

---

#### <kbd>property</kbd> unit

Unit that this execution is responsible for. 



---

<a href="../../charm/src/charm.py#L52"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `gen_env`

```python
gen_env() → dict[str, str]
```

Return the environment variables for django scripts. 



**Returns:**
  dict with environment variables. 

---

<a href="../../charm/src/charm.py#L157"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `reconcile`

```python
reconcile() → None
```

Reconcile all services. 

---

<a href="../../charm/src/charm.py#L71"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `s3_env`

```python
s3_env() → dict[str, str]
```

Environment variables for S3 for storage. 

This should disappear/get updated once Django 12 factor supports the S3 integration. 



**Returns:**
  dict with environment variables. 

---

<a href="../../charm/src/charm.py#L87"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `saml_env`

```python
saml_env() → dict[str, str]
```

Environment variables for SAML. 



**Returns:**
  dict with environment variables. 

---

<a href="../../charm/src/charm.py#L206"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `workload`

```python
workload() → Container
```

Get workload container. 

Delete this function when it is in the django 12 factor project. 



**Returns:**
  Workload Container 


---

## <kbd>class</kbd> `S3Parameters`
Configuration for accessing S3 bucket. 



**Attributes:**
 
 - <b>`access_key`</b>:  AWS access key. 
 - <b>`secret_key`</b>:  AWS secret key. 
 - <b>`region`</b>:  The region to connect to the object storage. 
 - <b>`bucket`</b>:  The bucket name. 
 - <b>`endpoint`</b>:  The endpoint used to connect to the object storage. 
 - <b>`path`</b>:  The path inside the bucket to store objects. 
 - <b>`s3_uri_style`</b>:  The S3 protocol specific bucket path lookup type. Can be "path" or "host". 
 - <b>`addressing_style`</b>:  S3 protocol addressing style, can be "path" or "virtual". 


---

#### <kbd>property</kbd> addressing_style

Translates s3_uri_style to AWS addressing_style. 



---

<a href="../../charm/src/charm.py#L313"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `to_env`

```python
to_env() → dict[str, str]
```

Convert to env variables. 



**Returns:**
  dict with environment variables for django storage. 


