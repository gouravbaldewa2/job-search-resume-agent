#!/bin/bash
# Phase B: Generate tailored resumes + InMail drafts for selected jobs.
#
# Usage:
#   ./generate_selected.sh 1 3 5 7        # by S.No from today's Excel
#   ./generate_selected.sh 2 4 --date 2026-03-03  # for a specific date
#
# This triggers an Oz cloud agent that reads the Excel tracker,
# generates PDFs + InMail drafts only for the jobs you picked,
# and commits the results.

set -u

ENV_ID="ZTk9B9h0Lmmrsf3FynCflv"
OZ_CLI="${OZ_CLI:-/Applications/Warp.app/Contents/Resources/bin/oz}"

# Parse args
DATE=$(date +%Y-%m-%d)
JOBS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --date) DATE="$2"; shift 2 ;;
    *) JOBS+=("$1"); shift ;;
  esac
done

if [ ${#JOBS[@]} -eq 0 ]; then
  echo "Usage: ./generate_selected.sh <S.No> [S.No...] [--date YYYY-MM-DD]"
  echo ""
  echo "Example: ./generate_selected.sh 1 3 5"
  echo "  Generates resumes + InMail drafts for jobs #1, #3, #5 from today's tracker."
  exit 1
fi

JOBS_STR=$(IFS=", "; echo "${JOBS[*]}")
echo "Triggering Phase B for S.No: ${JOBS_STR} (date: ${DATE})"

"$OZ_CLI" agent run-cloud \
  --environment "$ENV_ID" \
  --prompt "You are a resume tailoring agent. Generate tailored resumes, PDFs, and InMail drafts for ONLY the jobs with S.No ${JOBS_STR} from the tracker at output/${DATE}/job_tracker_${DATE}.xlsx.

STEP 1: SETUP
Run: pip install -r requirements.txt

STEP 2: READ TRACKER
Read the Excel file output/${DATE}/job_tracker_${DATE}.xlsx using openpyxl. Extract the rows matching S.No values: ${JOBS_STR}. For each selected job, note the Organization, Job Title, Location Group, City, LinkedIn Job Link, and Key JD Keywords.

STEP 3: FETCH FULL JDs
For each selected job, fetch the full job description from LinkedIn using:
  curl -s \"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/JOB_ID\"
Extract the JOB_ID from the LinkedIn URL (last large number before the ? in the path).

STEP 4: TAILOR RESUMES
Read base_resume.py to get the BASE_CONTENT dict. For each selected job:
- Create a modified copy of BASE_CONTENT tailored to that specific JD
- Rewrite the summary to echo the JD language
- Adjust domain and skills fields to match JD keywords
- Reword category labels and bullet text to emphasise JD-relevant experience
- KEEP all metrics and numbers identical - only change framing
- Do NOT use em-dashes. Use regular dashes or commas.
- Ensure content fits on ONE page

STEP 5: GENERATE PDFs
Import from resume_template and base_resume. For each tailored resume, call generate_resume() and save to output/${DATE}/COMPANY_ROLE_${DATE}.pdf. For Remote India jobs, prefix with Remote_.

STEP 6: WRITE InMail DRAFTS
For each selected job, write a personalized cold outreach message:
- Format as SUBJECT: ... then BODY: ...
- Under 300 chars for subject, under 1000 chars for body
- Open with something specific about the company or role from the JD
- Connect 1-2 concrete metrics from the resume that match the JD
- End with a soft ask
- Tone: confident, specific, human, not templated
- Do NOT use phrases like \"I noticed your posting\" or \"I am writing to express my interest\"
- Do NOT use em-dashes
- Each InMail must be unique to that job

STEP 7: UPDATE EXCEL
Using openpyxl, open the existing Excel tracker. Add or update two columns: Resume PDF (filename) and InMail Draft (the full draft text). Only fill these for the selected rows. Set InMail Draft column width to 80 with text wrapping. Save the file.

STEP 8: COMMIT AND PUSH
Stage the new PDFs and updated Excel. Commit with message: \"Phase B: Generated resumes + InMails for jobs ${JOBS_STR} (${DATE})\n\nCo-Authored-By: Oz <oz-agent@warp.dev>\"
Push to main."

echo ""
echo "Phase B agent launched. Monitor progress in Warp or with:"
echo "  ${OZ_CLI} run list --output-format text"
