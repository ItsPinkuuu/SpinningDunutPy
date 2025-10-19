import math, time, sys, os
import numpy as np

shades = ".:-=+*#%@"

A = 0.0
B = 0.0
theta_spacing = 0.03
phi_spacing = 0.02
fps_delay = 0.02

# Set your donut color here (R, G, B)
DONUT_COLOR = (255, 105, 180)  # HotPink

def enable_windows_ansi():
    if os.name == 'nt':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)
            mode = ctypes.c_ulong()
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                kernel32.SetConsoleMode(handle, mode.value | 0x0004)
        except Exception:
            pass

def colorize(char):
    r, g, b = DONUT_COLOR
    return f"\x1b[38;2;{r};{g};{b}m{char}\x1b[0m"

def render_frame(A, B, width, height):
    output = np.full((height, width), ' ', dtype='<U1')
    zbuffer = np.zeros((height, width))

    R2 = min(width, height) * 0.13    # Donut radius ~ half terminal
    R1 = R2 * 0.4                     # Tube thickness
    K2 = R2 * 2

    # Aggressive scaling to fill terminal
    K1 = width / (2 * (R1 + R2)) * 2.5
    vertical_scale = 0.9  # Adjust to terminal character aspect ratio

    cosA, sinA = math.cos(A), math.sin(A)
    cosB, sinB = math.cos(B), math.sin(B)

    theta_vals = np.arange(0, 2*math.pi, theta_spacing)
    phi_vals = np.arange(0, 2*math.pi, phi_spacing)

    for theta in theta_vals:
        cosTheta = math.cos(theta)
        sinTheta = math.sin(theta)
        for phi in phi_vals:
            cosPhi = math.cos(phi)
            sinPhi = math.sin(phi)

            circlex = R2 + R1 * cosTheta
            circley = R1 * sinTheta

            x = circlex * (cosB * cosPhi + sinA * sinB * sinPhi) - circley * cosA * sinB
            y = circlex * (sinB * cosPhi - sinA * cosB * sinPhi) + circley * cosA * cosB
            z = cosA * circlex * sinPhi + circley * sinA + K2

            inv_z = 1 / z
            xp = int(width / 2 + K1 * inv_z * x)
            yp = int(height / 2 - K1 * inv_z * y * vertical_scale)

            L = (cosPhi * cosTheta * sinB - cosA * cosTheta * sinPhi -
                 sinA * sinTheta + cosB * (cosA * sinTheta - cosTheta * sinA * sinPhi))

            if L > 0 and 0 <= xp < width and 0 <= yp < height:
                if inv_z > zbuffer[yp, xp]:
                    zbuffer[yp, xp] = inv_z
                    shade_index = int(L * (len(shades)-1))
                    shade_index = np.clip(shade_index, 0, len(shades)-1)
                    output[yp, xp] = shades[shade_index]

    return output

def main():
    enable_windows_ansi()
    global A, B
    sys.stdout.write('\x1b[2J')  # clear screen
    while True:
        try:
            width, height = os.get_terminal_size()
        except OSError:
            width, height = 140, 50

        frame = render_frame(A, B, width, height)

        sys.stdout.write('\x1b[H')  # move cursor top-left
        for row in range(height):
            line = ''.join([colorize(frame[row, col]) for col in range(width)])
            sys.stdout.write(line)
            if row < height - 1:
                sys.stdout.write('\n')
        sys.stdout.flush()

        A += 0.04
        B += 0.02
        time.sleep(fps_delay)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.stdout.write('\n')
        sys.exit(0)
