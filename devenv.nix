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

  dotenv.enable = true;

  languages.javascript.bun = {
    enable = true;
    install.enable = true;
  };
}
