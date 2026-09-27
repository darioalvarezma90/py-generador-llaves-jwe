

import argparse
import zlib
from jwcrypto import jwk, jwe

def encriptar_a_disco(archivo_entrada, archivo_salida, ruta_clave_publica):
    print(f"--- Iniciando proceso cliente: {archivo_entrada} ---")
    
    # 1. Leer el archivo de texto original
    try:
        with open(archivo_entrada, 'rb') as f:
            contenido_original = f.read()
    except FileNotFoundError:
        print("❌ Error: No se encuentra el archivo de entrada.")
        return

    # 2. COMPRESIÓN (Optimización previa al cifrado)
    # Reducimos el tamaño antes de aplicar criptografía.
    contenido_comprimido = zlib.compress(contenido_original)
    print(f"Tamaño original: {len(contenido_original)} bytes")
    print(f"Tamaño comprimido: {len(contenido_comprimido)} bytes")

    # 3. Cargar la Clave Pública del Servidor
    with open(ruta_clave_publica, 'r') as f:
        pub_key = jwk.JWK.from_json(f.read())

    # 4. CONFIGURACIÓN DEL JWE
    # [JWE ESTÁNDAR] Definimos el "JOSE Header" (Javascript Object Signing and Encryption)
    # "alg": RSA-OAEP-256 -> Algoritmo asimétrico para cifrar la clave de sesión (Content Encryption Key).
    # "enc": A256GCM      -> AES-256 Galois/Counter Mode. Cifra el contenido real y garantiza integridad.
    protected_header = {
        "alg": "RSA-OAEP-256",
        "enc": "A256GCM",
        "typ": "JWE",       # Tipo de token
        "cty": "zlib"       # Content Type (Opcional, indicamos que dentro hay algo comprimido)
    }

    # Instanciamos el objeto JWE con el payload (bytes comprimidos) y el header
    jwe_token = jwe.JWE(
        plaintext=contenido_comprimido,
        protected=protected_header # type: ignore
    )

    # [JWE ESTÁNDAR] Añadimos el destinatario.
    # La librería generará una clave aleatoria (CEK), cifrará el payload con ella,
    # y luego cifrará la CEK usando la llave pública RSA.
    jwe_token.add_recipient(pub_key)

    # [JWE ESTÁNDAR] Serialización Compacta.
    # Genera un string con formato: Header.KeyCifrada.IV.Ciphertext.Tag
    # Todo codificado en Base64URL.
    contenido_encriptado = jwe_token.serialize(compact=True)

    # 5. Escribir en disco el archivo encriptado
    # Se guarda como texto porque JWE es una cadena Base64 segura para URL/Archivos.
    with open(archivo_salida, 'w') as f:
        f.write(contenido_encriptado)

    print(f"✅ Archivo encriptado guardado en: {archivo_salida}")

# --- Ejecución ---
def main():
    parser = argparse.ArgumentParser(description="Comprime y cifra un archivo en formato JWE.")
    parser.add_argument("--key-file", required=True, help="Ruta del archivo JWK con la clave pública.")
    parser.add_argument("--in", dest="archivo_entrada", required=True, help="Ruta del archivo que se va a cifrar.")
    parser.add_argument("--out", dest="archivo_salida", required=True, help="Ruta del archivo JWE de salida.")
    args = parser.parse_args()
    encriptar_a_disco(args.archivo_entrada, args.archivo_salida, args.key_file)


if __name__ == "__main__":
    main()