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

# Function to fetch content from a URL
def fetch_content(url):
    page = requests.get(url)
    soup = bs(page.content, 'html.parser')
    paragraphs = [tag.text for tag in soup.select('p')]
    content = "\n".join(paragraphs)
    return content

# Function to save content to a text file
def save_content_to_txt(content):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp_file:
        tmp_file.write(content.encode('utf-8'))
        return tmp_file.name

# Function to save content to a PDF file
def save_content_to_pdf(content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, content)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        pdf.output(tmp_file.name)
        return tmp_file.name

# Streamlit app
def main():
    st.title("Web Content Search and Save")

    # Input search keyword
    keyword = st.text_input("Enter a search keyword:")

    if st.button("Search"):
        if keyword:
            # Perform Google search
            links = perform_google_search(keyword)
            if not links:
                st.write("No links found.")
                return

            # Loop through the links and fetch content
            contents = []
            for link in links[:3]:  # Fetching content from the first three links
                content = fetch_content(link)
                contents.append(content)

            # Combine contents for display and saving
            combined_content = "\n\n".join([f"Link {idx+1}:\n{link}\n\n{content}" for idx, (link, content) in enumerate(zip(links, contents))])
            st.write(combined_content)

            # Save content to a text file and provide download link
            txt_file_path = save_content_to_txt(combined_content)
            with open(txt_file_path, "rb") as file:
                btn = st.download_button(
                    label="Download as TXT",
                    data=file,
                    file_name="content.txt",
                    mime="text/plain"
                )

            # Save content to a PDF file and provide download link
            pdf_file_path = save_content_to_pdf(combined_content)
            with open(pdf_file_path, "rb") as file:
                btn = st.download_button(
                    label="Download as PDF",
                    data=file,
                    file_name="content.pdf",
                    mime="application/pdf"
                )

        else:
            st.write("Please enter a search keyword.")

if __name__ == "__main__":
    main()

