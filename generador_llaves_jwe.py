
# Script para generar clave pública (para compartir con cliente)
# y clave privada (para uso en servidor)

import argparse
from jwcrypto import jwk

def identificador_no_vacio(valor: str) -> str:
    if not valor:
        raise argparse.ArgumentTypeError("El identificador no puede estar vacío.")
    return valor


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera un par de claves RSA en formato JWK.")
    parser.add_argument(
        "--id", required=True, type=identificador_no_vacio,
        help="Identificador no vacío para los archivos public_key_ID.json y private_key_ID.json.",
    )
    args = parser.parse_args()
    cvePreval = args.id

    # Generar par de claves RSA 4096
    rsaKey = jwk.JWK.generate(kty='RSA', size=4096, kid='master-key-01')

    # Compartir con cliente.
    publicKeyFile = f"public_key_{cvePreval}.json"
    with open(publicKeyFile, "w") as fout:
        fout.write(rsaKey.export_public())
    
    # Solo para servidor
    privateKeyFile = f"private_key_{cvePreval}.json"
    with open(privateKeyFile, "w") as fout:
        fout.write(rsaKey.export_private())
    
    print(f"[{publicKeyFile}, {privateKeyFile}] generados para prevalidador {cvePreval} :)")
    return


if __name__ == "__main__":
    main()
