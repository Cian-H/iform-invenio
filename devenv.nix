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
    git
    jq
  ];

  languages.javascript.bun = {
    enable = true;
    install.enable = true;
  };
}
