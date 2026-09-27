# py-generador-llaves-jwe

Herramientas de Python para generar un par de claves RSA de **4096 bits**, cifrar archivos con la clave pública y recuperar su contenido con la clave privada mediante JWE (JSON Web Encryption).

| Script | Función |
| --- | --- |
| `generador_llaves_jwe.py` | Genera las claves pública y privada en formato JWK (JSON Web Key). |
| `encrypt_file.py` | Lee un archivo como bytes, lo comprime con `zlib` y guarda un JWE compacto. |
| `decrypt_file.py` | Descifra el JWE, descomprime su contenido y guarda los bytes originales. |

## Requisitos e instalación

- Python **3.10 o superior**, según los requisitos declarados por las dependencias fijadas en `requirements.txt`.
- `pip` y el módulo `venv`.

Desde la carpeta del proyecto, crea el entorno e instala las dependencias.

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Linux y macOS

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

No es necesario activar el entorno: los comandos utilizan su intérprete directamente.

Los scripts utilizan `jwcrypto` y, para la compresión, el módulo estándar `zlib`. `requirements.txt` fija las versiones de `jwcrypto`, `cryptography`, `cffi`, `pycparser` y `typing_extensions`.

## Uso desde la línea de comandos

Los tres scripts reciben argumentos obligatorios y muestran ayuda con `--help`. El identificador y las rutas se especifican desde la línea de comandos. Las rutas relativas se resuelven desde el **directorio de trabajo del comando**. Usa comillas cuando una ruta o identificador contenga espacios.

Los siguientes ejemplos usan `python`; debe corresponder al entorno donde instalaste las dependencias. Sin activar el entorno, puedes sustituirlo por `.\.venv\Scripts\python.exe` en Windows o `./.venv/bin/python` en Linux y macOS.

### 1. Generar las claves

```bash
python generador_llaves_jwe.py --id="000" # O cualquier cadena no vacia
```

| Argumento | Requerido | Uso |
| --- | --- | --- |
| `--id` | Sí | Cadena no vacía incorporada literalmente a los nombres de ambos archivos. Conserva los ceros iniciales. |

El comando genera estos archivos en el directorio de trabajo:

| Archivo | Contenido y uso |
| --- | --- |
| `public_key_000.json` | JWK público con `kty`, `kid`, `n` y `e`. Se comparte con el cliente que cifra. |
| `private_key_000.json` | JWK con los componentes públicos y privados de la misma clave RSA. Se conserva en el servidor que descifra. |

Los nombres siguen los patrones `public_key_{id}.json` y `private_key_{id}.json`. Por ejemplo:

```bash
python generador_llaves_jwe.py --id="cliente norte-01"
```

Genera `public_key_cliente norte-01.json` y `private_key_cliente norte-01.json`. El argumento admite cualquier cadena no vacía, sin convertirla a número, recortarla ni sustituir caracteres. Al usarse literalmente en nombres de archivo, su escritura queda sujeta a los caracteres y límites de rutas que permite el sistema operativo; los separadores de ruta no se escapan ni se crean directorios automáticamente.

Omitir `--id` o pasar `--id=""` produce un error de argumentos y termina con código de salida `2`, antes de generar claves.

Las claves utilizan RSA de **4096 bits** y el `kid` **`master-key-01`**. El identificador de la línea de comandos cambia los nombres de archivo, no el `kid`. Cada archivo contiene un objeto JWK individual, no un conjunto JWKS ni un archivo PEM.

**Cada ejecución genera un par nuevo y sobrescribe los archivos existentes con el mismo identificador sin confirmación.** Conserva las claves anteriores mientras sean necesarias para descifrar archivos ya cifrados.

### 2. Cifrar un archivo

```bash
python encrypt_file.py --key-file="public_key_000.json" --in="archivo_entrada.txt" --out="archivo_cifrado.txt"
```

| Argumento | Requerido | Uso |
| --- | --- | --- |
| `--key-file` | Sí | Ruta del archivo JWK con la clave pública. Puede tener cualquier nombre. |
| `--in` | Sí | Ruta del archivo que se va a cifrar. |
| `--out` | Sí | Ruta donde se guardará el JWE compacto. |

La función `encriptar_a_disco(archivo_entrada, archivo_salida, ruta_clave_publica)` lee el archivo completo como bytes, aplica `zlib.compress()`, cifra y escribe un token JWE compacto como texto. Muestra los tamaños original y comprimido y la ruta de salida. Esos tamaños no incluyen el tamaño final del JWE.

El cifrador y el descifrador admiten archivos de texto o binarios; el contenido original se conserva como bytes.

### 3. Descifrar el archivo

