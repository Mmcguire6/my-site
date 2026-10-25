/**
 * The onboarding questions, defined once: server validation (client.js) and the labelled answers
 * in the team email (mail.js) both read this. The Client Hub page mirrors the same keys and steps.
 * Only the essentials are required; everything else helps the build but can come later.
 * Never add a password field: access to domains, Google or phone providers is arranged separately.
 */
const YN = ["yes", "no"];
const YNU = ["yes", "no", "not_sure"];

const STEPS = [
  { id: "business", title: "Your business" },
  { id: "services", title: "Services" },
  { id: "brand", title: "Brand & website" },
  { id: "systems", title: "Your current systems", peak: true },
  { id: "goals", title: "Goals & notes" },
];

const FIELDS = [
  // 1. business
  { k: "business_name", step: "business", label: "Business name", req: true },
  { k: "contact_name", step: "business", label: "Primary contact", req: true },
  { k: "email", step: "business", label: "Email", req: true, type: "email" },
  { k: "phone", step: "business", label: "Business phone", req: true, type: "phone" },
  { k: "trade", step: "business", label: "Industry / trade", req: true },
  { k: "team_size", step: "business", label: "Team size", options: ["Just me", "2-5", "6-15", "16+"] },
  { k: "address", step: "business", label: "Business address", max: 300 },
  { k: "city", step: "business", label: "City", req: true },
  { k: "region", step: "business", label: "Province / state", req: true },
  { k: "country", step: "business", label: "Country", req: true, options: ["Canada", "United States", "Other"] },
  { k: "hours", step: "business", label: "Business hours", max: 300 },
  { k: "years_in_business", step: "business", label: "Years in business", max: 40 },
  { k: "licences_insurance", step: "business", label: "Licences, insurance, certifications", max: 500 },
  // 2. services
  { k: "services", step: "services", label: "Services offered", req: true, max: 2000 },
  { k: "top_services", step: "services", label: "Jobs they want more of", max: 1000 },
  { k: "service_area", step: "services", label: "Service area", req: true, max: 500 },
  { k: "description", step: "services", label: "About the business", req: true, max: 2000 },
  { k: "emergency_service", step: "services", label: "Emergency / after-hours service", options: YN },
  { k: "free_estimates", step: "services", label: "Free estimates", options: YN },
  { k: "financing", step: "services", label: "Offers financing", options: YN },
  // 3. brand & website
  { k: "has_website", step: "brand", label: "Has a website", req: true, options: YN },
  { k: "website_url", step: "brand", label: "Current website", type: "url", reqIf: (d) => d.has_website === "yes" },
  { k: "owns_domain", step: "brand", label: "Owns a domain", req: true, options: YNU },
  { k: "domain_registrar", step: "brand", label: "Domain registered with", max: 100 },
  { k: "desired_domain", step: "brand", label: "Domain they'd like", max: 200 },
  { k: "brand_colours", step: "brand", label: "Brand colours", max: 200 },
  { k: "brand_style", step: "brand", label: "Style", options: ["Clean and modern", "Bold and strong", "Classic and trustworthy", "Not sure"] },
  { k: "sites_you_like", step: "brand", label: "Websites they like", max: 1000 },
  { k: "social_links", step: "brand", label: "Social media", max: 1000 },
  { k: "google_reviews_link", step: "brand", label: "Google reviews link", max: 500 },
  // 4. systems (The Peak System only)
  { k: "uses_crm", step: "systems", label: "Uses a CRM", req: true, peak: true, options: YN },
  { k: "crm_name", step: "systems", label: "CRM", peak: true, reqIf: (d) => d.uses_crm === "yes" },
  { k: "has_gbp", step: "systems", label: "Has a Google Business Profile", req: true, peak: true, options: YNU },
  { k: "gbp_email", step: "systems", label: "Google account that manages the profile", peak: true, type: "email" },
  { k: "calls_number", step: "systems", label: "Number customers call", req: true, peak: true, type: "phone" },
  { k: "phone_carrier", step: "systems", label: "Phone provider", peak: true, max: 100 },
  { k: "missed_call", step: "systems", label: "Wants missed call text-back", req: true, peak: true, options: YNU },
  { k: "who_answers", step: "systems", label: "Who answers calls", peak: true, max: 300 },
  { k: "scheduling_software", step: "systems", label: "Scheduling / estimate software", peak: true, max: 500 },
  { k: "review_sites", step: "systems", label: "Review sites they use", peak: true, max: 300 },
  { k: "notify_email", step: "systems", label: "Send new-lead alerts to", peak: true, type: "email" },
  // 5. goals & notes
  { k: "main_goal", step: "goals", label: "Main goal", options: ["More calls and leads", "More estimates turned into jobs", "More Google reviews", "Less admin and follow-up", "A better website", "Not sure yet"] },
  { k: "lead_sources", step: "goals", label: "How customers find them now", max: 1000 },
  { k: "notes", step: "goals", label: "Anything else", max: 3000 },
];

const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

function forPlan(planKey) {
  return FIELDS.filter((f) => !f.peak || planKey === "peak");
}

/** Keep known keys only, trimmed and length-limited. */
function clean(data, planKey) {
  const out = {};
  for (const f of forPlan(planKey)) {
    const v = data && data[f.k];
    if (v === undefined || v === null) continue;
    out[f.k] = String(v).replace(/\u0000/g, "").trim().slice(0, f.max || 200);
  }
  return out;
}

function validate(d, planKey) {
  const errors = {};
  for (const f of forPlan(planKey)) {
    const v = d[f.k] || "";
    const required = f.req || (f.reqIf && f.reqIf(d));
    if (!v) {
      if (required) errors[f.k] = "required";
      continue;
    }
    if (f.options && !f.options.includes(v)) errors[f.k] = "invalid_option";
    else if (f.type === "email" && !EMAIL_RE.test(v)) errors[f.k] = "invalid_email";
    else if (f.type === "phone" && !/^[0-9+().\-\s]{7,25}$/.test(v)) errors[f.k] = "invalid_phone";
    else if (f.type === "url" && !/^(https?:\/\/)?[^\s/]+\.[^\s]{2,}$/i.test(v)) errors[f.k] = "invalid_url";
  }
  return errors;
}

/** Answers grouped by step with labels, for the team email. */
function labelled(d, planKey) {
  return STEPS.filter((s) => !s.peak || planKey === "peak").map((s) => ({
    title: s.title,
    rows: forPlan(planKey).filter((f) => f.step === s.id && d[f.k]).map((f) => [f.label, f.options && YNU.includes(d[f.k]) ? d[f.k].replace("_", " ") : d[f.k]]),
  })).filter((g) => g.rows.length);
}

module.exports = { STEPS, FIELDS, clean, validate, labelled, forPlan };
