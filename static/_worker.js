/**
 * Cloudflare Pages Worker: HTTP content negotiation for text/markdown
 *
 * Background
 * ----------
 * HTTP content negotiation (RFC 7231) lets a client declare what response
 * format it prefers via the Accept request header. AI agents and developer
 * tools such as Claude Code, Cursor, and OpenCode send "Accept: text/markdown"
 * when fetching documentation so they receive clean, structured markdown
 * instead of a full HTML page with navigation, sidebars, and scripts.
 *
 * How it works
 * ------------
 * Hugo pre-builds a .md file alongside every HTML page. For example:
 *   /docs/envoy/main/about/overview/index.html  (HTML page)
 *   /docs/envoy/main/about/overview.md  (markdown twin)
 *
 * This Worker intercepts every request before it reaches the static assets.
 * When the Accept header includes "text/markdown" and the URL looks like a
 * page (no file extension), the Worker tries to serve the markdown twin:
 *
 *   1. Strip the trailing slash and append .md
 *      /docs/foo/bar/  →  /docs/foo/bar.md   (regular doc pages)
 *
 *   2. If that file doesn't exist, try index.md inside the directory
 *      /docs/foo/      →  /docs/foo/index.md  (section landing pages)
 *
 *   3. If neither exists, fall through to the normal static asset response.
 *
 * URLs with file extensions (JS, CSS, images, etc.) are always passed through
 * unchanged so this Worker does not affect any non-page assets.
 *
 * The response includes:
 *   Content-Type: text/markdown; charset=utf-8
 *   Vary: Accept  — tells CDN caches to store HTML and markdown separately
 *
 * Origin
 * ------
 * Copied from agentgateway.dev (agentgateway-oss-website/static/_worker.js),
 * which has served markdown this way in production. Its _redirects rules kept
 * working after the Worker was added, so the same holds here. Keep the copies
 * in sync if one changes.
 *
 * Testing
 * -------
 * This Worker only runs in Cloudflare Pages, not in the local Hugo dev server.
 * There is no supported local emulator; the only way to test is to deploy to a
 * Cloudflare Pages preview or production environment and then run:
 *   curl -H "Accept: text/markdown" https://kgateway.dev/docs/envoy/main/about/overview/
 * or re-run the afdocs scorecard against the live site after deploying.
 */

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const accept = request.headers.get('Accept') || '';
    const path = url.pathname;

    // Only intercept page-like URLs (no file extension) when markdown is preferred
    const hasExtension = /\.[a-zA-Z0-9]{1,5}$/.test(path);
    const wantsMarkdown = accept.includes('text/markdown');

    if (wantsMarkdown && !hasExtension) {
      const base = path.replace(/\/$/, '');

      // Pages: /docs/foo/bar/ → /docs/foo/bar.md
      if (base) {
        const mdUrl = new URL(url);
        mdUrl.pathname = base + '.md';
        const mdResp = await env.ASSETS.fetch(new Request(mdUrl.href));
        if (mdResp.ok) {
          return new Response(mdResp.body, {
            status: 200,
            headers: {
              'Content-Type': 'text/markdown; charset=utf-8',
              'Cache-Control': 'public, max-age=3600',
              'Vary': 'Accept',
            },
          });
        }
      }

      // Sections: /docs/foo/ → /docs/foo/index.md
      const idxUrl = new URL(url);
      idxUrl.pathname = (base || '') + '/index.md';
      const idxResp = await env.ASSETS.fetch(new Request(idxUrl.href));
      if (idxResp.ok) {
        return new Response(idxResp.body, {
          status: 200,
          headers: {
            'Content-Type': 'text/markdown; charset=utf-8',
            'Cache-Control': 'public, max-age=3600',
            'Vary': 'Accept',
          },
        });
      }
    }

    return env.ASSETS.fetch(request);
  },
};
