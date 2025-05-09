# Modified performance improved and parallelization changes to VitoshAcademy Perlin
# Vitosh Academy Introduction: https://www.youtube.com/watch?v=5ojp-KPDsLk
# Source: https://github.com/Vitosh/Python_personal/blob/master/JupyterNotebook/Perlin-Noise/Perlin-Noise.ipynb

import numpy as np
from multiprocessing import Pool
import multiprocessing.shared_memory

def plot_noise(noise, plt_title, cmap_given="gray"):
    # Import matplotlib left here, as plotting not necessary to noise gen
    import matplotlib.pyplot as plt
    plt.imshow(noise, cmap=cmap_given, interpolation='nearest')
    plt.title(plt_title)
    plt.show()

def smoothstep(t):
    return t * t * (3 - 2 * t)

def lerp(a, b, t):
    return a + t * (b - a)

def compute_row(y, width, height, scale, gradients, shared_memory_name, shared_memory_dtype):
    """
    Compute row of Perlin noise, using global gradients

    Parameters:
    - y (int): Which row to be computed.
    - width (int): Width of the noise array.
    - scale (int): Scale factor for generating the noise.
    
    Returns:
    - row (1-dimensional array): Perlin noise array of length width.
    """

    # Create a vector of x coordinates for the row
    x = np.arange(width)

    # Compute the grid cell indices and fractional offsets
    cell_x = x // scale
    cell_y = y // scale  # Constant for the row
    cell_offset_x = x / scale - cell_x
    cell_offset_y = y / scale - cell_y  # Constant for the row


    # Fetch the gradient vectors for the four cell corners in a vectorized way.
    # gradients has shape (height//scale + 2, width//scale + 2, 2)
    grad_tl = gradients[cell_y, cell_x]      # Top-left gradients, shape (width, 2)
    grad_tr = gradients[cell_y, cell_x + 1]    # Top-right gradients
    grad_bl = gradients[cell_y + 1, cell_x]    # Bottom-left gradients
    grad_br = gradients[cell_y + 1, cell_x + 1]# Bottom-right gradients

    # SIGNIFICANT numpy performance increase, by dot product on rows
    # Compute the dot products in a vectorized fashion.
    # Each dot product is computed as: (offset_x * grad_x) + (offset_y * grad_y)
    dot_tl = cell_offset_x * grad_tl[:, 0] + cell_offset_y * grad_tl[:, 1]
    dot_tr = (cell_offset_x - 1) * grad_tr[:, 0] + cell_offset_y * grad_tr[:, 1]
    dot_bl = cell_offset_x * grad_bl[:, 0] + (cell_offset_y - 1) * grad_bl[:, 1]
    dot_br = (cell_offset_x - 1) * grad_br[:, 0] + (cell_offset_y - 1) * grad_br[:, 1]

    # Compute the smooth interpolation weights
    weight_x = smoothstep(cell_offset_x)
    weight_y = smoothstep(cell_offset_y)

    # Interpolate horizontally for the top and bottom edges
    interp_top = lerp(dot_tl, dot_tr, weight_x)
    interp_bottom = lerp(dot_bl, dot_br, weight_x)

    # Get shared memory
    shared_memory = multiprocessing.shared_memory.SharedMemory(name=shared_memory_name)
    shared_array = np.ndarray((height, width), dtype=shared_memory_dtype, buffer=shared_memory.buf)

    # Interpolate vertically between the top and bottom interpolations    
    shared_array[y,:] = lerp(interp_top, interp_bottom, weight_y)
    shared_memory.close()

def generate_perlin_noise(width, height, scale, cpu_count=3):
    """
    Generate Perlin noise using the given parameters.
    
    Parameters:
    - width (int): Width of the noise array.
    - height (int): Height of the noise array.
    - scale (int): Scale factor for generating the noise.
    - cpu_count (int) Number of parallel processes to run: 
    
    Returns:
    - noise (n-dimensional array): Perlin noise array of shape (height, width).
    """
    # Must be 0 to keep each run identical
    np.random.seed(0)

    # Empty noise array for shared memory array
    noise = np.zeros((height, width))
    shared_mem = multiprocessing.shared_memory.SharedMemory(create=True, size=noise.nbytes)
    shared_array = np.ndarray(noise.shape, dtype=noise.dtype, buffer=shared_mem.buf)

    # Generate random gradients with dimensions based on the grid
    gradients = np.random.randn(height // scale + 2, width // scale + 2, 2)

    # Prepare arguments for each row, where y is row number, provide shared memory noise to each process
    args = [(y, width, height, scale, gradients, shared_mem.name, noise.dtype) for y in range(height)]

    # Use multiprocessing Pool to compute each row in parallel
    Pool(processes=cpu_count).starmap(compute_row, args)  # Starmap uses arg tuple as multiple arguments

    # Normalize the noise to the range [0, 1]
    array_min = np.min(shared_array)
    divide_by = np.max(shared_array) - array_min
    shared_array = (shared_array - array_min) # Set min to 0
    shared_array /= divide_by # Set new max to 1 normalizing in between
    
    # Close memory
    shared_mem.close()
    shared_mem.unlink()    
    return shared_array

if __name__ == '__main__':
    # Demo Usage

    # Size of noise
    width = 512
    height = 512
    scale = 30  # Scale looks like "zoom" on noise

    # Benchmark parallelization of noise gen
    import time
    for cpu in range(1, 11):  # Pool count of 1 to 4 processes
        start = time.time()
        # Generate Perlin noise with cpu count pool
        noise = generate_perlin_noise(width, height, scale, cpu)
        total = time.time() - start
        print(f"{cpu} Cpu count took: {total:.6f}Seconds")
    
    # print(noise)

    # Example of plot
    plot_noise(noise, "Perlin noise example", cmap_given="twilight")