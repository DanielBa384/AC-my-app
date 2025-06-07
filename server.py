from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
import mysql.connector

# Configurare conexiune MySQL
import os

db_config = {
    "host": os.getenv("DB_HOST", "mysql-service"),
    "user": os.getenv("DB_USER", "Danu"),
    "password": os.getenv("DB_PASSWORD", "Danu"),
    "database": os.getenv("DB_NAME", "auth_demo")
}


class SimpleAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.show_home()
        elif self.path == "/login":
            self.show_login()
        elif self.path == "/register":
            self.show_register()
        else:
            self.send_error(404, "Pagina nu există.")

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode()
        data = parse_qs(post_data)

        username = data.get('username', [''])[0]
        password = data.get('password', [''])[0]

        if self.path == "/login":
            if self.check_login(username, password):
                self.respond_html(f"<h2>Bun venit, {username}!</h2><p>Autentificare reușită.</p>")
            else:
                self.respond_html("<h2>Autentificare eșuată</h2><p>Utilizator sau parolă greșite.</p>")
        elif self.path == "/register":
            if self.register_user(username, password):
                self.respond_html("<h2>Înregistrare reușită!</h2><a href='/login'>Loghează-te</a>")
            else:
                self.respond_html("<h2>Utilizatorul există deja!</h2><a href='/register'>Încearcă alt nume</a>")

    def connect_db(self):
        return mysql.connector.connect(**db_config)

    def register_user(self, username, password):
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
            return True
        except mysql.connector.IntegrityError:
            return False
        finally:
            cursor.close()
            conn.close()

    def check_login(self, username, password):
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result is not None

    def respond_html(self, content):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode())

    def show_home(self):
        html = """
        <h1>Bine ai venit!</h1>
        <ul>
            <li><a href="/register">Înregistrare</a></li>
            <li><a href="/login">Logare</a></li>
        </ul>
        """
        self.respond_html(html)

    def show_login(self):
        html = """
        <h2>Logare</h2>
        <form method="post" action="/login">
            Utilizator: <input type="text" name="username"><br>
            Parolă: <input type="password" name="password"><br>
            <input type="submit" value="Logare">
        </form>
        """
        self.respond_html(html)

    def show_register(self):
        html = """
        <h2>Înregistrare</h2>
        <form method="post" action="/register">
            Utilizator: <input type="text" name="username"><br>
            Parolă: <input type="password" name="password"><br>
            <input type="submit" value="Înregistrează-te">
        </form>
        """
        self.respond_html(html)

if __name__ == "__main__":
    PORT = 8000
    server = HTTPServer(("0.0.0.0", 8000), SimpleAuthHandler)
    server.serve_forever()
