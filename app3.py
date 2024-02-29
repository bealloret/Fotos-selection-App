import streamlit as st
from PIL import Image
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def main():
    st.title("Image Evaluation App")
    
     #Define the folder path containing the predefined set of pictures
    image_folder_path = "C:/Users/beall/ColabDocs/FotosApp/images"

    image_paths = load_images_from_folder(image_folder_path)
    image_names = [os.path.basename(image_path) for image_path in image_paths]

    if image_paths:
        # Initialize session state attributes
        if "selected_images" not in st.session_state:
            st.session_state.selected_images = {}
        if "all_images" not in st.session_state:
            st.session_state.all_images = {image_name: 0 for image_name in image_names}

        # Display the page content
        st.sidebar.header("Navigation")
        page = st.sidebar.radio("Go to", ["Pictures", "Summary"])

        if page == "Pictures":
            show_pictures_page(image_paths)
        elif page == "Summary":
            show_summary_page()
            
def show_pictures_page(images):
    selected_images = st.session_state.selected_images
    for i, image_path in enumerate(images):
        image = Image.open(image_path)
        st.write(f"### Image {i+1}")
            # Display image and ask user to select
        col1, col2 = st.columns([3, 1])
        with col1:
            small_image = image.resize((200, 250))
            st.image(small_image, caption=f"Image {i+1}")
        with col2:
            st.write("Do you like this picture?")
            selection = st.radio("", ("Unsure", "Yes", "No"), key=f"radio_{i}")
            if selection == "Yes":
                rating = st.slider("Evaluation (1 to 5)", 1, 5, key=f"slider_{i}")
                selected_images[os.path.basename(image_path)] = rating
            elif selection == "No":
                selected_images[os.path.basename(image_path)] = -1  # Store -1 for "No"
            if st.button("Open/Close Original Size", key=f"button_{i}"):
                show_image = st.session_state.get(f"show_image_{i}", False)
                st.session_state[f"show_image_{i}"] = not show_image
                if not show_image:
                    st.image(image, caption=f"Image {i+1}")
                
def load_images_from_folder(folder_path):
    image_paths = []
    if os.path.isdir(folder_path):
        for filename in os.listdir(folder_path):
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join(folder_path, filename)
                image_paths.append(image_path)
    return image_paths

def show_summary_page():
    st.title("Summary")

    # Fetch the selected images and ratings
    selected_images = st.session_state.selected_images
    all_images = st.session_state.all_images
    
    # Create lists to store the names and ratings of all selected images
    image_names = list(all_images.keys())
    ratings = [selected_images.get(image_name, 0) for image_name in image_names]
    # Update ratings list to replace "No" ratings with -1
    ratings = [-1 if rating == "No" else rating for rating in ratings]
            
    # Create a DataFrame for all selected images
    df = pd.DataFrame({
        "Image": image_names,
        "Rating": ratings
    })
    
    
    # Create a bar chart for ratings
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = plt.cm.Pastel1(np.linspace(0, 1, len(image_names)))
    bars = ax.bar(image_names, ratings, color=colors, width=0.5)
    
    ax.set_xlabel("Image")
    ax.set_ylabel("Rating")
    ax.set_title("Image Ratings Summary")
    
    ax.set_ylim(-1, 5)  # Adjust y-axis limits to include ratings from -1 to 5
    ax.tick_params(axis='x', rotation=45, labelsize=8)  # Rotate x-axis labels and adjust font size
        
    for bar in bars:
        height = bar.get_height()
        ax.annotate('{}'.format(height),
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=8)
        
    st.pyplot(fig)

    # Display the table
    st.write("### Image Ratings Summary")
    st.table(df)

if __name__ == "__main__":
    main()
