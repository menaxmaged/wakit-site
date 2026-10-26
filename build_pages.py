"""Writes the guide pages (*.html) and sitemap.xml from the content below. Run: python3 build_pages.py

The pages are plain static HTML (Vercel serves them as is); edit the text here and re-run.
"""
import html, json

SITE = "https://wakit-site.vercel.app"
REPO = "https://github.com/menaxmaged/wakit"
DL = f"{REPO}/releases/latest/download"

PAGES = [
    {
        "slug": "android-to-iphone",
        "title": "Move WhatsApp chats from Android to iPhone for free",
        "description": "Transfer WhatsApp history from an Android phone to an iPhone without a paid app and without "
                       "factory-resetting the iPhone. Free, open source, runs on your computer.",
        "h1": "Move WhatsApp from Android to iPhone, free",
        "lede": "WhatsApp's own route (Move to iOS) only works while you set up a new or freshly reset iPhone. wakit "
                "merges your Android history into the iPhone you already have, through an ordinary iPhone backup. "
                "There's no paid app and nothing leaves your computer.",
        "need": [
            "A computer (Mac, Windows or Linux) with <a href=\"/\">wakit</a>",
            "The Android phone, <b>rooted</b>. Or, experimentally, its end-to-end encrypted backup with the 64-digit key",
            "The iPhone, a cable, and <code>libimobiledevice</code> for making and restoring backups",
            "Free disk space for one full iPhone backup",
        ],
        "steps": [
            ("Copy WhatsApp off the Android phone",
             "wakit disables WhatsApp while it copies, so the database can't change halfway through.",
             "wakit device pull --out phone/\nwakit device pull-media --out phone-media/"),
            ("Make a fresh, full, unencrypted iPhone backup, then copy it",
             "Make the backup right before you start, because the restore at the end brings the iPhone back to it. "
             "Keep the original untouched: it's your undo.",
             "wakit ios-backup backup --out ~/Backups\ncp -cR ~/Backups/<device-id> ~/Backups/edit/"),
            ("Check both sides",
             "<code>doctor</code> confirms wakit knows both databases' layouts before anything is written.",
             "wakit doctor --path phone/msgstore.db\nwakit doctor --path ~/Backups/edit/<device-id>"),
            ("Merge Android into the iPhone backup",
             "Do a dry run first. Messages the iPhone already has are matched and skipped. Add <code>--apply</code> once the "
             "counts look right.",
             "wakit to-ios --db phone/msgstore.db --backup ~/Backups/edit/<device-id> --media phone-media/\n"
             "wakit to-ios --db phone/msgstore.db --backup ~/Backups/edit/<device-id> --media phone-media/ --apply"),
            ("Restore the edited backup",
             "Turn Find My off, set Auto-Lock to Never and keep the iPhone unlocked until it reboots. Then open "
             "WhatsApp, verify your number and skip any iCloud restore.",
             "wakit ios-backup restore --backup ~/Backups/edit/<device-id> --yes"),
        ],
        "warn": "A restore replaces everything on the iPhone with the backup's contents. Use a backup made just before, "
                "and never restore one cut down to WhatsApp only. wakit refuses those.",
        "carried": "Text, photos, videos, voice notes, stickers, documents, contact cards, locations, replies, stars, "
                   "and group senders. Reactions, polls and system notices don't carry over.",
        "faq": [
            ("Is this the same as Move to iOS?",
             "No. Move to iOS needs a new or erased iPhone and moves everything in one go. wakit adds the Android "
             "history to the iPhone's existing WhatsApp, keeping what's already there and skipping duplicates."),
            ("Do I need to jailbreak the iPhone?",
             "No. wakit edits a normal unencrypted backup made by Finder, iTunes, 3uTools or wakit itself, and "
             "restores it."),
            ("Will I lose anything on the iPhone?",
             "A restore brings the whole iPhone back to the moment of the backup. Anything added after that backup is "
             "lost, so make it right before. Keep the original backup as your undo."),
            ("What happens to WhatsApp on the Android phone?",
             "Once you verify your number on the iPhone, the Android phone is logged out. Its copy of the chats stays "
             "where it is."),
        ],
    },
    {
        "slug": "iphone-to-android",
        "title": "Move WhatsApp chats from iPhone to Android, merged with your chats",
        "description": "Bring WhatsApp history from an iPhone backup onto an Android phone, merged chat by chat with the "
                       "history already there. Free and open source.",
        "h1": "Move WhatsApp from iPhone to Android",
        "lede": "wakit reads an ordinary unencrypted iPhone backup and adds its WhatsApp chats to your Android phone. "
                "Chats are matched person by person, including WhatsApp's newer @lid ids, so each conversation ends "
                "up as one chat, with no duplicates.",
        "need": [
            "A computer with <a href=\"/\">wakit</a> and <code>adb</code>",
            "An unencrypted iPhone backup (Finder, iTunes, 3uTools, or <code>wakit ios-backup backup</code>)",
            "The Android phone, <b>rooted</b>. Without root, see <a href=\"/export-to-history\">the encrypted-backup route</a>",
        ],
        "steps": [
            ("Back up the iPhone (unencrypted)", "Turn backup encryption off first. wakit can't read encrypted backups.",
             "wakit ios-backup backup --out ~/Backups"),
            ("Copy WhatsApp off the Android phone", "WhatsApp is disabled while copying.",
             "wakit device pull --out phone/"),
            ("Dry run, then import",
             "Point <code>--backup</code> at the full backup folder. wakit extracts WhatsApp's files from it by itself. "
             "<code>--push</code> sends the photos and voice notes to the phone.",
             "wakit from-ios --db phone/msgstore.db --backup ~/Backups/<device-id>\n"
             "wakit from-ios --db phone/msgstore.db --backup ~/Backups/<device-id> --apply --push --phone-root /sdcard/WhatsApp"),
            ("Your stickers too (optional)", None,
             "wakit stickers-from-ios --db phone/stickers.db --backup ~/Backups/<device-id> --files-out Stickers --apply"),
            ("Put it back and start WhatsApp",
             "wakit copies the file's owner and SELinux label, which prevents \"something went wrong with chat history\".",
             "wakit device install --db phone/msgstore.db"),
        ],
        "warn": None,
        "carried": "Text, links, photos with captions, videos, GIFs, voice notes, stickers, documents, contact cards, "
                   "locations, deleted-message markers and group senders. Polls, reactions and calls don't carry over.",
        "faq": [
            ("Does the Android phone need root?",
             "For writing straight into WhatsApp's database, yes: it lives in a folder only root can reach. The "
             "experimental no-root route edits WhatsApp's end-to-end encrypted backup instead."),
            ("What if the Android phone already has some of the same chats?",
             "They're merged. Messages already there, matched by id or by sender, text and time, are skipped, so running "
             "it twice never duplicates anything."),
        ],
    },
    {
        "slug": "export-to-history",
        "title": "Turn a WhatsApp chat export back into chat history",
        "description": "Restore a WhatsApp \"Export chat\" .zip or _chat.txt as real messages, with photos and voice "
                       "notes, inside WhatsApp on Android. iPhone and Android export formats.",
        "h1": "Turn an exported chat back into WhatsApp history",
        "lede": "\"Export chat\" gives you a .zip with a <code>_chat.txt</code> and the media, but WhatsApp can't import it "
                "back. wakit can. It turns every line into a real message in the right chat, from the right person, at "
                "the right time, with photos, voice notes and captions attached.",
        "need": [
            "A computer with <a href=\"/\">wakit</a>",
            "The export: a .zip, a folder, or a bare <code>_chat.txt</code>, from an iPhone or an Android phone",
            "An Android phone, rooted. <b>No root?</b> Use its end-to-end encrypted backup and the 64-digit key (experimental, below)",
        ],
        "steps": [
            ("Copy WhatsApp off the phone", None, "wakit device pull --out phone/"),
            ("Dry run",
             "wakit reports how many messages it would add and how many are already in the chat. Exported from the "
             "other person's phone? Then the \"You …\" lines are theirs: pass <code>--me</code> with your name as it "
             "appears in the export.",
             "wakit import --db phone/msgstore.db --export \"WhatsApp Chat - Alex.zip\" --contact 15551234567"),
            ("Import", "A backup of the database is made first.",
             "wakit import --db phone/msgstore.db --export \"WhatsApp Chat - Alex.zip\" --contact 15551234567 \\\n"
             "    --apply --push --phone-root /sdcard/WhatsApp"),
            ("Put it back", None, "wakit device install --db phone/msgstore.db"),
        ],
        "noroot": ("No root: use the encrypted backup (experimental)",
                   "In WhatsApp, go to Settings → Chats → Chat backup → End-to-end encrypted backup → use a 64-digit "
                   "key, and back up. Copy <code>msgstore.db.crypt15</code> from <code>Android/media/com.whatsapp/"
                   "WhatsApp/Databases/</code>. Then:",
                   "wakit crypt decrypt --in msgstore.db.crypt15 --key \"<64-digit key>\" --out msgstore.db\n"
                   "wakit import --db msgstore.db --export \"WhatsApp Chat - Alex.zip\" --contact 15551234567 --apply\n"
                   "wakit crypt encrypt --in msgstore.db --like msgstore.db.crypt15 --key \"<64-digit key>\" "
                   "--out new/msgstore.db.crypt15",
                   "Copy the new file back into that folder, reinstall WhatsApp and tap Restore. Keep the original file. "
                   "Restoring an edited backup hasn't been confirmed on a phone yet."),
        "warn": None,
        "carried": "Text (including multi-line messages), photos, videos, voice notes, stickers, documents, contact "
                   "cards, captions and deleted-message markers. System notices (\"Messages are end-to-end encrypted\", "
                   "missed calls) are skipped, and so are attachments the export left out (\"Media omitted\").",
        "faq": [
            ("Will re-running it duplicate messages?",
             "No. Messages already in the chat are matched one to one by sender, text and time, so you can import "
             "several overlapping exports of the same chat."),
            ("Which export formats work?",
             "Both: iPhone (<code>[dd/mm/yyyy, h:mm:ss AM] Name: …</code>) and Android (<code>dd/mm/yyyy, hh:mm - "
             "Name: …</code>), in either date order. Group exports aren't supported yet."),
        ],
    },
    {
        "slug": "merge-databases",
        "title": "Merge two WhatsApp databases (msgstore.db) without duplicates",
        "description": "Copy the history of an old WhatsApp msgstore.db (old phone, WhatsApp mod, adb backup) into your "
                       "current one: messages, media, replies, reactions and calls, without duplicates.",
        "h1": "Merge an old WhatsApp database into your current one",
        "lede": "An old phone, a WhatsApp mod you switched away from, or an adb backup leaves you with a "
                "<code>msgstore.db</code> full of history your current WhatsApp doesn't have. wakit copies it across, "
                "chat by chat, and skips everything you already have.",
        "need": [
            "A computer with <a href=\"/\">wakit</a>",
            "The old <code>msgstore.db</code>. Encrypted <code>.crypt14</code> / <code>.crypt15</code>? Decrypt it with <code>wakit crypt</code>",
            "The current phone, rooted (to copy its database and put it back)",
        ],
        "steps": [
            ("Copy the current database", None, "wakit device pull --out phone/"),
            ("Check both", None, "wakit doctor --path old/msgstore.db\nwakit doctor --path phone/msgstore.db"),
            ("Dry run, then merge",
             "<code>--fuzzy</code> also skips messages that reached the current database another way (for example "
             "through an imported export) under a different id.",
             "wakit merge --old old/msgstore.db --new phone/msgstore.db --fuzzy\n"
             "wakit merge --old old/msgstore.db --new phone/msgstore.db --fuzzy --apply"),
            ("Favourite stickers (optional)", None,
             "wakit stickers --db phone/stickers.db --from old/stickers.db --from-files old/files/Stickers --files-out Stickers --apply"),
            ("Put it back", None, "wakit device install --db phone/msgstore.db"),
        ],
        "warn": None,
        "carried": "Messages, media references, replies and quotes, reactions, mentions, links, polls, calls and chat "
                   "settings. Media files themselves live in the phone's WhatsApp/Media folder, so copy that across too.",
        "faq": [
            ("The old database is from a WhatsApp mod (GB, 5Plus…). Does that work?",
             "Usually yes. Mods use WhatsApp's own database layout. Run <code>wakit doctor</code> on it first. If the "
             "layout differs, wakit refuses to write and tells you exactly which tables or columns are missing."),
            ("Why does sort order matter?",
             "WhatsApp gives each new message a sort position equal to its row id. Merged history has to fit under "
             "that, or new messages would appear in the middle of old chats. wakit renumbers everything in time "
             "order after each merge."),
        ],
    },
]


