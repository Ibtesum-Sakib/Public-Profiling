import streamlit as st
from bs4 import BeautifulSoup as bs
import requests
from googlesearch import search
import os
from fpdf import FPDF

# Function to perform Google search and retrieve text content
def google_search_and_display_content(keyword):
    # Perform the search and store the links
    links = []
    for url in search(keyword, num_results=10):
        links.append(url)

    # Fetch content from the first three links
    contents = []
    for link in links[:3]:
        page = requests.get(link)
        soup = bs(page.content, 'html.parser')
        paragraphs = [tag.text for tag in soup.select('p')]
        content = "\n".join(paragraphs)
        contents.append(content)

    return contents

# Function to save content to a text file
def save_content_to_txt(content, filename):
    with open(filename, "w", encoding="utf-8") as file:
        for idx, text in enumerate(content, start=1):
            file.write(f"===== Link {idx} =====\n")
            file.write(text)
            file.write("\n\n")

# Function to save content to a PDF file
def save_content_to_pdf(content, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for idx, text in enumerate(content, start=1):
        pdf.multi_cell(0, 10, f"===== Link {idx} =====\n{text}")
    pdf.output(filename)

# Streamlit app
def main():
    st.title("Public Profiling")
    st.write("Enter a name to search and display content.")

    # Input search query
    search_query = st.text_input("Enter a name:", "")

    # Select save format
    save_format = st.radio("Select format to save:", ("Text", "PDF"))

    # Perform search and display content
    if st.button("Search"):
        if search_query:
            results = google_search_and_display_content(search_query)
            for idx, result in enumerate(results, start=1):
                st.write(f"===== Link {idx} =====")
                st.write(result)

            # Save content to a file
            desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
            if save_format == "Text":
                filename = os.path.join(desktop_path, f"{search_query}_content.txt")
                save_content_to_txt(results, filename)
                st.write(f"Content saved to: {filename}")
            else:
                filename = os.path.join(desktop_path, f"{search_query}_content.pdf")
                save_content_to_pdf(results, filename)
                st.write(f"Content saved to: {filename}")
        else:
            st.write("Please enter a name to search.")

if __name__ == "__main__":
    main()
