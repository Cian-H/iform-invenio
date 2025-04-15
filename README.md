# Research Project Website

This repository contains the source code for I-Form's custom Invenio instance

## Deployment

This project is deployed via docker compose, by using the following command in the root directory:

```sh
docker compose up
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

Thanks to the extremely friendly community of the inveniosoftware discord, and in particular
Martin Fenner and his [alternative invenio deployment](https://github.com/front-matter/invenio-rdm-starter/tree/main) using gunicorn and caddy.
Trying to get this to work via the traditional uwsgi and nginx was a nightmare; one he had
apparently already discovered and worked around.
