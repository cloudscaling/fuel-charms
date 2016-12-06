# Overview

Fuel emulator for ScaleIO plugin development.
It emulates deployemnt of Fuel plugin without real Fuel deployment.
This is fully internal project that helps to quick check of Fuel plugin. These checks are not guarantee that fuel plugin is ready to release. Full Fuel deployment checks is needed in any case.

First, you need to deploy master node with config:

```
echo "fuel-master:
  branch-name:  $branch
  device-paths: $device_paths" >/tmp/config.yaml
juju-deploy --repository fuel-charms local:trusty/fuel-master --to $mch --config /tmp/config.yaml
```

Then, you need to deploy nodes, relate them to master, and set roles (set of - primary-controller, controller, scaleio, compute, cinder):

```
echo "$name:
  branch-name:  $branch
  storage-iface: $storage_iface" >/tmp/config.yaml
juju-deploy --repository fuel-charms local:trusty/fuel-node $name --to $mch --config /tmp/config.yaml
juju-add-relation fuel-master $name
juju-set $name roles="${roles}"
```

And start deployment with
```
juju-set fuel-master deploy=1
```

After some time all services should be active.