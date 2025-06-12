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
    export NEO4J_AUTH=neo4j/password
    export NEO4J_URI=bolt://localhost:7687
    export NEO4J_USERNAME=neo4j
    export NEO4J_PASSWORD=password
    export TEMPORAL_KG_ENABLED=true
  '';
} 