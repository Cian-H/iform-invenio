{
  pkgs,
  lib,
  config,
  inputs,
  ...
}: {
  packages = with pkgs; [
    bun
    git
  ];

  languages.javascript.bun = {
    enable = true;
    install.enable = true;
  };
}
