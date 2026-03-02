#!/usr/bin/env python3
"""Two-column one-page resume PDF template engine.

Usage:
    from resume_template import generate_resume
    generate_resume(content_dict, output_path)

The content_dict should follow the structure defined in base_resume.py.
"""
from fpdf import FPDF


class ResumePDF(FPDF):
    def __init__(self):
        super().__init__('P', 'mm', 'A4')
        self.set_auto_page_break(auto=False)
        self.sb_w = 62
        self.sb_x = 7
        self.sb_cw = 50
        self.mc_x = 66
        self.mc_cw = 138
        self.y0 = 12

    def draw_bg(self):
        self.set_fill_color(235, 235, 235)
        self.rect(0, 0, self.sb_w, 297, 'F')

    def use_sb(self):
        self.set_left_margin(self.sb_x)
        self.set_right_margin(210 - self.sb_x - self.sb_cw)

    def use_mc(self):
        self.set_left_margin(self.mc_x)
        self.set_right_margin(210 - self.mc_x - self.mc_cw)

    def sb_section(self, title):
        y = self.get_y()
        self.set_xy(self.sb_x, y)
        self.set_font('Helvetica', 'B', 8.5)
        self.set_text_color(30, 30, 30)
        self.cell(self.sb_cw, 5, title)
        self.set_draw_color(160, 160, 160)
        self.line(self.sb_x, y + 5.5, self.sb_x + self.sb_cw, y + 5.5)
        self.set_draw_color(0, 0, 0)
        self.set_text_color(0, 0, 0)
        self.set_y(y + 7.5)

    def sb_text(self, text, bold=False, size=7.5, color=(50, 50, 50)):
        self.set_x(self.sb_x)
        self.set_font('Helvetica', 'B' if bold else '', size)
        self.set_text_color(*color)
        self.multi_cell(self.sb_cw, 3.8, text)
        self.set_text_color(0, 0, 0)

    def sb_link(self, text, url, size=7.5):
        self.set_x(self.sb_x)
        self.set_font('Helvetica', '', size)
        self.set_text_color(0, 0, 150)
        self.cell(self.sb_cw, 4, text, link=url)
        self.set_text_color(0, 0, 0)
        self.ln(4)

    def sb_plain(self, text, size=7):
        self.set_x(self.sb_x)
        self.set_font('Helvetica', '', size)
        self.set_text_color(50, 50, 50)
        self.multi_cell(self.sb_cw, 3.5, text)
        self.set_text_color(0, 0, 0)

    def sb_bullet(self, text, size=7):
        saved = self.l_margin
        indent = 4
        self.set_x(saved)
        self.set_font('Helvetica', '', size)
        self.set_text_color(50, 50, 50)
        self.cell(indent, 3.5, '- ')
        self.set_left_margin(saved + indent)
        self.multi_cell(self.sb_cw - indent, 3.5, text)
        self.set_left_margin(saved)
        self.set_text_color(0, 0, 0)

    def mc_section(self, title):
        y = self.get_y()
        self.set_x(self.mc_x)
        self.set_font('Helvetica', 'B', 10)
        self.set_fill_color(220, 220, 220)
        self.cell(self.mc_cw, 6, '  ' + title, fill=True)
        self.set_y(y + 7.5)

    def mc_text(self, text):
        self.set_x(self.mc_x)
        self.set_font('Helvetica', '', 8)
        self.multi_cell(self.mc_cw, 4, text)
        self.ln(1)

    def mc_role(self, company, role, dates, tagline=''):
        self.set_x(self.mc_x)
        self.set_font('Helvetica', 'B', 9)
        self.cell(self.mc_cw, 4.5, company)
        self.ln(4.5)
        self.set_x(self.mc_x)
        self.set_font('Helvetica', 'I', 8)
        self.cell(self.mc_cw, 4, f'{role}  |  {dates}')
        self.ln(4)
        if tagline:
            self.set_x(self.mc_x)
            self.set_font('Helvetica', 'I', 7.5)
            self.set_text_color(80, 80, 80)
            self.multi_cell(self.mc_cw, 3.5, tagline)
            self.set_text_color(0, 0, 0)
        self.ln(0.5)

    def mc_bullet(self, text):
        saved = self.l_margin
        indent = 5
        self.set_x(self.mc_x)
        self.set_font('Helvetica', '', 8)
        self.cell(indent, 4, ' -')
        self.set_left_margin(self.mc_x + indent)
        self.multi_cell(self.mc_cw - indent, 4, text)
        self.set_left_margin(saved)

    def mc_category(self, label):
        self.set_x(self.mc_x)
        self.set_font('Helvetica', 'B', 8)
        self.set_text_color(60, 60, 60)
        self.multi_cell(self.mc_cw, 4.5, label)
        self.set_text_color(0, 0, 0)


