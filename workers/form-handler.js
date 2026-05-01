/**
 * Cloudflare Worker — piumosso.pl form handler (contact + newsletter subscribe)
 *
 * Routes:
 *   POST /          — contact form → dispatches "inbound-lead" to piumosso-engine
 *   POST /subscribe — newsletter    → dispatches "newsletter-subscribe" to piumosso-engine
 *
 * Required Worker Secrets (Cloudflare dashboard → Workers → Settings → Variables):
 *   GH_PAT          — GitHub Personal Access Token (repo scope)
 *   ALLOWED_ORIGIN  — e.g. https://piumosso.pl
 */

const GH_OWNER = "Piotr-piumosso";
const GH_REPO  = "piumosso-engine";

export default {
  async fetch(request, env) {
    const origin  = request.headers.get("Origin") || "";
    const allowed = env.ALLOWED_ORIGIN || "https://piumosso.pl";

    const corsHeaders = {
      "Access-Control-Allow-Origin": allowed,
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    };

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders });
    }

    if (request.method !== "POST") {
      return new Response("Method Not Allowed", { status: 405, headers: corsHeaders });
    }

    let payload;
    try {
      payload = await request.json();
    } catch {
      return new Response(JSON.stringify({ ok: false, error: "Invalid JSON" }), {
        status: 400,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const url  = new URL(request.url);
    const path = url.pathname.replace(/\/+$/, "") || "/";

    // ── Newsletter subscribe ──────────────────────────────────────────────────
    if (path === "/subscribe") {
      const email = (payload.email || "").trim();
      if (!email || !email.includes("@")) {
        return new Response(JSON.stringify({ ok: false, error: "invalid_email" }), {
          status: 422,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }

      const dispatchRes = await fetch(
        `https://api.github.com/repos/${GH_OWNER}/${GH_REPO}/dispatches`,
        {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${env.GH_PAT}`,
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "piumosso-form-worker/1.0",
          },
          body: JSON.stringify({
            event_type: "newsletter-subscribe",
            client_payload: {
              email:          email,
              name:           (payload.name || "").trim(),
              lang:           (payload.lang || "pl").trim().slice(0, 2),
              subscribedAt:   new Date().toISOString(),
              source:         "website-form",
            },
          }),
        }
      );

      if (dispatchRes.status === 204) {
        return new Response(JSON.stringify({ ok: true }), {
          status: 200,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }

      const errText = await dispatchRes.text().catch(() => "unknown");
      console.error("Subscribe dispatch failed:", dispatchRes.status, errText);
      return new Response(JSON.stringify({ ok: false, error: "dispatch_failed" }), {
        status: 502,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // ── Contact form (default) ────────────────────────────────────────────────
    const name  = (payload.name  || "").trim();
    const phone = (payload.phone || "").trim();
    if (!name || !phone) {
      return new Response(JSON.stringify({ ok: false, error: "name and phone required" }), {
        status: 422,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const dispatchRes = await fetch(
      `https://api.github.com/repos/${GH_OWNER}/${GH_REPO}/dispatches`,
      {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${env.GH_PAT}`,
          "Accept": "application/vnd.github+json",
          "Content-Type": "application/json",
          "User-Agent": "piumosso-form-worker/1.0",
        },
        body: JSON.stringify({
          event_type: "inbound-lead",
          client_payload: {
            name:        name,
            phone:       phone,
            email:       (payload.email      || "").trim(),
            eventType:   (payload.eventType  || "").trim(),
            city:        (payload.city       || "").trim(),
            eventDate:   (payload.eventDate  || "").trim(),
            scope:       (payload.scope      || "").trim(),
            message:     (payload.message    || "").trim(),
            source:      "website-form",
            submittedAt: new Date().toISOString(),
          },
        }),
      }
    );

    if (dispatchRes.status === 204) {
      return new Response(JSON.stringify({ ok: true }), {
        status: 200,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const errText = await dispatchRes.text().catch(() => "unknown");
    console.error("GitHub dispatch failed:", dispatchRes.status, errText);
    return new Response(JSON.stringify({ ok: false, error: "dispatch_failed" }), {
      status: 502,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  },
};
