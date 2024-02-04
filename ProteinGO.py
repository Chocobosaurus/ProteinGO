#!/usr/bin/env python3

import pygame, random, json, pygame.mask, os

def sign(x):
    return 0 if x == 0 else (-1 if x < 0 else 1)

def abs(x):
    return x if x > 0 else -x

pygame.init()
pygame.mixer.init()

score_dir = os.path.join(os.path.expanduser('~'), '.proteingo/scores')
os.makedirs(score_dir, exist_ok=True)

def save_scores(scores, mode):
    with open(os.path.join(score_dir, f"scores_{mode}.json"), "w") as file:
        json.dump(scores, file)

def load_scores(mode):
   # print(f"Loading scores! Cur file = {__file__} work dir = {os.getcwd()}")
    try:
        with open(os.path.join(score_dir, f"scores_{mode}.json"), "r") as file:
            scores = json.load(file)
            return scores
    except FileNotFoundError:
        return []

def show_high_scores(screen, endless_scores, normal_scores):
    font = pygame.font.Font("resources/ARCADECLASSIC.TTF", round(40 * scaling_factor))
    text_color_normal = (102, 178, 255)  # light blue
    text_color_endless = (255, 153, 51)
    y_position = round(80 * scaling_factor)
    
    normal_text = font.render("Normal   Mode   High Scores", True, text_color_normal)
    screen.blit(normal_text, (round(200 * scaling_factor), y_position))
    y_position += round(50 * scaling_factor)
    
    for score in normal_scores[:5]:
        score_text = font.render(str(score), True, text_color_normal)
        screen.blit(score_text, (round(300 * scaling_factor), y_position))
        y_position += round(40 * scaling_factor)     
    
    y_position += round(80 * scaling_factor)
    
    endless_text = font.render("Endless   Mode   High Scores", True, text_color_endless)
    screen.blit(endless_text, (round(200 * scaling_factor), y_position))
    y_position += round(50 * scaling_factor)
    
    for score in endless_scores[:5]:
        score_text = font.render(str(score), True, text_color_endless)
        screen.blit(score_text, (round(300 * scaling_factor), y_position))
        y_position += round(40 * scaling_factor)

def update_and_save_scores(scores, mode, points):
    if mode == "endless":
        scores.append(points)
    else:
        scores.append(points)
    scores.sort(reverse=True)
    save_scores(scores, mode)

def clear_scores_file(mode):
    empty_scores = []
    with open(f"scores/scores_{mode}.json", "w") as file:
        json.dump(empty_scores, file)


# Call this function to clear the scores
# clear_scores_file("endless")
# clear_scores_file("normal")


speed = [0, 8]
speed_0_by_1 = 1.0
acceleration = 3 / (30 * 30) # acceleration for endless
acceleration_normal = acceleration / 1.5 # acceleration for normal

game_time = 120
resolution = [1080, 810] # might need to check again [0], [1] if bug happens

# Detect the player's screen size
screen_info = pygame.display.Info()
screen_width = screen_info.current_w
screen_height = screen_info.current_h

# Desired aspect ratio
desired_width = 1080    
desired_height = 810
desired_aspect_ratio = desired_width / desired_height

# Calculate new screen size while maintaining aspect ratio
new_width = screen_width
new_height = int(new_width / desired_aspect_ratio)

# Check if the calculated height exceeds the screen height
if new_height > screen_height:
    new_height = int(screen_height - desired_height / 8)
    new_width = int(new_height * desired_aspect_ratio)

# Set the new screen size
resolution = (new_width, new_height)
#print(resolution)
screen = pygame.display.set_mode(resolution)

life = 4
available_life_values = [ -1, 0, 1, 2, 3, 4]  # Adjust this list as needed
protein_aggregated = False
time_up = False
endless = False
write_score = False


# Load the starting picture and score board pic
starting_picture = pygame.image.load("resources/starting_picture.png")

scaling_factor_width = resolution[0] / starting_picture.get_width()
scaling_factor_height = resolution[1] / starting_picture.get_height()
scaling_factor = min(scaling_factor_width, scaling_factor_height)
#print(scaling_factor)

