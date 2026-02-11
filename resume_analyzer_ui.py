import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import pdfplumber
import requests
import threading

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"


class ResumeAnalyzerPro:
    def __init__(self, root):
        self.root = root
        self.root.title("Resume Analyzer & Job Matcher")
        self.root.geometry("1200x720")
        self.root.configure(bg="#0f172a")

        self.resume_text = ""
        self.build_ui()

    def build_ui(self):
        # ===== HEADER =====
        header = tk.Frame(self.root, bg="#020617", height=70)
        header.pack(fill=tk.X)

        title = tk.Label(
            header,
            text="Resume Analyzer & Job Matcher",
            bg="#020617",
            fg="white",
            font=("Segoe UI", 22, "bold")
        )
        title.pack(pady=15)

        # ===== MAIN =====
        main = tk.Frame(self.root, bg="#0f172a")
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # ===== LEFT CARD =====
        left = tk.Frame(main, bg="#020617", width=380)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        left.pack_propagate(False)

        self.card_title(left, "Input")

        self.upload_btn = tk.Button(
            left,
            text="📄 Upload Resume (PDF)",
            bg="#2563eb",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            command=self.upload_resume
        )
        self.upload_btn.pack(padx=15, pady=10, fill=tk.X)

        self.section_label(left, "Job Description")

        self.jd_box = scrolledtext.ScrolledText(
            left,
            height=18,
            bg="#020617",
            fg="white",
            insertbackground="white",
            wrap=tk.WORD,
            font=("Segoe UI", 10)
        )
        self.jd_box.pack(padx=15, pady=10, fill=tk.BOTH, expand=True)

        self.analyze_btn = tk.Button(
            left,
            text="🔍 Analyze Resume",
            bg="#16a34a",
            fg="white",
            font=("Segoe UI", 12, "bold"),
            relief="flat",
            command=self.start_analysis
        )
        self.analyze_btn.pack(padx=15, pady=15, fill=tk.X)

        # ===== RIGHT CARD =====
        right = tk.Frame(main, bg="#020617")
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.card_title(right, "Analysis Result")

        self.result_box = scrolledtext.ScrolledText(
            right,
            bg="#020617",
            fg="#e5e7eb",
            insertbackground="white",
            wrap=tk.WORD,
            font=("Consolas", 11)
        )
        self.result_box.pack(padx=15, pady=10, fill=tk.BOTH, expand=True)

    # ===== UI HELPERS =====
    def card_title(self, parent, text):
        lbl = tk.Label(
            parent,
            text=text,
            bg="#020617",
            fg="#38bdf8",
            font=("Segoe UI", 14, "bold")
        )
        lbl.pack(anchor="w", padx=15, pady=(15, 5))

        divider = tk.Frame(parent, bg="#1e293b", height=2)
        divider.pack(fill=tk.X, padx=15, pady=(0, 10))

    def section_label(self, parent, text):
        lbl = tk.Label(
            parent,
            text=text,
            bg="#020617",
            fg="#e5e7eb",
            font=("Segoe UI", 11, "bold")
        )
        lbl.pack(anchor="w", padx=15, pady=(10, 5))

    # ===== LOGIC =====
    def upload_resume(self):
        path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if not path:
            return

        try:
            text = ""
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"

            self.resume_text = text
            messagebox.showinfo("Success", "Resume uploaded successfully!")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def start_analysis(self):
        if not self.resume_text:
            messagebox.showwarning("Missing", "Please upload resume first")
            return

        jd = self.jd_box.get("1.0", tk.END).strip()
        if not jd:
            messagebox.showwarning("Missing", "Please paste job description")
            return

        self.result_box.delete("1.0", tk.END)
        self.result_box.insert(tk.END, "⏳ Running ATS analysis...\n\n")

        threading.Thread(
            target=self.run_analysis,
            args=(self.resume_text, jd),
            daemon=True
        ).start()

    def run_analysis(self, resume, jd):
        prompt = f"""
You are an ATS Resume Analyzer.

Tasks:
- Extract skills
- Compare with job description
- Calculate ATS score (0-100)
- Identify missing skills
- Suggest resume improvements

RESUME:
{resume}

JOB DESCRIPTION:
{jd}

Format clearly with headings.
"""

        try:
            response = requests.post(
                OLLAMA_URL,
                json={"model": MODEL, "prompt": prompt, "stream": False}
            )

            result = response.json()["response"]
            self.result_box.insert(tk.END, result)

        except Exception as e:
            self.result_box.insert(tk.END, f"Error: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ResumeAnalyzerPro(root)
    root.mainloop()
