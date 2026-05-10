// ReaperX frontend - submits the module form and renders the JSON response.
(() => {
  setupSidebar();
  setupDashboardFilter();
  setupModuleForm();

  // ---- Sidebar -----------------------------------------------------------
  function setupSidebar() {
    const toggle = document.getElementById("sidebar-toggle");
    if (toggle) {
      toggle.addEventListener("click", () => {
        document.body.classList.toggle("sidebar-open");
      });
    }
    const filter = document.getElementById("module-filter");
    if (!filter) return;
    filter.addEventListener("input", () => {
      const q = filter.value.trim().toLowerCase();
      document.querySelectorAll(".nav-group").forEach((g) => {
        let visible = 0;
        g.querySelectorAll(".module-link").forEach((l) => {
          const name = (l.dataset.moduleName || "").toLowerCase();
          const ok = !q || name.includes(q);
          l.classList.toggle("match-hidden", !ok);
          if (ok) visible++;
        });
        g.classList.toggle("match-hidden", visible === 0);
      });
    });
  }

  // ---- Dashboard filter --------------------------------------------------
  function setupDashboardFilter() {
    const search = document.getElementById("dashboard-filter");
    const empty = document.getElementById("dashboard-empty");
    if (!search) return;
    let activeChip = "all";

    document.querySelectorAll(".chip").forEach((chip) => {
      chip.addEventListener("click", () => {
        document.querySelectorAll(".chip").forEach((c) => c.classList.remove("active"));
        chip.classList.add("active");
        activeChip = chip.dataset.filter;
        applyFilter();
      });
    });
    search.addEventListener("input", applyFilter);

    function applyFilter() {
      const q = search.value.trim().toLowerCase();
      let totalVisible = 0;
      document.querySelectorAll(".module-section").forEach((sec) => {
        const cat = sec.dataset.category;
        const catOk = activeChip === "all" || activeChip === cat;
        let secVisible = 0;
        sec.querySelectorAll(".card").forEach((card) => {
          const name = (card.dataset.cardName || "").toLowerCase();
          const blurb = (card.dataset.cardBlurb || "").toLowerCase();
          const queryOk = !q || name.includes(q) || blurb.includes(q);
          const ok = catOk && queryOk;
          card.classList.toggle("match-hidden", !ok);
          if (ok) secVisible++;
        });
        sec.classList.toggle("match-hidden", secVisible === 0);
        totalVisible += secVisible;
      });
      if (empty) empty.classList.toggle("hidden", totalVisible !== 0);
    }
  }

  // ---- Module form -------------------------------------------------------
  function setupModuleForm() {
    const form = document.getElementById("module-form");
    if (!form) return;

    const result = document.getElementById("module-result");
    const badge = document.getElementById("status-badge");
    const elapsed = document.getElementById("result-elapsed");
    const skel = document.getElementById("result-skeleton");
    const pretty = document.getElementById("result-pretty");
    const raw = document.getElementById("result-raw");
    const copyBtn = document.getElementById("copy-json");
    const dlBtn = document.getElementById("download-json");
    const csvBtn = document.getElementById("download-csv");
    const rawBtn = document.getElementById("toggle-raw");

    let lastJson = null;

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const endpoint = form.dataset.endpoint;
      const fd = new FormData(form);
      const submitBtn = form.querySelector("button[type=submit]");
      submitBtn.disabled = true;
      submitBtn.dataset.label = submitBtn.dataset.label || submitBtn.querySelector(".btn-label").textContent;
      submitBtn.querySelector(".btn-label").innerHTML = '<span class="spinner"></span> Running…';
      setBadge("busy", "running");
      result.classList.remove("hidden");
      pretty.innerHTML = "";
      raw.textContent = "";
      raw.classList.add("hidden");
      rawBtn.textContent = "Show raw";
      skel.classList.remove("hidden");
      elapsed.textContent = "";

      const t0 = performance.now();
      try {
        const resp = await fetch(endpoint, { method: "POST", body: fd });
        const data = await resp.json();
        lastJson = data;
        raw.textContent = JSON.stringify(data, null, 2);
        if (data.error) {
          setBadge("err", "error");
        } else {
          setBadge("ok", "done");
        }
        skel.classList.add("hidden");
        pretty.appendChild(renderResult(data, window.REAPERX_MODULE_KEY));
      } catch (err) {
        setBadge("err", "error");
        skel.classList.add("hidden");
        pretty.textContent = `Request failed: ${err}`;
      } finally {
        const dt = ((performance.now() - t0) / 1000).toFixed(2);
        elapsed.textContent = `${dt}s`;
        submitBtn.disabled = false;
        submitBtn.querySelector(".btn-label").textContent = submitBtn.dataset.label;
      }
    });

    copyBtn?.addEventListener("click", async () => {
      if (!lastJson) return;
      await navigator.clipboard.writeText(JSON.stringify(lastJson, null, 2));
      flash(copyBtn, "Copied!");
    });
    dlBtn?.addEventListener("click", () => {
      if (!lastJson) return;
      downloadBlob(JSON.stringify(lastJson, null, 2), "application/json", "json");
    });
    csvBtn?.addEventListener("click", () => {
      if (!lastJson) return;
      downloadBlob(toCsv(lastJson), "text/csv", "csv");
    });
    rawBtn?.addEventListener("click", () => {
      const isHidden = raw.classList.toggle("hidden");
      rawBtn.textContent = isHidden ? "Show raw" : "Hide raw";
    });

    function setBadge(cls, text) {
      badge.className = "status-badge " + cls;
      badge.textContent = text;
    }
    function flash(btn, text) {
      const orig = btn.textContent;
      btn.textContent = text;
      setTimeout(() => (btn.textContent = orig), 1100);
    }
    function downloadBlob(content, type, ext) {
      const blob = new Blob([content], { type });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `reaperx-${window.REAPERX_MODULE_KEY}-${Date.now()}.${ext}`;
      a.click();
      URL.revokeObjectURL(url);
    }
  }

  // ---- CSV export --------------------------------------------------------
  function toCsv(obj) {
    const rows = [];
    walk("", obj, rows);
    const escape = (v) => {
      if (v === null || v === undefined) return "";
      const s = typeof v === "object" ? JSON.stringify(v) : String(v);
      return '"' + s.replace(/"/g, '""') + '"';
    };
    return ["key,value", ...rows.map(([k, v]) => `${escape(k)},${escape(v)}`)].join("\n");

    function walk(prefix, value, acc) {
      if (value === null || typeof value !== "object") {
        acc.push([prefix || "value", value]);
        return;
      }
      if (Array.isArray(value)) {
        if (value.length === 0) {
          acc.push([prefix, "[]"]);
          return;
        }
        value.forEach((v, i) => walk(`${prefix}[${i}]`, v, acc));
        return;
      }
      const entries = Object.entries(value);
      if (!entries.length) {
        acc.push([prefix, "{}"]);
        return;
      }
      entries.forEach(([k, v]) => walk(prefix ? `${prefix}.${k}` : k, v, acc));
    }
  }

  // ---- Rendering ---------------------------------------------------------
  // Booleans whose `false` is the GOOD outcome (e.g. is_expired=false).
  const NEGATIVE_BOOL_KEYS = new Set([
    "is_expired",
    "is_random",
    "is_disposable",
    "is_role",
    "compromised",
  ]);

  function renderResult(data, key) {
    const wrap = document.createElement("div");
    if (data.error && !data.found) {
      wrap.appendChild(kv("Error", data.error, "bool-bad"));
      return wrap;
    }
    const renderer = renderers[key] || renderGeneric;
    renderer(wrap, data);
    return wrap;
  }

  function kv(k, v, klass = "") {
    const row = document.createElement("div");
    row.className = "kv";
    const ke = document.createElement("div");
    ke.className = "k";
    ke.textContent = k;
    const ve = document.createElement("div");
    ve.className = "v " + klass;
    if (Array.isArray(v)) {
      ve.classList.add("list");
      if (!v.length) {
        ve.textContent = "—";
        ve.style.color = "var(--muted)";
      } else {
        v.forEach((x) => {
          const span = document.createElement("span");
          span.textContent = typeof x === "object" ? JSON.stringify(x) : String(x);
          ve.appendChild(span);
        });
      }
    } else if (typeof v === "boolean") {
      ve.textContent = String(v);
      const isNegative = NEGATIVE_BOOL_KEYS.has(k);
      if (isNegative) {
        ve.classList.add(v ? "bool-bad" : "bool-good");
      } else {
        ve.classList.add(v ? "bool-true" : "bool-false");
      }
    } else if (v === null || v === undefined || v === "") {
      ve.textContent = "—";
      ve.style.color = "var(--muted)";
    } else if (typeof v === "object") {
      ve.textContent = JSON.stringify(v, null, 2);
    } else {
      ve.textContent = String(v);
    }
    row.append(ke, ve);
    return row;
  }

  function sectionTitle(text) {
    const h = document.createElement("h4");
    h.className = "section-title";
    h.textContent = text;
    return h;
  }

  function listCard(opts) {
    const wrap = document.createElement("div");
    wrap.className = "list-card";
    if (opts.title) {
      const t = document.createElement("div");
      t.className = "list-card-title";
      if (opts.titleHref) {
        const a = document.createElement("a");
        a.href = opts.titleHref;
        a.target = "_blank";
        a.rel = "noopener";
        a.textContent = opts.title;
        t.appendChild(a);
      } else {
        t.textContent = opts.title;
      }
      wrap.appendChild(t);
    }
    if (opts.meta?.length) {
      const m = document.createElement("div");
      m.className = "list-card-meta";
      opts.meta.forEach((piece) => {
        if (piece === null || piece === undefined || piece === "") return;
        const s = document.createElement("span");
        s.textContent = String(piece);
        m.appendChild(s);
      });
      wrap.appendChild(m);
    }
    if (opts.body) {
      const b = document.createElement("div");
      b.className = "list-card-body";
      b.textContent = opts.body;
      wrap.appendChild(b);
    }
    return wrap;
  }

  function renderGeneric(wrap, data) {
    Object.entries(data).forEach(([k, v]) => wrap.appendChild(kv(k, v)));
  }

  const renderers = {
    username(wrap, data) {
      wrap.appendChild(kv("Query", data.query));
      wrap.appendChild(kv("Hits", `${data.found} / ${data.total_sites}`));
      wrap.appendChild(sectionTitle("Found"));
      const hits = document.createElement("div");
      data.hits.forEach((h) => {
        const a = document.createElement("a");
        a.className = "tag present";
        a.target = "_blank";
        a.rel = "noopener";
        a.href = h.url;
        a.textContent = h.site;
        hits.appendChild(a);
      });
      if (!data.hits.length) hits.innerHTML = '<span class="muted">No hits.</span>';
      wrap.appendChild(hits);

      wrap.appendChild(sectionTitle("All checks"));
      const all = document.createElement("div");
      data.checks.forEach((c) => {
        const a = document.createElement("a");
        a.className =
          "tag " +
          (c.status === "present" ? "present" : c.status === "absent" ? "absent" : "unknown");
        a.target = "_blank";
        a.rel = "noopener";
        a.href = c.url;
        a.textContent = `${c.site} · ${c.status}`;
        all.appendChild(a);
      });
      wrap.appendChild(all);
    },

    github_user(wrap, data) {
      const p = data.profile || {};
      wrap.appendChild(kv("User", p.login));
      if (p.avatar_url) {
        const img = document.createElement("img");
        img.src = p.avatar_url;
        img.alt = "GitHub avatar";
        img.className = "gravatar-img";
        wrap.appendChild(img);
      }
      ["name", "bio", "company", "location", "blog", "twitter_username", "email", "hireable"].forEach((k) => {
        if (k in p) wrap.appendChild(kv(k, p[k]));
      });
      wrap.appendChild(sectionTitle("Stats"));
      ["public_repos", "public_gists", "followers", "following", "created_at", "updated_at"].forEach((k) => {
        if (k in p) wrap.appendChild(kv(k, p[k]));
      });
      const repos = data.top_repos || [];
      if (repos.length) {
        wrap.appendChild(sectionTitle(`Top repositories (${repos.length})`));
        repos.forEach((r) => {
          wrap.appendChild(
            listCard({
              title: r.name,
              titleHref: r.html_url,
              meta: [
                r.language && `lang: ${r.language}`,
                `★ ${r.stars}`,
                `⑂ ${r.forks}`,
                r.is_fork ? "fork" : null,
              ],
              body: r.description,
            })
          );
        });
      }
    },

    reddit_user(wrap, data) {
      const a = data.about || {};
      wrap.appendChild(kv("User", a.name));
      if (data.profile_url) {
        const link = document.createElement("a");
        link.className = "tag present";
        link.target = "_blank";
        link.rel = "noopener";
        link.href = data.profile_url;
        link.textContent = "Open profile";
        wrap.appendChild(link);
      }
      ["public_description", "subreddit"].forEach((k) => {
        if (k in a) wrap.appendChild(kv(k, a[k]));
      });
      wrap.appendChild(sectionTitle("Stats"));
      [
        "link_karma",
        "comment_karma",
        "total_karma",
        "is_gold",
        "is_mod",
        "is_employee",
        "verified",
        "has_verified_email",
        "created_utc",
      ].forEach((k) => {
        if (k in a) wrap.appendChild(kv(k, a[k]));
      });
      const posts = data.recent_posts || [];
      if (posts.length) {
        wrap.appendChild(sectionTitle(`Recent posts (${posts.length})`));
        posts.forEach((p) =>
          wrap.appendChild(
            listCard({
              title: p.title,
              titleHref: p.permalink,
              meta: [p.subreddit, `↑ ${p.score}`, `💬 ${p.num_comments}`],
            })
          )
        );
      }
      const comments = data.recent_comments || [];
      if (comments.length) {
        wrap.appendChild(sectionTitle(`Recent comments (${comments.length})`));
        comments.forEach((c) =>
          wrap.appendChild(
            listCard({
              title: c.link_title || "(comment)",
              titleHref: c.permalink,
              meta: [c.subreddit, `↑ ${c.score}`],
              body: c.body_excerpt,
            })
          )
        );
      }
    },

    domain(wrap, data) {
      wrap.appendChild(kv("Domain", data.query));
      wrap.appendChild(sectionTitle("WHOIS"));
      Object.entries(data.whois || {}).forEach(([k, v]) => wrap.appendChild(kv(k, v)));
      wrap.appendChild(sectionTitle("DNS records"));
      Object.entries(data.dns || {}).forEach(([rtype, vals]) => {
        if (vals && vals.length) wrap.appendChild(kv(rtype, vals));
      });
    },

    ip(wrap, data) {
      wrap.appendChild(kv("Query", data.query));
      wrap.appendChild(kv("Resolved IP", data.resolved_ip));
      wrap.appendChild(kv("Reverse DNS", data.reverse_dns));
      wrap.appendChild(sectionTitle("Geolocation"));
      Object.entries(data.geo || {}).forEach(([k, v]) => wrap.appendChild(kv(k, v)));
      const lat = data.geo?.lat;
      const lon = data.geo?.lon;
      if (typeof lat === "number" && typeof lon === "number") {
        wrap.appendChild(sectionTitle("Map"));
        const map = document.createElement("div");
        map.className = "result-map";
        const bbox = `${lon - 1},${lat - 1},${lon + 1},${lat + 1}`;
        const url = `https://www.openstreetmap.org/export/embed.html?bbox=${bbox}&layer=mapnik&marker=${lat},${lon}`;
        map.innerHTML = `<iframe loading="lazy" src="${url}"></iframe>`;
        wrap.appendChild(map);
        const link = document.createElement("a");
        link.className = "tag present";
        link.target = "_blank";
        link.rel = "noopener";
        link.href = `https://www.openstreetmap.org/?mlat=${lat}&mlon=${lon}#map=8/${lat}/${lon}`;
        link.textContent = "Open in OpenStreetMap";
        wrap.appendChild(link);
      }
    },

    mac_vendor(wrap, data) {
      ["query", "normalized", "oui", "found", "company", "address", "country", "block_type", "is_random", "updated"].forEach((k) => {
        if (k in data) wrap.appendChild(kv(k, data[k]));
      });
    },

    email(wrap, data) {
      wrap.appendChild(kv("Email", data.query));
      wrap.appendChild(kv("Domain", data.domain));
      wrap.appendChild(kv("MX records", data.mx_records || []));
      wrap.appendChild(sectionTitle("Gravatar"));
      Object.entries(data.gravatar || {}).forEach(([k, v]) => wrap.appendChild(kv(k, v)));
      if (data.gravatar?.exists && data.gravatar?.avatar_url) {
        const img = document.createElement("img");
        img.src = data.gravatar.avatar_url.replace("d=404", "d=mp");
        img.alt = "Gravatar avatar";
        img.className = "gravatar-img";
        wrap.appendChild(img);
      }
      wrap.appendChild(sectionTitle("HIBP"));
      Object.entries(data.hibp || {}).forEach(([k, v]) => wrap.appendChild(kv(k, v)));
    },

    phone(wrap, data) {
      [
        "e164",
        "international",
        "national",
        "is_valid",
        "is_possible",
        "type",
        "region",
        "location",
        "carrier",
        "country_code",
        "national_number",
        "timezones",
      ].forEach((k) => {
        if (k in data) wrap.appendChild(kv(k, data[k]));
      });
    },

    exif(wrap, data) {
      wrap.appendChild(kv("File", data.filename));
      wrap.appendChild(kv("Format", data.format));
      wrap.appendChild(kv("Mode", data.mode));
      wrap.appendChild(kv("Size", data.size));
      if (data.note) wrap.appendChild(kv("Note", data.note));
      if (data.gps) {
        wrap.appendChild(sectionTitle("GPS"));
        if (data.gps.latitude !== undefined) {
          wrap.appendChild(kv("Latitude", data.gps.latitude));
          wrap.appendChild(kv("Longitude", data.gps.longitude));
          const a = document.createElement("a");
          a.href = data.gps.maps_url;
          a.target = "_blank";
          a.rel = "noopener";
          a.className = "tag present";
          a.textContent = "Open in OpenStreetMap";
          wrap.appendChild(a);
        }
      }
      wrap.appendChild(sectionTitle("EXIF tags"));
      Object.entries(data.exif || {}).forEach(([k, v]) => wrap.appendChild(kv(k, v)));
    },

    reverse_image(wrap, data) {
      wrap.appendChild(kv("Image URL", data.query));
      wrap.appendChild(kv("Image host", data.image_host));
      wrap.appendChild(sectionTitle(`Search engines (${(data.engines || []).length})`));
      const list = document.createElement("div");
      (data.engines || []).forEach((e) => {
        const a = document.createElement("a");
        a.className = "tag present";
        a.target = "_blank";
        a.rel = "noopener";
        a.href = e.url;
        a.textContent = e.name;
        list.appendChild(a);
      });
      wrap.appendChild(list);
    },

    subdomains(wrap, data) {
      wrap.appendChild(kv("Domain", data.query));
      wrap.appendChild(kv("Count", data.count));
      if (data.truncated) wrap.appendChild(kv("Truncated", true));
      wrap.appendChild(sectionTitle("Subdomains"));
      const list = document.createElement("div");
      (data.subdomains || []).forEach((s) => {
        const span = document.createElement("a");
        span.className = "tag";
        span.href = `https://${s}`;
        span.target = "_blank";
        span.rel = "noopener";
        span.textContent = s;
        list.appendChild(span);
      });
      wrap.appendChild(list);
    },

    doh(wrap, data) {
      wrap.appendChild(kv("Host", data.query));
      wrap.appendChild(kv("Resolvers queried", data.resolver_count));
      (data.resolvers || []).forEach((r) => {
        wrap.appendChild(sectionTitle(`${r.resolver} · ${r.answer_count} answers`));
        Object.entries(r.records || {}).forEach(([rtype, vals]) => {
          if (vals && vals.length) wrap.appendChild(kv(rtype, vals));
        });
      });
    },

    wayback(wrap, data) {
      wrap.appendChild(kv("URL", data.query));
      wrap.appendChild(kv("Snapshots", data.count));
      wrap.appendChild(sectionTitle("Recent snapshots"));
      (data.snapshots || [])
        .slice(-25)
        .reverse()
        .forEach((s) => {
          const row = document.createElement("div");
          row.className = "kv";
          row.innerHTML = `<div class="k">${s.timestamp}</div><div class="v"><a target="_blank" rel="noopener" href="${s.snapshot_url}">${s.original}</a></div>`;
          wrap.appendChild(row);
        });
    },

    ssl(wrap, data) {
      [
        "query",
        "subject",
        "issuer",
        "serial_number",
        "version",
        "not_before",
        "not_after",
        "expires_in_days",
        "is_expired",
        "signature_algorithm",
        "subject_alt_names",
      ].forEach((k) => {
        if (k in data) wrap.appendChild(kv(k, data[k]));
      });
    },

    dorks(wrap, data) {
      wrap.appendChild(kv("Target", data.query));
      (data.dorks || []).forEach((d) => {
        wrap.appendChild(sectionTitle(d.label));
        wrap.appendChild(kv("Query", d.dork));
        const links = document.createElement("div");
        Object.entries(d.engines).forEach(([name, url]) => {
          const a = document.createElement("a");
          a.className = "tag present";
          a.target = "_blank";
          a.rel = "noopener";
          a.href = url;
          a.textContent = name;
          links.appendChild(a);
        });
        wrap.appendChild(links);
      });
    },

    threat_intel(wrap, data) {
      wrap.appendChild(kv("Target", data.query));
      wrap.appendChild(kv("Kind", data.kind));
      wrap.appendChild(sectionTitle("Verification links"));
      const links = document.createElement("div");
      Object.entries(data.verification_links || {}).forEach(([name, url]) => {
        const a = document.createElement("a");
        a.className = "tag present";
        a.target = "_blank";
        a.rel = "noopener";
        a.href = url;
        a.textContent = name;
        links.appendChild(a);
      });
      wrap.appendChild(links);
      const u = data.urlscan || {};
      wrap.appendChild(sectionTitle("urlscan.io"));
      wrap.appendChild(kv("Available", !!u.available));
      if ("total_matches" in u) wrap.appendChild(kv("Total matches", u.total_matches));
      if (u.error) wrap.appendChild(kv("Error", u.error, "bool-bad"));
      (u.scans || []).forEach((s) =>
        wrap.appendChild(
          listCard({
            title: s.url || s.domain || s.ip,
            meta: [s.task_time, s.country, s.ip, s.domain].filter(Boolean),
            body: `result: ${s.result || "—"}`,
          })
        )
      );
    },
  };
})();
