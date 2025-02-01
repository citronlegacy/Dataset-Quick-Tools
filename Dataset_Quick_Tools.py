import os
import gradio as gr
import cv2
import shutil
from PIL import Image

def quick_file_renamer(directory, word):
    if not os.path.isdir(directory):
        return "Invalid directory. Please try again."
    
    sanitized_word = word.replace(" ", "_")
    files = sorted([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])
    
    for index, filename in enumerate(files, start=1):
        file_extension = os.path.splitext(filename)[1]
        new_filename = f"{sanitized_word}_{index:03d}{file_extension}"
        old_path = os.path.join(directory, filename)
        new_path = os.path.join(directory, new_filename)
        os.rename(old_path, new_path)
    
    return f"Renamed {len(files)} files in {directory}."

def add_white_background(image_path, output_folder):
    try:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        img = Image.open(image_path).convert("RGBA")
        white_bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
        final_img = Image.alpha_composite(white_bg, img).convert("RGB")
        
        output_path = os.path.join(output_folder, os.path.basename(image_path))
        final_img.save(output_path)
        return f"Processed: {output_path}"
    except Exception as e:
        return f"Error processing {image_path}: {str(e)}"

def process_images(input_folder, output_folder=None):
    if not os.path.exists(input_folder):
        return "Input folder does not exist."
    
    if not output_folder:
        output_folder = input_folder
    
    images = [f for f in os.listdir(input_folder) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    
    results = []
    for img in images:
        img_path = os.path.join(input_folder, img)
        results.append(add_white_background(img_path, output_folder))
    
    return "\n".join(results)

def calculate_edge_density(image_path):
    image = cv2.imread(image_path)
    if image is None:
        return 0  
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    return cv2.countNonZero(edges)

def move_blurry_images(input_dir, threshold):
    if not os.path.isdir(input_dir):
        return "Invalid directory. Please enter a valid path."
    
    blurry_dir = f"{input_dir}_blurry"
    os.makedirs(blurry_dir, exist_ok=True)
    
    log = []
    moved_files = []
    for filename in os.listdir(input_dir):
        file_path = os.path.join(input_dir, filename)
        
        if os.path.isfile(file_path) and filename.lower().endswith((".png", ".jpg", ".jpeg")):
            edge_density = calculate_edge_density(file_path)
            log.append(f"{filename}: {edge_density}")
            if edge_density < threshold:
                shutil.move(file_path, os.path.join(blurry_dir, filename))
                moved_files.append(filename)
    
    log_output = "\n".join(log)
    return f"Moved {len(moved_files)} blurry images to {blurry_dir}\n\nEdge Density Log:\n{log_output}" if moved_files else f"No blurry images found.\n\nEdge Density Log:\n{log_output}"

with gr.Blocks(title="🍋 Dataset Quick Tools") as app:
    gr.Markdown("## 🍋 Dataset Quick Tools")
    
    with gr.Row():
        dir_input = gr.Textbox(label="Directory Path")
        output_dir = gr.Textbox(label="Output Folder Path (Leave blank to use input folder)")
    
    word_input = gr.Textbox(label="New Filename")
    threshold_input = gr.Number(label="Edge Density Threshold", value=1000)
    
    with gr.Row():
        rename_button = gr.Button("Rename Files")
        process_button = gr.Button("Add White Backgrounds")
        move_blurry_button = gr.Button("Move Blurry Images")
    
    output_box = gr.Textbox(label="Output", lines=10)
    
    rename_button.click(quick_file_renamer, inputs=[dir_input, word_input], outputs=output_box)
    process_button.click(process_images, inputs=[dir_input, output_dir], outputs=output_box)
    move_blurry_button.click(move_blurry_images, inputs=[dir_input, threshold_input], outputs=output_box)

    #Footer
    gr.Markdown("""
    <div style="text-align: center;">
    🍋 Dataset Quick Tools 1.0 | <a href="https://github.com/citronlegacy/Dataset-Quick-Tools" target="_blank">GitHub</a> | <a href="https://civitai.com/user/CitronLegacy/models" target="_blank">Check out my CivitAI</a>
    </div>
    """)

app.launch()