```bash
python decrypt_file.py --key-file="private_key_000.json" --in="archivo_cifrado.txt" --out="archivo_recuperado.txt"
```

| Argumento | Requerido | Uso |
| --- | --- | --- |
| `--key-file` | Sí | Ruta del archivo JWK con la clave privada correspondiente. |
| `--in` | Sí | Ruta del archivo JWE que se va a descifrar. |
| `--out` | Sí | Ruta donde se guardará el archivo recuperado. |

La función `desencriptar_desde_disco(archivo_encriptado, archivo_salida_final, ruta_clave_privada)` carga la clave privada, descifra y verifica el JWE, aplica `zlib.decompress()` y escribe los bytes recuperados en modo binario (`wb`). Así conserva la codificación y los saltos de línea del archivo original. Muestra la ruta de salida sin imprimir el contenido recuperado.

Elige una salida distinta del original si necesitas conservarlo. Las carpetas de destino deben existir.

### Ejemplo completo

Con un archivo `archivo_entrada.txt` en el directorio de trabajo:

```bash
python generador_llaves_jwe.py --id="000" # O cualquier cadena no vacia
python encrypt_file.py --key-file="public_key_000.json" --in="archivo_entrada.txt" --out="archivo_cifrado.txt"
python decrypt_file.py --key-file="private_key_000.json" --in="archivo_cifrado.txt" --out="archivo_recuperado.txt"
```

La extensión `.txt` del archivo cifrado es válida: su contenido sigue siendo un JWE compacto. Los scripts utilizan las rutas indicadas sin exigir una extensión específica.

También se acepta separar cada opción de su valor con un espacio, por ejemplo `--id "000"`.

```bash
python generador_llaves_jwe.py --help
python encrypt_file.py --help
python decrypt_file.py --help
```

## Formato del archivo cifrado

El cifrador define esta cabecera protegida:

```json
{
  "alg": "RSA-OAEP-256",
  "enc": "A256GCM",
  "typ": "JWE",
  "cty": "zlib"
}
```

`RSA-OAEP-256` se utiliza para cifrar la clave de contenido con la clave pública RSA; `A256GCM` cifra el contenido comprimido. La serialización contiene cinco segmentos Base64URL separados por puntos:

```text
cabecera.clave_cifrada.iv.contenido_cifrado.etiqueta_autenticacion
```

La compresión se realiza explícitamente mediante `zlib.compress()` antes de construir el JWE. El código declara `cty: zlib` y no configura un parámetro `zip`; el receptor debe aplicar la descompresión correspondiente después del descifrado. El descifrador actual llama a `zlib.decompress()` siempre, sin comprobar `cty`.

El `kid` de los archivos JWK no se incorpora explícitamente a la cabecera del token. El descifrador utiliza la clave indicada por su ruta y no implementa selección entre varias claves. Tampoco fija una lista propia de algoritmos permitidos: utiliza la configuración predeterminada de `jwcrypto.JWE()`.

## Limitaciones y manejo de errores

- Todos los archivos de salida se abren en modo de sobrescritura. No se solicita confirmación ni se crean carpetas de destino.
- La clave privada se guarda como JSON sin cifrado ni contraseña. El generador no establece permisos especiales; evita compartirla o incorporarla al repositorio.
- El `kid` permanece fijo aunque se generen claves nuevas. El proyecto no administra rotación ni almacenamiento seguro de claves.
- Los archivos se procesan completos en memoria, incluyendo compresión y descompresión. No hay procesamiento por bloques ni límites explícitos de tamaño.
- El cifrador captura la ausencia del archivo de entrada. Los errores al cargar la clave pública, cifrar o escribir se propagan como excepciones.
- El descifrador captura la ausencia de la clave privada o del archivo cifrado, y los errores de deserialización o descifrado del JWE. Una clave privada con JSON inválido, errores de descompresión o escritura quedan fuera de esas capturas.
- Los argumentos obligatorios ausentes producen un error y código de salida `2`. Los errores capturados dentro de las funciones de procesamiento se imprimen y la función retorna sin señalar un código de salida distinto de cero. Para automatizar el flujo, no basta con comprobar el código de salida del proceso.

## Estructura del proyecto

```text
py-generador-llaves-jwe/
├── .gitignore              # Exclusiones del control de versiones.
├── generador_llaves_jwe.py  # Generación y exportación de claves RSA/JWK.
├── encrypt_file.py         # Compresión y cifrado JWE con la clave pública.
├── decrypt_file.py         # Descifrado, descompresión y escritura binaria.
├── requirements.txt        # Dependencias con versiones fijadas.
└── README.md               # Instalación, configuración, uso y limitaciones.
```
