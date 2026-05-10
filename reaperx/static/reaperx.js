// ReaperX frontend - submits the module form and renders the JSON response.
(() => {
  const form = document.getElementById("module-form");
  if (!form) return;

  const result = document.getElementById("module-result");
  const badge = document.getElementById("status-badge");
  const pretty = document.getElementById("result-pretty");
  const raw = document.getElementById("result-raw");
  const copyBtn = document.getElementById("copy-json");
  const dlBtn = document.getElementById("download-json");

  let lastJson = null;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const endpoint = form.dataset.endpoint;
    const fd = new FormData(form);
    const submitBtn = form.querySelector("button[type=submit]");
    submitBtn.disabled = true;
    submitBtn.dataset.label = submitBtn.dataset.label || submitBtn.textContent;
    submitBtn.innerHTML = '<span class="spinner"></span>Running…';
    setBadge("busy", "running");
    result.classList.remove("hidden");
    pretty.innerHTML = "";
    raw.textContent = "";

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
      pretty.appendChild(renderResult(data, window.REAPERX_MODULE_KEY));
    } catch (err) {
      setBadge("err", "error");
      pretty.textContent = `Request failed: ${err}`;
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = submitBtn.dataset.label;
    }
  });

  copyBtn?.addEventListener("click", async () => {
    if (!lastJson) return;
    await navigator.clipboard.writeText(JSON.stringify(lastJson, null, 2));
    flash(copyBtn, "Copied!");
  });
  dlBtn?.addEventListener("click", () => {
    if (!lastJson) return;
    const blob = new Blob([JSON.stringify(lastJson, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `reaperx-${window.REAPERX_MODULE_KEY}-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
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

  // ---- Renderers ---------------------------------------------------------
  function renderResult(data, key) {
    const wrap = document.createElement("div");
    if (data.error) {
      wrap.appendChild(kv("Error", data.error, "bool-false"));
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
      v.forEach((x) => {
        const span = document.createElement("span");
        span.textContent = typeof x === "object" ? JSON.stringify(x) : String(x);
        ve.appendChild(span);
      });
    } else if (typeof v === "boolean") {
      ve.textContent = String(v);
      ve.classList.add(v ? "bool-true" : "bool-false");
    } else if (v === null || v === undefined) {
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
        a.className = "tag " + (c.status === "present" ? "present" : c.status === "absent" ? "absent" : "unknown");
        a.target = "_blank";
        a.rel = "noopener";
        a.href = c.url;
        a.textContent = `${c.site} · ${c.status}`;
        all.appendChild(a);
      });
      wrap.appendChild(all);
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
        img.style.cssText = "width:96px;height:96px;border-radius:8px;border:1px solid var(--border);";
        wrap.appendChild(img);
      }
      wrap.appendChild(sectionTitle("HIBP"));
      Object.entries(data.hibp || {}).forEach(([k, v]) => wrap.appendChild(kv(k, v)));
    },

    phone(wrap, data) {
      ["e164", "international", "national", "is_valid", "is_possible", "type", "region", "location", "carrier", "country_code", "national_number", "timezones"].forEach((k) => {
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

    wayback(wrap, data) {
      wrap.appendChild(kv("URL", data.query));
      wrap.appendChild(kv("Snapshots", data.count));
      wrap.appendChild(sectionTitle("Recent snapshots"));
      (data.snapshots || []).slice(-25).reverse().forEach((s) => {
        const row = document.createElement("div");
        row.className = "kv";
        row.innerHTML = `<div class="k">${s.timestamp}</div><div class="v"><a target="_blank" rel="noopener" href="${s.snapshot_url}">${s.original}</a></div>`;
        wrap.appendChild(row);
      });
    },

    ssl(wrap, data) {
      ["query", "subject", "issuer", "serial_number", "version", "not_before", "not_after", "expires_in_days", "is_expired", "signature_algorithm", "subject_alt_names"].forEach((k) => {
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
          a.className = "tag";
          a.href = url;
          a.target = "_blank";
          a.rel = "noopener";
          a.textContent = name;
          links.appendChild(a);
        });
        wrap.appendChild(links);
      });
    },
  };
})();