def esc(s):
    return html.escape(s, quote=True)


def code_block(text):
    return "<pre>" + "\n".join(f'<span class="p">$</span> {esc(l)}' if l and not l.startswith("    ") else esc(l)
                               for l in text.split("\n")) + "</pre>"


def page(p):
    steps = "\n".join(
        f"""      <li><h3>{esc(t)}</h3>{f"<p>{d}</p>" if d else ""}{code_block(c)}</li>""" for t, d, c in p["steps"])
    need = "\n".join(f"      <li>{n}</li>" for n in p["need"])
    faq = "\n".join(f"""      <details><summary>{esc(q)}</summary><p>{a}</p></details>""" for q, a in p["faq"])
    noroot = ""
    if p.get("noroot"):
        t, intro, c, after = p["noroot"]
        noroot = f"""
    <h2>{esc(t)}</h2>
    <p>{intro}</p>
    {code_block(c)}
    <p class="muted">{after}</p>"""
    warn = f'\n    <div class="warn">{esc(p["warn"])}</div>' if p.get("warn") else ""
    others = "\n".join(f'      <a class="card link" href="/{o["slug"]}"><b>{esc(o["h1"])}</b><span>{esc(o["description"][:110])}…</span></a>'
                       for o in PAGES if o is not p)
    faq_ld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": html.unescape(
            __import__("re").sub("<[^>]+>", "", a))}} for q, a in p["faq"]]}, ensure_ascii=False)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(p["title"])} — wakit</title>
