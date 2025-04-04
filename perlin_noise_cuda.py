# Source: https://github.com/Vitosh/Python_personal/blob/master/JupyterNotebook/Perlin-Noise/Perlin-Noise.ipynb
# Parallel not working

import math
import random
import numpy as np
import matplotlib.pyplot as plt
import pycuda.driver as cuda
import pycuda.autoinit, pycuda.compiler

def plot_noise(noise, plt_title, cmap_given = "gray"):
    plt.imshow(noise, cmap=cmap_given, interpolation='nearest')
    #plt.colorbar()
    plt.title(plt_title)
    plt.show()

mod = pycuda.compiler.SourceModule("""
#include <stdio.h>
__device__ float smoothstep(float t) {
  return t * t * (3 - 2 * t);
}
__device__ float lerp(float a, float b, float t) {
  return a + t * (b - a);
}
__global__ void generate_perlin_noise(float *noise, float *gradients, int scale) {
  const int x = threadIdx.x;
  const int y = threadIdx.y;
  int idx = threadIdx.x + threadIdx.y*32;
  printf("I am %d.%d\\n", threadIdx.x, threadIdx.y);

  int cell_x = x / scale;
  int cell_y = y / scale;

  float cell_offset_x = (float) x / scale - cell_x;
  float cell_offset_y = (float) y / scale - cell_y;

  float dot_product_tl = cell_offset_x * gradients[cell_x*10+cell_y*2] + cell_offset_y * gradients[cell_x*10+cell_y*2+1];
  float dot_product_tr = (cell_offset_x-1) * gradients[(cell_x+1)*10+cell_y*2] + cell_offset_y * gradients[(cell_x+1)*10+cell_y*2+1];
  float dot_product_bl = cell_offset_x * gradients[cell_x*10+(cell_y+1)*2] + (cell_offset_y-1) * gradients[cell_x*10+(cell_y+1)*2+1];
  float dot_product_br = (cell_offset_x-1) * gradients[(cell_x+1)*10+(cell_y+1)*2] + (cell_offset_y-1) * gradients[(cell_x+1)*10+(cell_y+1)*2+1];

  float weight_x = smoothstep(cell_offset_x);
  float weight_y = smoothstep(cell_offset_y);
  float interpolated_top = lerp(dot_product_tl, dot_product_tr, weight_x);
  float interpolated_bottom = lerp(dot_product_bl, dot_product_br, weight_x);
  float interpolated_value = lerp(interpolated_top, interpolated_bottom, weight_y);

  noise[idx] = interpolated_value;

}
""")

# CUDA 10+ supports maximum 1024 Threads - max sized noise map is 32x32
HEIGHT = 32
WIDTH = 32
SCALE = np.int32(10)

a = np.random.randn(HEIGHT,WIDTH).astype(np.float32)
gradients = np.random.randn(HEIGHT // SCALE + 2, WIDTH // SCALE + 2, 2).astype(np.float32)

a_dev = cuda.mem_alloc(a.nbytes)
b_dev = cuda.mem_alloc(gradients.nbytes)

cuda.memcpy_htod(a_dev, a)
cuda.memcpy_htod(b_dev, gradients)

func = mod.get_function("generate_perlin_noise")
func(a_dev, b_dev, SCALE, block=(HEIGHT,WIDTH,1))
cuda.Context.synchronize() # May not be necessary?

a_result = np.empty_like(a)
cuda.memcpy_dtoh(a_result, a_dev)
# print ("Input Matrix")
# print (a)
print ("Output Matrix")
print(a_result)

# Normalize
noise = (a_result - np.min(a_result)) / (np.max(a_result) - np.min(a_result))
plot_noise(noise, "Perlin noise example", cmap_given = "twilight")