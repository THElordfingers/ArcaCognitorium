# Departamentum Documentalis — templates.py
# v1.0.0
"""Built-in document template skeletons."""


TEMPLATES = {
    'expositio': """\
---
title: {title} — Expositio
type: expositio
version: 1.0
author: {author}
theme: wizdoc
---

|h1|Identity|
|bullet|Name: {title}|
|bullet|Version: 1.0.0|
|bullet|Tagline: |
|bullet|Classification: |
|bullet|Status: |

|h1|Purpose|
|h2|Problem Statement|
|body|
|/body|

|h2|Motivation|
|body|
|/body|

|h2|Intended Outcome|
|body|
|/body|

|h2|Anti-Purpose|
|body|
|/body|

|h1|Audience|
|bullet|Primary: |
|bullet|Secondary: |
|bullet|Assumed Knowledge: |

|h1|Design Philosophy|
|bullet||
|bullet||
|bullet||

|h1|Technical Concept|
|h2|Mental Model|
|body|
|/body|

|h2|Core Abstractions|
|bullet||
|bullet||

|h2|Key Technical Decisions|
|bullet||
|bullet||

|h1|Functional Scope|
|h2|Core Capabilities|
|bullet||
|bullet||

|h2|Explicit Exclusions|
|bullet||

|h1|Constraints & Context|
|bullet||

|h1|Success Criteria|
|bullet|Functional: |
|bullet|Quality: |
|bullet|Failure: |

|h1|Glossary|
|bullet||
""",

    'dux_tome': """\
---
title: {title}
type: dux_tome
version: 1.0
author: {author}
theme: wizdoc
---

|h1|Keyboard & Shortcut Reference|

|table|
|th|Key / Shortcut|Action|
|tr|||
|/table|

|h1|Features|

|table|
|th|Feature|Description|How to Trigger|Status|
|tr|||||
|/table|

|h1|Vision & Purpose|
|body|
|/body|

|h1|File & Folder Map|
|code||
|/code|

|h1|Features & Functions|
|h2|Feature Name|
|body|
|/body|

|h1|Logic|
|body|
|/body|

|h1|Input / Output|
|bullet||
|bullet||
""",

    'build_doc': """\
---
title: {title} — Build Document
type: build_doc
version: 1.0
author: {author}
theme: wizdoc
---

|h1|Overview & Architecture|
|body|
|/body|

|h1|Tech Stack|
|table|
|th|Tool|Version|Justification|
|tr||||
|/table|

|h1|Directory Tree & Database Schema|
|code||
|/code|

|h1|Module Breakdown|
|table|
|th|Module|Stage|Responsibility|Inputs|Outputs|Dependencies|
|tr|||||||
|/table|

|h1|UI Wireframe|
|code||
|/code|

|h1|Data Flow|
|body|
|/body|

|h1|Code Stubs|
|code|python|
|/code|

|h1|Error Handling|
|table|
|th|Module|Error|Strategy|
|tr||||
|/table|

|h1|Setup & Testing|
|body|
|/body|

|h1|Packaging|
|body|
|/body|

|h1|Extensibility|
|body|
|/body|
""",

    'palette_card': """\
---
title: {title}
type: palette_card
version: 1.0
author: {author}
theme: wizdoc
---

|h1|Chromata|
|table|
|th|Token|Hex|Role|
|tr||||
|/table|

|h1|Compliance|
|bullet|WCAG AA: |
|bullet|WCAG AAA: |
|bullet|Minimum WCAG ratio: |
|bullet|Minimum APCA Lc: |
""",

    'blank': """\
---
title: {title}
type: blank
version: 1.0
author: {author}
theme: wizdoc
---

""",
}


def get_template(template_type: str, title: str = 'Untitled',
                 author: str = '') -> str:
    """Return a .bureau template string with placeholders filled."""
    tmpl = TEMPLATES.get(template_type, TEMPLATES['blank'])
    return tmpl.format(title=title, author=author)


def list_templates() -> list[str]:
    """Return available template type names."""
    return list(TEMPLATES.keys())
