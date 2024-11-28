from tkinter import (
    Tk, Canvas, Label, Entry, Button, messagebox,
    StringVar, Frame, Toplevel
)
from PIL import Image, ImageTk
import os
import json
import random

# Create the main window
window = Tk()
window.title("DOUGHNUT DASH")
window.geometry("1428x867")
window.update()

canvas = Canvas(window, width=1428, height=867)
canvas.pack(fill="both", expand=True)

# Load and resize the initial background image using Pillow
image = Image.open("background.png")
resized_image = image.resize(
    (
        window.winfo_screenwidth(),
        window.winfo_screenheight()
    ),
    Image.Resampling.LANCZOS
)
background_image = ImageTk.PhotoImage(resized_image)
canvas.create_image(0, 0, image=background_image, anchor="nw")
# Keep a reference to prevent garbage collection
canvas.background_image = background_image

# Variables for user information
username = StringVar()
password = StringVar()

# Global variables
high_score = 0  # Initialize high_score globally
current_save_name = None
game_over_flag = False  # Flag to indicate if the game is over
boss_key_active = False  # Flag to indicate if the boss key screen is active

user_paused = False  # Indicates if the game is paused by the user
stage_paused = False  # Indicates if the game is paused during stage transition
pause_menu = None  # Initialize the pause_menu variable

# Enemy type variables
ENEMY_TYPES = ['falling', 'sideways', 'diagonal']
# Random initial enemy type(s)
current_enemy_types = [random.choice(ENEMY_TYPES)]
enemy_switch_timer = 0  # Timer to switch enemy types

# IDs for scheduled callbacks
increment_score_id = None
move_enemies_id = None
create_enemies_id = None
switch_enemy_type_id = None

# Stage variables
stage_number = 1  # Initialize stage number
stage_text_id = None  # ID for stage number text
enemy_speed = 3  # Starting enemy speed

# Cheat codes
invincibility = False
cheat_hitbox_visible = False

# Big enemy variables
big_enemy = None
big_enemy_hitbox = None
big_enemy_x = None
big_enemy_y = None
big_enemy_direction = None
big_enemy_state = None  # 'up_down' or 'across'

big_enemy_hitbox_width = None
big_enemy_hitbox_height = None

# Player invincibility after collision
player_invincible = False
invincibility_duration = 2000  # milliseconds

# Frame to hold the current view
current_frame = None


# Function to place frame on canvas
def switch_frame(new_frame):
    global current_frame
    try:
        if current_frame is not None and current_frame.winfo_exists():
            current_frame.place_forget()
    except AttributeError:
        pass
    current_frame = new_frame
    current_frame.place(relx=0.5, rely=0.5, anchor='center')


# Function to load the leaderboard
def load_leaderboard():
    if os.path.exists('leaderboard.json'):
        with open('leaderboard.json', 'r') as file:
            leaderboard = json.load(file)
    else:
        leaderboard = {}
    return leaderboard


# Function to save the leaderboard
def save_leaderboard(leaderboard):
    with open('leaderboard.json', 'w') as file:
        json.dump(leaderboard, file)


# Function to update the leaderboard
def update_leaderboard(username_info, score):
    leaderboard = load_leaderboard()
    previous_high_score = leaderboard.get(username_info, 0)
    if score > previous_high_score:
        leaderboard[username_info] = score
        save_leaderboard(leaderboard)


# Registration frame
def register_frame():
    frame = Frame(window, bg="white", bd=5)

    Label(frame, text="Please enter details below", bg="white").pack()
    Label(frame, text="", bg="white").pack()
    Label(frame, text="Username *", bg="white").pack()
    username_entry = Entry(frame, textvariable=username)
    username_entry.pack()
    Label(frame, text="Password *", bg="white").pack()
    password_entry = Entry(frame, textvariable=password, show="*")
    password_entry.pack()
    Label(frame, text="", bg="white").pack()
    Button(
        frame,
        text="Register",
        width=10,
        height=1,
        command=register_user,
        bg="lightblue",
        bd=3
    ).pack()
    Button(
        frame,
        text="Back",
        width=10,
        height=1,
        command=login_screen,
        bg="lightyellow",
        bd=3
    ).pack()

    switch_frame(frame)


# Checks user is not already there and lets them create an account
def register_user():
    username_info = username.get()
    password_info = password.get()

    if os.path.exists(username_info):
        messagebox.showerror("Error", "Username already taken")
        username.set("")
        password.set("")
        return

    with open(username_info, "w") as file:
        file.write(username_info + "\n")
        file.write(password_info + "\n")

    messagebox.showinfo("Success", "Registration Successful")
    main_menu()


# Login frame
def login_frame():
    frame = Frame(window, bg="white", bd=5)

    Label(frame, text="Please enter details below to login", bg="white").pack()
    Label(frame, text="", bg="white").pack()
    Label(frame, text="Username *", bg="white").pack()
    username_entry = Entry(frame, textvariable=username)
    username_entry.pack()
    Label(frame, text="Password *", bg="white").pack()
    password_entry = Entry(frame, textvariable=password, show="*")
    password_entry.pack()
    Label(
        frame,
        text="",
        bg="white"
    ).pack()
    Button(
        frame,
        text="Login",
        width=10,
        height=1,
        command=login_verify,
        bg="lightblue",
        bd=3
    ).pack()
    Button(
        frame,
        text="Back",
        width=10,
        height=1,
        command=login_screen,
        bg="lightyellow",
        bd=3
    ).pack()

    switch_frame(frame)


# Login verification
def login_verify():
    username_info = username.get()
    password_info = password.get()

    if os.path.exists(username_info):
        with open(username_info, "r") as file:
            verify = file.read().splitlines()
            if password_info in verify:
                # proceed to the game
                messagebox.showinfo("Success", "Login Successful")
                main_menu()
            else:
                messagebox.showerror("Error", "Password not recognized")
                username.set("")
                password.set("")
    else:
        messagebox.showerror("Error", "User not found")
        username.set("")


# Login frame with login and register button
def login_screen():
    frame = Frame(window, bg="white", bd=5)

    login_button = Button(
        frame,
        text="Login",
        width="30",
        height="2",
        command=login_frame,
        bg="lightblue",
        bd=3
    )
    register_button = Button(
        frame,
        text="Register",
        width="30",
        height="2",
        command=register_frame,
        bg="lightgreen",
        bd=3
    )
    exit_button = Button(
        frame,
        text="Exit",
        width="30",
        height="2",
        command=exit_game,
        bg="lightcoral",
        bd=3
    )

    login_button.pack(pady=10)
    register_button.pack(pady=10)
    exit_button.pack(pady=10)

    switch_frame(frame)


