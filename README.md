# Eleanor Toye Scott — personal website

Static HTML and CSS, compatible with GitHub Pages.

## Local preview

Run `docker compose up -d` and visit http://localhost:8080.
Run `docker compose down` to stop the preview. Files are mounted read-only; edits appear after refreshing.

Pages: home, councillor, music, writing (`blog/`, retaining existing URLs), and about & work.

Council contact information and updates should be reviewed before publishing. Existing essays and Substack links are preserved.

## RSS feed

The feed at `/blog/feed.xml` includes summaries of posts hosted on this website. External Substack and Green Party articles are not included. After adding or changing a local post card on the Writing page, run `python3 scripts/generate-feed.py` and commit the updated feed. Stable post URLs serve as feed identifiers. A GitHub check flags an out-of-date feed.
