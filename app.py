


from flask import Flask, render_template, request, redirect
import csv
import constantes
from reportlab.lib.pagesizes import letter
from datetime import datetime

import io
from reportlab.pdfgen import canvas


from Funciones import (
    validar_entero_positivo,
    validar_minutos,
    validar_texto_no_vacio,
    validar_si_no,
    validar_valor_personalizado,
    validar_metros_pieza,
    ingresar_items_adicionales,
    validar_entero_positivo2
)

app = Flask(__name__)

# Variables globales
Productos = []
id_actual = 1


@app.route("/descargar_pdf")
def descargar_pdf():
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    y = 750

    p.setFont("Helvetica", 12)
    p.drawString(50, y, "Resumen de Productos")
    y -= 30

    for producto in Productos:
        nombre = producto[constantes.texto18]
        costo_material = (producto[constantes.texto19] / producto[constantes.texto16]) * producto[constantes.texto14]
        costo_laboral = (producto[constantes.texto21] / 60) * producto[constantes.texto17]
        costo_luz = (producto[constantes.texto21] / 60) * producto[constantes.texto15]
        subtotal_pieza = costo_material + costo_laboral + costo_luz
        costo_pieza = round(subtotal_pieza / producto[constantes.texto27], 2)
        adicionales = sum([item["valor"] for item in producto.get(constantes.texto22, [])])
        ganancia = round((costo_pieza + adicionales) * (producto[constantes.texto20] / 100), 2)
        precio_final = round(costo_pieza + adicionales + ganancia, 2)

        texto = f"{nombre} | Costo: {costo_pieza} | Adicionales: {adicionales} | Ganancia: {ganancia} | Total: {precio_final}"
        p.drawString(50, y, texto)
        y -= 20
        if y < 50:
            p.showPage()
            y = 750

    p.save()
    buffer.seek(0)
    return Response(buffer, mimetype='application/pdf',
                    headers={"Content-Disposition": "attachment;filename=resumen.pdf"})


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/contacto")
def contacto():
    return render_template("contacto.html")

@app.route("/lenguajes")
def lenguajes():
    lenguajes = ["PHP", "Python", "C#"]
    return render_template("lenguajes.html", lenguajes=lenguajes)

@app.route("/ingresar", methods=["GET", "POST"])
def ingresar():
    global id_actual

    if request.method == "POST":

        try:

        # Simulación de entrada desde formulario (puedes adaptar con request.form)
            valor_rollo = validar_entero_positivo(request.form.get("valor_rollo"))
            hora_luz = validar_entero_positivo(request.form.get("hora_luz"))
            metros_bobina = validar_entero_positivo(request.form.get("metros_bobina"))
            hora_laboral = validar_entero_positivo(request.form.get("hora_laboral"))
            nombre_pieza = validar_texto_no_vacio(request.form.get("nombre_pieza"))
            divisor = validar_entero_positivo2(request.form.get("divisor"))
            metros_piezas1 = validar_metros_pieza(request.form.get("metros_pieza"))
            
            ganancia = validar_valor_personalizado(request.form.get("ganancia"), constantes.error)
            porcentaje1 = float(ganancia / constantes.ganancia) * 100      
            tiempo1 = validar_entero_positivo(request.form.get("tiempo_horas"))
            tiempo2 = validar_minutos(request.form.get("tiempo_minutos"))

            tiempo = (tiempo1 * 60) + tiempo2
            datos_adicionales = ingresar_items_adicionales(request.form)



            Productos.append({
                constantes.texto14: valor_rollo,
                constantes.texto15: hora_luz,
                constantes.texto16: metros_bobina,
                constantes.texto17: hora_laboral,
                constantes.texto18: nombre_pieza,
                constantes.texto19: metros_piezas1,
                constantes.texto20: float(porcentaje1),
                constantes.texto21: tiempo,
                constantes.texto22: datos_adicionales,
                constantes.texto27: divisor
            })
            

            id_actual += 1
            return redirect("/resumen")
        except ValueError as e:
            return render_template("ingresar.html", error=str(e))
    return render_template("ingresar.html")

@app.route("/resumen")
def resumen():
    resumen_datos = []

    for producto in Productos:
        # Cálculos detallados
        costo_material = (producto[constantes.texto19] / producto[constantes.texto16]) * producto[constantes.texto14]
        costo_laboral = (producto[constantes.texto21] / 60) * producto[constantes.texto17]
        costo_luz = (producto[constantes.texto21] / 60) * producto[constantes.texto15]
        subtotal_pieza = costo_material + costo_laboral + costo_luz
        costo_pieza = round(subtotal_pieza / producto[constantes.texto27], 2)
        adicionales = producto.get(constantes.texto22, [])
        costo_adicionales = sum([item["valor"] for item in adicionales])
        ganancia_total = round((costo_pieza + costo_adicionales) * (producto[constantes.texto20] / 100), 2)
        precio_final = round(costo_pieza + costo_adicionales + ganancia_total, 2)

        # Crear objeto con todos los detalles
        resumen_datos.append({
            "nombre": producto[constantes.texto18],
            "datos_entrada": {
                "valor_rollo": producto[constantes.texto14],
                "hora_luz": producto[constantes.texto15],
                "metros_bobina": producto[constantes.texto16],
                "hora_laboral": producto[constantes.texto17],
                "metros_pieza": producto[constantes.texto19],
                "porcentaje_ganancia": producto[constantes.texto20],
                "tiempo_total_minutos": producto[constantes.texto21],
                "divisor": producto[constantes.texto27]
            },
            "calculos": {
                "costo_material": round(costo_material, 2),
                "costo_laboral": round(costo_laboral, 2),
                "costo_luz": round(costo_luz, 2),
                "subtotal_pieza": round(subtotal_pieza, 2)
            },
            "costo_pieza": round(costo_pieza, 2),
            "adicionales": adicionales,
            "costo_adicionales": round(costo_adicionales, 2),
            "ganancia": round(ganancia_total, 2),
            "precio_final": precio_final
        })

    return render_template("resumen.html", resumen=resumen_datos)


from flask import Response

@app.route("/descargar_csv")
def descargar_csv():
    def generar_csv():
        yield "Nombre,Costo pieza,Adicionales,Ganancia,Precio final\n"
        for producto in Productos:
            nombre = producto[constantes.texto18]
            costo_material = (producto[constantes.texto19] / producto[constantes.texto16]) * producto[constantes.texto14]
            costo_laboral = (producto[constantes.texto21] / 60) * producto[constantes.texto17]
            costo_luz = (producto[constantes.texto21] / 60) * producto[constantes.texto15]
            subtotal_pieza = costo_material + costo_laboral + costo_luz
            costo_pieza = round(subtotal_pieza / producto[constantes.texto27], 2)
            adicionales = sum([item["valor"] for item in producto.get(constantes.texto22, [])])
            ganancia = round((costo_pieza + adicionales) * (producto[constantes.texto20] / 100), 2)
            precio_final = round(costo_pieza + adicionales + ganancia, 2)
            yield f"{nombre},{costo_pieza},{adicionales},{ganancia},{precio_final}\n"

    return Response(generar_csv(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=resumen.csv"})



@app.route("/cancelar")
def cancelar():
    global Productos, id_actual
    Productos.clear()
    id_actual = 1
    return redirect("/")


@app.context_processor
def inject_year():
    return {'current_year': datetime.now().year}









if __name__ == "__main__":
    app.run(debug=True, port=5018)
