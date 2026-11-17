from pypdf import PdfReader

reader = PdfReader("reports/Machine Learning.pdf")
print("Total pages:", len(reader.pages))

full_text = ""
for i, page in enumerate(reader.pages):
    text = page.extract_text()
    print(f"\n--- PAGE {i+1} ---")
    print(text[:500])
    full_text += f"\n\n=== PAGE {i+1} ===\n" + text

with open("reports/task_brief.txt", "w", encoding="utf-8") as f:
    f.write(full_text)
print("\nWrote full text to reports/task_brief.txt")