<meta name="description" content="{esc(p["description"])}">
<link rel="canonical" href="{SITE}/{p["slug"]}">
<meta property="og:title" content="{esc(p["title"])}">
<meta property="og:description" content="{esc(p["description"])}">
<meta property="og:image" content="{SITE}/gui-guides.jpg">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='8' fill='%23128c5e'/><text x='16' y='22' font-size='18' text-anchor='middle' fill='white' font-family='Arial'>⇄</text></svg>">
<link rel="stylesheet" href="/styles.css">
<script type="application/ld+json">{faq_ld}</script>
</head>
<body>
<div class="nav">
  <div class="wrap">
    <a class="brand" href="/"><span class="logo" aria-hidden="true">⇄</span>wakit</a>
    <nav aria-label="Sections">
      <a href="/#workflows">Workflows</a>
      <a href="/#faq">FAQ</a>
      <button class="theme" id="theme" aria-label="Switch light or dark theme">◐</button>
      <a class="btn small primary keep" href="{REPO}">GitHub</a>
    </nav>
  </div>
</div>
<main class="guide-page">
  <article class="wrap narrow">
    <p class="crumbs"><a href="/">wakit</a> / Guides</p>
    <h1>{esc(p["h1"])}</h1>
    <p class="lede">{p["lede"]}</p>
    <div class="cta left">
      <a class="btn primary" href="{DL}/wakit-macos-arm64">Download for Mac</a>
      <a class="btn" href="{DL}/wakit-windows-x86_64.exe">Windows</a>
      <a class="btn" href="{DL}/wakit-linux-x86_64">Linux</a>
      <a class="btn" href="{REPO}#install-with-pip">pipx install wakit</a>
    </div>

    <h2>What you need</h2>
    <ul class="need">
{need}
    </ul>

    <h2>Steps</h2>
    <p class="muted">Prefer clicking? Run <code>wakit gui</code> (or double-click the app): the same steps are under
    <b>Guides</b>, with file pickers and Dry run / Apply buttons. Every command is a dry run until you add <code>--apply</code>.</p>
    <ol class="steps">
{steps}
    </ol>{warn}{noroot}

    <h2>What carries over</h2>
    <p>{p["carried"]}</p>

    <h2>Questions</h2>
    <div class="faq">
{faq}
    </div>

    <h2>Other guides</h2>
    <div class="grid two">
{others}
    </div>
  </article>
