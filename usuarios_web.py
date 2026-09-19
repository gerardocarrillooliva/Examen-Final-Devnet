from flask import Flask, request, redirect, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

BASE_DATOS = "usuarios.db"


def conectar_db():
    return sqlite3.connect(BASE_DATOS)


def crear_base_datos():
    conexion = conectar_db()
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    conexion.commit()
    conexion.close()


@app.route("/")
def inicio():
    return """
    <html>
    <head>
        <title>Validación de Usuarios DEVNET</title>
    </head>
    <body>
        <h2>Inicio de sesión</h2>

        <form method="POST" action="/login">
            <label>Usuario:</label><br>
            <input type="text" name="usuario" required><br><br>

            <label>Contraseña:</label><br>
            <input type="password" name="password" required><br><br>

            <input type="submit" value="Ingresar">
        </form>

        <br>
        <a href="/crear">Crear usuario</a>
    </body>
    </html>
    """


@app.route("/crear", methods=["GET", "POST"])
def crear_usuario():
    if request.method == "POST":
        usuario = request.form["usuario"]
        password = request.form["password"]

        password_hash = generate_password_hash(password)

        conexion = conectar_db()
        cursor = conexion.cursor()

        try:
            cursor.execute(
                "INSERT INTO usuarios (usuario, password_hash) VALUES (?, ?)",
                (usuario, password_hash)
            )

            conexion.commit()
            mensaje = "Usuario creado correctamente."

        except sqlite3.IntegrityError:
            mensaje = "El usuario ya existe."

        conexion.close()

        return f"""
        <h2>{mensaje}</h2>
        <a href="/">Volver al inicio</a>
        """

    return """
    <html>
    <head>
        <title>Crear Usuario</title>
    </head>
    <body>
        <h2>Crear usuario</h2>

        <form method="POST">
            <label>Usuario:</label><br>
            <input type="text" name="usuario" required><br><br>

            <label>Contraseña:</label><br>
            <input type="password" name="password" required><br><br>

            <input type="submit" value="Crear usuario">
        </form>

        <br>
        <a href="/">Volver</a>
    </body>
    </html>
    """


@app.route("/login", methods=["POST"])
def login():
    usuario = request.form["usuario"]
    password = request.form["password"]

    conexion = conectar_db()
    cursor = conexion.cursor()

    cursor.execute(
        "SELECT password_hash FROM usuarios WHERE usuario = ?",
        (usuario,)
    )

    resultado = cursor.fetchone()
    conexion.close()

    if resultado and check_password_hash(resultado[0], password):
        return f"""
        <h2>Acceso correcto</h2>
        <p>Bienvenido, {usuario}</p>
        <a href="/">Volver</a>
        """
    else:
        return """
        <h2>Acceso denegado</h2>
        <p>Usuario o contraseña incorrectos.</p>
        <a href="/">Volver</a>
        """


if __name__ == "__main__":
    crear_base_datos()
    app.run(host="0.0.0.0", port=5800)