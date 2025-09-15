from flask import Flask, render_template

app= Flask(__name__) # verificar y controlar el archivo inicial


# @app.route("/") # definiendo ruta raiz

# def principal():
#     return "Bienvenidos a mi pagina"

# #Pagina secundaria
# @app.route("/contacto")
# def contacto():
#     return "Contacto"


@app.route("/") #Ruta principal

def principal():
    return render_template("index.html") #: retornaremos una plantilla

@app.route("/contacto")
def contacto():
    return render_template("contacto.html")

@app.route("/lenguajes")
def lenguaje():

    lenguajes=("PHP", "Python", "C#")
    return render_template("lenguajes.html", lenguajes=lenguajes)

# Levantamiento de servidor web
if __name__ == "__main__":
    app.run(debug=True, # Levanta y reinicia el server automatico
            port = 5017) # Cambio de Puerto