</main>
<footer>
  <div class="wrap">
    <span>wakit · MIT License · not affiliated with WhatsApp or Meta</span>
    <span><a href="{REPO}">GitHub</a> · <a href="{REPO}/blob/main/docs/how-it-works.md">How it works</a> · <a href="{REPO}/issues">Issues</a></span>
  </div>
</footer>
<script>
const root = document.documentElement;
try {{ const t = localStorage.getItem("wakit-theme"); if (t) root.dataset.theme = t; }} catch {{}}
document.getElementById("theme").addEventListener("click", () => {{
  const dark = matchMedia("(prefers-color-scheme: dark)").matches;
  const next = (root.dataset.theme || (dark ? "dark" : "light")) === "dark" ? "light" : "dark";
  root.dataset.theme = next;
  try {{ localStorage.setItem("wakit-theme", next); }} catch {{}}
}});
</script>
</body>
</html>
"""


if __name__ == "__main__":
    for p in PAGES:
        open(f"{p['slug']}.html", "w").write(page(p))
    urls = [""] + [p["slug"] for p in PAGES]
    open("sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n'
                                   '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                   + "".join(f"  <url><loc>{SITE}/{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    open("robots.txt", "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    print("wrote", ", ".join(p["slug"] + ".html" for p in PAGES), "+ sitemap.xml, robots.txt")
