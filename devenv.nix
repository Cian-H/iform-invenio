{
  pkgs,
  lib,
  config,
  inputs,
  ...
}: {
  packages = with pkgs; [
    awscli2
    bitwarden-cli
    cairo
    cairomm
    git
    jq
    nodejs
    uv
    libxcrypt
  ];

  dotenv.enable = true;

  enterShell = ''
    # Only set the exit trap if we are NOT in a direnv subshell
    if [ -z "$DIRENV_DIR" ]; then
      trap 'uv run cli bw lock' EXIT
    fi
  '';

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
    AWS_SHARED_CREDENTIALS_FILE = "${toString ./.}/.aws/credentials";
    AWS_CONFIG_FILE = "${toString ./.}/.aws/config";
    AWS_ENDPOINT_URL = "https://eu-west-1.storage.impossibleapi.net";
  };
}