# Main menu with play options
def main_menu():
    clear_game()  # Ensure all game loops are canceled and canvas is cleared
    global game_over_flag
    game_over_flag = False  # Reset game over flag when returning to main menu
    # Use "background.png" for the main menu background
    image = Image.open("background.png")
    resized_image = image.resize(
        (
            window.winfo_screenwidth(),
            window.winfo_screenheight()
        ),
        Image.Resampling.LANCZOS
    )
    background_image = ImageTk.PhotoImage(resized_image)
    canvas.create_image(0, 0, image=background_image, anchor="nw")
    # Keep a reference to prevent garbage collection
    canvas.background_image = background_image

    frame = Frame(window, bg="white", bd=5)

    Label(
        frame,
        text="Welcome to the Doughnut Dash!",
        bg="white",
        font=("Helvetica", 20)
    ).pack(pady=20)
    play_button = Button(
        frame,
        text="Play",
        width="30",
        height="2",
        command=play_game_menu,
        bg="lightblue",
        bd=3
    )
    controls_button = Button(
        frame,
        text="Controls",
        width="30",
        height="2",
        command=controls_menu,
        bg="lightgreen",
        bd=3
    )
    cheat_codes_button = Button(
        frame,
        text="Cheat Codes",
        width="30",
        height="2",
        command=show_cheat_codes,
        bg="lightgrey",
        bd=3
    )
    leaderboard_button = Button(
        frame,
        text="Leaderboard",
        width="30",
        height="2",
        command=show_leaderboard,
        bg="lightyellow",
        bd=3
    )
    exit_button = Button(
        frame,
        text="Save And Exit",
        width="30",
        height="2",
        command=exit_game,
        bg="lightcoral",
        bd=3
    )

    play_button.pack(pady=10)
    controls_button.pack(pady=10)
    cheat_codes_button.pack(pady=10)
    leaderboard_button.pack(pady=10)
    exit_button.pack(pady=10)

    switch_frame(frame)


# Function to handle global key presses for cheats and pause
def global_key_press(event):
    if event.keysym.lower() == "h":
        toggle_hitbox()
    elif event.keysym.lower() == "i":
        toggle_invincibility()
    elif event.keysym.lower() == "k":
        skip_stage()
    elif event.keysym.lower() == "l":
        add_extra_life()
    elif event.keysym.lower() == "c":
        clear_enemies()
    elif event.keysym.lower() == controls["pause"].lower():
        toggle_pause()


# Bind the cheat codes and pause globally
window.bind("<KeyPress>", global_key_press)

# Bind the boss key separately using Control+B
window.bind_all("<Control-b>", lambda event: toggle_boss_key())


def play_game_menu():
    clear_game()  # Ensure all game loops are canceled and canvas is cleared
    frame = Frame(window, bg="white", bd=5)
    Label(
        frame,
        text="Choose an option",
        bg="white",
        font=("Helvetica", 20)
    ).pack(pady=20)
    new_game_button = Button(
        frame,
        text="New Game",
        width="30",
        height="2",
        command=start_new_game,
        bg="lightblue",
        bd=3
    )
    load_game_button = Button(
        frame,
        text="Load Game",
        width="30",
        height="2",
        command=load_game_menu,
        bg="lightgreen",
        bd=3
    )
    back_button = Button(
        frame,
        text="Back",
        width="30",
        height="2",
        command=main_menu,
        bg="lightyellow",
        bd=3
    )

    new_game_button.pack(pady=10)
    load_game_button.pack(pady=10)
    back_button.pack(pady=10)

    switch_frame(frame)


def load_game_menu():
    username_info = username.get()
    # Find all saved game files for this user
    saved_games = []
    prefix = f"{username_info}_"
    suffix = "_game_state.json"
    for file in os.listdir():
        if file.startswith(prefix) and file.endswith(suffix):
            # Extract the save name, remove prefix and suffix
            save_name = file[len(prefix):-len(suffix)]
            if save_name.strip():  # Only add if save_name is not empty
                saved_games.append(save_name)
    if not saved_games:
        messagebox.showinfo(
            "No Saved Games", "No saved games found for this user."
        )
        return

    # Create a new window to list saved games
    load_window = Toplevel(window)
    load_window.title("Load Game")
    load_window.geometry("300x400")
    Label(
        load_window,
        text="Select a saved game to load:",
        font=("Helvetica", 14)
    ).pack(pady=10)

    # List the saved games
    for save_name in saved_games:
        display_name = save_name
        Button(
            load_window,
            text=display_name,
            command=lambda sn=save_name: load_game(sn, load_window),
            font=("Helvetica", 12)
        ).pack(pady=5)


def start_new_game():
    global player_x, player_y, score, user_paused, stage_paused, lives
    global current_save_name, high_score, game_over_flag, boss_key_active
    global current_enemy_types, enemy_switch_timer, stage_number, enemy_speed
    global invincibility, cheat_hitbox_visible
    global big_enemy_x, big_enemy_y, big_enemy_direction, big_enemy_state
    global player_invincible

    game_over_flag = False  # Reset the game over flag
    boss_key_active = False  # Ensure boss key is inactive

    # Random initial enemy type(s)
    current_enemy_types = [random.choice(ENEMY_TYPES)]

    enemy_switch_timer = 0
    stage_number = 1
    enemy_speed = 3  # Reset enemy speed
    invincibility = False  # Reset invincibility
    cheat_hitbox_visible = False  # Start with hitbox not visible
    player_invincible = False  # Reset player invincibility

    # Initialize big enemy variables
    big_enemy_x = window.winfo_width() - 150
    big_enemy_y = window.winfo_height() // 2
    big_enemy_direction = "up"
    big_enemy_state = "up_down"

    for widget in window.winfo_children():
        widget.destroy()

    # Set up the game canvas with "game_bg.png" background
    game_bg_image()

    username_info = username.get()
    # Load the user's high score
    leaderboard = load_leaderboard()
    high_score = leaderboard.get(username_info, 0)

    score = 0
    player_x, player_y = 100, 100
    user_paused = False
    stage_paused = False
    lives = 3  # Initialize lives
    current_save_name = None  # No save name yet

    game()


