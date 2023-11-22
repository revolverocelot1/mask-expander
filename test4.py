
import cv2
import numpy as np
import os
import PySimpleGUI as sg
import subprocess
import atexit
import webbrowser

# Define the paths for the webui and the exe files
webui_path = 'd:\\New folder\\sd\\stable-diffusion-webui\\webui-user.bat'
exe_path = 'E:\\DAIN_APP Alpha 1.0\\DAINAPP.exe'

# Define a function to open the exe file at exit
def open_exe():
    os.startfile(exe_path)

# Register the function
atexit.register(open_exe)

# Define a function to make frames from a video file
def make_frames(video_path, quality, output_folder):
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print('Error opening video file')
        return

    # Get the frame count
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Create the frames folder
    frames_folder = os.path.join(output_folder, 'frames')
    if not os.path.exists(frames_folder):
        os.makedirs(frames_folder)

    # Create the sorted frames folder
    sorted_folder = os.path.join(output_folder, 'sorted_frames')
    if not os.path.exists(sorted_folder):
        os.makedirs(sorted_folder)

    # Determine the frame interval based on quality
    if quality == 'low':
        frame_interval = 5
    elif quality == 'medium':
        frame_interval = 4
    elif quality == 'high':
        frame_interval = 3
    else:
        print('Invalid quality specified.')
        return

    # Extract and save frames
    for i in range(frame_count):
        ret, frame = cap.read()

        if i % frame_interval == 0:
            frame_name = f"{i}.jpg"
            frame_path = os.path.join(frames_folder, frame_name)
            cv2.imwrite(frame_path, frame)

    # Sort the frames and save to the sorted folder
    frames = os.listdir(frames_folder)
    frames.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))
    for frame_name in frames:
        frame_path = os.path.join(frames_folder, frame_name)
        sorted_path = os.path.join(sorted_folder, frame_name)
        os.rename(frame_path, sorted_path)

    print(f'{len(frames)} frames extracted and saved to {sorted_folder}')

    # Write output details to txt file
    output_file = os.path.join(output_folder, 'output.txt')
    with open(output_file, 'w') as f:
        f.write(f"Output folder: {sorted_folder}\n")
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = frame_count / fps
        f.write(f"FPS: {fps}\n")
        f.write(f"Duration: {duration} seconds\n")

# Define a function to expand the mask of an object in an image
def expand_mask(input_folder, output_folder, expansion):
    # Loop through the files in the input folder
    for filename in os.listdir(input_folder):
        # Get the file extension
        ext = os.path.splitext(filename)[1]

        # Check if the file is an image
        if ext.lower() in ('.jpg', '.png', '.bmp'):
            # Get the file name without the extension
            name = os.path.splitext(filename)[0]

            # Construct the mask path
            mask_path = os.path.join(input_folder, name + '_mask' + ext)

            # Check if the mask exists
            if os.path.exists(mask_path):
                # Read the image and the mask
                image = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
                mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)

                # Find the contours of the mask
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

                # Create a new blank image with the same size and type as the original image
                new_image = np.zeros(image.shape, image.dtype)

                # Get the average color of the mask
                color = cv2.mean(mask)[0]

                # Draw the contours on the new image with the same color as the mask
                cv2.drawContours(new_image, contours, -1, color, expansion)

                # Get the output file path
                output_path = os.path.join(output_folder, filename)

                # Save the new image
                cv2.imwrite(output_path, new_image)

# Define the UI theme
sg.theme('Dark Blue 3')

# Define the layout of the video frame extraction tab
video_layout = [
    [sg.Text('Video Path:'), sg.Input(), sg.FileBrowse()],
    [sg.Text('Output Folder:'), sg.Input(), sg.FolderBrowse()],
    [sg.Text('Quality:')],
    [sg.Radio('Low (fast)', 'quality', default=True, key='low'),
     sg.Radio('Medium (normal)', 'quality', key='medium'),
     sg.Radio('High (slow)', 'quality', key='high')],
    [sg.Checkbox('CHECK mark if using for Segmentation (Will redirect to colab)', key='open_site', default=False)],
    [sg.Button('Make Frames')]
]

# Define the layout of the image mask expansion tab
image_layout = [
    [sg.Text('Input Folder:'), sg.Input(), sg.FolderBrowse()],
    [sg.Text('Output Folder:'), sg.Input(), sg.FolderBrowse()],
    [sg.Text('Expansion (pixels):'), sg.InputText(10)],
    [sg.Button('Expand Mask')]
]

# Define the layout of the UI with two tabs
layout = [
    [sg.TabGroup([[sg.Tab('Video Frame Extraction', video_layout), sg.Tab('Image Mask Expansion', image_layout)]])],
    [sg.Button('Exit')]
]

# Create the window
window = sg.Window('Video Frame Extractor and Image Mask Expander', layout)

# Process UI events
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    elif event == 'Make Frames':
        # Get the video path and the output folder
        video_path = values[0]
        output_folder = values[1]

        # Get the quality
        quality = ''
        if values['low']:
            quality = 'low'
        elif values['medium']:
            quality = 'medium'
        elif values['high']:
            quality = 'high'

        # Make frames from the video file
        make_frames(video_path, quality, output_folder)

    elif event == 'Expand Mask':
        # Get the input and output folders
        input_folder = values[2]
        output_folder = values[3]

        # Get the expansion value and convert it to an integer
        try:
            expansion = int(values[4])
        except ValueError:
            # Show an error message if the conversion fails
            sg.popup('Invalid expansion value')
            continue

        # Check if the expansion value is positive
        if expansion <= 0:
            # Show an error message if the expansion value is negative or zero
            sg.popup('Expansion value must be positive')
            continue

        # Expand the mask of the object in the images
        expand_mask(input_folder, output_folder, expansion)

# Close the window
window.close()

if values['open_site']:  # Added conditional statement
    webbrowser.open('https://colab.research.google.com/github/revolverocelot1/mask-expander/blob/main/SAMTrack.ipynb')

# Open the web browser
webbrowser.open('http://127.0.0.1:7860/')
