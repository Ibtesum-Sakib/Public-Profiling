import streamlit as st
from bs4 import BeautifulSoup as bs
import requests
from googlesearch import search
from fpdf import FPDF
import tempfile

# Function to perform Google search and retrieve links
def perform_google_search(keyword, num_results=10):
    links = []
    for url in search(keyword, num_results=num_results):
        links.append(url)
    return links

# Function to fetch content and an image URL from a page
def fetch_content_and_image(url, keyword):
    page = requests.get(url)
    soup = bs(page.content, 'html.parser')
    paragraphs = [tag.text for tag in soup.select('p')]
    content = "\n".join(paragraphs)
    
    # Try to find an image of the person
    image = None
    img_tags = soup.find_all('img')
    
    # Search for image with keyword in alt text
    for img in img_tags:
        alt_text = img.get('alt', '').lower()
        if keyword.lower() in alt_text:
            image = img.get('src')
            break
    
    # If no specific image is found, take the second image
    if not image and len(img_tags) > 2:
        image = img_tags[2].get('src')
    
    # Adjust the image URL if necessary
    if image:
        if image.startswith('//'):
            image = 'https:' + image
        elif not image.startswith('http'):
            image = requests.compat.urljoin(url, image)
    
    return content, image

# Function to save content to a text file
def save_content_to_txt(content):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode='w', encoding='utf-8') as tmp_file:
        tmp_file.write(content)
        return tmp_file.name

# Function to save content to a PDF file
def save_content_to_pdf(content, image_url=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Add the image if available
    if image_url:
        try:
            pdf.image(image_url, x=10, y=8, w=100)
            pdf.ln(85)  # Move below the image
        except Exception as e:
            st.write(f"Could not load image: {e}")

    pdf.multi_cell(0, 10, content.encode('latin-1', 'replace').decode('latin-1'))  # Handling encoding issues for PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        pdf.output(tmp_file.name)
        return tmp_file.name

# Streamlit app
def main():
    st.title("Public Profiling")

    # Input search keyword
    keyword = st.text_input("Enter a name of a person:")

    if st.button("Search"):
        if keyword:
            # Perform Google search
            links = perform_google_search(keyword)
            if not links:
                st.write("No links found.")
                return

            # Loop through the links and fetch content and images
            contents = []
            images = []
            for link in links[:3]:  # Fetching content from the first three links
                content, image = fetch_content_and_image(link, keyword)
                contents.append(content)
                images.append(image)

            # Combine contents for display and saving
            combined_content = "\n\n".join([f"Link {idx+1}:\n{link}\n\n{content}" for idx, (link, content) in enumerate(zip(links, contents))])
            st.write(combined_content)
            
            # Display the first person image if available
            if images[0]:
                st.image(images[0], caption='Image of the person from the first link')

            # Save content to a text file and provide download link
            txt_file_path = save_content_to_txt(combined_content)
            with open(txt_file_path, "rb") as file:
                st.download_button(
                    label="Download as TXT",
                    data=file,
                    file_name="content.txt",
                    mime="text/plain"
                )

            # Save content to a PDF file and provide download link
            pdf_file_path = save_content_to_pdf(combined_content, images[0] if images[0] else None)
            with open(pdf_file_path, "rb") as file:
                st.download_button(
                    label="Download as PDF",
                    data=file,
                    file_name="content.pdf",
                    mime="application/pdf"
                )

        else:
            st.write("Please enter a search keyword.")

if __name__ == "__main__":
    main()
