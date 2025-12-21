# docker-zyxel-ssh-connector

[![Docker Image](https://img.shields.io/badge/docker-zyxel--ssh--connector-blue.svg)](https://hub.docker.com/r/hellqvio86/zyxel-ssh-connector)
[![Latest Release](https://img.shields.io/github/v/release/hellqvio86/docker-zyxel-ssh-connector)](https://github.com/hellqvio86/docker-zyxel-ssh-connector/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE.md)
[![Build Status](https://img.shields.io/github/actions/workflow/status/hellqvio86/docker-zyxel-ssh-connector/docker-publish.yml?branch=main)](https://github.com/hellqvio86/docker-zyxel-ssh-connector/actions)

Docker container for connecting to legacy Zyxel network equipment over SSH. This container uses Ubuntu 18.04 with older OpenSSH that supports legacy cryptographic algorithms required by older Zyxel switches and routers.

## Why This Container?

Modern SSH clients (OpenSSH 8.8+) have deprecated older algorithms like `ssh-rsa`, `diffie-hellman-group1-sha1`, and legacy ciphers. This makes it impossible to connect to older network equipment. This container provides a compatible SSH client environment.

## Quick Start

### Using Docker/Podman

Pull the latest image:
```bash
docker pull hellqvio/zyxel-ssh-connector:latest
```

Connect directly to your device:
```bash
docker run -it --rm --net=host hellqvio/zyxel-ssh-connector:latest ssh admin@192.168.1.1
```

Or with Podman:
```bash
podman run -it --rm --net=host hellqvio/zyxel-ssh-connector:latest ssh admin@192.168.1.1
```

### Using the Makefile (for development)

Clone and build locally:
```bash
git clone https://github.com/hellqvio86/docker-zyxel-ssh-connector.git
cd docker-zyxel-ssh-connector
make build
```

Connect to your device:
```bash
make connect host=192.168.1.1
make connect host=switch.local user=root
```

Run interactive bash shell:
```bash
make run
# Then inside: ssh admin@192.168.1.1
```

## Makefile Commands

| Command | Description | Example |
|---------|-------------|---------|
| `make build` | Build the container locally | `make build` |
| `make connect` | Connect to device (requires `host=`) | `make connect host=192.168.1.1` |
| `make connect` | Connect with custom user | `make connect host=192.168.1.1 user=root` |
| `make run` | Start interactive bash shell | `make run` |
| `make clean` | Remove local container image | `make clean` |

## Supported Devices

This container should work with any legacy network equipment requiring older SSH algorithms, including:

- Zyxel switches (GS series, XGS series)
- Zyxel routers and firewalls
- Other network equipment with OpenSSH 6.x or older

## Version Tags

- `latest` - Latest stable release from main branch
- `1.0.0` - Specific version releases
- `1.0` - Latest patch version of 1.0.x
- `1` - Latest minor version of 1.x.x

## Releases

### Creating a New Release

Maintainers can create a new release by tagging a commit:

```bash
# Ensure you're on main and up to date
git checkout main
git pull

# Create and push a version tag
git tag v1.0.0
git push origin v1.0.0
```

This will automatically:
1. Trigger the GitHub Actions workflow
2. Build the Docker image
3. Push to Docker Hub with appropriate version tags
4. Create a GitHub release

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR** version: Incompatible changes (e.g., base image change)
- **MINOR** version: New features, backwards compatible
- **PATCH** version: Bug fixes, backwards compatible

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Troubleshooting

### Connection Issues

If you still can't connect:
1. Verify your device's IP/hostname is correct
2. Check if the device's SSH port is 22 (default)
3. Try connecting with verbose output: `ssh -vvv admin@device-ip`

### Network Access

The container uses `--net=host` to access your local network directly. If you're using a different network configuration, you may need to adjust the network settings.

## Security Note

This container intentionally uses legacy SSH algorithms to connect to older equipment. Only use this for connecting to trusted devices on secure networks. Consider upgrading your network equipment if possible.