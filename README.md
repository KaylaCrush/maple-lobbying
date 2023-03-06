# Maple Lobbying Scraper

Standalone client to scrape lobbyist disclosure pages from www.sec.state.ma.us/LobbyistPublicSearch/ and upload them to a postgres database

# Local Docker

The `docker-compose.yml` file configures a postgres database and a python container for the scraper:

1. Install docker and [docker compose v2](https://docs.docker.com/compose/compose-v2/).
2. Build the images with `docker compose build`
3. Start the services with `docker compose up -d`. This will return once they're up.
4. Open a shell into the python container with `docker compose exec lobby bash`. This gives you a terminal into the development environment, connected to your source directory. So this will reflect changes you make.
5. Run your scraper commands `poetry run python main.py`
6. Shut down the services: `docker compose down`. Add `-v` to also delete the database