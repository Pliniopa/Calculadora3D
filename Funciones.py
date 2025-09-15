def validar_entero_positivo(valor):
    try:
        valor = int(valor)
        if valor > 0:
            return valor
        else:
            raise ValueError("Debe ser mayor que cero")
    except:
        raise ValueError("Debe ser un número entero positivo")


def validar_minutos(valor):
    try:
        minutos = int(valor)
        if 0 <= minutos < 60:
            return minutos
        else:
            raise ValueError("Minutos deben estar entre 0 y 59")
    except:
        raise ValueError("Debe ingresar un número entero válido")


def validar_texto_no_vacio(valor):
    if not valor or valor.strip() == "":
        raise ValueError("Este campo no puede estar vacío")
    return valor.strip()


def validar_si_no(valor):
    valor = valor.strip().lower()
    if valor in ["sí", "si", "no"]:
        return valor
    else:
        raise ValueError("Responde con 'sí' o 'no'")


def validar_valor_personalizado(valor, mensaje_error="Valor inválido"):
    if not str(valor).isdigit():
        raise ValueError(mensaje_error)
    valor = int(valor)
    if valor <= 0:
        raise ValueError(mensaje_error)
    return valor


def validar_metros_pieza(valor):
    try:
        metros = int(valor)
        if metros > 0:
            return metros
        else:
            raise ValueError("El valor debe ser mayor que cero")
    except:
        raise ValueError("Debe ingresar un número entero válido")


def validar_entero_positivo2(valor):
    if not str(valor).isdigit() or int(valor) <= 0:
        raise ValueError("Debe ingresar un número entero positivo")
    return int(valor)

def ingresar_items_adicionales(form_data):
    items = []
    index = 1
    while True:
        nombre = form_data.get(f"adicional_nombre_{index}")
        valor = form_data.get(f"adicional_valor_{index}")
        if not nombre or not valor:
            break
        try:
            items.append({"descripcion": nombre, "valor": float(valor)})
        except ValueError:
            pass  # puedes registrar el error si lo deseas
        index += 1
    return items


