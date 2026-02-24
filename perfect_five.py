import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont
import math


# Set appearance mode and color theme
ctk.set_appearance_mode("dark")  # "dark", "light", or "system"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"


#create a list of EDGE points that make up the number 5. Full pixels in 5 value some parts more than others -> uneven scoring.
def generate_reference_five():

    #blank image
    img = Image.new('L', (500, 500), 'white')
    draw = ImageDraw.Draw(img)

    #Load the font
    try:
        font = ImageFont.truetype("LibreFranklin-Bold.ttf", 350)
    except:
        print("font not found! Using default.")
        font = ImageFont.load_default()


    # Figure out where to put the "5" so it's centered
    bbox = draw.textbbox((0, 0), "5", font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (500 - text_width) // 2
    y = (500 - text_height) // 2 - 40  # Shift up a bit
    
    # Draw the "5" in black
    draw.text((x, y), "5", font=font, fill='black')
    
    # Now find all the black pixels (these are our reference points)
    pixels = img.load()
    edge_points = []
    
    for py in range(1, 499):
        for px in range(1, 499):
            if pixels[px, py] < 128:  # This pixel is black
                # Check if any neighbor is white (making this an edge)
                is_edge = False
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    if pixels[px + dx, py + dy] >= 128:
                        is_edge = True
                        break
                
                if is_edge:
                    edge_points.append((px, py))
    
    print(f"Generated {len(edge_points)} edge points!")
    return edge_points


#We should be able to draw the 5 anywhere.
def get_bounding_box(points):
    if not points:
        return 0, 0, 0, 0
    
    min_x = min(p[0] for p in points)
    max_x = max(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)
    
    return min_x, min_y, max_x, max_y


#Normalize points to a 0-100 scale, centered
def normalize_points(points):

    if len(points) < 2:
        return points
    
    min_x, min_y, max_x, max_y = get_bounding_box(points)
    
    width = max_x - min_x
    height = max_y - min_y
    
    if width == 0 or height == 0:
        return points
    
    # Use the larger dimension to maintain aspect ratio
    scale = max(width, height)
    
    normalized = []
    for x, y in points:
        # Center and scale to 0-100
        new_x = ((x - min_x) / scale) * 100
        new_y = ((y - min_y) / scale) * 100
        normalized.append((new_x, new_y))
    
    return normalized


#Compare your drawing to the referenced 5
def calculate_score():
    
    if len(user_points) < 10:
        return 0.0
    
    norm_user = normalize_points(user_points)
    norm_ref = normalize_points(reference_points)

    sampled_user = norm_user[::3]
    sampled_ref = norm_ref[::3]
    
    # PART 1: How close are user points to the reference?
    # (Are you drawing ON the "5"?)
    user_to_ref_total = 0
    for user_x, user_y in sampled_user:
        min_distance = float('inf')
        for ref_x, ref_y in sampled_ref:
            distance = math.sqrt((user_x - ref_x)**2 + (user_y - ref_y)**2)
            if distance < min_distance:
                min_distance = distance
        user_to_ref_total += min_distance
    
    user_to_ref_avg = user_to_ref_total / len(sampled_user) if sampled_user else 0
    
    # PART 2: How close are reference points to user points?
    # (Did you cover ALL parts of the "5"?)
    ref_to_user_total = 0
    for ref_x, ref_y in sampled_ref:
        min_distance = float('inf')
        for user_x, user_y in sampled_user:
            distance = math.sqrt((ref_x - user_x)**2 + (ref_y - user_y)**2)
            if distance < min_distance:
                min_distance = distance
        ref_to_user_total += min_distance
    
    ref_to_user_avg = ref_to_user_total / len(sampled_ref) if sampled_ref else 0
    
    # Combine both scores (average of both directions)
    combined_avg = (user_to_ref_avg + ref_to_user_avg) / 2
    
    # Convert to percentage
    # Lower combined_avg = better score
    score = max(0, 100 - (combined_avg * 3))
    
    return score


# Generate the reference when the program starts
reference_points = generate_reference_five()


# Colors
BG_COLOR = "#1a1a2e"        # Dark blue background
CANVAS_BG = "#16213e"       # Slightly lighter for canvas
LINE_COLOR = "#e94560"      # Vibrant pink/red for drawing
ACCENT_COLOR = "#0f3460"    # Accent blue

# Create the window
window = ctk.CTk()
window.title("Draw a 5")
window.geometry("600x800")
window.configure(fg_color=BG_COLOR)

# Title label
title_label = ctk.CTkLabel(
    window, 
    text="Perfect Five", 
    font=ctk.CTkFont(family="Helvetica", size=32, weight="bold"),
    text_color="#ffffff"
)
title_label.pack(pady=(30, 10))

# Subtitle
subtitle_label = ctk.CTkLabel(
    window, 
    text="Draw the number 5", 
    font=ctk.CTkFont(size=14),
    text_color="#888888"
)
subtitle_label.pack(pady=(0, 20))

# Canvas frame (for rounded corners effect)
canvas_frame = ctk.CTkFrame(window, fg_color=CANVAS_BG, corner_radius=20)
canvas_frame.pack(padx=40, pady=10)

# Canvas (still using tk.Canvas for drawing functionality)
canvas = tk.Canvas(
    canvas_frame, 
    width=500, 
    height=500, 
    bg=CANVAS_BG,
    highlightthickness=0,  # Remove border
    cursor="crosshair"     # Cool cursor
)
canvas.pack(padx=10, pady=10)

# Score label
score_label = ctk.CTkLabel(
    window, 
    text="Start drawing", 
    font=ctk.CTkFont(family="Helvetica", size=28, weight="bold"),
    text_color="#ffffff"
)
score_label.pack(pady=(20, 10))

# Hint label for after drawing
hint_label = ctk.CTkLabel(
    window, 
    text="", 
    font=ctk.CTkFont(size=14),
    text_color="#888888"
)
hint_label.pack(pady=(0, 20))

user_points = []
# Add a counter to throttle updates
draw_counter = 0
last_x = None  # stores the last position of your mouse
last_y = None  # stores the last position of your mouse
drawing_complete = False  #Track if drawing is done


#Reset what you drew
def reset():
    global user_points, draw_counter, last_x, last_y, drawing_complete
    canvas.delete("all")
    score_label.configure(text="Start drawing!", text_color="#ffffff")
    hint_label.configure(text="")
    user_points = []
    draw_counter = 0
    last_x = None
    last_y = None
    drawing_complete = False

def on_click(event):
    global last_x, last_y, drawing_complete
    
    # If drawing is complete, reset and start fresh
    if drawing_complete:
        reset()
    
    # Start tracking from this point
    last_x = event.x
    last_y = event.y


def draw(event):
    global last_x, last_y, draw_counter

    # Don't allow drawing if complete
    if drawing_complete:
        return
    
    if last_x is not None and last_y is not None:
        canvas.create_line(
            last_x, last_y, 
            event.x, event.y, 
            width=6,
            fill=LINE_COLOR,
            capstyle=tk.ROUND,
            joinstyle=tk.ROUND,
            smooth=True,
            splinesteps=36
        )
    
    
    last_x = event.x
    last_y = event.y
    user_points.append((event.x, event.y))
    
    draw_counter += 1
    if draw_counter % 10 == 0:
        score = calculate_score()  # Use the SAME function
        score_label.configure(text=f"Score: {score:.1f}%")


# runs when you release the mouse button
def stop_drawing(event):
    global last_x, last_y, drawing_complete
    
    # Don't process if already complete
    if drawing_complete:
        return
    
    last_x = None
    last_y = None
    
    # Mark drawing as complete
    drawing_complete = True

    score = calculate_score()  # Same function, same score

     # Change color based on score
    if score >= 80:
        color = "#4ade80"  # Green
    elif score >= 60:
        color = "#facc15"  # Yellow
    elif score >= 40:
        color = "#fb923c"  # Orange
    else:
        color = "#f87171"  # Red

    score_label.configure(text=f"Final: {score:.1f}%", text_color=color)
    hint_label.configure(text="Click anywhere to try again")
    

# Connect mouse actions to functions
canvas.bind("<Button-1>", on_click)         # B1-Motion = moving while left-click held
canvas.bind("<B1-Motion>", draw)  # Released left-click
canvas.bind("<ButtonRelease-1>", stop_drawing)  # Capture initial click

window.mainloop()