def generate_resume(content, output_path):
    """Generate a one-page two-column resume PDF from a content dict.

    Args:
        content: dict following the structure in base_resume.py
        output_path: where to save the PDF
    """
    pdf = ResumePDF()
    pdf.add_page()
    pdf.draw_bg()

    # ===== SIDEBAR =====
    pdf.use_sb()
    pdf.set_y(pdf.y0)

    # Name
    pdf.set_x(pdf.sb_x)
    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(pdf.sb_cw, 8, content['first_name'])
    pdf.ln(8)
    pdf.set_x(pdf.sb_x)
    pdf.cell(pdf.sb_cw, 8, content['last_name'])
    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)

    # Contact
    pdf.sb_section('CONTACT')
    pdf.sb_plain(content['phone'])
    pdf.ln(0.5)
    pdf.sb_link(content['email'], f"mailto:{content['email']}", size=7)
    pdf.sb_link('LinkedIn Profile', content['linkedin'], size=7)
    pdf.sb_plain(content['location'])
    pdf.ln(3)

    # Education
    pdf.sb_section('EDUCATION')
    for edu in content['education']:
        pdf.sb_text(edu['school'], bold=True, size=7.5)
        pdf.sb_plain(edu['years'])
        pdf.ln(1.5)
    pdf.ln(1.5)

    # AI Projects
    pdf.sb_section('AI PROJECTS')
    pdf.sb_link('github.com/gouravbaldewa2', content['github'], size=7)
    pdf.ln(0.5)
    for proj in content['projects']:
        pdf.sb_bullet(proj)
        pdf.ln(0.5)
    pdf.ln(2.5)

    # Skills & Domain
    pdf.sb_section('SKILLS & DOMAIN')
    pdf.sb_plain(content['skills'])
    pdf.ln(1.5)
    pdf.sb_text('Domain:', bold=True, size=7)
    pdf.sb_plain(content['domain'])
    pdf.ln(3)

    # Tools & Certifications
    pdf.sb_section('TOOLS & CERTIFICATIONS')
    pdf.sb_text('AI tools:', bold=True, size=7)
    pdf.sb_plain(content['ai_tools'])
    pdf.ln(1.5)
    pdf.sb_text('Certifications:', bold=True, size=7)
    for cert in content['certifications']:
        pdf.sb_plain(cert)

    # ===== MAIN COLUMN =====
    pdf.use_mc()
    pdf.set_y(pdf.y0)

    # Summary
    pdf.mc_section('PROFESSIONAL SUMMARY')
    pdf.mc_text(content['summary'])

    # Work Experience
    pdf.mc_section('WORK EXPERIENCE')
    for i, role in enumerate(content['roles']):
        pdf.mc_role(role['company'], role['title'], role['dates'], role.get('tagline', ''))
        for block in role['blocks']:
            if block['type'] == 'category':
                pdf.mc_category(block['text'])
            elif block['type'] == 'bullet':
                pdf.mc_bullet(block['text'])
        if i < len(content['roles']) - 1:
            pdf.ln(1.5)

    pdf.output(output_path)
    print(f'Resume saved to: {output_path}')


if __name__ == '__main__':
    from base_resume import BASE_CONTENT
    generate_resume(BASE_CONTENT, 'output/test_resume.pdf')
