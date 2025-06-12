{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    (python311.withPackages (ps: with ps; [
      neo4j
      python-dateutil
      dateparser
      # Add other Python dependencies here
    ]))
    neo4j
    curl
    gnupg
  ];

  shellHook = ''
    # Set up Neo4j directories in user's home
    export NEO4J_HOME="$HOME/.neo4j"
    export NEO4J_DATA="$NEO4J_HOME/data"
    export NEO4J_LOGS="$NEO4J_HOME/logs"
    export NEO4J_CONF="$NEO4J_HOME/conf"
    
    # Create necessary directories
    mkdir -p "$NEO4J_DATA"
    mkdir -p "$NEO4J_LOGS"
    mkdir -p "$NEO4J_CONF"
    
    # Copy default config if it doesn't exist
    if [ ! -f "$NEO4J_CONF/neo4j.conf" ]; then
      cp ${pkgs.neo4j}/share/neo4j/conf/neo4j.conf "$NEO4J_CONF/"
      # Update paths in config
      sed -i "s|data.directories.data=.*|data.directories.data=$NEO4J_DATA|" "$NEO4J_CONF/neo4j.conf"
      sed -i "s|logs.directories.logs=.*|logs.directories.logs=$NEO4J_LOGS|" "$NEO4J_CONF/neo4j.conf"
      
      # Configure for external access
      echo "server.default_listen_address=0.0.0.0" >> "$NEO4J_CONF/neo4j.conf"
      echo "server.memory.heap.initial_size=1g" >> "$NEO4J_CONF/neo4j.conf"
      echo "server.memory.heap.max_size=1g" >> "$NEO4J_CONF/neo4j.conf"
      echo "server.memory.pagecache.size=1g" >> "$NEO4J_CONF/neo4j.conf"
      
      # Configure Bolt connector (using port 7688)
      echo "server.bolt.enabled=true" >> "$NEO4J_CONF/neo4j.conf"
      echo "server.bolt.listen_address=0.0.0.0:7688" >> "$NEO4J_CONF/neo4j.conf"
      
      # Configure HTTP connector (using port 7475)
      echo "server.http.enabled=true" >> "$NEO4J_CONF/neo4j.conf"
      echo "server.http.listen_address=0.0.0.0:7475" >> "$NEO4J_CONF/neo4j.conf"
      
      # Configure HTTPS connector (using port 7476)
      echo "server.https.enabled=true" >> "$NEO4J_CONF/neo4j.conf"
      echo "server.https.listen_address=0.0.0.0:7476" >> "$NEO4J_CONF/neo4j.conf"
    fi
    
    # Set environment variables
    export NEO4J_AUTH=neo4j/password
    export NEO4J_URI=bolt://localhost:7688
    export NEO4J_USERNAME=neo4j
    export NEO4J_PASSWORD=password
    export TEMPORAL_KG_ENABLED=true
    
    # Start Neo4j if not running
    if ! pgrep -x "neo4j" > /dev/null; then
      echo "Starting Neo4j..."
      NEO4J_CONF="$NEO4J_CONF" neo4j start
      echo "Neo4j is now accessible at:"
      echo "  - HTTP:  http://localhost:7475"
      echo "  - HTTPS: https://localhost:7476"
      echo "  - Bolt:  bolt://localhost:7688"
    else
      echo "Neo4j is already running"
    fi
  '';
} 