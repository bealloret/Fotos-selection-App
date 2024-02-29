import streamlit as st
from PIL import Image
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import requests
from bs4 import BeautifulSoup

def main():
    st.title("Image Evaluation App")
    
    # Define the URL of the GitHub repository containing the images
    github_repo_url = "https://github.com/bealloret/Fotos-selection-App/tree/main/images"

    # Fetch the image paths from the GitHub repository
    image_urls = load_images_from_github(github_repo_url)

    if image_urls:
        # Initialize session state attributes
        if "selected_images" not in st.session_state:
            st.session_state.selected_images = {}
        if "all_images" not in st.session_state:
            st.session_state.all_images = {os.path.basename(image_url): 0 for image_url in image_urls}

        # Display the page content
        st.sidebar.header("Navigation")
        page = st.sidebar.radio("Go to", ["Pictures", "Summary"])

        if page == "Pictures":
            show_pictures_page(image_urls)
        elif page == "Summary":
            show_summary_page()
            
def show_pictures_page(image_urls):
    selected_images = st.session_state.selected_images
    for i, image_url in enumerate(image_urls):
        image = fetch_image(image_url)
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
                selected_images[os.path.basename(image_url)] = rating
            elif selection == "No":
                selected_images[os.path.basename(image_url)] = -1  # Store -1 for "No"
            if st.button("Open/Close Original Size", key=f"button_{i}"):
                show_image = st.session_state.get(f"show_image_{i}", False)
                st.session_state[f"show_image_{i}"] = not show_image
                if not show_image:
                    st.image(image, caption=f"Image {i+1}")
                
def load_images_from_github(repo_url):
    response = requests.get(repo_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    image_urls = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and href.endswith(('.png', '.jpg', '.jpeg')):
            image_urls.append(href)
    return image_urls

def fetch_image(url):
    # Fetch the image from the URL
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    return image

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

