import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "..", "..");
const defaultManifest = path.join(
  repoRoot,
  "backups",
  "live-baselines",
  "2026-07-27-index-now",
  "manifest.json",
);

const mode = process.argv[2] ?? "preflight";
const manifestPath = process.argv[3]
  ? path.resolve(process.cwd(), process.argv[3])
  : defaultManifest;

function fail(message) {
  console.error(`\n[release-guard] FAIL: ${message}`);
  process.exit(1);
}

function loadManifest() {
  if (!fs.existsSync(manifestPath)) {
    fail(`Manifest not found: ${manifestPath}`);
  }
  const raw = fs.readFileSync(manifestPath, "utf8");
  const manifest = JSON.parse(raw);
  if (!Array.isArray(manifest.requiredMarkers) || !Array.isArray(manifest.requiredAssets)) {
    fail("Manifest must contain requiredMarkers[] and requiredAssets[].");
  }
  if (!Array.isArray(manifest.prohibitedMarkers)) {
    manifest.prohibitedMarkers = [];
  }
  return manifest;
}

function repoFilePath(manifestRelativePath) {
  const normalized = manifestRelativePath.replace(/[\\/]/g, path.sep);
  return path.join(repoRoot, normalized);
}

function sha256File(filePath) {
  const hash = crypto.createHash("sha256");
  hash.update(fs.readFileSync(filePath));
  return hash.digest("hex");
}

function verifyContentMarkers(content, required, prohibited, label) {
  const issues = [];
  for (const marker of required) {
    if (!content.includes(marker)) {
      issues.push(`[${label}] missing required marker: ${marker}`);
    }
  }
  for (const marker of prohibited) {
    if (content.includes(marker)) {
      issues.push(`[${label}] found prohibited marker: ${marker}`);
    }
  }
  return issues;
}

function verifyRequiredAssets(requiredAssets) {
  const issues = [];
  for (const item of requiredAssets) {
    const fullPath = repoFilePath(item.path);
    if (!fs.existsSync(fullPath)) {
      issues.push(`[assets] missing file: ${item.path}`);
      continue;
    }
    if (item.sha256) {
      const actual = sha256File(fullPath);
      if (actual !== String(item.sha256).toLowerCase()) {
        issues.push(
          `[assets] sha256 mismatch for ${item.path} expected=${item.sha256} actual=${actual}`,
        );
      }
    }
  }
  return issues;
}

async function fetchWithRetry(url, attempts = 8, delayMs = 1500) {
  let lastError = null;
  for (let i = 1; i <= attempts; i += 1) {
    try {
      const res = await fetch(url, { redirect: "follow" });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      return await res.text();
    } catch (error) {
      lastError = error;
      if (i < attempts) {
        await new Promise((resolve) => setTimeout(resolve, delayMs));
      }
    }
  }
  throw lastError;
}

function printPass(modeName, profileId) {
  console.log(`[release-guard] PASS (${modeName}) profile=${profileId}`);
}

function enforceOwnershipState(manifest, modeName) {
  const ownership = manifest.ownership;
  if (!ownership) {
    return;
  }
  const state = String(ownership.state ?? "").toLowerCase();
  if (state !== "blocked") {
    return;
  }

  const bypassEnvVar = ownership.bypassEnvVar || "RELEASE_GUARD_ALLOW_BLOCKED_OWNERSHIP";
  if (process.env[bypassEnvVar] === "1") {
    console.warn(
      `[release-guard] WARN (${modeName}) ownership migration is blocked but bypassed via ${bypassEnvVar}=1`,
    );
    return;
  }

  const reason = ownership.reason || "Ownership migration is blocked.";
  const expectedDeployService = ownership.expectedDeployService || "unknown";
  const expectedCustomDomainService = ownership.expectedCustomDomainService || "unknown";
  const migrationPlan = ownership.migrationPlan || "docs/runbooks/OWNERSHIP-MIGRATION.md";
  const evidenceLog = ownership.evidenceLog || "docs/runbooks/OWNERSHIP-EVIDENCE-2026-08-10.md";
  fail(
    [
      `Ownership state is BLOCKED in release manifest.`,
      `reason: ${reason}`,
      `deploy service: ${expectedDeployService}`,
      `custom-domain service: ${expectedCustomDomainService}`,
      `migration plan: ${migrationPlan}`,
      `evidence log: ${evidenceLog}`,
      `To acknowledge temporary risk and continue, set ${bypassEnvVar}=1 for this command.`,
    ].join("\n"),
  );
}

async function runPreflight(manifest) {
  enforceOwnershipState(manifest, "preflight");

  const indexPath = path.join(repoRoot, "public", "index.html");
  if (!fs.existsSync(indexPath)) {
    fail(`Missing public/index.html at ${indexPath}`);
  }

  const html = fs.readFileSync(indexPath, "utf8");
  const issues = [
    ...verifyContentMarkers(html, manifest.requiredMarkers, manifest.prohibitedMarkers, "public/index.html"),
    ...verifyRequiredAssets(manifest.requiredAssets),
  ];

  if (issues.length > 0) {
    fail(issues.join("\n"));
  }

  printPass("preflight", manifest.profileId ?? "unknown");
}

async function runPostdeploy(manifest) {
  enforceOwnershipState(manifest, "postdeploy");

  const workersUrl = manifest.productionUrls?.workers;
  const customDomainUrl = manifest.productionUrls?.customDomain;
  if (!workersUrl || !customDomainUrl) {
    fail("Manifest must define productionUrls.workers and productionUrls.customDomain for postdeploy checks.");
  }

  const [workersHtml, customHtml] = await Promise.all([
    fetchWithRetry(workersUrl),
    fetchWithRetry(customDomainUrl),
  ]);

  const workersIssues = verifyContentMarkers(
    workersHtml,
    manifest.requiredMarkers,
    manifest.prohibitedMarkers,
    workersUrl,
  );
  const customIssues = verifyContentMarkers(
    customHtml,
    manifest.requiredMarkers,
    manifest.prohibitedMarkers,
    customDomainUrl,
  );

  const parityIssues = [];
  const parityChecks = [...manifest.requiredMarkers, ...manifest.prohibitedMarkers];
  for (const marker of parityChecks) {
    const workersHas = workersHtml.includes(marker);
    const customHas = customHtml.includes(marker);
    if (workersHas !== customHas) {
      parityIssues.push(
        `[parity] marker mismatch between workers/custom domain for "${marker}" (workers=${workersHas}, custom=${customHas})`,
      );
    }
  }

  const issues = [...workersIssues, ...customIssues, ...parityIssues];
  if (issues.length > 0) {
    fail(issues.join("\n"));
  }

  printPass("postdeploy", manifest.profileId ?? "unknown");
}

async function main() {
  const manifest = loadManifest();
  if (mode === "preflight") {
    await runPreflight(manifest);
    return;
  }
  if (mode === "postdeploy") {
    await runPostdeploy(manifest);
    return;
  }
  fail(`Unknown mode "${mode}". Use "preflight" or "postdeploy".`);
}

main().catch((error) => fail(error?.stack || String(error)));
