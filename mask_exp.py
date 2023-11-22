import cv2
import os
import PySimpleGUI as sg

# Define the input and output folders
input_folder = "input"  # Change this to your input folder name
output_folder = "output"  # Change this to your output folder name

# Define the amount of expansion in pixels
expansion = 10  # Change this to your desired value

# Define the UI layout
layout = [
    [sg.Text("Image Mask Expander")],
    [sg.Text("Input folder:"), sg.InputText(input_folder), sg.FolderBrowse()],
    [sg.Text("Output folder:"), sg.InputText(output_folder), sg.FolderBrowse()],
    [sg.Text("Expansion (pixels):"), sg.InputText(expansion)],
    [sg.Button("Process"), sg.Button("Exit")]
]

# Create the UI window
window = sg.Window("Image Mask Expander", layout)

# Main loop
while True:
    # Read the user input event, values = window.read()
    event, values = window.read()

    # If the user clicks Exit or closes the window, break the loop
    if event in (None, "Exit"):
        break

    # If the user clicks Process, start the processing
    if event == "Process":
        # Get the input and output folders from the UI
        input_folder = values[0]
        output_folder = values[1]

        # Get the expansion value from the UI and convert it to an integer
        expansion = int(values[2])

        # Loop through the files in the input folder
        for filename in os.listdir(input_folder):
            # Get the full path of the file
            filepath = os.path.join(input_folder, filename)

            # Read the image as grayscale
            image = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)

            # Find the contours of the mask
            contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

            # Create a new image with the same size and type as the original image
            new_image = image.copy()

            # Draw the contours on the new image with a thicker line
            cv2.drawContours(new_image, contours, -1, 255, expansion)

            # Get the output file path
            output_path = os.path.join(output_folder, filename)

            # Save the new image
            cv2.imwrite(output_path, new_image)

        # Show a message that the processing is done
        sg.popup("Processing done!")


window.close()
