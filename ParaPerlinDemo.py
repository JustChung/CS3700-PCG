from tkinter import *
import tkinter.ttk as ttk
import time
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from perlin_noise_parallel import generate_perlin_noise
from multiprocessing import cpu_count
from collections import namedtuple

Grid = namedtuple("Grid", ["row", "column"] )

class AdjustablePerlin:

    def __init__(self, root):
        root.title("Procedural Parallelization Demo")
        root.geometry("800x600")
        
        bgcolor = "white"
        root.configure(bg=bgcolor)
        
        mainframe = Frame(root, bg=bgcolor)
        mainframe.grid(sticky=(N,W,E,S))

        root.columnconfigure(0, weight=1)
        root.rowconfigure(1, weight=1)
        # Controls Frame
        control_frame = LabelFrame(mainframe, text="Controls", padx=3, pady=3, bg=bgcolor)
        control_frame.grid(row=1, column=0, sticky=(N,W,E,S))

        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(1, weight=1)
        # control_frame.rowconfigure(0, weight=1)
        

        gui_grid = type("Gui Grid", (object,), {"Dimension": Grid(0,0),
                                                "Scale": Grid(0,1),
                                                "CPU": Grid(0,2),
                                                "GenTime": Grid(0,3)})

        # **** DIMENSION CONTROL
        dimension_frame = Frame(control_frame, bg=bgcolor)
        dimension_frame.grid(row=gui_grid.Dimension.row, column=gui_grid.Dimension.column, sticky=(N,W,E,S))
        # Dimension Label
        dim_label = Label(dimension_frame, text="Dimensions", font="Helvetica 25 bold", justify="center", bg=bgcolor)
        dim_label.grid(row=0, column=0)

        dim_slider_frame = Frame(dimension_frame, bg=bgcolor)
        dim_slider_frame.grid(row=1, column=0, sticky=(N,W,E,S))
        # Make Dimension Slider
        self.dimension_input = IntVar()
        self.dimension_input.set(512)
        self.dimension_input.trace_add("write", self.update_noise)
        dimension_slider = ttk.Scale(dim_slider_frame, from_=512, to=3333, orient=HORIZONTAL, variable=self.dimension_input)
      
        # Make Dimension Integer Text
        self.dimension_str = StringVar()
        self.dimension_str.set(str(self.dimension_input.get()))
        dimension_label = Label(dim_slider_frame, textvariable=self.dimension_str, font="Helvetica 25 bold", width=4, justify="center", bg=bgcolor)

        grid_columize_widgets(dimension_slider, dimension_label)


        # **** SCALE CONTROL
        scale_frame = Frame(control_frame, bg=bgcolor)
        scale_frame.grid(row=gui_grid.Scale.row, column=gui_grid.Scale.column, sticky=(N,W,E,S))
        # Scale Text
        Label(scale_frame, text="Scale", font="Helvetica 25 bold", justify="center", bg=bgcolor).grid()

        scale_slider_frame = Frame(scale_frame, bg=bgcolor)
        scale_slider_frame.grid(row=1, column=0, sticky=(N,W,E,S))
        # Make Scale Slider
        self.scale_input = IntVar()
        self.scale_input.set(50)
        self.scale_input.trace_add("write", self.update_noise)
        scale_slider = ttk.Scale(scale_slider_frame, from_=10, to=200, orient=HORIZONTAL, variable=self.scale_input)

        # Make Scale Integer Text
        self.scale_str = StringVar()
        self.scale_str.set(str(self.scale_input.get()))
        scale_label = Label(scale_slider_frame, textvariable=self.scale_str, font="Helvetica 25 bold", width=3, justify="center", bg=bgcolor)
        
        grid_columize_widgets(scale_slider, scale_label)

        # **** CPU CONTROL
        cpu_frame = Frame(control_frame, bg=bgcolor)
        cpu_frame.grid(row=gui_grid.CPU.row, column=gui_grid.CPU.column, sticky=(N,W,E,S))

        # Make Cpu Count Label
        Label(cpu_frame, text="CPU", font="Helvetica 25 bold", justify="center", bg=bgcolor).grid()
        self.cpu_count_label = StringVar()
        self.cpu_count_label.set("1")
        
        # Cpu Count Slider
        cpu_slider_frame = Frame(cpu_frame, bg=bgcolor)
        cpu_slider_frame.grid(row=1, column=0, sticky=(N,W,E,S))

        cpu_count_label = Label(cpu_slider_frame, textvariable=self.cpu_count_label, font="Helvetica 25 bold", width=2, justify="center", bg=bgcolor)
        self.cpu_count_input = IntVar()
        self.cpu_count_input.set(1)
        self.cpu_count_input.trace_add("write", self.update_noise)
        cpu_slider = ttk.Scale(cpu_slider_frame, from_=1, to=cpu_count(), orient=HORIZONTAL, variable=self.cpu_count_input)
        
        grid_columize_widgets(cpu_slider, cpu_count_label)

        # Make Noise Gen Time Label
        Label(mainframe, text="Gen Time:", font="Helvetica 25 bold", justify="center", bg=bgcolor).grid()
        self.noise_gen_time = StringVar()
        self.noise_gen_time.set("0")
        Label(mainframe, textvariable=self.noise_gen_time, font="Helvetica 25 bold", justify="center", bg=bgcolor).grid()

        # Colormap drop down
        cmaps = ["flag", "prism", "ocean", "gist_earth", "terrain", "twilight", "Dark2", "tab20c", "hot", "afmhot", "gist_heat", "gray", "binary"]
        self.cmap_choice = StringVar()
        
        self.cmap_dropdown = ttk.OptionMenu(mainframe, self.cmap_choice, cmaps[0], *cmaps)
        self.cmap_choice.trace_add("write", self.update_noise)
        self.cmap_dropdown.grid()

        # Create noise figure
        fig = Figure(figsize=(5, 5), dpi=100)
        self.plt = fig.add_subplot()
        self.canvas = FigureCanvasTkAgg(fig, master = mainframe)
        self.canvas.get_tk_widget().grid(sticky=(N,W,E,S))
        # Generate noise for first time
        self.update_noise(None, None, None)

        # Give equal weight to each column (Window resize squish)
        for i in range(control_frame.grid_size()[0]):
            control_frame.columnconfigure(i, weight=1)
    
    # Call back to update noise
    def update_noise(self, var, index, mode):
        # Get gui changed values, and update gui labels
        dimension = self.dimension_input.get()
        self.dimension_str.set(str(dimension))
        scale = self.scale_input.get()
        self.scale_str.set(str(scale))
        cpu_count = self.cpu_count_input.get()
        self.cpu_count_label.set(str(cpu_count))

        # Time noise generation
        start_time = time.time()
        # Gen noise
        noise = generate_perlin_noise(dimension, dimension, scale, cpu_count)
        noise_gen_time = time.time() - start_time

        # Update generation time label
        self.noise_gen_time.set(f"{noise_gen_time:.3f}")

        # Clear previous plot and draw new one
        self.plt.cla()
        self.plt.imshow(noise, cmap=self.cmap_choice.get(), interpolation='nearest')
        self.canvas.draw()

def grid_columize_widgets(*widgets: Widget):
    for i, widget in enumerate(widgets):
        widget.grid(row=0, column=i)

if __name__ == "__main__":
    root = Tk()
    root.style = ttk.Style()
    root.style.theme_use("clam")
    AdjustablePerlin(root)
    root.mainloop()