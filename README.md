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
```bash
bun dev
```

The site will be available at `http://localhost:5173`

### Other Commands

- `bun preview`: Run a preview of the production build
- `bun build`: Build the site for production

## Deployment

The website is automatically deployed via GitHub Actions when changes are pushed to the main branch. The production site can be found at `https://am-d-model.eu`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

