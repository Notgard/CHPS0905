import numpy as np
from scipy.ndimage import gaussian_filter
from imageio import imread, imwrite

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

def gaussian_denoise(input_filename, output_filename=None, sigma=1.0):
    """
        Apply Gaussian filter to denoise an image.
        Parameters:
        input_filename (str): Path to the input image file.
        output_filename (str, optional): Path to save the denoised image file. If not provided, 
                                        the output filename will be generated based on the input filename.
        sigma (float, optional): Standard deviation for Gaussian kernel. Default is 1.0.
        Returns:
        str: Path to the saved denoised image file.
        Raises:
        FileNotFoundError: If the input file is not found.
    """
    # Read the input image
    image = imread(input_filename)
    
    if image is None:
        raise FileNotFoundError(f"Input file {input_filename} not found.")
    
    # Apply Gaussian filter to denoise the image
    denoised_image = gaussian_filter(image, sigma=sigma)
    
    # If output filename is not provided, create one based on input filename
    if output_filename is None:
        output_filename = input_filename.rsplit('.', 1)[0] + '_denoised.' + input_filename.rsplit('.', 1)[1]
    
    # Save the denoised image
    imwrite(output_filename, denoised_image)
    
    return output_filename

# Example usage:
# denoised_image_path = gaussian_denoise('input_image.jpg', 'output_image.jpg')

def add_gaussian_noise(input_filename, input_dir="images/", output_dir=None):
    """
        Add Gaussian noise to an image.
        Parameters:
        input_filename (str): Path to the input image file.
        Returns:
        ndarray: Noisy image array.
        Raises:
        FileNotFoundError: If the input file is not found.
    """
    filepath = input_dir + input_filename
    print(filepath)
    # Read the input image
    image = imread(filepath)
    
    print(image.shape)
    
    if image is None:
        raise FileNotFoundError(f"Input file {filepath} not found.")
    
    # Generate Gaussian noise
    noise = np.random.normal(loc=0, scale=25, size=image.shape)
    
    # Add Gaussian noise to the image
    noisy_image = image + noise
    print(noisy_image.shape)
    
    noisy_image = np.clip(noisy_image, 0, 255).astype(np.uint8)
    
    print(noisy_image.shape)
    
    # Extract the filename without extension
    base_filename = input_filename.rsplit('.', 1)[0]
    if output_dir:
        # Create the output filename by adding '_gnoise' before the extension
        output_filename = output_dir + base_filename + '_gnoise.' + input_filename.rsplit('.', 1)[1]
    else:
        output_filename = base_filename + '_gnoise.' + input_filename.rsplit('.', 1)[1]
        
    print(noisy_image.shape)
    
    # Save the noisy image
    imwrite(output_filename, noisy_image)
    
    return output_filename

def add_rician_noise(input_filename, input_dir="images/", output_dir=None):
    """
        Add Rician noise to an image.
        Parameters:
        input_filename (str): Path to the input image file.
        Returns:
        ndarray: Noisy image array.
        Raises:
        FileNotFoundError: If the input file is not found.
    """
    filepath = input_dir + input_filename
    # Read the input image
    image = imread(filepath)
    
    if image is None:
        raise FileNotFoundError(f"Input file {filepath} not found.")
    
    # Parameters of Rician noise
    v = 8
    s = 5
    N = image.size

    noise = np.random.normal(scale=s, size=(N, 2)) + [[v,0]]
    noise = np.linalg.norm(noise, axis=1)
    
    # Add Gaussian noise to the image
    noisy_image = image + noise.reshape(image.shape)
    
    noisy_image = np.clip(noisy_image, 0, 255).astype(np.uint8)
    
    # Extract the filename without extension
    base_filename = input_filename.rsplit('.', 1)[0]
    if output_dir:
        # Create the output filename by adding '_gnoise' before the extension
        output_filename = output_dir + base_filename + '_rnoise.' + input_filename.rsplit('.', 1)[1]
    else:
        output_filename = base_filename + '_rnoise.' + input_filename.rsplit('.', 1)[1]
    # Save the noisy image
    imwrite(output_filename, noisy_image)
    
    return output_filename

def add_salt_and_pepper_noise(input_filename, input_dir="images/", output_dir=None):
    """
        Add Salt and Pepper noise to an image.
        Parameters:
        input_filename (str): Path to the input image file.
        Returns:
        ndarray: Noisy image array.
        Raises:
        FileNotFoundError: If the input file is not found.
    """
    filepath = input_dir + input_filename
    # Read the input image
    image = imread(filepath)
    
    if image is None:
        raise FileNotFoundError(f"Input file {filepath} not found.")
    
    # Parameters of Salt and Pepper noise
    p = 0.05
    q = 0.05
    N = image.size
    
    # Generate Salt and Pepper noise
    noise = np.random.choice([0, 1, 2], size=N, p=[1-p-q, p, q])
    noise = noise.reshape(image.shape)
    
    # Add Salt and Pepper noise to the image
    noisy_image = image.copy()
    noisy_image[noise == 1] = 0
    noisy_image[noise == 2] = 255
    
    noisy_image = np.clip(noisy_image, 0, 255).astype(np.uint8)
    
    # Extract the filename without extension
    base_filename = input_filename.rsplit('.', 1)[0]
    if output_dir:
        # Create the output filename by adding '_gnoise' before the extension
        output_filename = output_dir + base_filename + '_spnoise.' + input_filename.rsplit('.', 1)[1]
    else:
        output_filename = base_filename + '_spnoise.' + input_filename.rsplit('.', 1)[1]
    # Save the noisy image
    imwrite(output_filename, noisy_image)
    
    return output_filename

def display_images(noise_img_path, denoised_img_path, original_img_path):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    ax = axes.ravel()

    ax[0].imshow(mpimg.imread(original_img_path))
    ax[0].set_title('Original Image')
    ax[0].axis('off')

    ax[1].imshow(mpimg.imread(noise_img_path))
    ax[1].set_title('Noisy Image')
    ax[1].axis('off')

    ax[2].imshow(mpimg.imread(denoised_img_path))
    ax[2].set_title('Denoised Image')
    ax[2].axis('off')

    plt.show()