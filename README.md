# APPECK Local

Experimental local Home Assistant integration for APPECK/Tuya permanent outdoor lights.

This project is based on protocol reverse engineering performed against an APPECK Permanent Outdoor Lights Pro controller using Tuya protocol 3.5, TinyTuya, and LocalTuya.

> [!WARNING]
> This repository is an early development scaffold. It has not yet been validated against a production Home Assistant installation. Keep the Smart Life application available as a recovery path and do not expose device IDs or local keys in issues or logs.

## Current protocol knowledge

| DP | Meaning |
|---:|---|
| 20 | Power |
| 21 | Mode (`colour`, `scene`) |
| 22 | Brightness |
| 23 | Scene speed / color temperature depending on mode |
| 24 | Whole-string HSV payload |
| 47 | Maximum bulb count |
| 51 | Built-in scene payload |
| 53 | Configured bulb count |
| 61 | Raw per-pixel command channel |
| 104 | Custom scene slot selector |

Confirmed DP61 single-pixel packets:

```text
Enable/apply HSV:
00 01 [COUNT:2] 01 [HUE:2] [SAT:2] [VAL:2] 81 [PIXEL:1]

Disable:
00 01 [COUNT:2] 02 00 00 00 00 00 00 81 [PIXEL:1]
```

For the original test installation, pixels **49-53** are physically located above the front door.

## Planned v0.1 capabilities

- UI configuration for host, device ID, local key, protocol version, and bulb count
- Local power control
- Whole-string brightness and HSV control
- Built-in scene payload support
- Per-pixel HSV and off commands through `appeck_local.set_pixels`
- Multiple controller config entries

## Installation for development

Copy `custom_components/appeck_local` into the Home Assistant configuration directory:

```text
/config/custom_components/appeck_local
```

Restart Home Assistant, then add **APPECK Local** from **Settings → Devices & services → Add integration**.

The repository can also be added to HACS as a custom integration repository once the first working release is published.

## Example pixel action

After setup, the intended service call is:

```yaml
action: appeck_local.set_pixels
target:
  entity_id: light.appeck_permanent_lights
data:
  pixels: [49, 50, 51, 52, 53]
  hue: 45
  saturation: 1000
  value: 1000
```

Turn those pixels off:

```yaml
action: appeck_local.set_pixels
target:
  entity_id: light.appeck_permanent_lights
data:
  pixels: [49, 50, 51, 52, 53]
  state: "off"
```

## Security

Never commit:

- Tuya device IDs
- Local keys
- Controller IP addresses from private installations
- `devices.json`
- Packet captures containing credentials

## Related projects

- [TinyTuya](https://github.com/jasonacox/tinytuya)
- [LocalTuya](https://github.com/rospogrigio/localtuya)
- [Home Assistant](https://www.home-assistant.io/)
- [HACS](https://www.hacs.xyz/)

## Status

The protocol encoder and Home Assistant structure are roughed in. Connection handling, state synchronization, config-flow validation, and real-device testing remain before the first usable release.

## License

MIT