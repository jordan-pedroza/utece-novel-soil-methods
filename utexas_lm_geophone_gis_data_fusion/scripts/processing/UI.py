import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import scipy.signal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class SplashScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Home Screen")

        # Load the background image using Pillow
        self.bg_image = Image.open("f35-zoom.jpg")
        self.bg_image = ImageTk.PhotoImage(self.bg_image)

        # Create a label to hold the background image
        self.bg_label = tk.Label(self.root, image=self.bg_image)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.header_label = tk.Label(
            self.root,
            text="Welcome to LM UT ECE Emergency Landing Senior Design Project",
            font=('Helvetica', 24, 'bold'),  # Bigger font for header
            bg='#f0f0f0',  # Background color
            fg='#333333'  # Text color (dark gray)
        )
        self.header_label.pack(pady=(50, 20))  # Add padding (top=50, bottom=20)
        # Add a button to move to the main screen
        self.check_graphs_button = tk.Button(
            self.root,
            text="Check Graphs",
            command=self.go_to_main_screen,
            font=('Helvetica', 16, 'bold'),  # Bigger, bold font
            bg='#FFFFFF',  # Background color (e.g., green)
            fg='black',  # Text color (white)
            activebackground='#45a049',  # Background color when the button is pressed
            activeforeground='white',  # Text color when the button is pressed
            padx=20,  # Add padding to make the button larger horizontally
            pady=10  # Add padding to make the button larger vertically
        )
        self.check_graphs_button.pack(expand=True, fill=tk.NONE)

    def go_to_main_screen(self):
        self.root.destroy()
        main_root = tk.Tk()
        app = DataProcessorApp(main_root)
        main_root.mainloop()


class DataProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Geophone Data Processor")

        # Create UI elements
        self.create_widgets()

    def create_widgets(self):
        # File selection buttons
        self.load_button1 = tk.Button(self.root, text="Load Signal 1", command=self.load_signal1)
        self.load_button1.pack(pady=5)

        self.load_button2 = tk.Button(self.root, text="Load Signal 2", command=self.load_signal2)
        self.load_button2.pack(pady=5)

        # Process button
        self.process_button = tk.Button(self.root, text="Process Data", command=self.process_data)
        self.process_button.pack(pady=10)

        # Plot area
        self.figure, self.ax = plt.subplots(2, 2, figsize=(10, 8))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.signal1 = None
        self.signal2 = None
        self.duration = 60
        self.sampling_rate = None

    def load_signal1(self):
        filepath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if filepath:
            with open(filepath, 'r') as f:
                self.signal1 = list(map(float, f.readlines()))
            self.sampling_rate = len(self.signal1) / self.duration
            messagebox.showinfo("Success", "Signal 1 loaded successfully.")

    def load_signal2(self):
        filepath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if filepath:
            with open(filepath, 'r') as f:
                self.signal2 = list(map(float, f.readlines()))
            messagebox.showinfo("Success", "Signal 2 loaded successfully.")

    def process_data(self):
        if self.signal1 is None or self.signal2 is None:
            messagebox.showerror("Error", "Please load both signals first.")
            return

        # Ensure signals are the same length
        min_len = min(len(self.signal1), len(self.signal2))
        self.signal1 = self.signal1[:min_len]
        self.signal2 = self.signal2[:min_len]

        # Time axis
        t = np.linspace(-self.duration, self.duration, len(self.signal1), endpoint=False)

        # Remove DC component
        b, a = scipy.signal.butter(5, 3, btype='highpass', fs=self.sampling_rate)
        signal1 = scipy.signal.lfilter(b, a, self.signal1)
        signal2 = scipy.signal.lfilter(b, a, self.signal2)

        # Remove out of band noise
        b, a = scipy.signal.butter(5, self.sampling_rate / 2 - 1, btype='lowpass', fs=self.sampling_rate)
        signal1 = scipy.signal.lfilter(b, a, signal1)
        signal2 = scipy.signal.lfilter(b, a, signal2)

        # Correlation Calculations
        correlation = scipy.signal.correlate(signal1, signal2, mode='full')
        correlation_lags = scipy.signal.correlation_lags(len(self.signal1), len(self.signal2), mode='full')

        # FFT Calculations
        N = len(signal1)
        T = 1 / self.sampling_rate
        fft_freq = np.fft.fftfreq(N, d=T)
        fft_output1 = np.fft.fft(signal1)
        fft_output2 = np.fft.fft(signal2)

        # Plot results
        self.ax[0, 0].clear()
        self.ax[0, 0].plot(t, signal1, linewidth=0.5, label='Signal 1')
        self.ax[0, 0].plot(t, signal2, linewidth=0.5, label='Signal 2')
        self.ax[0, 0].set_title('Input Signals')
        self.ax[0, 0].set_xlabel('Time (s)')
        self.ax[0, 0].set_ylabel('Amplitude')
        self.ax[0, 0].legend()

        self.ax[0, 1].clear()
        self.ax[0, 1].stem(correlation_lags, correlation, markerfmt=" ", basefmt="-b")
        self.ax[0, 1].set_title('Correlation')
        self.ax[0, 1].set_xlabel('Lag (samples)')
        self.ax[0, 1].set_ylabel('Magnitude')
        self.ax[0, 1].set_xlim(0, len(correlation) // 2)

        zoom_factor = 10
        self.ax[1, 0].clear()
        self.ax[1, 0].plot(t[:len(t) // zoom_factor], signal1[:len(t) // zoom_factor], linewidth=0.5, label='Signal 1')
        self.ax[1, 0].plot(t[:len(t) // zoom_factor], signal2[:len(t) // zoom_factor], linewidth=0.5, label='Signal 2')
        self.ax[1, 0].set_title(f'Input Signals ({zoom_factor}x Zoom)')
        self.ax[1, 0].set_xlabel('Time (s)')
        self.ax[1, 0].set_ylabel('Amplitude')
        self.ax[1, 0].legend()

        self.ax[1, 1].clear()
        self.ax[1, 1].plot(fft_freq[:N // 2], np.abs(fft_output1[:N // 2]), 'b', label='FFT Signal 1')
        self.ax[1, 1].plot(fft_freq[:N // 2], np.abs(fft_output2[:N // 2]), 'r', label='FFT Signal 2')
        self.ax[1, 1].set_title('Magnitude of FFT')
        self.ax[1, 1].set_xlabel('Frequency (Hz)')
        self.ax[1, 1].set_ylabel('Magnitude')
        self.ax[1, 1].set_xlim(0, self.sampling_rate / 2)
        self.ax[1, 1].grid()
        self.ax[1, 1].legend()

        self.figure.tight_layout()
        self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    splash = SplashScreen(root)
    root.mainloop()
