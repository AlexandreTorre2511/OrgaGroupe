"""Génère index.html à partir de dossier.md."""
import re
import unicodedata
from pathlib import Path

import markdown

ROOT = Path(__file__).parent
src = (ROOT / "dossier.md").read_text(encoding="utf-8")

# Ligne d'auteur exportée depuis Claude Docs remplacée par une signature lisible
src = re.sub(r"^Oct 30, 2026 · @Alex\s*$", "", src, count=1, flags=re.M)
title_match = re.match(r"# (.+)\n", src)
title = title_match.group(1).strip()
src = src[title_match.end():]

body = markdown.markdown(src, extensions=["tables", "sane_lists", "toc"], extension_configs={"toc": {"slugify": lambda v, s: re.sub(r"[^a-z0-9]+", "-", unicodedata.normalize("NFKD", v.lower()).encode("ascii", "ignore").decode()).strip("-")}})

# Cases à cocher
body = re.sub(r"<li>\[ \] ", '<li class="task"><input type="checkbox" aria-label="Fait"> ', body)

# Tableaux défilants sur mobile
body = body.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")

# Pastilles d'étape dans le tableau de suivi
for step, cls in [("À contacter", "todo"), ("Contacté", "done1"), ("RDV calé", "rdv"), ("Devis envoyé", "devis"), ("Signé", "signed"), ("Perdu", "lost")]:
    body = body.replace(f"<td>{step}</td>", f'<td><span class="pill {cls}">{step}</span></td>')

# Sommaire à partir des titres de niveau 2
toc = re.findall(r'<h2 id="([^"]+)">(.+?)</h2>', body)
toc_html = "\n".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in toc)

template = (ROOT / "template.html").read_text(encoding="utf-8")
html = template.replace("{{TITLE}}", title).replace("{{TOC}}", toc_html).replace("{{BODY}}", body)
(ROOT / "index.html").write_text(html, encoding="utf-8")
print("index.html généré", len(html), "octets")
