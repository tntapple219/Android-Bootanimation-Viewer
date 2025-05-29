import zipfile
import os
import re
import pygame
from PIL import Image
import shutil
import argparse

def preview_bootanimation(zip_path):
    """
    Previews a bootanimation.zip file.
    """
    if not os.path.exists(zip_path):
        print(f"Oops! File '{zip_path}' not found! (>_<)")
        return

    temp_dir = "bootanimation_temp_preview"
    # Ensure the temporary directory is clean. If old one exists, delete it first.
    if os.path.exists(temp_dir):
        try:
            shutil.rmtree(temp_dir)
            print(f"Cleaning up old temporary directory '{temp_dir}'! (o゜▽゜)o☆")
        except Exception as e:
            print(f"Error cleaning up old temp directory! ε(┬┬﹏┬┬)3 Error: {e}")
            return # Cannot proceed if cleanup fails

    os.makedirs(temp_dir, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            # Although zipfile can extract without checking compression method,
            # the standard requires 'store'. Not explicitly checking each file's
            # compression method here, assuming the file is valid.
            zf.extractall(temp_dir)
        print(f"Successfully extracted to '{temp_dir}'! (o゜▽゜)o☆")
    except zipfile.BadZipFile:
        print("Whoops, this is not a valid ZIP file, or it's compressed instead of 'store'!")
        # Clean up failed extraction directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        return
    except Exception as e:
        print(f"Error during extraction! ε(┬┬﹏┬┬)3 Error: {e}")
        # Clean up failed extraction directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        return

    desc_path = os.path.join(temp_dir, 'desc.txt')
    if not os.path.exists(desc_path):
        print(f"Oh no! 'desc.txt' not found in '{temp_dir}'! This doesn't seem to be a standard bootanimation.zip! (°ー°〃)")
        shutil.rmtree(temp_dir) # Clean up regardless
        return

    width, height, fps = 0, 0, 0
    parts = [] # Stores information for each animation part: (directory, play_count, delay)

    try:
        with open(desc_path, 'r') as f:
            lines = f.readlines()

        # Parse the first line: width height fps
        header_match = re.match(r'(\d+)\s+(\d+)\s+(\d+)', lines[0].strip())
        if header_match:
            width, height, fps = map(int, header_match.groups())
            print(f"Animation parameters: Width={width}, Height={height}, FPS={fps}! (≧▽≦)")
        else:
            print("First line of desc.txt has an incorrect format! It should be 'width height fps'! (>_<)")
            shutil.rmtree(temp_dir)
            return

        # Parse subsequent lines: play_count delay directory
        # Changed 'p' to 'c' to match formats like 'c 0 0 Part0'
        for line in lines[1:]:
            # This is the corrected regex!
            part_match = re.match(r'[pc]\s+(\d+)\s+(\d+)\s+(.+)', line.strip())
            if part_match:
                count, delay, directory = part_match.groups()
                parts.append((directory, int(count), int(delay)))
                print(f"Found animation part: Directory='{directory}', Play Count={count}, Delay={delay} ms")

    except Exception as e:
        print(f"Error parsing desc.txt! ε(┬┬﹏┬┬)3 Error: {e}")
        shutil.rmtree(temp_dir)
        return

    if not parts:
        print("No animation parts defined in desc.txt! Nothing to play! (＞﹏＜)")
        shutil.rmtree(temp_dir)
        return

    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(f"Bootanimation Previewer - {os.path.basename(zip_path)}")
    clock = pygame.time.Clock()

    current_part_idx = 0
    current_frame_idx = 0
    current_part_play_count = 0
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: # Press ESC to exit
                    running = False

        if not running:
            break

        # Get information for the current playing part
        current_part_dir, play_count, delay_ms = parts[current_part_idx]
        part_full_path = os.path.join(temp_dir, current_part_dir)

        # Load images for the current part
        # A list of common image extensions to check for
        # (You can add more if needed, like .webp, .bmp, etc.)
        image_extensions = ('.png', '.jpg', '.jpeg') 

        frames = sorted([f for f in os.listdir(part_full_path) if f.lower().endswith(image_extensions)])
        if not frames:
            print(f"No PNG images found in current part '{current_part_dir}'! (°ー°〃)")
            # If a part has no images, skip it to prevent crashes
            current_part_idx = (current_part_idx + 1) % len(parts)
            current_frame_idx = 0
            current_part_play_count = 0
            # If there's only one part and it has no images, terminate to avoid infinite loop
            if len(parts) == 1:
                print("Only one part and no images, ending preview.")
                running = False
            continue

        # Display the current frame
        frame_file = os.path.join(part_full_path, frames[current_frame_idx])
        try:
            pil_image = Image.open(frame_file).convert("RGBA") # Ensure RGBA format
            pygame_image = pygame.image.fromstring(pil_image.tobytes(), pil_image.size, pil_image.mode)
            screen.fill((0, 0, 0)) # Clear screen with black background
            screen.blit(pygame_image, (0, 0))
            pygame.display.flip() # Update display
        except Exception as e:
            print(f"Error loading or displaying image '{frame_file}'! ε(┬┬﹏┬┬)3 Error: {e}")
            running = False
            break

        # Calculate the next frame
        current_frame_idx += 1
        if current_frame_idx >= len(frames):
            # End of one part
            current_frame_idx = 0
            current_part_play_count += 1
            
            # Check if the part needs to loop (count 0 means infinite loop)
            if play_count != 0 and current_part_play_count >= play_count:
                # Reached play count for this part, switch to next part
                current_part_idx = (current_part_idx + 1) % len(parts)
                current_part_play_count = 0
                print(f"Switching to the next animation part! Now on part {current_part_idx + 1}.")
            
            # Handle delay between parts
            if delay_ms > 0:
                pygame.time.delay(delay_ms)

        # Control frame rate (if no explicit part delay)
        if delay_ms == 0:
            clock.tick(fps) # Limit frame rate for smoother animation

    pygame.quit()
    print("Preview ended! Bye bye! (⌒▽⌒)☆")

    # Clean up temporary files
    try:
        shutil.rmtree(temp_dir)
        print(f"Temporary folder '{temp_dir}' cleaned up! (ง •̀_•́)ง")
    except Exception as e:
        print(f"Error cleaning temporary folder! ε(┬┬﹏┬┬)3 Error: {e}")


# --- Usage Example ---
if __name__ == '__main__':
    # Create an argument parser
    parser = argparse.ArgumentParser(
        description='Preview an Android bootanimation.zip file. '
                    'By default, it looks for "bootanimation.zip" in the current directory.'
    )
    
    # Add the -f or --file argument, now optional with a default value
    parser.add_argument('-f', '--file', 
                        type=str, 
                        default='bootanimation.zip', # Set a default value
                        help='Path to the bootanimation.zip file to preview. '
                             'Defaults to "bootanimation.zip" in the current directory.')

    # Parse the arguments from the command line
    args = parser.parse_args()

    # Use the file path provided by the argument, or the default
    boot_animation_file = args.file
    
    print(f"Preparing to preview file: {boot_animation_file}! (ﾉ◕ヮ◕)ﾉ*:･ﾟﾟ✧")
    preview_bootanimation(boot_animation_file)