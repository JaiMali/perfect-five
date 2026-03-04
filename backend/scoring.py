from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math

#So this goes to backend/ folder for the font, no matter where I run it from...
BASE_DIR = Path(__file__).parent

#create a list of EDGE points that make up the number 5. Full pixels in 5 value some parts more than others -> uneven scoring.
#Now edge points for any character...
def generate_reference(character="5"):

    #blank image
    img = Image.new('L', (500, 500), 'white')
    draw = ImageDraw.Draw(img)

    #Load the font
    font_path = BASE_DIR / "librefranklin-bold.ttf"
    
    try:
        if font_path.exists():
            font = ImageFont.truetype(str(font_path), 350)
        else:
            print(f"Font not found at {font_path}, using default.")
            font = ImageFont.load_default()
    except Exception as e:
        print(f"Font error: {e}, using default.")
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
    
    print(f"Generated {len(edge_points)} edge points for {character}")
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

def render_points_to_image(points, size=100, line_width=3):
    """Render a list of points as a binary image."""
    img = Image.new('L', (size, size), 0)
    draw = ImageDraw.Draw(img)
    
    if len(points) < 2:
        return img
    
    # Draw lines connecting consecutive points
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        # Skip if points are too far apart (likely a stroke break)
        if math.sqrt((x2 - x1)**2 + (y2 - y1)**2) < 20:
            draw.line([(x1, y1), (x2, y2)], fill=255, width=line_width)
    
    return img


def render_reference_to_image(points, size=100, point_radius=2):
    """Render reference edge points as a binary image with thickness."""
    img = Image.new('L', (size, size), 0)
    draw = ImageDraw.Draw(img)
    
    for x, y in points:
        draw.ellipse(
            [x - point_radius, y - point_radius, x + point_radius, y + point_radius],
            fill=255
        )
    
    return img


def calculate_image_overlap(user_img, ref_img):
    """Calculate how much the user drawing overlaps with reference."""
    user_pixels = user_img.load()
    ref_pixels = ref_img.load()
    width, height = user_img.size
    
    user_on_ref = 0      # User pixels that are on the reference
    user_off_ref = 0     # User pixels that are off the reference
    ref_covered = 0      # Reference pixels covered by user
    ref_total = 0        # Total reference pixels
    user_total = 0       # Total user pixels
    
    # Dilate reference for tolerance
    tolerance = 5
    
    for y in range(height):
        for x in range(width):
            user_val = user_pixels[x, y]
            ref_val = ref_pixels[x, y]
            
            if ref_val > 128:
                ref_total += 1
            
            if user_val > 128:
                user_total += 1
                
                # Check if user pixel is near any reference pixel
                near_ref = False
                for dy in range(-tolerance, tolerance + 1):
                    for dx in range(-tolerance, tolerance + 1):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < width and 0 <= ny < height:
                            if ref_pixels[nx, ny] > 128:
                                near_ref = True
                                break
                    if near_ref:
                        break
                
                if near_ref:
                    user_on_ref += 1
                else:
                    user_off_ref += 1
            
            if ref_val > 128:
                # Check if reference pixel is covered by user
                covered = False
                for dy in range(-tolerance, tolerance + 1):
                    for dx in range(-tolerance, tolerance + 1):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < width and 0 <= ny < height:
                            if user_pixels[nx, ny] > 128:
                                covered = True
                                break
                    if covered:
                        break
                
                if covered:
                    ref_covered += 1
    
    return {
        'user_on_ref': user_on_ref,
        'user_off_ref': user_off_ref,
        'user_total': user_total,
        'ref_covered': ref_covered,
        'ref_total': ref_total
    }


def calculate_aspect_ratio_similarity(user_points, ref_points):
    """Compare aspect ratios of user drawing vs reference."""
    user_box = get_bounding_box(user_points)
    ref_box = get_bounding_box(ref_points)
    
    user_width = user_box[2] - user_box[0]
    user_height = user_box[3] - user_box[1]
    ref_width = ref_box[2] - ref_box[0]
    ref_height = ref_box[3] - ref_box[1]
    
    if user_height == 0 or ref_height == 0:
        return 0.0
    
    user_ratio = user_width / user_height
    ref_ratio = ref_width / ref_height
    
    # Calculate similarity (1.0 = identical, 0.0 = very different)
    ratio_diff = abs(user_ratio - ref_ratio)
    similarity = max(0, 1 - ratio_diff)
    
    return similarity



#Compare your drawing to the referenced 5, Returns score 0-100
#Improved scoring algorithm that considers:
#1. Precision - How much of user's drawing is on the reference
#2. Recall - How much of the reference is covered
#3. Aspect ratio similarity
#4. Original bidirectional distance (reduced weight)

def calculate_score(user_points, reference_points):
    
    if len(user_points) < 10:
        return 0.0

    # Normalize both sets of points
    norm_user = normalize_points(user_points)
    norm_ref = normalize_points(reference_points)

    # --- COMPONENT 1: Image-based overlap analysis ---
    user_img = render_points_to_image(norm_user, size=100, line_width=4)
    ref_img = render_reference_to_image(norm_ref, size=100, point_radius=3)
    
    overlap = calculate_image_overlap(user_img, ref_img)
    
    # Precision: What percentage of user's drawing is on the reference?
    if overlap['user_total'] > 0:
        precision = overlap['user_on_ref'] / overlap['user_total']
    else:
        precision = 0.0
    
    # Recall: What percentage of the reference is covered?
    if overlap['ref_total'] > 0:
        recall = overlap['ref_covered'] / overlap['ref_total']
    else:
        recall = 0.0

    # --- COMPONENT 2: Aspect ratio check ---
    aspect_similarity = calculate_aspect_ratio_similarity(user_points, reference_points)

    # --- COMPONENT 3: Original distance-based score (simplified) ---
    sampled_user = norm_user[::5]
    sampled_ref = norm_ref[::5]

    if not sampled_user or not sampled_ref:
        return 0.0

    # User to reference distance
    user_to_ref_total = 0
    for user_x, user_y in sampled_user:
        min_distance = float('inf')
        for ref_x, ref_y in sampled_ref:
            distance = math.sqrt((user_x - ref_x)**2 + (user_y - ref_y)**2)
            if distance < min_distance:
                min_distance = distance
        user_to_ref_total += min_distance

    user_to_ref_avg = user_to_ref_total / len(sampled_user)
    distance_score = max(0, 100 - (user_to_ref_avg * 4)) / 100

    # --- COMBINE SCORES ---
    # Weights for each component
    precision_weight = 0.35    # Penalize drawing outside the shape
    recall_weight = 0.35       # Reward covering the full shape
    aspect_weight = 0.10       # Small penalty for wrong proportions
    distance_weight = 0.20     # Original distance metric

    final_score = (
        precision * precision_weight +
        recall * recall_weight +
        aspect_similarity * aspect_weight +
        distance_score * distance_weight
    ) * 100

    # Apply minimum thresholds
    # If precision is too low, cap the score (drawing mostly outside)
    if precision < 0.4:
        final_score = min(final_score, 25)
    elif precision < 0.5:
        final_score = min(final_score, 40)
    
    # If recall is too low, cap the score (didn't cover enough)
    if recall < 0.4:
        final_score = min(final_score, 30)
    elif recall < 0.5:
        final_score = min(final_score, 45)

    return round(final_score, 1)