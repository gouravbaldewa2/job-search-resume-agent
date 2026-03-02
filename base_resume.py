"""Base resume content for Gourav Baldewa.

The Oz agent reads this, modifies fields to match each JD, and passes
the result to resume_template.generate_resume().

CUSTOMISATION GUIDE (for the agent):
- summary: Rewrite to match JD keywords (e.g. marketplace, consumer experience, fintech, etc.)
- skills / domain: Swap in terms from the JD (e.g. design thinking, lean product, reengagement)
- roles[*].tagline: Adjust to highlight JD-relevant context
- roles[*].blocks: Reword category labels and bullets to echo JD language
  Keep all metrics/numbers identical - only change framing and emphasis.
- Do NOT invent new achievements or metrics. Only reframe existing ones.
- Do NOT use em-dashes. Use regular dashes or commas.
- Use sentence case for headings. Avoid capitalising every word.
- Keep the total content to fit on ONE page (A4). About 12-14 bullets total in
  the main column, 6-7 lines of summary, 3 AI project bullets in sidebar.
"""

BASE_CONTENT = {
    'first_name': 'Gourav',
    'last_name': 'Baldewa',
    'phone': '+91-7042500365',
    'email': 'gouravbaldewa1@gmail.com',
    'linkedin': 'https://www.linkedin.com/in/gouravbaldewa',
    'location': 'Mumbai, India',
    'github': 'https://github.com/gouravbaldewa2',

    'education': [
        {'school': 'MBA - MDI, Gurgaon', 'years': '2014 - 2016'},
        {'school': 'B.Tech - CET, Bhubaneswar', 'years': '2008 - 2012'},
    ],

    'projects': [
        'AI Dev Tools Tracker: Next.js/TypeScript app that scrapes AI tool updates '
        'via autonomous Oz cloud agent on 24-hour cron',
        'Orbit: real-time location sharing app built with Antigravity, Stitch, '
        'Flutter SDK, and Android Studio',
        'RBI Data Automation: Python pipeline for RBI NEFT data across 233 banks, '
        '177K+ branches',
    ],

    'skills': (
        'A/B testing, design thinking, lean product, agile/scrum, SQL, behavioural '
        'analytics, funnel optimisation, road-mapping, stakeholder management'
    ),
    'domain': (
        'Fintech, digital banking, consumer products, marketplace, '
        'customer segmentation, experimentation, regulated environments'
    ),
    'ai_tools': 'Cursor (AI IDE), Claude Code, Warp Oz (terminal agent), Ollama, Perplexity',
    'certifications': [
        'Advanced tech & AI program',
        'Product sense & strategy',
        'Advanced product growth',
    ],

    'summary': (
        'Senior product leader with 9+ years building high-traffic, consumer-facing digital '
        'products across marketplace, fintech, and mobility platforms. I have led end-to-end '
        'product lifecycles spanning research, discovery, design, and continuous optimisation '
        'for products serving 10Mn+ users across India, Europe (Amsterdam-based at Freenow), '
        'and Latin America. I am comfortable influencing senior stakeholders without direct '
        'authority, championing experimentation culture across engineering and design, and '
        'mentoring product managers to raise the bar on product practices.'
    ),

    'roles': [
        {
            'company': 'Mahindra Finance',
            'title': 'Group Product Manager (Vice President)',
            'dates': 'July 2023 - Present',
            'tagline': "India's top digital NBFC | 20Mn+ customers | Promoted to VP on accelerated track",
            'blocks': [
                {'type': 'category', 'text': 'Consumer experience in a high-traffic environment'},
                {'type': 'bullet', 'text': (
                    'Built the entire FD platform from scratch as a consumer product, turning complex '
                    'regulatory onboarding (KYC, AML) into a simple digital experience that drove instant '
                    'customer acquisition and created a Rs 350 Crs business line within 6 months'
                )},
                {'type': 'bullet', 'text': (
                    'Set up a multi-channel distribution strategy with API-driven partner integrations, '
                    'working with brokers and branch networks across Tier-1 and Tier-2 markets'
                )},
                {'type': 'category', 'text': 'Data-driven experimentation & growth'},
                {'type': 'bullet', 'text': (
                    'Developed targeted customer segmentation using behavioural data and ran systematic '
                    'funnel experiments, improving FDs per user by 57%, renewal rate by 42%, and lifting '
                    'conversion from 3.4% to 6.3%'
                )},
                {'type': 'bullet', 'text': (
                    'Grew product organisation from 1 to 5 PMs, putting in place discovery frameworks '
                    'and agile rituals that improved cross-functional collaboration and delivered 37% YoY growth'
                )},
            ],
        },
        {
            'company': 'Freenow (Lyft Group)',
            'title': 'Lead Product Manager - Pricing',
            'dates': 'July 2022 - Feb 2023',
            'tagline': 'Two-sided marketplace | Amsterdam-based | 5Mn+ rides daily | Multi-country European & LatAm markets',
            'blocks': [
                {'type': 'bullet', 'text': (
                    'Owned the pricing domain end-to-end across multiple countries, building real-time fare '
                    'adjustment algorithms that balanced marketplace supply (driver compensation) with demand '
                    '(rider price sensitivity)'
                )},
                {'type': 'bullet', 'text': (
                    'Found that 10-17% of rides were underpriced through data discovery across ride history '
                    'and behavioural signals, unlocking EUR 50K in monthly revenue and improving driver '
                    'retention by 12%'
                )},
                {'type': 'bullet', 'text': (
                    'Generated EUR 1.2Mn in revenue through pricing experiments and A/B testing frameworks, '
                    'championing an experimentation mindset across product and engineering teams'
                )},
            ],
        },
        {
            'company': 'Walmart',
            'title': 'Platform Product Manager',
            'dates': 'Feb 2021 - July 2022',
            'tagline': 'Consumer marketplace | Catalogue discoverability across 250Mn+ SKUs',
            'blocks': [
                {'type': 'bullet', 'text': (
                    'Built ML-powered deduplication engine using similarity algorithms to improve product '
                    'discovery for consumers, improving conversion of treatment items by 2.5X'
                )},
                {'type': 'bullet', 'text': (
                    'Designed automated content verification platform for 290+ users, cutting allocation '
                    'time from 10 hours to 5 minutes through data-driven workflow automation'
                )},
                {'type': 'bullet', 'text': (
                    'Defined API contracts and data pipelines for catalogue enrichment, letting '
                    'cross-functional product teams consume structured product data at scale'
                )},
            ],
        },
        {
            'company': 'Bounce',
            'title': 'Consumer Product Manager',
            'dates': 'Oct 2019 - Dec 2020',
            'tagline': 'Consumer marketplace for young urban commuters',
            'blocks': [
                {'type': 'bullet', 'text': (
                    'Built a commuter-matching carpooling platform using preference-based algorithms, '
                    'personalising the consumer experience to improve rider-driver pairing and retention'
                )},
                {'type': 'bullet', 'text': (
                    'Spotted the COVID-driven demand shift early and independently defined a new product '
                    'vertical, launching a long-term rental product that captured the 7-90 day market '
                    'and contributed 32% of revenue'
                )},
            ],
        },
        {
            'company': 'McKinsey & Company',
            'title': 'Senior Product Consultant - Digital Practice',
            'dates': 'April 2016 - Oct 2019',
            'tagline': '5+ enterprise clients across India, Singapore, Thailand & Indonesia',
            'blocks': [
                {'type': 'bullet', 'text': (
                    'Defined digital product strategies for banking, telecom, and insurance clients across '
                    '4 countries, navigating complex stakeholder environments and aligning diverse teams '
                    'around shared consumer outcomes'
                )},
                {'type': 'bullet', 'text': (
                    'Designed a conversational UX for telecom utility payments reducing support friction '
                    'from 4 min to under 1 min, achieving 23% digital adoption by making the experience '
                    'intuitive for everyday users'
                )},
                {'type': 'bullet', 'text': (
                    'Built A/B testing methodology and funnel optimisation framework driving 40% '
                    'install-to-registration improvement and 16% sales growth across client digital products'
                )},
            ],
        },
    ],
}
