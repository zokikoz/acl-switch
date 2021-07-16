English | [Русский](./README-ru.md)

# acl-switch
Switches between two ACL on the selected interface of Cisco device.

## Usage
At startup, the script reads the configuration from file ```config.yaml```. If the file is not found or the parameters are missing, you will be prompted to enter them.

To enable / disable acl, you can use the value ```'not set'``` for one of the ACLs.

### Options
```
acl.py [-v]
```

```-v``` - Verbose mode.
