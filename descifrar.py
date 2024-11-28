import numpy as np
from sympy import Matrix
from tkinter import Tk, filedialog
from tqdm import tqdm
import os


def mod_matrix_inverse(matrix, mod):
    det = int(round(np.linalg.det(matrix)))  
    det_inv = pow(det, -1, mod)  
    matrix_mod_inv = (
        det_inv * Matrix(matrix).adjugate() % mod
    ) 
    return np.array(matrix_mod_inv).astype(int) % mod

def unpad_data(data):
    padding_length = data[-1]
    return data[:-padding_length]

def hill_decrypt(encrypted_path, output_path, key_path, mod=256):
    with open(encrypted_path, "rb") as f:
        encrypted_data = f.read()
    key = np.load(key_path)  

    key_inverse = mod_matrix_inverse(key, mod)  

    decrypted_data = bytearray()
    num_blocks = len(encrypted_data) // key.shape[0]  
    with tqdm(total=num_blocks, desc="Descifrando archivo", unit="bloque") as pbar:
        for i in range(0, len(encrypted_data), key.shape[0]):
            block = np.array(list(encrypted_data[i:i + key.shape[0]])).reshape(-1, 1)
            decrypted_block = np.dot(key_inverse, block) % mod 
            decrypted_data.extend(decrypted_block.flatten().astype(np.uint8))
            pbar.update(1)  # Actualizar barra de progreso

    decrypted_data = unpad_data(decrypted_data)  # Eliminar padding

    # Guardar el archivo descifrado en la ruta especificada
    with open(output_path, "wb") as f:
        f.write(decrypted_data)

    print(f"Archivo descifrado guardado en: {output_path}")

def select_file(title):
    root = Tk()
    root.withdraw() 
    file_path = filedialog.askopenfilename(title=title)
    return file_path

def main():
    print("Selecciona el archivo cifrado:")
    encrypted_file = select_file("Seleccionar archivo cifrado")
    
    if not encrypted_file:
        print("No se seleccionó el archivo cifrado.")
        return

    print("Selecciona el archivo de clave:")
    key_file = select_file("Seleccionar archivo de clave")
    
    if not key_file:
        print("No se seleccionó el archivo de clave.")
        return

    print("Selecciona la carpeta donde guardar el archivo descifrado:")
    output_dir = filedialog.askdirectory(title="Seleccionar carpeta de salida")
    
    if not output_dir:
        print("No se seleccionó la carpeta de salida.")
        return

    output_file = os.path.join(output_dir, os.path.basename(encrypted_file).replace("encrypted_", "descifrado_"))

    hill_decrypt(encrypted_file, output_file, key_file)

if __name__ == "__main__":
    main()
