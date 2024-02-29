import streamlit as st
from PIL import Image
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import requests
from io import BytesIO

def main():
    # Define the raw GitHub URL of the folder containing the images
    github_raw_url = "https://github.com/bealloret/Fotos-selection-App/tree/main/images/"
    
    # Replace 'your_access_token' with your actual GitHub access token
    access_token = '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'

    image_names = load_image_names_from_github(github_raw_url, access_token)

    if image_names:
        # Initialize session state attributes
        if "selected_images" not in st.session_state:
            st.session_state.selected_images = {}
        if "all_images" not in st.session_state:
            st.session_state.all_images = {image_name: 0 for image_name in image_names}

        # Display the page content
        st.sidebar.header("Navigation")
        page = st.sidebar.radio("Go to", ["Pictures", "Summary"])

        if page == "Pictures":
            show_pictures_page(image_names, github_raw_url)
        elif page == "Summary":
            show_summary_page()

def load_image_names_from_github(github_raw_url, access_token):
    headers = {"Authorization": f"token {access_token}"}
    response = requests.get(github_raw_url, headers=headers)
    if response.status_code == 200:
        # Extract image names from the response
        image_names = [filename for filename in response.text.splitlines() if filename.endswith(('.png', '.jpg', '.jpeg'))]
        return image_names
    else:
        st.error("Failed to fetch image names from GitHub.")
        return []

def show_pictures_page(image_names, github_raw_url):
    selected_images = st.session_state.selected_images
    for i, image_name in enumerate(image_names):
        image_url = github_raw_url + image_name
        response = requests.get(image_url)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
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
                    selected_images[image_name] = rating
                elif selection == "No":
                    selected_images[image_name] = -1  # Store -1 for "No"
            if st.button("Open/Close Original Size", key=f"button_{i}"):
                show_image = st.session_state.get(f"show_image_{i}", False)
                st.session_state[f"show_image_{i}"] = not show_image
                if not show_image:
                    st.image(image, caption=f"Image {i+1}")
        else:
            st.error(f"Failed to fetch image {image_name} from GitHub.")


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

