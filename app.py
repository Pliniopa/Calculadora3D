


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
    
    def draw_text_block(text_lines, start_y, font_size=10):
        y = start_y
        p.setFont("Helvetica", font_size)
        for line in text_lines:
            p.drawString(50, y, line)
            y -= 15
        return y

    for producto in Productos:
        y = 750  # Reset Y position for each new page
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y, f"Detalle de producto: {producto[constantes.texto18]}")
        y -= 30

        # Datos de entrada
        text_lines = [
            "DATOS DE ENTRADA:",
            f"Valor rollo: ${producto[constantes.texto14]}",
            f"Hora luz: ${producto[constantes.texto15]}",
            f"Metros bobina: {producto[constantes.texto16]}m",
            f"Hora laboral: ${producto[constantes.texto17]}",
            f"Metros pieza: {producto[constantes.texto19]}m",
            f"Tiempo total: {producto[constantes.texto21]} minutos",
            f"Porcentaje ganancia: {producto[constantes.texto20]}%",
            f"Divisor: {producto[constantes.texto27]}"
        ]
        y = draw_text_block(text_lines, y)
        y -= 20

        # Cálculos
        costo_material = (producto[constantes.texto19] / producto[constantes.texto16]) * producto[constantes.texto14]
        costo_laboral = producto[constantes.texto17]  # Valor directo de hora laboral
        costo_luz = (producto[constantes.texto21] / 60) * producto[constantes.texto15]
        subtotal_pieza = costo_material + costo_laboral + costo_luz
        costo_pieza = round(subtotal_pieza / producto[constantes.texto27], 2)
        
        text_lines = [
            "DESGLOSE DE COSTOS:",
            f"Costo material: ${round(costo_material, 2)}",
            f"Costo laboral: ${round(costo_laboral, 2)}",
            f"Costo luz: ${round(costo_luz, 2)}",
            f"Subtotal por pieza: ${round(subtotal_pieza, 2)}"
        ]
        y = draw_text_block(text_lines, y)
        y -= 20

        # Adicionales
        adicionales = producto.get(constantes.texto22, [])
        if adicionales:
            text_lines = ["COSTOS ADICIONALES:"]
            for item in adicionales:
                text_lines.append(f"{item['descripcion']}: ${item['valor']}")
            y = draw_text_block(text_lines, y)
            y -= 20

        # Resumen final
        costo_adicionales = sum([item["valor"] for item in adicionales])
        ganancia = round((costo_pieza + costo_adicionales) * (producto[constantes.texto20] / 100), 2)
        precio_final = round(costo_pieza + costo_adicionales + ganancia, 2)

        text_lines = [
            "RESUMEN FINAL:",
            f"Costo por pieza: ${costo_pieza}",
            f"Total adicionales: ${costo_adicionales}",
            f"Ganancia ({producto[constantes.texto20]}%): ${ganancia}",
            f"PRECIO FINAL: ${precio_final}"
        ]
        y = draw_text_block(text_lines, y, 12)

        # Nueva página para el siguiente producto
        p.showPage()

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
        # Encabezados
        yield "Nombre,Valor rollo,Hora luz,Metros bobina,Hora laboral,Metros pieza,Tiempo total (min),Porcentaje ganancia,Divisor,"
        yield "Costo material,Costo laboral,Costo luz,Subtotal pieza,Costo por pieza,Total adicionales,Ganancia,Precio final,Detalles adicionales\n"

        for producto in Productos:
            # Cálculos
            costo_material = (producto[constantes.texto19] / producto[constantes.texto16]) * producto[constantes.texto14]
            costo_laboral = producto[constantes.texto17]  # Valor directo de hora laboral
            costo_luz = (producto[constantes.texto21] / 60) * producto[constantes.texto15]
            subtotal_pieza = costo_material + costo_laboral + costo_luz
            costo_pieza = round(subtotal_pieza / producto[constantes.texto27], 2)
            adicionales = producto.get(constantes.texto22, [])
            costo_adicionales = sum([item["valor"] for item in adicionales])
            ganancia = round((costo_pieza + costo_adicionales) * (producto[constantes.texto20] / 100), 2)
            precio_final = round(costo_pieza + costo_adicionales + ganancia, 2)
            
            # Detalles de adicionales como texto
            detalles_adicionales = "; ".join([f"{item['descripcion']}: ${item['valor']}" for item in adicionales]) if adicionales else ""
            
            # Datos básicos
            yield f"{producto[constantes.texto18]}," # Nombre
            yield f"{producto[constantes.texto14]}," # Valor rollo
            yield f"{producto[constantes.texto15]}," # Hora luz
            yield f"{producto[constantes.texto16]}," # Metros bobina
            yield f"{producto[constantes.texto17]}," # Hora laboral
            yield f"{producto[constantes.texto19]}," # Metros pieza
            yield f"{producto[constantes.texto21]}," # Tiempo total
            yield f"{producto[constantes.texto20]}," # Porcentaje ganancia
            yield f"{producto[constantes.texto27]}," # Divisor
            
            # Resultados de cálculos
            yield f"{round(costo_material, 2)}," # Costo material
            yield f"{round(costo_laboral, 2)}," # Costo laboral
            yield f"{round(costo_luz, 2)}," # Costo luz
            yield f"{round(subtotal_pieza, 2)}," # Subtotal pieza
            yield f"{costo_pieza}," # Costo por pieza
            yield f"{costo_adicionales}," # Total adicionales
            yield f"{ganancia}," # Ganancia
            yield f"{precio_final}," # Precio final
            yield f"{detalles_adicionales}\n" # Detalles de adicionales

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
