"""معیارهای انتخاب خبر روزانه و پرامپت‌ها. برای تغییر حوزه‌ها یا سخت‌گیری فقط همین فایل را ویرایش کنید."""
import re


# ── معیارهای انتخاب خبر روزانه (به انگلیسی؛ هم به جست‌وجوگر داده می‌شود و هم به Gemini) ──
# برای تغییر حوزه‌ها یا سخت‌گیری، فقط همین متن را ویرایش کنید. حواستان باشد آکولاد { } در آن نباشد.
SUGGEST_CRITERIA_EN = (
    "DOMAINS (spread the picks across DIFFERENT domains; at most 2 per domain):\n"
    "1) biology, biotech and medicine (gene editing, new drugs and therapies, brain-computer interfaces, "
    "longevity, lab-grown food)\n"
    "2) machines of every kind (robots, vehicles, aircraft, ships, drones, industrial and construction machines)\n"
    "3) artificial intelligence (new models and capabilities, safety incidents, regulation)\n"
    "4) space (missions, telescopes, discoveries, launch and satellite technology)\n"
    "5) weapons and defense technology (new systems, drones, hypersonics, AI in warfare)\n"
    "6) software, internet and cybersecurity (major platforms, big breaches and vulnerabilities, open source, privacy)\n"
    "7) energy, batteries and materials (fusion, nuclear, solar, superconductors, battery breakthroughs)\n"
    "8) chips and computing (semiconductors, quantum computing, new hardware)\n"
    "RANK stories by the combination of:\n"
    "- FRESH: published inside the window, ideally within the last 3 days; newer is better.\n"
    "- VIRAL: widely covered or heavily discussed (front pages, trending on social media, Hacker News, Reddit).\n"
    "- BIG IMPACT: affects the lives, jobs, health, safety or money of many people.\n"
    "- CONTROVERSIAL: a real public debate, so credible sources exist on both the supporting and the opposing side.\n"
    "RULES:\n"
    "- Stay inside the 8 domains above. Skip anything that is not science or technology news (politics, banking "
    "or finance outages, social issues, lifestyle), even if it is very popular.\n"
    "- One story = one item. If several articles cover the same event, merge them into ONE item; never list the "
    "same event twice under different headlines.\n"
    "- At most ONE item per company or person.\n"
    "- Skip routine or incremental news: minor product updates and point releases, small funding rounds, "
    "unsourced rumors, earnings reports, routine launches or test flights, listicles, opinion pieces, sponsored posts.\n"
    "- Elon Musk's companies (SpaceX, Tesla, xAI, X, Neuralink, Starlink) only if the story is a genuine "
    "world-level headline, never routine news, and at most ONE such item overall.\n"
)

SUGGEST_FORMAT_EN = (
    "OUTPUT: write the result in PERSIAN. One item per line, best item first, exactly in this format with the "
    "separator | and no other text:\n"
    "Persian short headline | Persian summary of 1-2 sentences (what happened and why it matters) | "
    "publication date YYYY-MM-DD | source name | domain (Persian, one or two words) | "
    "story key (3-4 lowercase English words, identical for the same story) | "
    "what is disputed and by whom (Persian, one short sentence; write - if nothing is disputed)\n"
)

SUGGEST_PROMPT = (
    "You are the research assistant of a Persian-language technology YouTube channel. Use web search to find up "
    "to {n} technology news items PUBLISHED between {start} and {end} (both inclusive). Use only reputable news "
    "sources and never invent links or facts.\n" + SUGGEST_CRITERIA_EN + SUGGEST_FORMAT_EN + "{avoid}"
)

GROQ_SUGGEST_PROMPT = (
    "Use web search (English and Persian sources) to find up to {n} technology news items PUBLISHED between "
    "{start} and {end} inclusive, ranked best first.\n" + SUGGEST_CRITERIA_EN +
    "OUTPUT: one item per line, best first, in English, exactly in this format with the separator | and no other "
    "text:\n"
    "headline | 1-2 sentence summary (what happened and why it matters) | publication date YYYY-MM-DD taken from the "
    "source | source name | domain | story key (3-4 lowercase words, identical for the same story) | what is "
    "disputed and by whom (one short sentence; write - if nothing is disputed)\n"
    "Include only items whose publication date you can confirm. Do not invent anything.\n{avoid}"
)

SUGGEST_FROM_SOURCES = (
    "Below are materials collected from the web by a search engine. Pick up to {n} items published between "
    "{start} and {end} (both inclusive) that best fit these criteria. Use only what is in the materials; add "
    "nothing of your own; skip any item whose publication date is not in the materials.\n"
    + SUGGEST_CRITERIA_EN + SUGGEST_FORMAT_EN + "{avoid}\n"
)

SUGGEST_FROM_CANDIDATES = (
    "Below is a numbered list of CANDIDATE technology news items that were automatically collected from reputable "
    "sources. Each line shows: [id], (domain tag), headline, sources, publication date, optional Hacker News score, "
    "the number of independent sources that covered it, and a short snippet. All were published between {start} and "
    "{end}.\nPick up to {n} items that best fit the criteria below. Choose ONLY from this list and refer to items by "
    "their id. Use the signals as evidence: many independent sources and a high Hacker News score indicate VIRAL; a "
    "high comment count relative to points indicates CONTROVERSIAL. Write each summary using ONLY the headline and "
    "snippet given; never add facts that are not in them.\n"
    + SUGGEST_CRITERIA_EN +
    "OUTPUT: write in PERSIAN. One item per line, best first, exactly in this format with the separator | and no "
    "other text:\n"
    "id (number only) | Persian short headline | Persian summary of 1-2 sentences (what happened and why it matters) | "
    "domain (Persian, one or two words) | story key (3-4 lowercase English words, identical for the same story) | "
    "what is disputed and by whom (Persian, one short sentence; write - if nothing is disputed)\n"
    "{avoid}\nCANDIDATES:\n"
)

SUGGEST_PICK_EN = (
    "Below is a numbered list of CANDIDATE technology news items automatically collected from reputable sources. "
    "Each line shows: [id], (domain tag), headline, sources, publication date, optional Hacker News score, the number "
    "of independent sources that covered it, and a short snippet. All were published between {start} and {end}.\n"
    "Pick up to {n} items that best fit the criteria below. Choose ONLY from this list and refer to items by id. "
    "Many independent sources and a high Hacker News score indicate VIRAL; a high comment count relative to points "
    "indicates CONTROVERSIAL. Use ONLY the headline and snippet; never add facts.\n"
    + SUGGEST_CRITERIA_EN +
    "OUTPUT: in English. One item per line, best first, exactly in this format with the separator | and no other "
    "text:\n"
    "id (number only) | clear short English headline | English summary of 1-2 sentences (what happened and why it "
    "matters) | story key (3-4 lowercase words, identical for the same story) | what is disputed and by whom (one "
    "short sentence; write - if nothing is disputed)\n"
    "{avoid}\nCANDIDATES:\n"
)

MUSK_RE = re.compile(r"spacex|starship|starlink|tesla|\bxai\b|neuralink|boring company|elon|musk|optimus", re.I)