def game():
    global hitbox, player_x, player_y, player, lives_label
    global enemies, enemy_switch_timer
    global invincibility_label, hitbox_label
    global big_enemy, big_enemy_hitbox, big_enemy_x
    global big_enemy_y, big_enemy_direction, big_enemy_state
    global big_enemy_hitbox_width, big_enemy_hitbox_height
    global score_label  # Declare as global to use in clear_game()

    # Initialize enemies
    enemies = []

    # Load custom controls for the current user
    username_info = username.get()
    loaded_controls = load_controls(username_info)
    controls.update(loaded_controls)

    # Player and hitbox initial positions
    x1, y1 = player_x, player_y
    # Offset values for hitbox positioning relative to the player
    hitbox_offset_x, hitbox_offset_y = 95, 115

    # Load the player image
    player_image = Image.open("player_img.png")
    player_image = player_image.resize((450, 300), Image.Resampling.LANCZOS)
    player_image_tk = ImageTk.PhotoImage(player_image)

    # Create the player image on the canvas
    player = canvas.create_image(x1, y1, image=player_image_tk, anchor="nw")

    # Define hitbox rectangle dimensions based on player image size
    hitbox_width, hitbox_height = 120, 45
    hitbox_x1 = x1 + hitbox_offset_x
    hitbox_y1 = y1 + hitbox_offset_y
    hitbox_x2 = hitbox_x1 + hitbox_width
    hitbox_y2 = hitbox_y1 + hitbox_height

    # Create the hitbox rectangle
    hitbox = canvas.create_rectangle(
        hitbox_x1,
        hitbox_y1,
        hitbox_x2,
        hitbox_y2,
        outline="red",
        tags="hitbox"
    )
    if not cheat_hitbox_visible:
        canvas.itemconfigure(hitbox, outline="")  # Hide hitbox outline

    # Rectangle movement step size
    step_size = 10

    # Set to keep track of pressed keys
    pressed_keys = set()

    # Keep references to prevent garbage collection
    canvas.player_image_tk = player_image_tk

    # Initialize big enemy
    # Load big enemy image
    big_enemy_image = Image.open("big_enemy.png")
    big_enemy_image = big_enemy_image.resize(
        (300, 200),
        Image.Resampling.LANCZOS
    )
    big_enemy_image_tk = ImageTk.PhotoImage(big_enemy_image)
    big_enemy_width, big_enemy_height = big_enemy_image.size
    # Get the dimensions

    # Set hitbox dimensions
    big_enemy_hitbox_width = big_enemy_width * 0.5
    big_enemy_hitbox_height = big_enemy_height * 0.6

    # Create the big enemy image on the canvas
    big_enemy = canvas.create_image(
        big_enemy_x,
        big_enemy_y,
        image=big_enemy_image_tk
    )

    # Create big enemy hitbox centered on the image
    big_enemy_hitbox = canvas.create_rectangle(
        big_enemy_x - big_enemy_hitbox_width / 2,
        big_enemy_y - big_enemy_hitbox_height / 2,
        big_enemy_x + big_enemy_hitbox_width / 2,
        big_enemy_y + big_enemy_hitbox_height / 2,
        outline="blue",
        tags="big_enemy_hitbox"
    )
    if not cheat_hitbox_visible:
        canvas.itemconfigure(
            big_enemy_hitbox,
            outline=""
        )  # Hide big enemy hitbox outline

    # Keep references to prevent garbage collection
    canvas.big_enemy_image_tk = big_enemy_image_tk

    # Function to move the player (both the hitbox and the image)
    def move_player():
        global player_x, player_y
        # Get the current position of the player image
        coords = canvas.coords(player)
        if coords:
            x1, y1 = coords
        else:
            return  # Player does not exist, exit the function

        # Calculate new positions based on pressed keys
        if (
            controls["up"] in pressed_keys and
            y1 + hitbox_offset_y > 0
        ):
            y1 -= step_size
        if (
            controls["down"] in pressed_keys and
            y1 + hitbox_offset_y + hitbox_height < 867
        ):
            y1 += step_size
        if (
            controls["left"] in pressed_keys and
            x1 + hitbox_offset_x > 0
        ):
            x1 -= step_size
        if (
            controls["right"] in pressed_keys and
            x1 + hitbox_offset_x + hitbox_width < 1428
        ):
            x1 += step_size

        player_x, player_y = x1, y1  # Update global player position

        # Update player and hitbox coordinates
        hitbox_x1 = x1 + hitbox_offset_x
        hitbox_y1 = y1 + hitbox_offset_y
        hitbox_x2 = hitbox_x1 + hitbox_width
        hitbox_y2 = hitbox_y1 + hitbox_height

        canvas.coords(player, x1, y1)
        canvas.coords(hitbox, hitbox_x1, hitbox_y1, hitbox_x2, hitbox_y2)

    # Function to handle key press events
    def key_press(event):
        if boss_key_active:
            return  # Ignore other key presses when boss key is active

        if event.keysym in controls.values() and not game_over_flag:
            pressed_keys.add(event.keysym)
            move_player()
        elif event.keysym == "Escape":
            toggle_pause()

    # Function to handle key release events
    def key_release(event):
        if event.keysym in pressed_keys:
            pressed_keys.discard(event.keysym)

    # Bind keys to control player movement
    canvas.focus_set()
    canvas.bind("<KeyPress>", key_press)
    canvas.bind("<KeyRelease>", key_release)

    # Display the score in the top left corner
    score_label = Label(
        window,
        text=f"Score: {score}",
        font=("Helvetica", 16),
        bg="lightblue"
        )
    score_label.place(x=0, y=40)

    # Display the lives in the top left corner
    lives_label = Label(
        window,
        text=f"Lives: {lives}",
        font=("Helvetica", 16),
        bg="lightblue"
        )
    lives_label.place(x=0, y=70)

    # Indicators for cheats
    invincibility_label = Label(
        window, text="",
        font=("Helvetica", 12),
        bg="lightblue"
        )
    invincibility_label.place(x=0, y=100)
    hitbox_label = Label(
        window, text="",
        font=("Helvetica", 12),
        bg="lightblue"
    )
    hitbox_label.place(x=0, y=120)
    # Set initial label texts
    invincibility_status = "ON" if invincibility else "OFF"
    invincibility_label.config(text=f"Invincibility: {invincibility_status}")

    hitbox_status = "ON" if cheat_hitbox_visible else "OFF"
    hitbox_label.config(text=f"Hitbox Visible: {hitbox_status}")

    # Display the "Pause" button
    global pause_button
    pause_button = Button(
        window,
        text="Pause",
        command=toggle_pause,
        bg="lightgreen",
        font=("Helvetica", 16)
    )
    canvas.create_window(
        0,
        0,
        window=pause_button,
        anchor="nw"
    )  # Position the button

    # Start the game loops
    increment_score()
    move_enemies()
    create_enemies()
    switch_enemy_type()
    move_big_enemy()


def create_enemy(x_position=None, y_position=None, enemy_type=None):
    global enemies
    if enemy_type is None:
        enemy_type = random.choice(ENEMY_TYPES)
    enemy = None
    if enemy_type == 'falling':
        if x_position is None:
            x_position = random.randint(0, window.winfo_width() - enemy_width)
        if y_position is None:
            y_position = 0
        enemy = canvas.create_rectangle(
            x_position,
            y_position,
            x_position + enemy_width,
            y_position + enemy_height,
            fill="black",
            tags=("enemy", "falling")
        )
    elif enemy_type == 'sideways':
        if x_position is None:
            x_position = 0
        if y_position is None:
            y_position = random.randint(
                0,
                window.winfo_height() - enemy_height
            )
        enemy = canvas.create_rectangle(
            x_position,
            y_position,
            x_position + enemy_width,
            y_position + enemy_height,
            fill="red",
            tags=("enemy", "sideways")
        )
    elif enemy_type == 'diagonal':
        # Randomly choose start position and direction
        direction = random.choice(
            ['down_right', 'down_left', 'up_right', 'up_left']
        )
        if direction == 'down_right':
            x_position = 0
            y_position = 0
        elif direction == 'down_left':
            x_position = window.winfo_width() - enemy_width
            y_position = 0
        elif direction == 'up_right':
            x_position = 0
            y_position = window.winfo_height() - enemy_height
        elif direction == 'up_left':
            x_position = window.winfo_width() - enemy_width
            y_position = window.winfo_height() - enemy_height
        enemy = canvas.create_rectangle(
            x_position,
            y_position,
            x_position + enemy_width,
            y_position + enemy_height,
            fill="green",
            tags=(
                "enemy",
                "diagonal",
                direction
            )
        )
    if enemy:
        enemies.append(enemy)


def create_enemies():
    global create_enemies_id
    if (
        not (user_paused or stage_paused)
        and not game_over_flag
        and not boss_key_active
    ):
        for enemy_type in current_enemy_types:
            # Introduce randomness in enemy creation timing
            delay = random.randint(500, 1500)
            window.after(delay, create_enemy, None, None, enemy_type)
    if not game_over_flag:
        # Schedule the next call with a random delay
        next_call_delay = random.randint(1000, 2000)
        create_enemies_id = window.after(next_call_delay, create_enemies)


def move_enemies():
    global move_enemies_id
    if (
        not (user_paused or stage_paused)
        and not game_over_flag
        and not boss_key_active
    ):
        for enemy in enemies[:]:
            if enemy:
                coords = canvas.coords(enemy)
                if coords:
                    x1, y1, x2, y2 = coords
                    tags = canvas.gettags(enemy)
                    if "falling" in tags:
                        canvas.move(enemy, 0, enemy_speed)
                    elif "sideways" in tags:
                        canvas.move(enemy, enemy_speed, 0)
                    elif "diagonal" in tags:
                        direction = tags[2]  # Get the direction tag
                        if direction == 'down_right':
                            dx, dy = enemy_speed, enemy_speed
                        elif direction == 'down_left':
                            dx, dy = -enemy_speed, enemy_speed
                        elif direction == 'up_right':
                            dx, dy = enemy_speed, -enemy_speed
                        elif direction == 'up_left':
                            dx, dy = -enemy_speed, -enemy_speed
                        canvas.move(enemy, dx, dy)
                    # Check if the enemy collides with the player hitbox
                    if canvas.bbox(enemy):
                        enemy_coords = canvas.bbox(enemy)
                        hitbox_coords = canvas.coords(hitbox)
                        if check_collision(enemy_coords, hitbox_coords):
                            print("Collision detected!")
                            canvas.delete(enemy)
                            enemies.remove(enemy)
                            handle_collision()
                        elif (
                            y2 < 0 or
                            y1 > window.winfo_height() or
                            x2 < 0 or
                            x1 > window.winfo_width()
                        ):
                            # Remove off-screen enemies
                            canvas.delete(enemy)
                            enemies.remove(enemy)
                else:
                    enemies.remove(enemy)
        if not game_over_flag:
            move_enemies_id = window.after(50, move_enemies)
    else:
        if not game_over_flag:
            move_enemies_id = window.after(50, move_enemies)


def move_big_enemy():
    global big_enemy_x, big_enemy_y, big_enemy_direction, big_enemy_state
    if (
        not (user_paused or stage_paused)
        and not game_over_flag
        and not boss_key_active
    ):
        if big_enemy_state == "up_down":
            # Move up and down on the right side
            if big_enemy_direction == "up":
                big_enemy_y -= 5
                if big_enemy_y <= 50:
                    big_enemy_direction = "down"
            else:
                big_enemy_y += 5
                if big_enemy_y >= window.winfo_height() - 50:
                    big_enemy_direction = "up"
            # Update big enemy position
            canvas.coords(big_enemy, big_enemy_x, big_enemy_y)
            canvas.coords(
                big_enemy_hitbox,
                big_enemy_x - big_enemy_hitbox_width / 2,
                big_enemy_y - big_enemy_hitbox_height / 2,
                big_enemy_x + big_enemy_hitbox_width / 2,
                big_enemy_y + big_enemy_hitbox_height / 2
            )
        elif big_enemy_state == "across":
            # Move across the screen from left to right
            big_enemy_x += 10  # Move faster when moving across
            # Update big enemy position
            canvas.coords(big_enemy, big_enemy_x, big_enemy_y)
            canvas.coords(
                big_enemy_hitbox,
                big_enemy_x - big_enemy_hitbox_width / 2,
                big_enemy_y - big_enemy_hitbox_height / 2,
                big_enemy_x + big_enemy_hitbox_width / 2,
                big_enemy_y + big_enemy_hitbox_height / 2
            )
            if big_enemy_x >= window.winfo_width() + big_enemy_hitbox_width:
                # Reached the right side, teleport back to starting position
                big_enemy_x = window.winfo_width() - 150  # Original x position
                big_enemy_state = "up_down"
        # Randomly trigger across movement from stage 3 onwards
        if stage_number >= 3 and big_enemy_state == "up_down":
            if random.randint(1, 200) == 1:  # 0.5% chance each time
                big_enemy_state = "across"
                big_enemy_x = -big_enemy_hitbox_width
                # start from the left of the screen
                # Update big enemy position immediately
                canvas.coords(big_enemy, big_enemy_x, big_enemy_y)
                canvas.coords(
                    big_enemy_hitbox,
                    big_enemy_x - big_enemy_hitbox_width / 2,
                    big_enemy_y - big_enemy_hitbox_height / 2,
                    big_enemy_x + big_enemy_hitbox_width / 2,
                    big_enemy_y + big_enemy_hitbox_height / 2
                )
        # Check collision with player
        if canvas.bbox(big_enemy_hitbox) and canvas.bbox(hitbox):
            big_enemy_coords = canvas.bbox(big_enemy_hitbox)
            hitbox_coords = canvas.coords(hitbox)
            if check_collision(big_enemy_coords, hitbox_coords):
                print("Collision with big enemy detected!")
                handle_collision()
        # Schedule next move
        if not game_over_flag:
            window.after(50, move_big_enemy)
    else:
        # Reschedule when unpaused
        if not game_over_flag:
            window.after(50, move_big_enemy)


def switch_enemy_type():
    global current_enemy_types, enemy_switch_timer, stage_paused
    global switch_enemy_type_id, stage_number, enemy_speed
    if not game_over_flag and not boss_key_active:
        enemy_switch_timer += 1
        if enemy_switch_timer >= 20:  # Switch every 20 seconds
            stage_paused = True
            # Remove existing enemies
            for enemy in enemies:
                canvas.delete(enemy)
            enemies.clear()
            # Increase stage number
            stage_number += 1
            # Increase enemy speed over time
            enemy_speed += 1  # Increase speed
            # Display stage number
            display_stage_number()
            # Wait for 3 seconds before switching enemy type
            window.after(3000, resume_enemy_creation)
            enemy_switch_timer = 0
        else:
            switch_enemy_type_id = window.after(1000, switch_enemy_type)
    else:
        enemy_switch_timer = 0


def resume_enemy_creation():
    global current_enemy_types, stage_paused, enemy_switch_timer
    # Randomly select new enemy type(s)
    if stage_number >= 6:
        # After stage 6, all enemy types are active
        current_enemy_types = ENEMY_TYPES.copy()  # All enemy types
    elif stage_number >= 3:
        # From stage 3 to 5, two enemy types are active
        current_enemy_types = random.sample(ENEMY_TYPES, 2)
    else:
        # Before stage 3, one enemy type
        current_enemy_types = [random.choice(ENEMY_TYPES)]
    print(f"Stage {stage_number}: Enemy types active: {current_enemy_types}")
    # Remove stage number display
    remove_stage_number()
    stage_paused = False  # Clear stage pause flag
    enemy_switch_timer = 0  # Reset the timer
    # Start the game loops only if the user hasn't paused
    if not user_paused:
        increment_score()
        move_enemies()
        create_enemies()
        switch_enemy_type()  # Restart the enemy switch timer


def display_stage_number():
    global stage_text_id
    stage_text = f"Stage {stage_number}"
    stage_text_id = canvas.create_text(
        window.winfo_width()/2,
        window.winfo_height()/2,
        text=stage_text,
        font=("Helvetica", 48),
        fill="yellow"
    )


def remove_stage_number():
    global stage_text_id
    if stage_text_id is not None:
        canvas.delete(stage_text_id)
        stage_text_id = None


def cancel_game_loops():
    global increment_score_id, move_enemies_id
    global create_enemies_id, switch_enemy_type_id
    if increment_score_id is not None:
        window.after_cancel(increment_score_id)
        increment_score_id = None
    if move_enemies_id is not None:
        window.after_cancel(move_enemies_id)
        move_enemies_id = None
    if create_enemies_id is not None:
        window.after_cancel(create_enemies_id)
        create_enemies_id = None
    if switch_enemy_type_id is not None:
        window.after_cancel(switch_enemy_type_id)
        switch_enemy_type_id = None


def handle_collision():
    global lives, game_over_flag, player_invincible
    if invincibility or player_invincible:
        return  # Do not reduce lives if invincibility is active
    if game_over_flag:
        return  # Game is already over, do nothing
    lives -= 1
    lives_label.config(text=f"Lives: {lives}")
    if lives <= 0:
        game_over()
    else:
        player_invincible = True
        # Optionally, change player's appearance here to indicate invincibility
        window.after(invincibility_duration, reset_player_invincibility)


def reset_player_invincibility():
    global player_invincible
    player_invincible = False
    # Optionally, revert player's appearance here


def game_over():
    global user_paused, current_save_name, game_over_flag, pause_button
    user_paused = True  # Pause the game
    game_over_flag = True  # Set the game over flag

    # Disable the pause button
    pause_button.config(state="disabled")

    # Update the leaderboard with the user's score
    username_info = username.get()
    update_leaderboard(username_info, high_score)

    # Delete current save file
    if current_save_name:
        save_file = f"{username_info}_{current_save_name}_game_state.json"
        if os.path.exists(save_file):
            os.remove(save_file)

    # Display Game Over window
    game_over_window = Toplevel(window)
    game_over_window.title("Game Over")
    game_over_window.geometry("400x300")

    Label(
        game_over_window,
        text="Game Over",
        font=("Helvetica", 20)
    ).pack(pady=20)
    Label(
        game_over_window,
        text=f"Your Score: {score}",
        font=("Helvetica", 16)
    ).pack(pady=10)
    Label(
        game_over_window,
        text=f"High Score: {high_score}",
        font=("Helvetica", 16)
    ).pack(pady=10)

    def view_leaderboard():
        # Hide the game over window
        game_over_window.withdraw()
        # Show the leaderboard
        show_leaderboard(callback=lambda: game_over_window.deiconify())

    def play_again():
        game_over_window.destroy()
        start_new_game()

    def back_to_main_menu():
        game_over_window.destroy()
        clear_game()
        main_menu()

    Button(
        game_over_window,
        text="View Leaderboard",
        command=view_leaderboard,
        font=("Helvetica", 16)
    ).pack(pady=5)
    Button(
        game_over_window,
        text="Play Again",
        command=play_again,
        font=("Helvetica", 16)
    ).pack(pady=5)
    Button(
        game_over_window,
        text="Main Menu",
        command=back_to_main_menu,
        font=("Helvetica", 16)
    ).pack(pady=5)


# Function to check collision between two rectangles
def check_collision(rect1, rect2):
    x1, y1, x2, y2 = rect1
    a1, b1, a2, b2 = rect2
    return not (x2 < a1 or x1 > a2 or y2 < b1 or y1 > b2)


enemy_width, enemy_height = 40, 40


def increment_score():
    global score, high_score, increment_score_id
    if (
        not (user_paused or stage_paused)
        and not game_over_flag
        and not boss_key_active
    ):
        score += 1
        score_label.config(text=f"Score: {score}")
        if score > high_score:
            high_score = score
    if not game_over_flag:
        increment_score_id = window.after(1000, increment_score)


def toggle_pause():
    global user_paused, pause_menu, high_score
    # Do not allow toggling pause if game is over or boss key is active
    if game_over_flag or boss_key_active:
        return
    user_paused = not user_paused
    if user_paused:
        cancel_game_loops()
        # Show pause menu with score, high score, resume, and quit
        pause_menu = Toplevel(window)
        pause_menu.title("Pause Menu")
        pause_menu.geometry("400x400")

        Label(
            pause_menu,
            text=f"Score: {score}",
            font=("Helvetica", 16)
        ).pack(pady=10)
        Label(
            pause_menu,
            text=f"High Score: {high_score}",
            font=("Helvetica", 16)
        ).pack(pady=10)

        def save_game_prompt():
            cancel_game_loops()  # Cancel game loops while saving

            def save():
                save_name = save_name_entry.get().strip()
                if save_name == "":
                    save_name = "autosave"
                save_game_state(save_name)
                messagebox.showinfo("Success", f"Game saved as '{save_name}'.")
                save_window.destroy()
                # After saving, resume the game loops if the game is not paused
                if not user_paused and not stage_paused:
                    increment_score()
                    move_enemies()
                    create_enemies()
                    switch_enemy_type()
                    move_big_enemy()
            save_window = Toplevel(pause_menu)
            save_window.title("Save Game")
            save_window.geometry("300x150")

            Label(
                save_window,
                text="Enter save name:",
                font=("Helvetica", 12)
            ).pack(pady=10)
            save_name_entry = Entry(save_window)
            save_name_entry.pack(pady=5)
            Button(save_window, text="Save", command=save).pack(pady=10)

        def resume_game():
            global user_paused
            user_paused = False
            pause_menu.destroy()
            # Restart the game loops
            if not stage_paused:
                increment_score()
                move_enemies()
                create_enemies()
                switch_enemy_type()
                move_big_enemy()

        def back_to_menu():
            # Do not save game state here
            # Update the leaderboard with the user's score
            username_info = username.get()
            update_leaderboard(username_info, high_score)
            pause_menu.destroy()
            clear_game()
            main_menu()

        def show_cheat_codes_from_pause():
            show_cheat_codes()

        Button(
            pause_menu,
            text="Resume",
            command=resume_game,
            font=("Helvetica", 16)
        ).pack(pady=10)
        Button(
            pause_menu,
            text="Save Game As",
            command=save_game_prompt,
            font=("Helvetica", 16)
            ).pack(pady=10)
        Button(
            pause_menu,
            text="Cheat Codes",
            command=show_cheat_codes_from_pause,
            font=("Helvetica", 16)
        ).pack(pady=10)
        Button(
            pause_menu,
            text="Back to Menu",
            command=back_to_menu,
            font=("Helvetica", 16)
        ).pack(pady=10)
    else:
        # Restart the game loops
        if not stage_paused:
            increment_score()
            move_enemies()
            create_enemies()
            switch_enemy_type()
            move_big_enemy()
        # Destroy the pause menu if it exists
        if pause_menu:
            pause_menu.destroy()


# Function to toggle the boss key screen
def toggle_boss_key():
    global boss_key_active, boss_key_window, current_frame
    if boss_key_active:
        # Hide the boss key window and resume
        boss_key_window.destroy()
        boss_key_active = False
        if 'game' in globals() and not game_over_flag:
            # Resume the game if the user hasn't paused
            if not user_paused and not stage_paused:
                increment_score()
                move_enemies()
                create_enemies()
                switch_enemy_type()
                move_big_enemy()
    else:
        # Show the boss key window and pause if in game
        boss_key_active = True
        if 'game' in globals() and not game_over_flag:
            # Pause the game loops
            cancel_game_loops()
        boss_key_window = Toplevel(window)
        boss_key_window.title("Work")
        boss_key_window.geometry(
            f"{window.winfo_width()}x{window.winfo_height()}+0+0"
            )
        boss_key_window.overrideredirect(True)
        # Load the boss key image
        boss_image = Image.open("boss_key.png")
        resized_boss_image = boss_image.resize(
            (1428, 867),
            Image.Resampling.LANCZOS
            )  # sets dimensions of the image
        boss_image_tk = ImageTk.PhotoImage(resized_boss_image)
        boss_canvas = Canvas(boss_key_window, width=1428, height=867)
        boss_canvas.pack()
        boss_canvas.create_image(0, 0, image=boss_image_tk, anchor="nw")
        boss_canvas.boss_image_tk = boss_image_tk  # Prevent garbage collection

        # Bind 'Control+B' to toggle back
        boss_key_window.bind_all(
            "<Control-b>",
            lambda event: toggle_boss_key()
            )
        boss_key_window.focus_set()


# Function to clear game canvas and reset elements
def clear_game():
    cancel_game_loops()
    canvas.delete("all")
    for widget in window.winfo_children():
        if isinstance(widget, Button) or isinstance(widget, Label):
            widget.destroy()
    # Destroy labels if they exist
    global score_label, lives_label, invincibility_label, hitbox_label
    try:
        score_label.destroy()
    except NameError:
        pass
    try:
        lives_label.destroy()
    except NameError:
        pass
    try:
        invincibility_label.destroy()
    except NameError:
        pass
    try:
        hitbox_label.destroy()
    except NameError:
        pass


def save_game_state(save_name=None):
    global current_save_name
    username_info = username.get()
    game_state = {
        "player_x": player_x,
        "player_y": player_y,
        "score": score,
        "lives": lives,
        "enemies": [
            {
                "position": canvas.coords(enemy),
                "tags": canvas.gettags(enemy),
            } for enemy in enemies
        ],
        "current_enemy_types": current_enemy_types,
        "enemy_switch_timer": enemy_switch_timer,
        "stage_number": stage_number,
        "enemy_speed": enemy_speed,
        "invincibility": invincibility,
        "cheat_hitbox_visible": cheat_hitbox_visible,
        "big_enemy_x": big_enemy_x,
        "big_enemy_y": big_enemy_y,
        "big_enemy_direction": big_enemy_direction,
        "big_enemy_state": big_enemy_state,
        "player_invincible": player_invincible
    }
    if save_name is None:
        if current_save_name:
            save_name = current_save_name
        else:
            save_name = "autosave"
    save_name = save_name.strip()
    if save_name == "":
        save_name = "autosave"
    with open(f"{username_info}_{save_name}_game_state.json", "w") as file:
        json.dump(game_state, file)
    current_save_name = save_name  # Update current save name


