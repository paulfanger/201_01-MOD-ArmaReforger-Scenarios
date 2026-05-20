# License

## Mission Content

All mission content in `missions/*/output/` is distributed under:

**Arma Public License — No Derivatives (APL-ND)**

Copyright © 2026 Paul Fanger / ELOS

This license applies to all produced mission content, including:
- `.gproj`, `.conf`, `.ent`, `.layer`, `.meta` files
- Any mission scenarios, briefings, or narrative content

### APL-ND Key Terms

- ✅ You MAY use this mission for personal or clan play
- ✅ You MAY distribute this mission unchanged
- ✅ You MAY upload to Arma Reforger Workshop (with Attribution)
- ❌ You MAY NOT modify and redistribute
- ❌ You MAY NOT embed Bohemia Interactive assets directly
- ❌ You MAY NOT use commercially

Full APL-ND text: https://www.bohemia.net/community/licenses/arma-public-license-nd

### Attribution Requirement

Mission files contain the following attribution fields (automatically generated):
- `m_sAuthor`: "ELOS AI-Native Mission Authoring System"
- `m_sDescription`: includes disclosure text

---

## Authoring Tools (this repository)

The ELOS AI-Native Mission Authoring System code (`backend/`, `.claude/`, tooling):

**MIT License**

Copyright © 2026 Paul Fanger / ELOS

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## Third-Party Content

The asset catalog (`catalog/`) contains metadata extracted from these open-source repositories:

- **Arma-Reforger-Samples** (BohemiaInteractive) — [APL-ND](https://www.bohemia.net/community/licenses/arma-public-license-nd)
- **Reforger-Sample-Coop** (exocs) — see repo license
- **CombatOpsEnhanced_AR** (Kexanone) — see repo license
- **GRAD-COOP-Template-Reforger** (gruppe-adler) — see repo license

Only metadata (GUIDs, paths, class names) is stored — no binary assets.

---

## AI Authoring Disclosure

This project uses Claude by Anthropic for mission content generation.
No Arma Reforger assets are used for AI training.
No live AI calls occur during gameplay.
See `playbook/EULA_COMPLIANCE.md` for full compliance documentation.
