/**
 * MediumArchive4furuhashilab — Track B backfill collector.
 *
 * Run this by hand in Chrome DevTools (not from GitHub Actions — Medium's
 * Cloudflare bot protection blocks non-browser clients; a real logged-in
 * browser session gets through). See SPEC.md section 2 and README.md for
 * background.
 *
 * USAGE
 * 1. Open https://medium.com/furuhashilab/all in Chrome.
 * 2. Open DevTools (Cmd+Option+J) > Console, paste this whole file, press Enter.
 *    A small counter overlay appears bottom-right.
 * 3. Scroll down the page yourself with the mouse/trackpad (this must be a
 *    real scroll gesture — Medium's infinite-scroll loader does not respond
 *    to scripted/programmatic scrolling). Keep scrolling until the counter
 *    stops increasing for ~15-20 seconds — that means you've reached the
 *    oldest post.
 * 4. In the console, run:  downloadPostList()
 *    This downloads furuhashilab_post_list.json (just id/title/date — fast).
 * 5. In the console, run:  await fetchAllContent()
 *    This fetches full content for every collected post (same-origin fetch,
 *    ~2-3 requests/sec, so a few hundred posts takes a few minutes) and
 *    downloads furuhashilab_full_content.json when done.
 * 6. Hand furuhashilab_full_content.json to the archive pipeline:
 *      python scripts/import_export.py /path/to/furuhashilab_full_content.json
 *      python scripts/build_index.py
 */
(function () {
  const STATE_KEY = "__mediumArchiveBackfill";
  if (!window[STATE_KEY]) {
    window[STATE_KEY] = { posts: new Map(), polling: null };
  }
  const state = window[STATE_KEY];

  function collectFromCache() {
    const client = window.__APOLLO_CLIENT__;
    if (!client) return state.posts.size;
    const cache = client.cache.extract();
    Object.keys(cache)
      .filter((k) => k.startsWith("Post:"))
      .forEach((k) => {
        const p = cache[k];
        const id = k.replace("Post:", "");
        if (p && p.uniqueSlug) {
          state.posts.set(id, {
            id,
            title: p.title,
            uniqueSlug: p.uniqueSlug,
            firstPublishedAt: p.firstPublishedAt,
          });
        }
      });
    return state.posts.size;
  }

  function showOverlay(text) {
    let el = document.getElementById("__archiveOverlay");
    if (!el) {
      el = document.createElement("div");
      el.id = "__archiveOverlay";
      el.style.cssText =
        "position:fixed;bottom:16px;right:16px;z-index:999999;background:#111;" +
        "color:#0f0;font:13px monospace;padding:10px 14px;border-radius:6px;" +
        "box-shadow:0 2px 8px rgba(0,0,0,.4);max-width:320px;white-space:pre-wrap";
      document.body.appendChild(el);
    }
    el.textContent = text;
  }

  if (state.polling) clearInterval(state.polling);
  state.polling = setInterval(() => {
    const n = collectFromCache();
    showOverlay(
      `Medium Archive: ${n} posts collected.\nKeep scrolling (real mouse/trackpad).\nWhen the count stops growing, run downloadPostList().`
    );
  }, 1000);
  collectFromCache();

  window.downloadPostList = function () {
    const posts = [...state.posts.values()];
    const blob = new Blob([JSON.stringify(posts, null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "furuhashilab_post_list.json";
    a.click();
    console.log(`Downloaded ${posts.length} posts. Next: await fetchAllContent()`);
    return posts.length;
  };

  window.fetchAllContent = async function () {
    clearInterval(state.polling);
    const posts = [...state.posts.values()];
    const results = [];
    let done = 0;

    for (const p of posts) {
      try {
        const url = `https://medium.com/furuhashilab/${encodeURIComponent(p.uniqueSlug)}`;
        const resp = await fetch(url, { credentials: "include" });
        const html = await resp.text();
        const m = html.match(/window\.__APOLLO_STATE__\s*=\s*(\{[\s\S]*?\});?\s*<\/script>/);
        if (m) {
          const pageState = JSON.parse(m[1]);
          const postKey = Object.keys(pageState).find((k) => k.startsWith(`Post:${p.id}`));
          const post = postKey ? pageState[postKey] : null;
          if (post) {
            const contentField = Object.keys(post).find((k) => k.startsWith("content("));
            const bodyModel = contentField && post[contentField] && post[contentField].bodyModel;
            const paraRefs = bodyModel ? bodyModel.paragraphs : [];
            const paragraphs = paraRefs.map((r) => pageState[r.__ref]).filter(Boolean);
            const creator = post.creator && pageState[post.creator.__ref];
            results.push({
              id: p.id,
              title: post.title,
              uniqueSlug: post.uniqueSlug,
              mediumUrl: post.mediumUrl,
              firstPublishedAt: post.firstPublishedAt,
              tags: post.tags || [],
              author: creator ? creator.name : null,
              paragraphs,
            });
          } else {
            console.warn("no Post entity found for", p.uniqueSlug);
          }
        } else {
          console.warn("no __APOLLO_STATE__ found for", p.uniqueSlug);
        }
      } catch (e) {
        console.error("failed", p.uniqueSlug, e);
      }
      done++;
      showOverlay(`Fetching content: ${done}/${posts.length}\n(${p.title || p.uniqueSlug})`);
      await new Promise((r) => setTimeout(r, 400));
    }

    const blob = new Blob([JSON.stringify(results)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "furuhashilab_full_content.json";
    a.click();
    showOverlay(`Done. Downloaded full content for ${results.length}/${posts.length} posts.`);
    console.log(`Downloaded full content for ${results.length} posts.`);
    return results.length;
  };

  showOverlay(
    `Medium Archive: ${state.posts.size} posts collected.\nKeep scrolling (real mouse/trackpad).\nWhen the count stops growing, run downloadPostList().`
  );
  console.log(
    "%cMedium Archive collector started. Scroll down with a real mouse/trackpad gesture " +
      "(scripted scrolling does not trigger Medium's loader). When the on-screen counter " +
      "stops growing, run downloadPostList(), then await fetchAllContent().",
    "color: green; font-weight: bold;"
  );
})();
