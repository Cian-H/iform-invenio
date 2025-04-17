{
  pkgs,
  lib,
  config,
  inputs,
  ...
}: {
  packages = with pkgs; [
    awscli2
    bun
    docker
    docker-compose
    git
    jq
  ];

  containers.docker.enable = true;

  languages.javascript.bun = {
    enable = true;
    install.enable = true;
  };
}
