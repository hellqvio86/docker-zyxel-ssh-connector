# docker-zyxel-ssh-connector

[![Docker Image](https://img.shields.io/badge/docker-zyxel--ssh--connector-blue.svg)](https://hub.docker.com/r/hellqvio/zyxel-ssh-connector)
[![Docker Image](https://img.shields.io/badge/docker-zyxel--ssh--bash-blue.svg)](https://hub.docker.com/r/hellqvio/zyxel-ssh-bash)
[![Latest Release](https://img.shields.io/github/v/release/hellqvio86/docker-zyxel-ssh-connector)](https://github.com/hellqvio86/docker-zyxel-ssh-connector/releases)
[![zyxel-ssh-connector pulls](https://img.shields.io/docker/pulls/hellqvio/zyxel-ssh-connector.svg?label=zyxel-ssh-connector%20pulls)](https://hub.docker.com/r/hellqvio/zyxel-ssh-connector)
[![zyxel-ssh-bash pulls](https://img.shields.io/docker/pulls/hellqvio/zyxel-ssh-bash.svg?label=zyxel-ssh-bash%20pulls)](https://hub.docker.com/r/hellqvio/zyxel-ssh-bash)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE.md)
[![Python CI](https://github.com/hellqvio86/docker-zyxel-ssh-connector/actions/workflows/python_ci.yml/badge.svg?branch=main)](https://github.com/hellqvio86/docker-zyxel-ssh-connector/actions/workflows/python_ci.yml)
[![Bash CI](https://github.com/hellqvio86/docker-zyxel-ssh-connector/actions/workflows/bash_ci.yml/badge.svg?branch=main)](https://github.com/hellqvio86/docker-zyxel-ssh-connector/actions/workflows/bash_ci.yml)
[![Coverage](coverage.svg)](coverage.svg)
[![mypy](https://img.shields.io/badge/mypy-checked-brightgreen)](https://github.com/python/mypy)
[![python](https://img.shields.io/badge/python-3.14%2B-blue)](https://www.python.org/)

Python CLI tool and Docker container for connecting to legacy Zyxel network equipment over SSH. This tool uses compatible SSH algorithms required by older Zyxel switches and routers.

## Why This Tool?

Modern SSH clients (OpenSSH 8.8+) have deprecated older algorithms like `ssh-rsa`, `diffie-hellman-group1-sha1`, and legacy ciphers. This makes it impossible to connect to older network equipment. This tool provides two solutions:
- **Python CLI**: Direct command-line tool (requires compatible SSH setup)
- **Docker Container**: Includes legacy SSH support (works everywhere)

## Quick Start

### Option 1: Using Pre-built Docker Containers (Recommended)

The fastest way to get started without installing anything or cloning the repo.

```bash
# Get switch version
docker run --rm --net=host hellqvio/zyxel-ssh-connector:latest zyxel-cli -H 192.168.1.1 version

# Start an interactive session
docker run -it --rm --net=host hellqvio/zyxel-ssh-connector:latest zyxel-cli -H 192.168.1.1 interactive

# Or use the minimal bash-only container
docker run -it --rm --net=host hellqvio/zyxel-ssh-bash:latest
```

### Option 2: Local Docker Development

Best for active development or if you need to build the containers locally:

```bash
# Build the runtime container
make build

# Use local build via Makefile
make show-version host=192.168.1.1
make connect host=192.168.1.1
```

### Option 3: Local Python CLI

Best for developers contributing to the code.

```bash
# Set up environment and install
make python-build
make python-install

# Use the CLI directly
uv run zyxel-cli -H 192.168.1.1 version
```

**Note**: The local CLI (Option 3) may require legacy SSH support on your host. If you have connection issues, use the Docker method (Option 1).

## Installation & Setup

### Prerequisites

- Python 3.14+ (for local development)
- [uv](https://github.com/astral-sh/uv) - Python package installer
- Docker or Podman (for containerized usage)

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/docker-zyxel-ssh-connector.git
cd docker-zyxel-ssh-connector

# Set up Python environment
make python-build

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
make python-install

# Run tests to verify setup
make test
```

### Validation

We use `uv` for dependency management and development tasks. Run the project validation (formatting and static typing checks) with:

```bash
make python-validate
```

This runs `isort`, `black`, and `mypy` (via `uv`) to ensure imports, formatting, and types are correct.

Note: `python-validate` assumes development tools are already installed. Run the following once to install dev dependencies before using the validation target:

```bash
make python-install
make python-validate
```

## Usage

### Local CLI Commands

Use these for development and testing (requires legacy SSH support):

```bash
# Show switch information
make cli-version host=192.168.1.1


# Network configuration
make cli-interfaces host=192.168.1.1
make cli-vlans host=192.168.1.1
make cli-config host=192.168.1.1

# MAC address table
make cli-mac-table host=192.168.1.1

# Interactive session
make cli-connect host=192.168.1.1

# Execute custom command
make cli-exec host=192.168.1.1 cmd="show ip interface"

# With authentication
make cli-version host=192.168.1.1 user=admin password=mypass
```

### Docker Commands

Use these for guaranteed compatibility with legacy switches:

```bash
# Build the final runtime image (builds builder first)
make docker-final

# If you want to inspect or rebuild only the builder image:
make docker-build

# Show switch information
make show-version host=192.168.1.1


# Network configuration
make show-interfaces host=192.168.1.1
make show-vlans host=192.168.1.1
make show-config host=192.168.1.1

# MAC address table
make show-mac-table host=192.168.1.1

# Interactive session
make connect host=192.168.1.1

# Run bash in container
make run
```

### Direct Python Usage

If you have the virtual environment activated:

```bash
# Show version
zyxel-cli -H 192.168.1.1 -u admin version

# Get configuration
zyxel-cli -H 192.168.1.1 -u admin config

# Interactive session
zyxel-cli -H 192.168.1.1 -u admin interactive

# Execute custom command
zyxel-cli -H 192.168.1.1 -u admin exec "show ip interface"

# Password will be prompted if not provided with -p
zyxel-cli -H 192.168.1.1 -u admin -p mypassword version
```

#### Command Supported with JSON Output

Following commands are supported with JSON output:

| Command | Description | Status | Example output |
|---------|-------------|--------|----------------|
| `version` | Show switch version | ✅ | [version_cmd.json](https://raw.githubusercontent.com/hellqvio86/docker-zyxel-ssh-connector/main/src/tests/data/version_cmd.json) |
| `config` | Show running configuration | ❌ | [config_cmd.json](https://raw.githubusercontent.com/hellqvio86/docker-zyxel-ssh-connector/main/src/tests/data/config_cmd.json) |
| `interfaces` | Show interface status | ✅ | [intefaces_cmd.json](https://raw.githubusercontent.com/hellqvio86/docker-zyxel-ssh-connector/main/src/tests/data/intefaces_cmd.json) |
| `vlans` | Show VLAN configuration | ✅ | [vlans_cmd.json](https://raw.githubusercontent.com/hellqvio86/docker-zyxel-ssh-connector/main/src/tests/data/vlans_cmd.json) |
| `mac-table` | Show MAC address table | ✅| [mac_tabble_cmd.json](https://raw.githubusercontent.com/hellqvio86/docker-zyxel-ssh-connector/main/src/tests/data/mac_table_cmd.json) |

## Development

### Running Tests

```bash
# Run all tests
make test

# Run with verbose output
make test-verbose

# Run with coverage report
make test-cov

# View coverage report
open htmlcov/index.html
```

### Code Quality

```bash
# Check code style
make lint

# Fix code style issues automatically
make lint-fix

# Format code with black
make format

# Check formatting without changes
make format-check
```

### Project Structure

```
docker-zyxel-ssh-connector/
├── src/
│   └── zyxel_cli/
│       ├── __init__.py
│       ├── client.py          # SSH session handling
│       └── cli.py             # CLI interface
├── src/tests/
│   ├── test_client.py         # Client tests
│   └── test_cli.py            # CLI tests
├── Dockerfile                 # Multi-stage Docker container definition (builder + runtime)
├── pyproject.toml             # Python project configuration
├── Makefile                   # Build and run commands
└── README.md
```

## Makefile Commands Reference

### Quick Start
| Command | Description |
|---------|-------------|
| `make python-build` | Set up Python venv and install package |
| `make python-install` | Install with dev dependencies |
| `make test` | Run tests |

### Local CLI (without Docker)
| Command | Description | Example |
|---------|-------------|---------|
| `make cli-version` | Show version | `make cli-version host=192.168.1.1` |
| `make cli-config` | Show config | `make cli-config host=switch.local` |
| `make cli-interfaces` | Show interfaces | `make cli-interfaces host=192.168.1.1` |
| `make cli-vlans` | Show VLANs | `make cli-vlans host=192.168.1.1` |
| `make cli-mac-table` | Show MAC table | `make cli-mac-table host=192.168.1.1` |
| `make cli-connect` | Interactive SSH | `make cli-connect host=192.168.1.1` |
| `make cli-exec` | Custom command | `make cli-exec host=192.168.1.1 cmd='show ip'` |

### Docker CLI (recommended for legacy devices)
| Command | Description | Example |
|---------|-------------|---------|
| `make build` | Build container | `make build` |
| `make show-version` | Show version | `make show-version host=192.168.1.1` |
| `make show-config` | Show config | `make show-config host=192.168.1.1` |
| `make show-interfaces` | Show interfaces | `make show-interfaces host=192.168.1.1` |
| `make show-vlans` | Show VLANs | `make show-vlans host=192.168.1.1` |
| `make show-mac-table` | Show MAC table | `make show-mac-table host=192.168.1.1` |
| `make connect` | Interactive SSH | `make connect host=192.168.1.1` |
| `make run` | Bash shell | `make run` |

### Testing & Quality
| Command | Description |
|---------|-------------|
| `make test` | Run tests |
| `make test-verbose` | Run tests with verbose output |
| `make test-cov` | Run tests with coverage report |
| `make lint` | Check code style |
| `make lint-fix` | Fix code style issues |
| `make format` | Format code with black |

### Cleanup
| Command | Description |
|---------|-------------|
| `make python-clean` | Clean Python artifacts |
| `make clean` | Remove Docker image |

## Supported Devices

This tool should work with any legacy network equipment requiring older SSH algorithms, including:

- Zyxel GS1900 series switches
- Zyxel XGS series switches
- Zyxel routers and firewalls
- Other network equipment with OpenSSH 6.x or older

## Troubleshooting

### Local CLI Connection Issues

If the local CLI doesn't work:
```bash
# Your system's SSH may not support legacy algorithms
# Solution: Use Docker commands instead
make build
make show-version host=192.168.1.1
```

### Docker Network Access

The container uses `--net=host` to access your local network. If using a different network configuration, you may need to adjust network settings.

### Test Failures

```bash
# Clean and rebuild environment
make python-clean
make python-build
make python-install
make test
```

## Security Note

This tool intentionally uses legacy SSH algorithms to connect to older equipment. Only use this for connecting to trusted devices on secure networks. Consider upgrading your network equipment if possible.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`make test`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request
