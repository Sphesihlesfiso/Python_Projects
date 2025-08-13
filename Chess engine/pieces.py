import pygame
import numpy as np
import os
import wave

def generate_and_save_sound(filename, frequency, duration, volume):
    """Generates a sine wave and saves it as a WAV file."""
    sample_rate = 44100
    num_samples = int(sample_rate * duration)
    amplitude = np.iinfo(np.int16).max * volume
    
    # Generate a sine wave
    sine_wave = amplitude * np.sin(2 * np.pi * frequency * np.arange(num_samples) / sample_rate)
    
    # Convert to 16-bit integers
    int_sine_wave = sine_wave.astype(np.int16)

    # Ensure the 'sounds' directory exists
    if not os.path.exists("sounds"):
        os.makedirs("sounds")
        
    output_path = os.path.join("sounds", filename)

    # Write to a WAV file
    with wave.open(output_path, 'w') as obj:
        obj.setnchannels(1)  # Mono
        obj.setsampwidth(2)  # 16-bit
        obj.setframerate(sample_rate)
        obj.writeframes(int_sine_wave.tobytes())

if __name__ == '__main__':
    # You can customize these values to create different sounds
    generate_and_save_sound('move.wav', 880, 0.1, 0.5)
    generate_and_save_sound('capture.wav', 440, 0.2, 0.7)
    generate_and_save_sound('check.wav', 1320, 0.3, 0.6)
    generate_and_save_sound('game_over.wav', 220, 1.0, 0.8)
    generate_and_save_sound('checkmate.wav', 1760, 0.5, 0.9)
    print("Sound files generated successfully in the 'sounds' folder.")