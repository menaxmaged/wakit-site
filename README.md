# wakit-site

The website for [wakit](https://github.com/menaxmaged/wakit), a free tool to move WhatsApp chat history between chat exports, Android and iPhone.

It's a plain static site: `index.html`, the guide pages, `styles.css`, two screenshots and `vercel.json`. There's no build step on Vercel. The guide pages (`android-to-iphone.html` …) and `sitemap.xml` are generated from the text in `build_pages.py`: edit it, run `python3 build_pages.py`, and commit the results. To deploy it, import this repo in Vercel with the default settings.

```sh
open index.html          # preview locally
```
