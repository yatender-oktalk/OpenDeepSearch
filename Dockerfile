# Use Nix as the base image
FROM nixos/nix:2.19.2

# Enable Nix flakes
RUN nix-channel --add https://nixos.org/channels/nixpkgs-unstable nixpkgs && \
    nix-channel --update

# Set working directory
WORKDIR /app

# Copy Nix configuration files
COPY flake.nix shell.nix ./

# Copy application code
COPY . .

# Build the application using Nix
RUN nix build .#dockerImage

# Create a script to start both Neo4j and the application
RUN echo '#!/bin/bash\n\
service neo4j start\n\
# Wait for Neo4j to be ready\n\
until curl -s http://localhost:7474 > /dev/null; do\n\
    echo "Waiting for Neo4j to start..."\n\
    sleep 1\n\
done\n\
# Start the application\n\
python -m opendeepsearch.main\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose ports
EXPOSE 7474 7687 8000

# Set environment variables
ENV NEO4J_AUTH=neo4j/password
ENV NEO4J_URI=bolt://localhost:7687
ENV NEO4J_USERNAME=neo4j
ENV NEO4J_PASSWORD=password
ENV TEMPORAL_KG_ENABLED=true

# Start the application
CMD ["/app/start.sh"] 