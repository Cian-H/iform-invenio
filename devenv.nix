{
  pkgs,
  lib,
  config,
  inputs,
  ...
}: {
  packages = with pkgs; [
    awscli2
    git
    jq
    nodejs
    uv
  ];

  dotenv.enable = true;

  languages = {
    python = {
      enable = true;
      uv.enable = true;
    };
    javascript.npm = {
      enable = true;
      install.enable = true;
    };
  };
}
