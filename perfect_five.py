import tkinter as tk

# Create the window
window = tk.Tk()
window.title("Draw a Perfect 5!")

# Create a canvas - this is like a drawing board
canvas = tk.Canvas(window, width=500, height=500, bg="white")
canvas.pack()  # This adds the canvas to the window

#Show instructions and score
score_label = tk.Label(window, text="Draw a 5", font=("Arial", 24))
score_label.pack(pady=10)

user_points = []


#Reset what you drew
def reset():
    global user_points
    canvas.delete("all")
    score_label.config(text="Draw a 5")
    user_points = []

reset_button = tk.Button(window, text="Reset", command=reset, font=("Arial", 10))
reset_button.pack(pady=10)


# This variable stores the last position of your mouse
last_x = None
last_y = None

# This function runs every time you move the mouse while clicking
def draw(event):
    global last_x, last_y
    
    if last_x is not None and last_y is not None:
        # Draw a line from the last position to current position
        canvas.create_line(last_x, last_y, event.x, event.y, width=5)
    
    # Update last position
    last_x = event.x
    last_y = event.y

    #Save each point
    user_points.append((event.x, event.y))

# This function runs when you release the mouse button
def reset_position(event):
    global last_x, last_y
    last_x = None
    last_y = None

    #Show how many points were drawn (temporary, for testing)
    print(f"You drew {len(user_points)} points!")

# Connect mouse actions to functions
canvas.bind("<B1-Motion>", draw)         # B1-Motion = moving while left-click held
canvas.bind("<ButtonRelease-1>", reset_position)  # Released left-click

window.mainloop()