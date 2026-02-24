from PIL import Image, ImageDraw, ImageFont
import math

#create a list of EDGE points that make up the number 5. Full pixels in 5 value some parts more than others -> uneven scoring.
#Now edge points for any character...
def generate_reference(character="5"):

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
    bbox = draw.textbbox((0, 0), character, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (500 - text_width) // 2
    y = (500 - text_height) // 2 - 40  # Shift up a bit
    
    # Draw the "5" in black
    draw.text((x, y), character, font=font, fill='black')
    
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


#We should be able to draw the character anywhere.
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


#Compare your drawing to the referenced 5, Returns score 0-100
def calculate_score(user_points, reference_points):
    
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
    
    return round(score, 1)