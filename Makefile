.PHONY: build run connect clean show-version show-config show-interfaces show-vlans show-mac-table show-system backup-config

# Build the container
build:
	podman build -t zyxel-ssh-connector -f Dockerfile.zyxel .

# Run the container with bash
run:
	@echo "Running zyxel-ssh-connector"
	podman run -it --rm --net=host zyxel-ssh-connector bash

# Connect directly to the Zyxel switch
# Usage: make connect host=192.168.1.1 [user=admin]
connect:
	@if [ -z "$(host)" ]; then \
		echo "Error: host parameter required"; \
		echo "Usage: make connect host=192.168.1.1 [user=admin]"; \
		exit 1; \
	fi
	@echo "Connecting to Zyxel switch at $(host)..."
	podman run -it --rm --net=host zyxel-ssh-connector ssh $(if $(user),$(user),admin)@$(host)

# Clean up the container image
clean:
	podman rmi zyxel-ssh-connector

# Show switch version and model info
# Usage: make show-version host=192.168.1.1 [user=admin]
show-version:
	@if [ -z "$(host)" ]; then \
		echo "Error: host parameter required"; \
		echo "Usage: make show-version host=192.168.1.1 [user=admin]"; \
		exit 1; \
	fi
	@echo "Getting version info from $(host)..."
	@podman run -it --rm --net=host zyxel-ssh-connector ssh $(if $(user),$(user),admin)@$(host) "show version"

# Show running configuration
# Usage: make show-config host=192.168.1.1 [user=admin]
show-config:
	@if [ -z "$(host)" ]; then \
		echo "Error: host parameter required"; \
		echo "Usage: make show-config host=192.168.1.1 [user=admin]"; \
		exit 1; \
	fi
	@echo "Getting configuration from $(host)..."
	@podman run -it --rm --net=host zyxel-ssh-connector ssh $(if $(user),$(user),admin)@$(host) "show running-config"

# Show interface status
# Usage: make show-interfaces host=192.168.1.1 [user=admin]
show-interfaces:
	@if [ -z "$(host)" ]; then \
		echo "Error: host parameter required"; \
		echo "Usage: make show-interfaces host=192.168.1.1 [user=admin]"; \
		exit 1; \
	fi
	@echo "Getting interface status from $(host)..."
	@podman run -it --rm --net=host zyxel-ssh-connector ssh $(if $(user),$(user),admin)@$(host) "show interface status"

# Show VLAN configuration
# Usage: make show-vlans host=192.168.1.1 [user=admin]
show-vlans:
	@if [ -z "$(host)" ]; then \
		echo "Error: host parameter required"; \
		echo "Usage: make show-vlans host=192.168.1.1 [user=admin]"; \
		exit 1; \
	fi
	@echo "Getting VLAN info from $(host)..."
	@podman run -it --rm --net=host zyxel-ssh-connector ssh $(if $(user),$(user),admin)@$(host) "show vlan"

# Show MAC address table
# Usage: make show-mac-table host=192.168.1.1 [user=admin]
show-mac-table:
	@if [ -z "$(host)" ]; then \
		echo "Error: host parameter required"; \
		echo "Usage: make show-mac-table host=192.168.1.1 [user=admin]"; \
		exit 1; \
	fi
	@echo "Getting MAC address table from $(host)..."
	@podman run -it --rm --net=host zyxel-ssh-connector ssh $(if $(user),$(user),admin)@$(host) "show mac address-table"

# Show system information
# Usage: make show-system host=192.168.1.1 [user=admin]
show-system:
	@if [ -z "$(host)" ]; then \
		echo "Error: host parameter required"; \
		echo "Usage: make show-system host=192.168.1.1 [user=admin]"; \
		exit 1; \
	fi
	@echo "Getting system info from $(host)..."
	@podman run -it --rm --net=host zyxel-ssh-connector ssh $(if $(user),$(user),admin)@$(host) "show system-info"

# Backup configuration to file
# Usage: make backup-config host=192.168.1.1 [user=admin] [file=backup.cfg]
backup-config:
	@if [ -z "$(host)" ]; then \
		echo "Error: host parameter required"; \
		echo "Usage: make backup-config host=192.168.1.1 [user=admin] [file=backup.cfg]"; \
		exit 1; \
	fi
	@echo "Backing up configuration from $(host)..."
	@podman run -it --rm --net=host zyxel-ssh-connector ssh $(if $(user),$(user),admin)@$(host) "show running-config" > $(if $(file),$(file),backup-$(host)-$(shell date +%Y%m%d-%H%M%S).cfg)
	@echo "Configuration saved to $(if $(file),$(file),backup-$(host)-$(shell date +%Y%m%d-%H%M%S).cfg)"

# Show all available commands
help:
	@echo "Zyxel SSH Connector - Available Commands"
	@echo ""
	@echo "Build & Run:"
	@echo "  make build                  - Build the container"
	@echo "  make run                    - Run interactive bash shell"
	@echo "  make connect host=HOST      - Connect to switch"
	@echo "  make clean                  - Remove container image"
	@echo ""
	@echo "Zyxel GS1900 Commands:"
	@echo "  make show-version host=HOST      - Show switch version and model"
	@echo "  make show-config host=HOST       - Show running configuration"
	@echo "  make show-interfaces host=HOST   - Show interface status"
	@echo "  make show-vlans host=HOST        - Show VLAN configuration"
	@echo "  make show-mac-table host=HOST    - Show MAC address table"
	@echo "  make show-system host=HOST       - Show system information"
	@echo "  make backup-config host=HOST     - Backup config to file"
	@echo ""
	@echo "Optional parameters:"
	@echo "  user=USERNAME  - Specify SSH user (default: admin)"
	@echo "  file=FILENAME  - Specify backup filename (backup-config only)"
	@echo ""
	@echo "Examples:"
	@echo "  make show-version host=192.168.1.1"
	@echo "  make show-interfaces host=switch.local user=root"
	@echo "  make backup-config host=192.168.1.1 file=myswitch.cfg"