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
                count, delay, full_directory_name_from_desc = part_match.groups()
                
                # --- NEW ADDITION START ---
                # Extract the actual directory name (e.g., 'part0' from 'part0 #FFFFFF -1')
                # This assumes the actual directory name is the first word before any spaces or '#'
                actual_directory_name = full_directory_name_from_desc.split(' ')[0].split('#')[0]
                actual_directory_name = os.path.normpath(actual_directory_name.strip()) # Clean up any leading/trailing spaces
                # --- NEW ADDITION END ---

                # Use os.path.normpath to handle potential path inconsistencies (e.g., / vs \)
                parts.append((actual_directory_name, int(count), int(delay))) # Use the actual_directory_name here
                print(f"Found animation part: Original Desc='{full_directory_name_from_desc}', Actual Directory='{actual_directory_name}', Play Count={count}, Delay={delay} ms")

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

    # Get screen resolution
    infoObject = pygame.display.Info()
    screen_width_max = infoObject.current_w
    screen_height_max = infoObject.current_h

    # Calculate base scale factors to fit the animation within the screen while maintaining aspect ratio
    scale_by_width = screen_width_max / width
    scale_by_height = screen_height_max / height
    
    # Choose the smaller scale factor to ensure the entire animation fits within the screen
    initial_scale_factor = min(scale_by_width, scale_by_height)

    # Optional: If the animation is much smaller than the screen, you might not want to upscale it too much.
    # For a high-res boot animation, it's generally scaled down.
    # This prevents tiny animations from becoming gigantic and pixelated if your screen is huge.
    max_upscale_factor_auto = 1.0 # By default, do not upscale beyond original animation size
    if initial_scale_factor > max_upscale_factor_auto:
        initial_scale_factor = max_upscale_factor_auto

    # Apply the user-defined scale factor from command line arguments
    # args.scale comes from the argparse, default is 1.0
    display_width = int(width * initial_scale_factor * args.scale)
    display_height = int(height * initial_scale_factor * args.scale)
    
    # Ensure minimum size to prevent tiny windows or zero dimensions, which can cause Pygame errors
    if display_width < 100: display_width = 100
    if display_height < 100: display_height = 100

    # Set the Pygame window size using the scaled dimensions, allowing it to be resizable by the user
    screen = pygame.display.set_mode((display_width, display_height), pygame.RESIZABLE)
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
            # Handle window resizing if RESIZABLE flag is set
            if event.type == pygame.VIDEORESIZE:
                # Update display_width and display_height to the new window size
                # Ensure the new size is at least 1x1 to prevent errors
                new_width, new_height = event.size
                if new_width < 1: new_width = 1
                if new_height < 1: new_height = 1
                display_width = new_width
                display_height = new_height
                # Recreate the screen surface with the new size (important for correct blitting)
                screen = pygame.display.set_mode((display_width, display_height), pygame.RESIZABLE)

        if not running:
            break

        # Get information for the current playing part
        current_part_dir, play_count, delay_ms = parts[current_part_idx]
        part_full_path = os.path.join(temp_dir, current_part_dir)

        # A list of common image extensions to check for
        image_extensions = ('.png', '.jpg', '.jpeg') 

        frames = []
        try:
            # Filter out any files that are not images (like +trim.txt files)
            frames = sorted([f for f in os.listdir(part_full_path) if f.lower().endswith(image_extensions)])
        except FileNotFoundError:
            print(f"Oof! The directory '{part_full_path}' for animation part '{current_part_dir}' was not found after extraction! Skipping this part. (つд⊂)")
            current_part_idx = (current_part_idx + 1) % len(parts)
            current_frame_idx = 0
            current_part_play_count = 0
            # If we've looped through all parts and none worked, terminate to avoid infinite loop
            if current_part_idx == 0 and len(parts) > 0: # Check if we wrapped around all parts and are back at start
                print("Cycled through all parts, none found or contained images. Ending preview. (T_T)")
                running = False
            continue
        except Exception as e:
            print(f"Error accessing directory '{part_full_path}'! ε(┬┬﹏┬┬)3 Error: {e}")
            running = False
            break

        if not frames:
            print(f"No PNG/JPG images found in current part '{current_part_dir}'! (°ー°〃)")
            # If a part has no images, skip it to prevent crashes
            current_part_idx = (current_part_idx + 1) % len(parts)
            current_frame_idx = 0
            current_part_play_count = 0
            # If there's only one part and it has no images, terminate to avoid infinite loop
            if len(parts) == 1 or (current_part_idx == 0 and len(parts) > 0): # Ensure we don't infinitely loop on a single empty part
                print("Only one part and no images, or cycled through all parts. Ending preview.")
                running = False
            continue

        # Display the current frame
        frame_file = os.path.join(part_full_path, frames[current_frame_idx])
        
        # --- HERE: Add logic to handle +trim.txt files ---
        trim_info_file = frame_file + "+trim.txt"
        
        # Load the base image
        pil_image = Image.open(frame_file).convert("RGBA")
        pygame_image_trimmed = pygame.image.fromstring(pil_image.tobytes(), pil_image.size, pil_image.mode)

        # This will be the image that has original animation dimensions (width x height)
        pygame_final_animation_frame = None 

        if os.path.exists(trim_info_file):
            # Parse trim_info_file to get original_width, original_height, offset_x, offset_y
            with open(trim_info_file, 'r') as f:
                trim_data = f.readline().strip().split()
                if len(trim_data) == 4:
                    # original_width, original_height from trim.txt are often for a virtual canvas
                    # Here we only care about offset_x, offset_y for placement on the 'width x height' surface.
                    offset_x = int(trim_data[2])
                    offset_y = int(trim_data[3])
                else:
                    # Handle unexpected trim.txt format
                    print(f"Warning: Unexpected format in {trim_info_file}. Trying to display without trim info. (・_・;)")
                    offset_x, offset_y = 0, 0 # Fallback
            
            # Create a blank surface with the animation's total width and height
            display_surface = pygame.Surface((width, height), pygame.SRCALPHA) # SRCALPHA for transparency
            display_surface.fill((0, 0, 0, 0)) # Fill with transparent black
            # Blit the trimmed image onto the display_surface at the correct offset
            display_surface.blit(pygame_image_trimmed, (offset_x, offset_y)) 
            pygame_final_animation_frame = display_surface
            
        else:
            # No trim.txt, so display as is, scaled to fit the animation's (width, height)
            pygame_final_animation_frame = pygame_image_trimmed
            # Check if the image size already matches the desc.txt width/height
            if pil_image.size != (width, height):
                # If not, scale it to match the animation's defined width/height
                pygame_final_animation_frame = pygame.transform.scale(pygame_final_animation_frame, (width, height))
        # --- END of +trim.txt logic ---

        try:
            screen.fill((0, 0, 0)) # Clear screen with black background

            # --- NEW! Calculate scaling for the image to fit the *current window* while maintaining aspect ratio ---
            img_aspect_ratio = width / height # Aspect ratio of the original animation (e.g., 1080/1920)
            window_aspect_ratio = display_width / display_height # Aspect ratio of the current Pygame window

            scaled_img_width = display_width
            scaled_img_height = int(display_width / img_aspect_ratio)

            # If scaling by width makes the image too tall for the window's height,
            # then scale by height instead to ensure it fits vertically.
            if scaled_img_height > display_height:
                scaled_img_height = display_height
                scaled_img_width = int(display_height * img_aspect_ratio)
            
            # Ensure scaled dimensions are at least 1x1 to prevent errors
            if scaled_img_width < 1: scaled_img_width = 1
            if scaled_img_height < 1: scaled_img_height = 1

            # Perform the final scaling of the image to the calculated dimensions
            scaled_image_to_blit = pygame.transform.scale(pygame_final_animation_frame, (scaled_img_width, scaled_img_height))
            
            # Calculate position to center the image within the window
            pos_x = (display_width - scaled_img_width) // 2
            pos_y = (display_height - scaled_img_height) // 2

            screen.blit(scaled_image_to_blit, (pos_x, pos_y)) # Use the scaled and positioned image
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
        # Only tick the clock if there's no part-specific delay, otherwise the delay already handles timing.
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

    # Add the -s or --scale argument for overall window scaling
    parser.add_argument('-s', '--scale', 
                        type=float, 
                        default=1.0, # Default to no additional scaling (auto-fit to screen)
                        help='Overall scaling factor for the preview window. '
                             'e.g., -s 0.5 to make the window half size. '
                             'Defaults to 1.0 (auto-fit to screen without additional scaling).')

    # Parse the arguments from the command line
    args = parser.parse_args()

    # Use the file path provided by the argument, or the default
    boot_animation_file = args.file
    
    print(f"Preparing to preview file: {boot_animation_file}! (ﾉ◕ヮ◕)ﾉ*:･ﾟﾟ✧")
    preview_bootanimation(boot_animation_file)
