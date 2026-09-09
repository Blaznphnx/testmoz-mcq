import streamlit as st
import pandas as pd
import io
import re

# --- Page Configuration ---
st.set_page_config(page_title="MCQ to Testmoz", layout="centered")

# --- UI Header ---
st.title("MCQ to Testmoz - Excel Generator")
st.write("Extract your questions, paste the clean text here, and instantly generate your Testmoz upload file.")

# --- Instructions & Formatting ---
st.markdown("""
### 1. Format your MCQs
Make sure every Question & Answer block is separated by a **blank line**. Use `Answer:` for the correct option and `Explanation:` for the reasoning.

**Example Format:**
```text
Which membrane covers the human lungs?
A. Pericardium
B. Periosteum
C. Pleura
D. Perichondrium
Answer: C
Explanation: The pleura is the protective membrane that surrounds the lungs.
""")

# --- Input Area ---
st.markdown("### 2. Paste your cleaned MCQs")
mcq_text = st.text_area("Review your MCQs here:", height=350, label_visibility="collapsed")

# --- Processing & Output ---
if st.button("Generate Testmoz Excel"):
    if not mcq_text.strip():
        st.warning("Please paste some questions first.")
    else:
        # Split the text by double spaces (blank lines) to isolate each question block
        blocks = mcq_text.strip().split('\n\n')
        testmoz_rows = []
        
        for block in blocks:
            lines = [line.strip() for line in block.split('\n') if line.strip()]
            if not lines:
                continue
            
            question = lines[0]
            options = []
            correct_indices = []
            explanation = ""
            
            # Parse the lines under the question
            for line in lines[1:]:
                if line.lower().startswith("answer:"):
                    # Extract the correct letter(s)
                    ans_letter = line.split(":", 1)[1].strip().upper()
                    # Map A->0, B->1, C->2, D->3
                    for char in ans_letter:
                        if 'A' <= char <= 'Z':
                            idx = ord(char) - ord('A')
                            correct_indices.append(idx)
                            
                elif line.lower().startswith("explanation:"):
                    # Extract the explanation text
                    explanation = line.split(":", 1)[1].strip()
                    
                else:
                    # Treat the line as an option. 
                    # This regex safely removes prefixes like "A. ", "b) ", etc.
                    opt_text = re.sub(r'^[A-Za-z][\.\)]\s*', '', line)
                    options.append(opt_text)
            
            # Construct the Testmoz Row Format
            points = 1  # Default to 1 point
            modifiers = ""
            testmoz_rows.append([question, points, modifiers, explanation])
            
            for idx, opt in enumerate(options):
                is_correct = "*" if idx in correct_indices else ""
                testmoz_rows.append([is_correct, opt, "", ""])
                
            # Add a blank row to separate this question from the next in the Excel file
            testmoz_rows.append(["", "", "", ""]) 
            
        # Create a Pandas DataFrame
        df = pd.DataFrame(testmoz_rows)
        
        # Convert DataFrame to an Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, header=False)
        output.seek(0)
        
        # --- Download Button ---
        st.success("Testmoz file generated successfully! Ready for download.")
        st.download_button(
            label="Download testmoz_output.xlsx",
            data=output,
            file_name="testmoz_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )