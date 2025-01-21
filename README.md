# Research Project Website

This repository contains the source code for the AM-D-Model project's public-facing website. The site serves as an info page, as well as an invitation to collaborators and portal to our other tools.

## Getting Started

### Prerequisites

This project uses `devenv.nix` to manage the development environment, which will handle all prerequisites automatically. Make sure you have `devenv` installed on your system. If you wish to avoid using devenv it should also work fine directly using bun, node, or deno, but i can't make any promises as i use devenv.

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Cian-H/am-d-model.eu.git
cd am-d-model.eu
```

2. Start the development server:
    - via bun (recommended)
    ```bash
    bun install
    bun run dev
    ```
    - via node.js
    ```bash
    npm install
    npm run dev
    ```
    - via deno
    ```bash
    deno install --allow-scripts=npm:svelte-preprocess,npm:@parcel/watcher
    deno run dev
    ```
    - via docker
    ```bash
    docker build --tag am-d-model-site:latest .
    docker run -p 3000:3000 am-d-model-site
    ```

The site will be available at `http://localhost:3000`

### Other Commands

- `bun preview`: Run a preview of the production build
- `bun build`: Build the site for production
- `docker compose up`: Deploys a docker composition including a caddy reverse proxy, ready to be deployed to web infrastructure

## Deployment

For simplicity, deployment is manually triggered via justfiles. More complex solutions may be
implemented in future but for now, simplicity is a virtue.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

