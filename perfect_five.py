import tkinter as tk
from PIL import Image, ImageDraw, ImageFont
import math


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

# Generate the reference when the program starts
reference_points = generate_reference_five()


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
    
    # PART 1: How close are user points to the reference?
    # (Are you drawing ON the "5"?)
    user_to_ref_total = 0
    for user_point in norm_user:
        user_x, user_y = user_point
        min_distance = float('inf')
        
        for ref_point in norm_ref:
            ref_x, ref_y = ref_point
            distance = math.sqrt((user_x - ref_x)**2 + (user_y - ref_y)**2)
            if distance < min_distance:
                min_distance = distance
        
        user_to_ref_total += min_distance
    
    user_to_ref_avg = user_to_ref_total / len(norm_user)
    
    # PART 2: How close are reference points to user points?
    # (Did you cover ALL parts of the "5"?)
    ref_to_user_total = 0
    for ref_point in norm_ref:
        ref_x, ref_y = ref_point
        min_distance = float('inf')
        
        for user_point in norm_user:
            user_x, user_y = user_point
            distance = math.sqrt((ref_x - user_x)**2 + (ref_y - user_y)**2)
            if distance < min_distance:
                min_distance = distance
        
        ref_to_user_total += min_distance
    
    ref_to_user_avg = ref_to_user_total / len(norm_ref)
    
    # Combine both scores (average of both directions)
    combined_avg = (user_to_ref_avg + ref_to_user_avg) / 2
    
    # Convert to percentage
    # Lower combined_avg = better score
    score = max(0, 100 - (combined_avg * 5))
    
    return score


#Real time scoring
def calculate_score_fast():
    
    if len(user_points) < 10:
        return 0.0
    
    norm_user = normalize_points(user_points)
    norm_ref = normalize_points(reference_points)
    
    # Sample for speed
    sampled_user = norm_user[::5]
    sampled_ref = norm_ref[::5]
    
    # Direction 1: User → Reference
    user_to_ref = 0
    for ux, uy in sampled_user:
        min_dist = min(
            math.sqrt((ux - rx)**2 + (uy - ry)**2)
            for rx, ry in sampled_ref
        )
        user_to_ref += min_dist
    
    user_to_ref_avg = user_to_ref / len(sampled_user) if sampled_user else 0
    
    # Direction 2: Reference → User
    ref_to_user = 0
    for rx, ry in sampled_ref:
        min_dist = min(
            math.sqrt((rx - ux)**2 + (ry - uy)**2)
            for ux, uy in sampled_user
        )
        ref_to_user += min_dist
    
    ref_to_user_avg = ref_to_user / len(sampled_ref) if sampled_ref else 0
    
    # Combine both
    combined = (user_to_ref_avg + ref_to_user_avg) / 2
    score = max(0, 100 - (combined * 5))
    
    return score


# Create the window
window = tk.Tk()
window.title("Draw a Perfect 5")

# Create a canvas - this is like a drawing board
canvas = tk.Canvas(window, width=500, height=500, bg="white")
canvas.pack()  # This adds the canvas to the window

#Show instructions and score
score_label = tk.Label(window, text="Draw a 5", font=("Arial", 24))
score_label.pack(pady=10)

user_points = []


#Reset what you drew
def reset():
    global user_points, draw_counter
    canvas.delete("all")
    score_label.config(text="Draw a 5!")
    user_points = []
    draw_counter = 0

reset_button = tk.Button(window, text="Reset", command=reset, font=("Arial", 10))
reset_button.pack(pady=10)


# This variable stores the last position of your mouse
last_x = None
last_y = None

# Add a counter to throttle updates
draw_counter = 0

def draw(event):
    global last_x, last_y, draw_counter
    
    if last_x is not None and last_y is not None:
        canvas.create_line(last_x, last_y, event.x, event.y, width=5)
    
    last_x = event.x
    last_y = event.y
    user_points.append((event.x, event.y))
    
    draw_counter += 1
    if draw_counter % 10 == 0:
        score = calculate_score()  # Use the SAME function
        score_label.config(text=f"Score: {score:.1f}%")


# This function runs when you release the mouse button
def reset_position(event):
    global last_x, last_y
    last_x = None
    last_y = None
    
    score = calculate_score()  # Same function, same score
    score_label.config(text=f"Final Score: {score:.1f}%")

# Connect mouse actions to functions
canvas.bind("<B1-Motion>", draw)         # B1-Motion = moving while left-click held
canvas.bind("<ButtonRelease-1>", reset_position)  # Released left-click

window.mainloop()