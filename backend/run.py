from my_server import app, is_production
import os

if __name__ == "__main__":
    if is_production:
        # Production
        host = "0.0.0.0"
        if os.path.exists("production.txt"):
            with open("production.txt") as file:
                line = file.readline().strip()
                if len(line) > 0:
                    host = line

        print("Using " + host + " as the host.")
        app.run(host=host)
    else:
        # Development mode
        app.run(host="0.0.0.0", port=8080, debug=True)
