{
  description = "Temporal Knowledge Graph Integration for OpenDeepSearch";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pythonEnv = pkgs.python311.withPackages (ps: with ps; [
          neo4j
          python-dateutil
          dateparser
          # Add other Python dependencies here
        ]);
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            pythonEnv
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
        };

        packages = {
          dockerImage = pkgs.dockerTools.buildImage {
            name = "temporal-kg";
            tag = "latest";
            copyToRoot = pkgs.buildEnv {
              name = "image-root";
              paths = with pkgs; [
                pythonEnv
                neo4j
                curl
                gnupg
              ];
            };
            config = {
              Cmd = [ "${pkgs.bash}/bin/bash" "/app/start.sh" ];
              WorkingDir = "/app";
              ExposedPorts = {
                "7474/tcp" = { };
                "7687/tcp" = { };
                "8000/tcp" = { };
              };
              Env = [
                "NEO4J_AUTH=neo4j/password"
                "NEO4J_URI=bolt://localhost:7687"
                "NEO4J_USERNAME=neo4j"
                "NEO4J_PASSWORD=password"
                "TEMPORAL_KG_ENABLED=true"
              ];
            };
          };
        };
      });
} 