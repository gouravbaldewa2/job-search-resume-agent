# Job Search Resume Agent

An Oz cloud agent that runs every 24 hours to:

1. Search LinkedIn for PM job postings (Lead / Staff / Principal / Group Product Manager)
2. Filter to jobs posted in the last 24 hours in **Bangalore**, **Dubai/UAE**, and **Netherlands**
3. Fetch each job description
4. Tailor Gourav Baldewa's resume to match each JD
5. Generate a one-page two-column PDF resume per job
6. Commit all generated PDFs to the `output/` directory

## Repo structure

- `resume_template.py` - Two-column PDF layout engine (ResumePDF class + `generate_resume()`)
- `base_resume.py` - Default resume content as a Python dict, with customisation guide
- `requirements.txt` - Python dependencies (fpdf2, beautifulsoup4, requests)
- `output/` - Generated PDFs (committed by the agent)

## Manual usage

```bash
pip install -r requirements.txt
python resume_template.py  # generates output/test_resume.pdf from base content
```
