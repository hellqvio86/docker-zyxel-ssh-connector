.PHONY: build run connect clean python-build python-install python-clean python-test python-test-verbose python-test-cov python-lint python-lint-fix python-format python-format-check python-validate show-version show-config show-interfaces show-vlans show-mac-table cli-version cli-config cli-interfaces cli-vlans cli-mac-table cli-connect cli-exec help shell docker-build docker-final docker-clean docker-final-bash

# Python development commands
python-build:
	@echo "Setting up Python development environment..."
	uv sync --no-dev
	@echo "✅ Python environment ready!"
	@echo "Activate with: source .venv/bin/activate"

python-install:
	@echo "Installing package with dev dependencies..."
	uv sync
	@echo "✅ Development dependencies installed!"

python-clean:
	@echo "Cleaning Python artifacts..."
	rm -rf .venv
	rm -rf build dist *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache htmlcov .coverage
	@echo "✅ Python artifacts cleaned!"

# Testing commands
python-test:
	uv run pytest

python-test-verbose:
	uv run pytest -vv

python-test-cov:
	uv run pytest --cov=src/zyxel_cli --cov-report=html --cov-report=term-missing

python-lint:
	uv run ruff check src

python-lint-fix:
	uv run ruff check --fix src

python-format:
	uv run black src

python-format-check:
	uv run black --check src

# Validation: code formatting and static typing
.PHONY: python-validate
python-validate:
	@echo "Running import sorting (isort) and static typing (mypy)..."
	uv run isort src
	uv run isort src/tests
	uv run black src
	uv run mypy --show-error-codes src

# Local CLI commands (without Docker) - requires legacy SSH on your system
cli-version:
	@if [ -z "$(host)" ]; then \
		echo "Error: host parameter required"; \
		echo "Usage: make cli-version host=192.168.1.1 [user=admin] [password=secret]"; \
		exit 1; \
	fi
	@echo "Getting version from $(host)..."
	uv run zyxel-cli -H $(host) -u $(if $(user),$(user),admin) $(if $(password),-p $(password),) version

cli-config:
	@if [ -z "$(host)" ]; then \
		echo "Error: host parameter required"; \
		echo "Usage: make cli-config host=192.168.1.1 [user=admin] [password=secret]"; \
		exit 1; \
	fi
	@echo "Getting configuration from $(host)..."
	uv run zyxel-cli -H $(host) -u $(if $(user),$(user),admin) $(if $(password),-p $(password),) config

cli-interfaces:
	@if [ -z "$(host)" ]; then \
		echo "Error: host parameter required"; \
		echo "Usage: make cli-interfaces host=192.168.1.1 [user=admin] [password=secret]"; \
		exit 1; \
	fi
	@echo "Getting interface status from $(host)..."
	uv run zyxel-cli -H $(host) -u $(if $(user),$(user),admin) $(if $(password),-p $(password),) interfaces

cli-vlans:
	@if [ -z "$(host)" ]; then \
		echo "Error: host parameter required"; \
		echo "Usage: make cli-vlans host=192.168.1.1 [user=admin] [password=secret]"; \
		exit 1; \
	fi
	@echo "Getting VLAN configuration from $(host)..."
	uv run zyxel-cli -H $(host) -u $(if $(user),$(user),admin) $(if $(password),-p $(password),) vlans

cli-mac-table:
	@if [ -z "$(host)" ]; then \
		echo "Error: host parameter required"; \
		echo "Usage: make cli-mac-table host=192.168.1.1 [user=admin] [password=secret]"; \
		exit 1; \
	fi
	@echo "Getting MAC address table from $(host)..."
	uv run zyxel-cli -H $(host) -u $(if $(user),$(user),admin) $(if $(password),-p $(password),) mac-table


cli-connect:
	@if [ -z "$(host)" ]; then \
		echo "Error: host parameter required"; \
		echo "Usage: make cli-connect host=192.168.1.1 [user=admin] [password=secret]"; \
		exit 1; \
	fi
	@echo "Connecting to $(host)..."
	uv run zyxel-cli -H $(host) -u $(if $(user),$(user),admin) $(if $(password),-p $(password),) interactive

cli-exec:
	@if [ -z "$(host)" ]; then \
		echo "Error: host parameter required"; \
		echo "Usage: make cli-exec host=192.168.1.1 cmd='show ip' [user=admin] [password=secret]"; \
		exit 1; \
	fi
	@if [ -z "$(cmd)" ]; then \
		echo "Error: cmd parameter required"; \
		echo "Usage: make cli-exec host=192.168.1.1 cmd='show ip' [user=admin] [password=secret]"; \
		exit 1; \
	fi
	@echo "Executing command on $(host)..."
	uv run zyxel-cli -H $(host) -u $(if $(user),$(user),admin) $(if $(password),-p $(password),) exec "$(cmd)"

shell:
	@echo "Starting a bash shell on zyxel-ssh-connector"
	podman run --rm -it localhost/zyxel-ssh-connector:latest /bin/bash

bash-zyxel:
	@echo "Starting a bash shell on zyxel-ssh-bash"
	podman run --rm -it localhost/zyxel-ssh-bash:latest /bin/bash

# Docker commands
build:
	@echo "Building Docker container (multi-stage builder + final)..."
	@$(MAKE) docker-final

docker-build:
	@echo "Building builder image (zyxel-builder)..."
	podman build -t zyxel-builder -f Dockerfile.build .

docker-final: docker-build
	@echo "Building final runtime image (zyxel-ssh-connector)..."
	podman build -t zyxel-ssh-connector -f Dockerfile .


docker-final-bash: docker-build
	@echo "Building final runtime image (zyxel-ssh-bash)..."
	podman build -t zyxel-ssh-bash -f Dockerfile.bash.zyxel .

docker-clean:
	@echo "Removing images zyxel-builder and zyxel-ssh-connector..."
	-podman rmi zyxel-ssh-connector || true
	-podman rmi zyxel-builder || true

run:
	@echo "Running zyxel-ssh-connector container..."
	podman run -it --rm --net=host zyxel-ssh-connector bash

clean:
	@echo "Removing Docker container..."
	podman rmi zyxel-ssh-connector

# Docker-based Zyxel switch commands (use these if legacy SSH not available locally)
connect:
	@if [ -z "$(host)" ]; then \
		echo "Error: host parameter required"; \
		echo "Usage: make connect host=192.168.1.1 [user=admin] [password=secret]"; \
		exit 1; \
	fi
	@echo "Connecting to $(host) via Docker..."
	podman run -it --rm --net=host zyxel-ssh-connector zyxel-cli -H $(host) -u $(if $(user),$(user),admin) $(if $(password),-p $(password),) interactive

show-version:
	@if [ -z "$(host)" ]; then \
		echo "Error: host parameter required"; \
		echo "Usage: make show-version host=192.168.1.1 [user=admin] [password=secret]"; \
		exit 1; \
	fi
	@echo "Getting version from $(host) via Docker..."
	@podman run -it --rm --net=host zyxel-ssh-connector zyxel-cli -H $(host) -u $(if $(user),$(user),admin) $(if $(password),-p $(password),) version

show-config:
	@if [ -z "$(host)" ]; then \
		echo "Error: host parameter required"; \
		echo "Usage: make show-config host=192.168.1.1 [user=admin] [password=secret]"; \
		exit 1; \
	fi
	@echo "Getting configuration from $(host) via Docker..."
	@podman run -it --rm --net=host zyxel-ssh-connector zyxel-cli -H $(host) -u $(if $(user),$(user),admin) $(if $(password),-p $(password),) config