starting_picture = pygame.transform.scale(starting_picture, (starting_picture.get_width() * scaling_factor,
                                                            starting_picture.get_height() * scaling_factor))

high_score_background = pygame.image.load("resources/high_score_background.png")
high_score_background = pygame.transform.scale(high_score_background, (high_score_background.get_width() * scaling_factor,
                                                            high_score_background.get_height() * scaling_factor))

credits_picture = pygame.image.load("resources/credits.png")
credits_picture = pygame.transform.scale(credits_picture, (credits_picture.get_width() * scaling_factor,
                                                            credits_picture.get_height() * scaling_factor))


icon = pygame.image.load("resources/protein_down4.png")
pygame.display.set_icon(icon)
pygame.display.set_caption('ProteinGO!')

# Creates protein
class ProteinClass(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("resources/protein_down4.png")
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.center = [resolution[0]/2, 100]
        self.angle = 0
        self.current_life = life
        self.image_index = available_life_values.index(self.current_life)
    def is_aggregated(self):
        return protein_aggregated

   # Turns protein
    def turn(self, direction):
        self.angle += direction
        if self.angle < 0:
            self.angle = 0
        elif self.angle >= len(self.image_filenames):
            self.angle = len(self.image_filenames) - 1
        self.load_image()
        speed = [0, 8]  # Speed doesn't change when turning
        return speed

    # Moves protein left and right
    def move(self, speed):
        if speed[1] > 0:  # Only move if speed is greater than 0
            self.rect.centerx += speed[0]
            if self.rect.centerx < 20:
                self.rect.centerx = 20
            if self.rect.centerx > resolution[0] - 20:
                self.rect.centerx = resolution[0] - 20

# Creates obstacles
class ObstacleClass(pygame.sprite.Sprite):
    def __init__(self, image_file, location, obs_type):
        pygame.sprite.Sprite.__init__(self)
        self.image_file = image_file
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.center = location
        self.obs_type = obs_type
        self.passed = False
        
    # Makes scenery scroll up
    def update(self):
        global speed
        self.rect.centery -= speed[1]
        # Deletes obstacles that have scrolled off the top of the screen
        if self.rect.centery < -(resolution[1]/ 20):
            self.kill()
            
            
# Creates one screen full of random obstacles
obstacle_number = round(15 * scaling_factor)
def create_map():
    global obstacles
    locations = []
    spawn_zone_edge = round(30 * scaling_factor)
    for i in range(obstacle_number):
        row = random.randint(0, obstacle_number - 1)
        col = random.randint(0, obstacle_number - 1)
        location = [col * resolution[0] / obstacle_number + spawn_zone_edge, 
                    row * resolution[1] / obstacle_number + spawn_zone_edge + resolution[1]]
        if not (location in locations):
            locations.append(location)
            obs_type = random.choice(["agg1", "agg2", "agg3", "agg4", "agg5",
                                      "rna1", "rna2", "rna3", "rna4",
                                      "proteasome"])  # Add new obs types
            if obs_type == "agg1":
                img = "resources/agg1.png"
            elif obs_type == "agg2":
                img = "resources/agg2.png"
            elif obs_type == "agg3":
                img = "resources/agg3.png"
            elif obs_type == "agg4":
                img = "resources/agg4.png"
            elif obs_type == "agg5":
                img = "resources/agg5.png"
            elif obs_type == "rna1":
                img = "resources/rna1.png"
            elif obs_type == "rna2":
                img = "resources/rna2.png"
            elif obs_type == "rna3":
                img = "resources/rna3.png"
            elif obs_type == "rna4":
                img = "resources/rna4.png"
            elif obs_type == "proteasome":
                img = "resources/proteasome.png"
            obstacle = ObstacleClass(img, location, obs_type)
            obstacles.add(obstacle)
            
            
# Redraws screen
def animate():
    screen.fill([255, 255, 240])
    obstacles.draw(screen)
    screen.blit(protein.image, protein.rect)
    
    screen.blit(time_text, [round(10 * scaling_factor), round(10 * scaling_factor)])
    screen.blit(life_text, [round(10 * scaling_factor), round(60 * scaling_factor)])
    screen.blit(score_text, [round(10 * scaling_factor), round(110 * scaling_factor)])
    
    if protein_aggregated:
        # Draw aggregated message
        message11 = font.render("Your   Protein   is   Too   Aggregated   to   function", 1, (255, 0, 0))
        message12 = small_font.render("Press   R   to   Restart", 1, (255, 0, 0))
        screen.blit(message11, (resolution[0] / 2 - message11.get_width() // 2, 
                                resolution[1] - 70 - message11.get_height()))
        screen.blit(message12, (resolution[0] / 2 - message12.get_width() // 2, 
                                resolution[1] - 20 - message12.get_height()))
        
    elif time_up:
        # Draw praise message
        message01 = font.render("The   cell   is   healthy   and   functional", 1, (255, 102, 178)) #pink
        message02 = font.render("You   have   been   a   great   protein!", 1, (255, 165, 0))
        message03 = small_font.render("Press   R   to   Restart", 1, (255, 165, 0))
        screen.blit(message01, (resolution[0] / 2 - message01.get_width() // 2, 
                               resolution[1] - 120 - message01.get_height()))
        screen.blit(message02, (resolution[0] / 2 - message02.get_width() // 2, 
                               resolution[1] - 70 - message02.get_height()))
        screen.blit(message03, (resolution[0] / 2 - message03.get_width() // 2, 
                               resolution[1] - 20 - message03.get_height()))
        pygame.display.flip()

    
    pygame.display.flip()


# Gets everything ready
pygame.init()
screen = pygame.display.set_mode(resolution)
clock = pygame.time.Clock()
protein = ProteinClass()
obstacles = pygame.sprite.Group()
create_map()
font = pygame.font.Font("resources/ARCADECLASSIC.TTF", round(40 * scaling_factor))  # Load the custom font
small_font = pygame.font.Font("resources/ARCADECLASSIC.TTF", round(30 * scaling_factor))
agg_sound = pygame.mixer.Sound("resources/hit_agg.wav")
rna_sound = pygame.mixer.Sound("resources/gain_points.wav")
proteasome_sound = pygame.mixer.Sound("resources/increase_life.wav")



# Starts the main loop
running = True
show_starting_picture = True
show_score = False
show_credits = False
is_music_playing = False
scrolling = False
endless_scores = load_scores("endless")
normal_scores = load_scores("normal")

while running:
    clock.tick(30)  # fps

    # Checks for keypresses or window close
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            
            if show_starting_picture and event.key == pygame.K_RETURN:
                show_starting_picture = False
                # Restart the main loop
                write_score = False
                time_up = False
                endless = False
                scrolling = True
                protein_aggregated = False
                start_time = pygame.time.get_ticks()
                speed = [0, 8]
                life = 4
                points = 0
                map_position = 0
                obstacles.empty()
                create_map()
                protein = ProteinClass()
                protein.image = pygame.image.load("resources/protein_down4.png")
                # Play BG
                if not is_music_playing:
                  pygame.mixer.music.load("resources/bg.mp3")
                  pygame.mixer.music.play(-1)  # loop forever
                  is_music_playing = True 
                 
            elif event.key == pygame.K_LEFT:
                if speed[1] > 0:
                    if speed[0] == 0:
                        speed[0] = -8
               #         print(f"\n\n\nHIT {speed[0]=}\n\n\n")
                    elif speed[0] > 0:
                        speed[0] = -speed[0]
                if speed[1] == 0:
                    speed[0] = 0
                    scrolling = False
            elif event.key == pygame.K_RIGHT:
                if speed[1] > 0:
                    if speed[0] == 0:
                        speed[0] = 8
                    elif speed[0] < 0:
                        speed[0] = -speed[0]
                if speed[1] == 0:
                    speed[0] = 0
                    scrolling = False
                    
            elif event.key == pygame.K_ESCAPE:
                running = False
            
            elif show_starting_picture and event.key == pygame.K_u:
                endless = True
                show_starting_picture = False
                # Restart the main loop
                write_score = False
                time_up = False
                scrolling = True
                protein_aggregated = False
                start_time = pygame.time.get_ticks()
                speed = [0, 8]
                life = 4
                points = 0
                map_position = 0
                obstacles.empty()
                create_map()
                protein = ProteinClass()
                protein.image = pygame.image.load("resources/protein_down4.png")
                # Play BG
                if not is_music_playing:
                  pygame.mixer.music.load("resources/bg.mp3")
                  pygame.mixer.music.play(-1)
                  is_music_playing = True 
                
            elif event.key == pygame.K_r:
                # Writes in highscore
                if write_score:
                    if endless:
                        update_and_save_scores(endless_scores, "endless", points)
                    else:
                        update_and_save_scores(normal_scores, "normal", points)
                # Show starting pic
                show_starting_picture = True
                screen.blit(starting_picture, (0, 0))
                pygame.display.flip()
                pygame.mixer.music.stop()
                is_music_playing = False
                # Restart the main loop
                write_score = False
                time_up = False
                endless = False
                scrolling = True
                protein_aggregated = False
                start_time = pygame.time.get_ticks()
                speed = [0, 8]
                life = 4
                points = 0
                map_position = 0
                obstacles.empty()
                create_map()
                protein = ProteinClass()
                protein.image = pygame.image.load("resources/protein_down4.png")
                
                
            # Enter score board    
            elif show_starting_picture and event.key == pygame.K_p:
                 show_score = True
                              
            elif show_score and event.key == pygame.K_p:
                 show_score = False
                 # Show starting pic
                 show_starting_picture = True
                 screen.blit(starting_picture, (0, 0))
                 pygame.display.flip()
                 pygame.mixer.music.stop()
                 is_music_playing = False
                 # Restart the main loop
                 write_score = False
                 time_up = False
                 endless = False
                 scrolling = True
                 protein_aggregated = False
                 start_time = pygame.time.get_ticks()
                 speed = [0, 8]
                 life = 4
                 points = 0
                 map_position = 0
                 obstacles.empty()
                 create_map()
                 protein = ProteinClass()
                 protein.image = pygame.image.load("resources/protein_down4.png")
                 
            # Enter credits
            elif show_score and event.key == pygame.K_c:
                 show_credits = True
                 show_score = False
                              
            elif show_credits and event.key == pygame.K_c:
                 show_credits = False
                 # Show starting pic
                 show_starting_picture = True
                 screen.blit(starting_picture, (0, 0))
                 pygame.display.flip()
                 pygame.mixer.music.stop()
                 is_music_playing = False
                 # Restart the main loop
                 write_score = False
                 time_up = False
                 endless = False
                 scrolling = True
                 protein_aggregated = False
                 start_time = pygame.time.get_ticks()
                 speed = [0, 8]
                 life = 4
                 points = 0
                 map_position = 0
                 obstacles.empty()
                 create_map()
                 protein = ProteinClass()
                 protein.image = pygame.image.load("resources/protein_down4.png")
                    
    if show_score:
        screen.blit(high_score_background, (0, 0))
        show_high_scores(screen, endless_scores, normal_scores)
        pygame.display.flip()
        show_starting_picture = False
        continue
    
    if show_credits:
        screen.blit(credits_picture, (0, 0))
        pygame.display.flip()
        show_starting_picture = False
        continue
                
    # Display starting picture until return key is pressed
    if show_starting_picture:
        screen.blit(starting_picture, (0, 0))
        pygame.display.flip()
        continue  # Skip the rest of the loop    
    
    # Start the count down
    current_time = pygame.time.get_ticks()
    elapsed_time = (current_time - start_time) // 1000  
    #  print(elapsed_time)
   
    if endless == False:
        if elapsed_time >= game_time:
            # Halt protein movement and scrolling
            speed = [0, 0]  # Set both horizontal and vertical speeds to 0
            protein.image = pygame.image.load("resources/winner.png")
            scrolling = False
            time_up = True
            write_score = True
 
    # Stop protein if the vertical speed is 0
    if life <= 0:
        life = 0
        protein_aggregated = True
        speed = [0, 0]
        protein.image = pygame.image.load("resources/protein_crash0.png")
        scrolling = False
        write_score = True
            
    # Update protein's vertical movement
    protein.move(speed)
        
    
    if scrolling:
        map_position += speed[1]  # Scrolls scenery with acceleration
        if endless:
            speed[1] += acceleration
        else:
            speed[1] += acceleration_normal 
        if speed[0] != 0:
            speed[0] = sign(speed[0]) * speed_0_by_1 * speed[1]  #protein horizontal speed increases too

    # Creates a new screen full of scenery
    if map_position >= resolution[1]:
        create_map()
        map_position = 0

    # Checks for hitting obstacles and getting flags
    hit = pygame.sprite.spritecollide(protein, obstacles, False)
    for collision in hit:
      if collision.mask.overlap(protein.mask, (protein.rect.x - collision.rect.x, protein.rect.y - collision.rect.y)):
        # Collision occurred between protein and obstacle
          if "agg" in hit[0].obs_type and not hit[0].passed:
              life -= 1
              # Stop protein if the vertical speed is 0
              if life <= 0:
                  life = 0
                  protein_aggregated = True
                  speed = [0, 0]
                  protein.image = pygame.image.load("resources/protein_crash0.png")
                  scrolling = False
                  write_score = True
              protein.current_life = life
              protein.image_index = available_life_values.index(protein.current_life)
              
         #     print("Current life:", protein.current_life)  # Print current life for debugging
              
              if protein.current_life >= 0:
         #         print("Loading crash image")
                  protein.image = pygame.image.load(f"resources/protein_crash{int(protein.current_life)}.png")
                  protein.rect = protein.image.get_rect(center=protein.rect.center)
                  protein.mask = pygame.mask.from_surface(protein.image)
                  animate()
                  agg_sound.play() 
                  pygame.time.delay(1000)
              
              if protein.current_life > 0:
         #        print("Loading down image")
                  protein.image = pygame.image.load(f"resources/protein_down{int(protein.current_life)}.png")
              
              speed[1] -= 2  # Reduce speed when crashing 
              if speed[0] != 0:
                 speed[0] = sign(speed[0]) * speed_0_by_1 * speed[1]
              hit[0].passed = True
              hit[0].kill()  # Remove the obstacle
              
          elif "rna" in hit[0].obs_type and not hit[0].passed:
              points += 1
              rna_sound.play()
              hit[0].kill()
              
          elif "proteasome" in hit[0].obs_type and not hit[0].passed:
               if protein.current_life == 4:
                   pygame.time.delay(1000)
                   hit[0].passed = True
                   hit[0].kill()
               elif protein.current_life < 4:
          #         print("Loading down image")
                   proteasome_sound.play()
                   pygame.time.delay(1000)
                   life += 1
                   protein.current_life = life
                   protein.image_index = available_life_values.index(protein.current_life)
                   protein.image = pygame.image.load(f"resources/protein_down{int(protein.current_life)}.png")
                   speed[1] += 2  
                   if speed[0] != 0:
                       speed[0] = sign(speed[0]) * speed_0_by_1 * speed[1]
                   hit[0].passed = True
                   hit[0].kill()  
  
    #  print(f"{speed[0]=}")
         

    # Draw score text
    if endless:
        display_time = 9999
    elif protein_aggregated:
        display_time = 0
    else: 
        display_time = max(game_time - elapsed_time, 0)
        
    time_text = font.render("Time    " + str(display_time), 1, (0, 128, 255))  # Blue 
    life_text = font.render("Life    " + str(life), 1, (102, 204, 0))  # Green
    score_text = font.render("Function    Score    " + str(points), 1, (255, 165, 0))  # Orange
    
    obstacles.update()
    
    animate()
    
pygame.quit()
