# Gymnasiearbete
This is an final school project / extended essay / "Gymnasiearbete".

The frontend code is made using Vue.js and built using Vite. See the frontend readme for installation and running instructions.

The backend code is made using Flask. See the backend readme for installation and running instructions.

Google oauth2 credentials are required to run the project to enable logging in with Google. Start the backend server for more information on where to place the JSON file.

## Running

Open two terminal tabs.

In one of them, cd into `frontend` and run `pnpm install` then `pnpm dev` (NodeJS and PNPM need to be installed).

In the other terminal tab, cd into `backend` and enter the virtual environment (venv) and then run `python run.py` after installing the dependencies that you can find in the [backend readme](./backend/README.md). Do not open the backend in the browser, you need to open the frontend in the browser.

## Running in production
To run the project in production, first build the frontend using `pnpm build` in the `frontend` folder. Then start the backend server. The backend server will send the built frontend files. Alternatively, set up a static HTTP server to serve the frontend files. All HTTP requests that request HTML will need to respond with the `index.html`, no matter the path. Routing is done client side instead.

To notify the backend that it is running in production mode. Either set the `ENV` environment variable to `production`, or create a `production.txt` file (empty) in the `backend` folder. You can also type the host to start the server on in the `production.txt` file and the server will be started on that host.