show-interfaces:
	@if [ -z "$(host)" ]; then \
		echo "Error: host parameter required"; \
		echo "Usage: make show-interfaces host=192.168.1.1 [user=admin] [password=secret]"; \
		exit 1; \
	fi
	@echo "Getting interface status from $(host) via Docker..."
	@podman run -it --rm --net=host zyxel-ssh-connector zyxel-cli -H $(host) -u $(if $(user),$(user),admin) $(if $(password),-p $(password),) interfaces

show-vlans:
	@if [ -z "$(host)" ]; then \
		echo "Error: host parameter required"; \
		echo "Usage: make show-vlans host=192.168.1.1 [user=admin] [password=secret]"; \
		exit 1; \
	fi
	@echo "Getting VLAN configuration from $(host) via Docker..."
	@podman run -it --rm --net=host zyxel-ssh-connector zyxel-cli -H $(host) -u $(if $(user),$(user),admin) $(if $(password),-p $(password),) vlans

show-mac-table:
	@if [ -z "$(host)" ]; then \
		echo "Error: host parameter required"; \
		echo "Usage: make show-mac-table host=192.168.1.1 [user=admin] [password=secret]"; \
		exit 1; \
	fi
	@echo "Getting MAC address table from $(host) via Docker..."
	@podman run -it --rm --net=host zyxel-ssh-connector zyxel-cli -H $(host) -u $(if $(user),$(user),admin) $(if $(password),-p $(password),) mac-table


# Help
help:
	@echo "Zyxel SSH Connector - Available Commands"
	@echo ""
	@echo "=== Quick Start ==="
	@echo "  make python-build       - Set up Python environment (do this first!)"
	@echo "  make python-install     - Install dev dependencies for testing"
	@echo "  make test               - Run tests"
	@echo ""
	@echo "=== Local CLI (without Docker) ==="
	@echo "  Note: May not work on modern systems without legacy SSH support"
	@echo "  Usage: make cli-<command> host=<IP> [user=admin] [password=secret]"
	@echo ""
	@echo "  make cli-version        - Show switch version"
	@echo "  make cli-config         - Show configuration"
	@echo "  make cli-interfaces     - Show interfaces"
	@echo "  make cli-vlans          - Show VLANs"
	@echo "  make cli-mac-table      - Show MAC table"

	@echo "  make cli-connect        - Interactive session"
	@echo "  make cli-exec cmd='...' - Execute custom command"
	@echo ""
	@echo "=== Docker CLI (recommended for legacy switches) ==="
	@echo "  Usage: make <command> host=<IP> [user=admin] [password=secret]"
	@echo ""
	@echo "  make build              - Build Docker container (do this first!)"
	@echo "  make show-version       - Show switch version"
	@echo "  make show-config        - Show configuration"
	@echo "  make show-interfaces    - Show interfaces"
	@echo "  make show-vlans         - Show VLANs"
	@echo "  make show-mac-table     - Show MAC table"

	@echo "  make connect            - Interactive session"
	@echo "  make run                - Run bash in container"
	@echo ""
	@echo "=== Testing & Quality ==="
	@echo "  make test               - Run tests"
	@echo "  make test-verbose       - Run tests (verbose)"
	@echo "  make test-cov           - Run tests with coverage"
	@echo "  make lint               - Check code style"
	@echo "  make lint-fix           - Fix code style issues"
	@echo "  make format             - Format code"
	@echo ""
	@echo "=== Cleanup ==="
	@echo "  make python-clean       - Clean Python artifacts"
	@echo "  make clean              - Remove Docker image"
	@echo ""
	@echo "Examples:"
	@echo "  # Local (if legacy SSH works on your system)"
	@echo "  make cli-version host=192.168.1.1"
	@echo "  make cli-exec host=192.168.1.1 cmd='show ip interface'"
	@echo ""
	@echo "  # Docker (works everywhere)"
	@echo "  make build"
	@echo "  make show-version host=192.168.1.1"
	@echo "  make connect host=192.168.1.1 user=admin password=secret"