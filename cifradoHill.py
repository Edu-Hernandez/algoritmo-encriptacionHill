import os
import numpy as np
from sympy import Matrix
from numpy.linalg import inv
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from tqdm import tqdm  # Barra de progreso

# ----------------------
# Funciones Auxiliares
# ----------------------

def generate_invertible_matrix(n, mod):
    """
    Genera una matriz invertible de tamaño n x n en el módulo mod.
    """
    while True:
        matrix = np.random.randint(1, mod, size=(n, n))  
        det = int(np.round(np.linalg.det(matrix)))  
        if np.gcd(det, mod) == 1:
            return matrix

def mod_matrix_inverse(matrix, mod):
    """
    Calcula la inversa modular de la matriz dada en un módulo específico.
    """
    det = int(round(np.linalg.det(matrix)))  
    det_inv = pow(det, -1, mod) 
    matrix_mod_inv = (det_inv * Matrix(matrix).adjugate() % mod)  
    return np.array(matrix_mod_inv).astype(int) % mod

def pad_data(data, block_size):
    """
    Aplica padding al archivo para que su tamaño sea un múltiplo del tamaño del bloque.
    """
    padding_length = (block_size - len(data) % block_size) % block_size
    return data + bytes([padding_length] * padding_length)

def unpad_data(data):
    """
    Elimina el padding del archivo descifrado.
    """
    padding_length = data[-1]
    return data[:-padding_length]

# ----------------------
# Cifrado y Descifrado
# ----------------------

def hill_encrypt(file_path, output_path, key_size, mod=256):
    
    with open(file_path, "rb") as f:
        data = f.read()

    key = generate_invertible_matrix(key_size, mod)  # Generar clave
    padded_data = pad_data(data, key_size)  # Aplicar padding

    encrypted_data = bytearray()
    num_blocks = len(padded_data) // key_size
    with tqdm(total=num_blocks, desc="Cifrando archivo", unit="bloque") as pbar:
        for i in range(0, len(padded_data), key_size):
            block = np.array(list(padded_data[i : i + key_size])).reshape(-1, 1)
            encrypted_block = np.dot(key, block) % mod
            encrypted_data.extend(encrypted_block.flatten().astype(np.uint8))
            pbar.update(1)  

    os.makedirs(os.path.dirname(output_path), exist_ok=True)  # Crear carpeta si no existe
    with open(output_path, "wb") as f:
        f.write(encrypted_data)

    np.save(output_path + ".key", key)  
    print(f"Archivo cifrado guardado en: {output_path}")
    print(f"Clave guardada en: {output_path}.key")

def hill_decrypt(encrypted_path, output_path, key_path, mod=256):
    """
    Descifra un archivo utilizando el algoritmo de Hill y la clave correspondiente.
    """
    with open(encrypted_path, "rb") as f:
        encrypted_data = f.read()
    key = np.load(key_path)  # Cargar la clave

    key_inverse = mod_matrix_inverse(key, mod) 

    decrypted_data = bytearray()
    num_blocks = len(encrypted_data) // key.shape[0]
    with tqdm(total=num_blocks, desc="Descifrando archivo", unit="bloque") as pbar:
        for i in range(0, len(encrypted_data), key.shape[0]):
            block = np.array(list(encrypted_data[i : i + key.shape[0]])).reshape(-1, 1)
            decrypted_block = np.dot(key_inverse, block) % mod
            decrypted_data.extend(decrypted_block.flatten().astype(np.uint8))
            pbar.update(1) 

    decrypted_data = unpad_data(decrypted_data)  # Eliminar padding

    os.makedirs(os.path.dirname(output_path), exist_ok=True)  
    with open(output_path, "wb") as f:
        f.write(decrypted_data)

    print(f"Archivo descifrado guardado en: {output_path}")

# ----------------------
# Cargar archivo desde interfaz gráfica (Tkinter)
# ----------------------

def select_file():
   
    root = Tk()
    root.withdraw() 
    file_path = askopenfilename()  
    return file_path

def save_file(file_name):
    """
    Guarda el archivo en una ubicación fija.
    """
    save_path = r"C:\Users\USER\Desktop\cifrado\encrypted"  
    os.makedirs(save_path, exist_ok=True)  # Crear la carpeta si no existe
    return os.path.join(save_path, f"encrypted_{file_name}")  

# ----------------------
# Ejemplo de Uso con Tkinter para seleccionar archivo
# ----------------------

original_file = select_file()

if original_file:  
    
    block_size = 3 
    modulo = 256  

    file_name = os.path.basename(original_file) 
    encrypted_file = save_file(file_name)  
    decrypted_file = save_file(f"decrypted_{file_name}") 

    # Cifrado
    hill_encrypt(original_file, encrypted_file, block_size, mod=modulo)

else:
    print("No se seleccionó ningún archivo.")
