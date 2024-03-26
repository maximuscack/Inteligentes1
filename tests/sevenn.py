import os
import random
import heapq
import matplotlib.pyplot as plt
from PIL import Image
import imageio
import streamlit as st


''''''


''''''


# Definir una carpeta para almacenar las imágenes
IMAGES_DIR = 'app/data/images'
os.makedirs(IMAGES_DIR, exist_ok=True)


def save_image(step):
    # Generar la imagen usando Matplotlib
    plt.figure()
    plt.text(0.5, 0.5, f'Step: {step}', ha='center', va='center', fontsize=20)
    plt.axis('off')
    plt.savefig(os.path.join(IMAGES_DIR, f'image_{step}.png'))
    plt.close()


def generate_images():
    start = random.choice(list(G.nodes))
    end = random.choice(list(G.nodes))
    a_star(start, end)
    reconstruct_path(start, end)


def create_animation():
    # Crear una lista de nombres de archivos de imágenes
    image_files = [os.path.join(IMAGES_DIR, f'image_{i}.png') for i in range(
        1, len(os.listdir(IMAGES_DIR)) + 1)]

    # Crear una animación a partir de las imágenes
    images = []
    for filename in image_files:
        images.append(imageio.imread(filename))
    imageio.mimsave(os.path.join(IMAGES_DIR, 'animation.gif'), images, fps=1)


# Generar y guardar las imágenes
generate_images()

# Crear la animación
create_animation()

# Mostrar la animación en Streamlit
st.title('Animación de pasos')
animation_path = os.path.join(IMAGES_DIR, 'animation.gif')
st.image(animation_path, use_column_width=True)

# Añadir controles para navegar por la animación
frame_index = st.slider('Seleccionar paso:', 1, len(os.listdir(IMAGES_DIR)), 1)
frame_path = os.path.join(IMAGES_DIR, f'image_{frame_index}.png')
st.image(frame_path, use_column_width=True)