def load_game(save_name, load_window=None):
    global player_x, player_y, score, enemies
    global user_paused, stage_paused, lives, current_save_name, high_score
    global game_over_flag, boss_key_active
    global current_enemy_types, enemy_switch_timer, stage_number, enemy_speed
    global invincibility, cheat_hitbox_visible
    global big_enemy_x, big_enemy_y, big_enemy_direction, big_enemy_state
    global player_invincible

    enemies = []  # Initialize the list of enemies
    game_over_flag = False  # Reset the game over flag
    boss_key_active = False  # Ensure boss key is inactive
    username_info = username.get()

    # Load the user's high score
    leaderboard = load_leaderboard()
    high_score = leaderboard.get(username_info, 0)

    try:
        with open(f"{username_info}_{save_name}_game_state.json", "r") as file:
            game_state = json.load(file)
            player_x = game_state["player_x"]
            player_y = game_state["player_y"]
            score = game_state.get("score", 0)
            lives = game_state.get("lives", 3)  # Load lives, default to 3
            current_enemy_types = game_state.get(
                "current_enemy_types",
                [random.choice(ENEMY_TYPES)]
                )
            enemy_switch_timer = game_state.get(
                "enemy_switch_timer",
                0
            )
            stage_number = game_state.get(
                "stage_number",
                1
                )
            enemy_speed = game_state.get(
                "enemy_speed",
                3
                )
            invincibility = game_state.get(
                "invincibility",
                False
                )
            cheat_hitbox_visible = game_state.get(
                "cheat_hitbox_visible",
                False
                )
            enemy_data = game_state.get(
                "enemies", []
                )
            big_enemy_x = game_state.get(
                "big_enemy_x",
                window.winfo_width() - 150
                )
            big_enemy_y = game_state.get(
                "big_enemy_y", window.winfo_height() // 2
                )
            big_enemy_direction = game_state.get(
                "big_enemy_direction",
                "up"
                )
            big_enemy_state = game_state.get(
                "big_enemy_state",
                "up_down"
                )
            player_invincible = game_state.get(
                "player_invincible", False
                )

    except FileNotFoundError:
        messagebox.showerror("Error", f"Save file '{save_name}' not found.")
        if load_window:
            load_window.destroy()
        return

    # Set the current save name
    current_save_name = save_name

    # Close the load window if it is open
    if load_window:
        load_window.destroy()

    # Destroy widgets and recreate canvas
    for widget in window.winfo_children():
        widget.destroy()
    game_bg_image()

    # Start the game to initialize everything
    game()

    # Update the player position
    canvas.coords(player, player_x, player_y)

    # Update big enemy position and state
    canvas.coords(big_enemy, big_enemy_x, big_enemy_y)
    canvas.coords(
        big_enemy_hitbox,
        big_enemy_x - big_enemy_hitbox_width / 2,
        big_enemy_y - big_enemy_hitbox_height / 2,
        big_enemy_x + big_enemy_hitbox_width / 2,
        big_enemy_y + big_enemy_hitbox_height / 2
    )

    # Update hitbox visibility
    if cheat_hitbox_visible:
        canvas.itemconfigure(hitbox, outline="red")
        canvas.itemconfigure(big_enemy_hitbox, outline="blue")
    else:
        canvas.itemconfigure(hitbox, outline="")
        canvas.itemconfigure(big_enemy_hitbox, outline="")

    # Update cheat indicators
    invincibility_status = "ON" if invincibility else "OFF"
    invincibility_label.config(text=f"Invincibility: {invincibility_status}")

    hitbox_status = "ON" if cheat_hitbox_visible else "OFF"
    hitbox_label.config(text=f"Hitbox Visible: {hitbox_status}")

    # Now create the enemies on the new canvas
    for enemy_info in enemy_data:
        position = enemy_info["position"]
        tags = enemy_info["tags"]
        if position:
            x1, y1, x2, y2 = position
            color = (
                "black" if "falling" in tags
                else "red" if "sideways" in tags
                else "green"
            )
            enemy = canvas.create_rectangle(
                x1,
                y1,
                x2,
                y2,
                fill=color,
                tags=tags
                )
            enemies.append(enemy)

    user_paused = False
    stage_paused = False

    # Start the game loops after loading
    if not user_paused and not stage_paused:
        increment_score()
        move_enemies()
        create_enemies()
        switch_enemy_type()
        move_big_enemy()


def game_bg_image():
    """Sets up the game canvas with 'game_bg.png' as the background image."""
    global canvas  # Use global to retain references
    canvas = Canvas(
        window,
        width=window.winfo_width(),
        height=window.winfo_height()
        )
    canvas.pack(fill="both", expand=True)
    # Load the game background image
    image = Image.open("game_bg.png")  # Use "game_bg.png" during gameplay
    resized_image = image.resize(
        (
            window.winfo_width(),
            window.winfo_height()
            ),
        Image.Resampling.LANCZOS
        )
    game_background_image = ImageTk.PhotoImage(resized_image)
    canvas.create_image(0, 0, image=game_background_image, anchor="nw")
    # Keep a reference to prevent garbage collection
    canvas.game_background_image = game_background_image


controls = {
    "up": "Up",
    "down": "Down",
    "left": "Left",
    "right": "Right",
    "pause": "Escape"  # Pause key is now fixed and cannot be remapped
}


# Load controls from file if they exist
def load_controls(username_info):
    config_file = f"{username_info}_config.json"
    if os.path.exists(config_file):
        with open(config_file, "r") as file:
            return json.load(file)
    return controls.copy()


# Save controls to file
def save_controls(username_info, controls):
    messagebox.showinfo("Success", "Controls Saved")
    config_file = f"{username_info}_config.json"
    with open(config_file, "w") as file:
        json.dump(controls, file)


