{
  pkgs,
  lib,
  config,
  inputs,
  ...
}: {
  packages = with pkgs; [
    awscli2
    cairo
    cairomm
    git
    jq
    nodejs
    uv
  ];

  dotenv.enable = true;

  languages = {
    python = {
      enable = true;
      version = "3.12";
      uv.enable = true;
    };
    javascript.npm = {
      enable = true;
      install.enable = true;
    };
  };

  env = {
    NIX_LD_LIBRARY_PATH = lib.makeLibraryPath (with pkgs; [
      cairo
      cairomm
    ]);
    NIX_LD = lib.fileContents "${pkgs.stdenv.cc}/nix-support/dynamic-linker";
  };
}
