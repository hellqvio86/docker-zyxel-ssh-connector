.PHONY: build run connect clean

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