# Set up the controls frame
def controls_menu():
    frame = Frame(window, bg="white", bd=15)
    frame.place(relx=0.5, rely=0.5, anchor="center")
    Label(
        frame,
        text="Controls",
        bg="white",
        font=("Helvetica", 20)
        ).pack(pady=20)
    controls_text = "Use the buttons below to change the controls:"
    Label(
        frame,
        text=controls_text,
        bg="white",
        font=("Helvetica", 14)
        ).pack(pady=10)

    def set_control(button, direction):
        original_text = button['text']
        button.config(text="Tap any key")

        def capture_key(event):
            key = event.keysym

            # Prevent changing the boss key or pause key
            reserved_keys = ['h', 'k', 'i', 'c', 'l']
            if key.lower() in reserved_keys:
                messagebox.showerror(
                    "Invalid Key",
                    f"The key '{key.upper()}' is reserved and cannot be used."
                )
                button.config(text=original_text)
            elif key in controls.values():
                messagebox.showerror(
                    "Duplicate Key Error",
                    (
                        f"The key '{key.upper()}' "
                        "is already assigned to another control. "
                        "Please choose a different key."
                    )
                )
                button.config(text=original_text)
            else:
                controls[direction] = key
                button.config(text=key.upper())
                # Update the button with the new keybind

            # Unbind after capturing the key
            frame.unbind("<Key>")

        # Bind the key press to the frame
        frame.bind("<Key>", capture_key)
        frame.focus_set()

    username_info = username.get()
    loaded_controls = load_controls(username_info)
    controls.update(loaded_controls)

    # Set up buttons for each control direction
    control_frame = Frame(frame)
    control_frame.pack(pady=10)

    Label(
        control_frame,
        text="Up:",
        bg="white"
        ).grid(row=0, column=0, padx=5, pady=5)
    up_button = Button(
        control_frame,
        text=controls["up"].upper(),
        width=10,
        command=lambda: set_control(up_button, "up")
        )
    up_button.grid(
        row=0,
        column=1,
        padx=5,
        pady=5
        )

    Label(
        control_frame,
        text="Down:",
        bg="white"
        ).grid(row=1, column=0, padx=5, pady=5)
    down_button = Button(
        control_frame,
        text=controls["down"].upper(),
        width=10,
        command=lambda: set_control(down_button, "down")
        )
    down_button.grid(
        row=1,
        column=1,
        padx=5,
        pady=5
        )

    Label(
        control_frame,
        text="Left:",
        bg="white"
        ).grid(row=2, column=0, padx=5, pady=5)
    left_button = Button(
        control_frame,
        text=controls["left"].upper(),
        width=10,
        command=lambda: set_control(left_button, "left")
        )
    left_button.grid(
        row=2,
        column=1,
        padx=5,
        pady=5
        )

    Label(
        control_frame,
        text="Right:",
        bg="white"
        ).grid(row=3, column=0, padx=5, pady=5)
    right_button = Button(
        control_frame,
        text=controls["right"].upper(),
        width=10,
        command=lambda: set_control(right_button, "right")
        )
    right_button.grid(
        row=3,
        column=1,
        padx=5,
        pady=5
        )

    Label(
        control_frame,
        text="Pause:",
        bg="white"
        ).grid(row=4, column=0, padx=5, pady=5)
    pause_label = Label(
        control_frame,
        text=controls["pause"].upper(),
        width=10, bg="lightgray")
    pause_label.grid(
        row=4,
        column=1,
        padx=5,
        pady=5
        )
    pause_label.config(state="disabled")
    # Disable the label to prevent changes

    Label(
        control_frame,
        text="Boss Key:",
        bg="white"
        ).grid(row=5, column=0, padx=5, pady=5)
    bosskey_label = Label(
        control_frame,
        text="Ctrl+B",
        width=10,
        bg="lightgray"
        )
    bosskey_label.grid(
        row=5,
        column=1,
        padx=5,
        pady=5
        )
    bosskey_label.config(state="disabled")
    # Disable the label to prevent changes

    # Button to save the controls
    save_button = Button(
        frame,
        text="Save Controls",
        width=20, height=2,
        command=lambda: save_controls(username_info, controls),
        bg="lightblue", bd=3)
    save_button.pack(pady=15)

    # Button to go back to main menu
    back_button = Button(
        frame,
        text="Back",
        width=20, height=2,
        command=lambda: (frame.destroy(), main_menu()),
        bg="lightyellow", bd=3)
    back_button.pack(pady=10)


def show_leaderboard(callback=None):
    leaderboard = load_leaderboard()
    if not leaderboard:
        messagebox.showinfo("Leaderboard", "No scores available yet.")
        if callback:
            callback()
        return

    # Sort the leaderboard by high score in descending order
    sorted_leaderboard = sorted(
        leaderboard.items(),
        key=lambda x: x[1],
        reverse=True)

    # Create a new window to display the leaderboard
    leaderboard_window = Toplevel(window)
    leaderboard_window.title("Leaderboard")
    leaderboard_window.geometry("400x500")

    Label(
        leaderboard_window,
        text="Leaderboard",
        font=("Helvetica", 20)).pack(pady=10)

    # Display the top scores
    for index, (username_info, high_score_value) in enumerate(
        sorted_leaderboard[:10]
    ):
        Label(
            leaderboard_window,
            text=f"{index + 1}. {username_info}: {high_score_value}",
            font=("Helvetica", 16)
            ).pack(pady=5)

    # When the leaderboard window is closed, call the callback
    def on_close():
        if callback:
            callback()
        leaderboard_window.destroy()

    leaderboard_window.protocol("WM_DELETE_WINDOW", on_close)


def exit_game():
    window.destroy()


# Cheat code functions
def toggle_hitbox():
    global cheat_hitbox_visible
    cheat_hitbox_visible = not cheat_hitbox_visible
    if cheat_hitbox_visible:
        canvas.itemconfigure(hitbox, outline="red")
        canvas.itemconfigure(big_enemy_hitbox, outline="blue")
    else:
        canvas.itemconfigure(hitbox, outline="")
        canvas.itemconfigure(big_enemy_hitbox, outline="")
    # Update label
    if 'hitbox_label' in globals():
        status = "ON" if cheat_hitbox_visible else "OFF"
        hitbox_label.config(text=f"Hitbox Visible: {status}")


def toggle_invincibility():
    global invincibility
    invincibility = not invincibility
    status = "ON" if invincibility else "OFF"
    print(f"Invincibility mode: {status}")
    # Update label
    if 'invincibility_label' in globals():
        invincibility_label.config(text=f"Invincibility: {status}")


def skip_stage():
    global enemy_switch_timer
    enemy_switch_timer = 20  # Set timer to trigger stage switch
    print("Stage skipped!")


def add_extra_life():
    global lives, lives_label
    lives += 1
    lives_label.config(text=f"Lives: {lives}")
    print("Extra life added!")


def clear_enemies():
    global enemies
    for enemy in enemies:
        canvas.delete(enemy)
    enemies.clear()
    print("All enemies cleared!")


def show_cheat_codes():
    cheat_window = Toplevel(window)
    cheat_window.title("Cheat Codes")
    cheat_window.geometry("400x300")

    Label(
        cheat_window,
        text="Cheat Codes",
        font=("Helvetica", 20)).pack(pady=10)

    cheats = [
        ("H", "Toggle Hitbox Visibility"),
        ("I", "Toggle Invincibility Mode"),
        ("K", "Skip to Next Stage"),
        ("L", "Add an Extra Life"),
        ("C", "Clear All Enemies from Screen")
    ]

    for key, description in cheats:
        Label(
            cheat_window,
            text=f"Press '{key}' to {description}",
            font=("Helvetica", 14)
            ).pack(pady=5)

    # Close button
    Button(
        cheat_window, text="Close",
        command=cheat_window.destroy,
        font=("Helvetica", 14)
        ).pack(pady=10)


login_screen()

window.mainloop()
