# servidor_decrypt.py
import argparse
import zlib
from jwcrypto import jwk, jwe

def desencriptar_desde_disco(archivo_encriptado, archivo_salida_final, ruta_clave_privada):
    print(f"--- Iniciando proceso servidor: {archivo_encriptado} ---")

    # 1. Cargar la Clave Privada (Solo el servidor la tiene)
    try:
        with open(ruta_clave_privada, 'r') as f:
            priv_key = jwk.JWK.from_json(f.read())
    except FileNotFoundError:
        print("❌ Error: No se encuentra la clave privada.")
        return

    # 2. Leer el archivo JWE del disco
    try:
        with open(archivo_encriptado, 'r') as f:
            jwe_string = f.read()
    except FileNotFoundError:
        print("❌ Error: No se encuentra el archivo encriptado.")
        return

    # 3. PROCESO DE DESENCRIPTADO JWE
    try:
        # Instanciamos un objeto JWE vacío
        jwe_token = jwe.JWE()

        # [JWE ESTÁNDAR] Deserialización y Descifrado
        # La función 'deserialize':
        #   a. Lee el Header para saber qué algoritmos usar.
        #   b. Usa la clave privada RSA para descifrar la clave simétrica (CEK).
        #   c. Usa la CEK para descifrar el contenido (AES-256-GCM).
        #   d. Verifica el "Auth Tag". Si el archivo fue modificado un solo bit, esto FALLA.
        jwe_token.deserialize(jwe_string, key=priv_key)

        # Si llegamos aquí, la criptografía es válida y auténtica.
        payload_comprimido = jwe_token.payload

    except Exception as e:
        print(f"⛔ ERROR DE SEGURIDAD: El archivo está corrupto o la clave es incorrecta.\nDetalle: {e}")
        return

    # 4. Descomprimir
    contenido_recuperado = zlib.decompress(payload_comprimido)

    # 5. Guardar los bytes originales sin convertir codificación ni saltos de línea.
    with open(archivo_salida_final, 'wb') as f:
        f.write(contenido_recuperado)

    print(f"✅ Archivo desencriptado y guardado en: {archivo_salida_final}")



# --- Ejecución ---
def main():
    parser = argparse.ArgumentParser(description="Descifra un archivo JWE y recupera el archivo original.")
    parser.add_argument("--key-file", required=True, help="Ruta del archivo JWK con la clave privada.")
    parser.add_argument("--in", dest="archivo_entrada", required=True, help="Ruta del archivo JWE que se va a descifrar.")
    parser.add_argument("--out", dest="archivo_salida", required=True, help="Ruta del archivo recuperado.")
    args = parser.parse_args()
    desencriptar_desde_disco(args.archivo_entrada, args.archivo_salida, args.key_file)


if __name__ == "__main__":
    main()
