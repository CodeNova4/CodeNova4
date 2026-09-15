import React, { useState, useMemo } from "react";
import { LineChart, Line, ResponsiveContainer } from "recharts";

/* ---------------------------------------------------------------- */
/* Seeded RNG so the demo data is stable across renders             */
/* ---------------------------------------------------------------- */
function mulberry32(seed) {
  let a = seed;
  return function () {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
const rng = mulberry32(88301);

/* ---------------------------------------------------------------- */
/* Component templates per platform category                       */
/* ---------------------------------------------------------------- */
const COMPONENT_TEMPLATES = {
  aircraft: [
    { key: "engine", name: "Engine", metric: "Oil Debris", unit: "ppm", threshold: 120, action: "Pull oil filter, run debris sample analysis" },
    { key: "drivetrain", name: "Main Rotor / Drivetrain", metric: "Vibration", unit: "mm/s", threshold: 12, action: "Inspect rotor mounts and drivetrain, run balance check" },
    { key: "avionics", name: "Avionics / Fire Control", metric: "Thermal Drift", unit: "°C", threshold: 85, action: "Run avionics diagnostic, inspect cooling loop" },
    { key: "hydraulics", name: "Hydraulic System", metric: "Pressure Loss", unit: "%", threshold: 15, action: "Inspect hydraulic lines and seals, service fluid" },
  ],
  ground: [
    { key: "engine", name: "Engine", metric: "Oil Debris", unit: "ppm", threshold: 110, action: "Pull oil filter, run debris sample analysis" },
    { key: "drivetrain", name: "Track & Suspension", metric: "Vibration", unit: "mm/s", threshold: 14, action: "Inspect track tension and road wheels" },
    { key: "avionics", name: "Fire Control System", metric: "Thermal Drift", unit: "°C", threshold: 80, action: "Run fire-control diagnostic, inspect cooling" },
    { key: "hydraulics", name: "Hydraulic System", metric: "Pressure Loss", unit: "%", threshold: 15, action: "Inspect hydraulic lines and seals, service fluid" },
  ],
  equipment: [
    { key: "engine", name: "Power Unit", metric: "Oil Debris", unit: "ppm", threshold: 100, action: "Inspect generator oil filter and debris sample" },
    { key: "drivetrain", name: "Elevation / Traverse Drive", metric: "Vibration", unit: "mm/s", threshold: 10, action: "Inspect drive gearing and bearings" },
    { key: "avionics", name: "Radar / Targeting", metric: "Thermal Drift", unit: "°C", threshold: 75, action: "Run radar diagnostic, inspect cooling loop" },
    { key: "hydraulics", name: "Hydraulic Actuators", metric: "Pressure Loss", unit: "%", threshold: 15, action: "Inspect actuator seals, service fluid" },
  ],
};

const PLATFORMS = [
  { tail: "AH-64E · 17-03411", name: "Apache Attack Helicopter", category: "aircraft" },
  { tail: "UH-60M · 19-08823", name: "Black Hawk Utility Helicopter", category: "aircraft" },
  { tail: "F-35A · 21-05561", name: "Lightning II Strike Fighter", category: "aircraft" },
  { tail: "C-130J · 14-07729", name: "Hercules Transport", category: "aircraft" },
  { tail: "MQ-9 · 22-01187", name: "Reaper UAS", category: "aircraft" },
  { tail: "M1A2 · B-2231", name: "Abrams Main Battle Tank", category: "ground" },
  { tail: "M2A3 · B-1146", name: "Bradley Fighting Vehicle", category: "ground" },
  { tail: "STRYKER · B-4409", name: "Stryker ICV", category: "ground" },
  { tail: "HIMARS · B-7723", name: "M142 HIMARS Launcher", category: "equipment" },
  { tail: "PATRIOT · E-1190", name: "PAC-3 Fire Unit", category: "equipment" },
  { tail: "AH-64E · 18-09902", name: "Apache Attack Helicopter", category: "aircraft" },
  { tail: "M1A2 · B-3387", name: "Abrams Main Battle Tank", category: "ground" },
  { tail: "UH-60M · 20-04471", name: "Black Hawk Utility Helicopter", category: "aircraft" },
  { tail: "STRYKER · B-5518", name: "Stryker ICV", category: "ground" },
];

/* ---------------------------------------------------------------- */
/* Rule-based predictive engine                                     */
/* ---------------------------------------------------------------- */
function daysToBreach(current, threshold, dailyRate) {
  if (current >= threshold) return 0;
  if (dailyRate <= 0.001) return Infinity;
  return Math.max(0, Math.round((threshold - current) / dailyRate));
}
function statusFromDays(days) {
  if (days <= 3) return "critical";
  if (days <= 14) return "watch";
  return "ok";
}
function pickProfile() {
  const r = rng();
  if (r < 0.58) return "stable";
  if (r < 0.84) return "watch";
  return "critical";
}

function generateFleet() {
  return PLATFORMS.map((p, idx) => {
    const missionWindowDays = 2 + Math.floor(rng() * 27);
    const templates = COMPONENT_TEMPLATES[p.category];
    const components = templates.map((t) => {
      const profile = pickProfile();
      let current, dailyRate;
      if (profile === "stable") {
        current = t.threshold * (0.28 + rng() * 0.25);
        dailyRate = rng() * 0.15;
      } else if (profile === "watch") {
        current = t.threshold * (0.62 + rng() * 0.18);
        dailyRate = t.threshold * (0.015 + rng() * 0.02);
      } else {
        current = t.threshold * (0.86 + rng() * 0.2);
        dailyRate = t.threshold * (0.03 + rng() * 0.035);
      }
      current = Math.round(current * 10) / 10;
      dailyRate = Math.round(dailyRate * 100) / 100;

      const history = [];
      for (let i = 13; i >= 0; i--) {
        const val = Math.max(0, current - dailyRate * i + (rng() - 0.5) * (t.threshold * 0.02));
        history.push({ d: 13 - i, v: Math.round(val * 10) / 10 });
      }

      const days = daysToBreach(current, t.threshold, dailyRate);
      const status = statusFromDays(days);
      const lastServiceDaysAgo = 8 + Math.floor(rng() * 150);

      return {
        ...t,
        current,
        dailyRate,
        history,
        days,
        status,
        lastServiceDaysAgo,
        beforeMission: days === Infinity ? null : missionWindowDays - days,
      };
    });

    const worst = components.reduce((acc, c) => {
      const order = { critical: 2, watch: 1, ok: 0 };
      return order[c.status] > order[acc] ? c.status : acc;
    }, "ok");

    const flaggedBeforeMission = components.some(
      (c) => c.status !== "ok" && c.beforeMission !== null && c.beforeMission >= 0
    );

    let assetStatus = "ready";
    if (worst === "critical") assetStatus = "nmc";
    else if (worst === "watch" && flaggedBeforeMission) assetStatus = "risk";
    else if (worst === "watch") assetStatus = "risk";

    const minDays = Math.min(...components.map((c) => (c.days === Infinity ? 9999 : c.days)));

    return {
      id: idx,
      ...p,
      missionWindowDays,
      components,
      status: assetStatus,
      minDays,
    };
  });
}

const STATUS_META = {
  ready: { label: "Mission Ready", color: "var(--ok)" },
  risk: { label: "At Risk", color: "var(--watch)" },
  nmc: { label: "Non-Mission-Capable", color: "var(--critical)" },
};
const COMP_STATUS_META = {
  ok: { label: "Nominal", color: "var(--ok)" },
  watch: { label: "Watch", color: "var(--watch)" },
  critical: { label: "Critical", color: "var(--critical)" },
};
const CATEGORY_LABEL = { aircraft: "Aircraft", ground: "Ground Vehicle", equipment: "Equipment" };

function explainComponent(c, missionWindowDays) {
  if (c.status === "ok") return null;
  const pct = Math.round((c.current / c.threshold) * 100);
  const daysText =
    c.days === 0
      ? "has already crossed"
      : c.days === Infinity
      ? "is not currently projected to cross"
      : `is projected to cross in ${c.days} day${c.days === 1 ? "" : "s"}`;
  const missionText =
    c.beforeMission === null
      ? ""
      : c.beforeMission >= 0
      ? ` — that is ${c.beforeMission} day${c.beforeMission === 1 ? "" : "s"} before the next mission window (T+${missionWindowDays}d).`
      : ` — after the next mission window, but trending the wrong way.`;
  return `${c.name} ${c.metric.toLowerCase()} reads ${c.current}${c.unit} (${pct}% of the ${c.threshold}${c.unit} limit) and has climbed ~${c.dailyRate}${c.unit}/day over the last two weeks. At this rate it ${daysText} the limit${missionText}`;
}

/* ---------------------------------------------------------------- */
/* UI atoms                                                          */
/* ---------------------------------------------------------------- */
function Sparkline({ data, color }) {
  return (
    <div style={{ width: 84, height: 28 }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <Line type="monotone" dataKey="v" stroke={color} strokeWidth={1.75} dot={false} isAnimationActive={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

function Pill({ color, children }) {
  return (
    <span
      className="pill"
      style={{ color, borderColor: color, background: `${color}1a` }}
    >
      {children}
    </span>
  );
}

/* ---------------------------------------------------------------- */
/* Main App                                                          */
/* ---------------------------------------------------------------- */
export default function App() {
  const fleet = useMemo(() => generateFleet(), []);
  const [selectedId, setSelectedId] = useState(fleet[0].id);
  const [catFilter, setCatFilter] = useState("all");
  const [tab, setTab] = useState("fleet");

  const filtered = fleet.filter((a) => catFilter === "all" || a.category === catFilter);
  const selected = fleet.find((a) => a.id === selectedId) || filtered[0];

  const readyCount = fleet.filter((a) => a.status === "ready").length;
  const riskCount = fleet.filter((a) => a.status === "risk").length;
  const nmcCount = fleet.filter((a) => a.status === "nmc").length;

  const maintenancePlan = useMemo(() => {
    const items = [];
    fleet.forEach((a) => {
      a.components.forEach((c) => {
        if (c.status !== "ok") {
          items.push({
            assetId: a.id,
            tail: a.tail,
            name: a.name,
            component: c,
            missionWindowDays: a.missionWindowDays,
          });
        }
      });
    });
    return items.sort((x, y) => {
      const dx = x.component.days === Infinity ? 9999 : x.component.days;
      const dy = y.component.days === Infinity ? 9999 : y.component.days;
      return dx - dy;
    });
  }, [fleet]);

  return (
    <div className="app">
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

        :root {
          --bg: #10141a;
          --panel: #171d24;
          --panel-2: #1e262f;
          --border: #2a323b;
          --text: #e7ebee;
          --text-dim: #8c98a4;
          --text-faint: #5b6570;
          --ok: #4f9c83;
          --watch: #c99a3e;
          --critical: #c1523f;
          --accent: #5f8fbf;
        }
        * { box-sizing: border-box; }
        .app {
          background: var(--bg);
          color: var(--text);
          font-family: 'IBM Plex Sans', sans-serif;
          min-height: 100%;
          width: 100%;
          padding: 0;
        }
        .mono { font-family: 'IBM Plex Mono', monospace; }
        .display { font-family: 'Barlow Condensed', sans-serif; }

        .topbar {
          display: flex; align-items: center; justify-content: space-between;
          padding: 18px 24px; border-bottom: 1px solid var(--border);
          flex-wrap: wrap; gap: 14px;
        }
        .brand { display: flex; align-items: baseline; gap: 10px; }
        .brand .mark { width: 9px; height: 9px; background: var(--accent); display: inline-block; }
        .brand h1 { font-family: 'Barlow Condensed', sans-serif; font-weight: 600; font-size: 22px; letter-spacing: 0.3px; margin: 0; }
        .brand p { color: var(--text-faint); font-size: 12.5px; margin: 2px 0 0; }

        .summary { display: flex; gap: 22px; align-items: center; }
        .summary .stat { text-align: right; }
        .summary .stat .num { font-family: 'Barlow Condensed', sans-serif; font-size: 26px; font-weight: 600; line-height: 1; }
        .summary .stat .lbl { color: var(--text-faint); font-size: 11px; margin-top: 3px; }

        .tabs { display: flex; gap: 2px; padding: 0 24px; border-bottom: 1px solid var(--border); }
        .tab { padding: 11px 16px; font-size: 13.5px; color: var(--text-dim); cursor: pointer; border-bottom: 2px solid transparent; }
        .tab.active { color: var(--text); border-bottom-color: var(--accent); }

        .body { display: grid; grid-template-columns: 360px 1fr; min-height: 640px; }
        @media (max-width: 900px) { .body { grid-template-columns: 1fr; } }

        .list-col { border-right: 1px solid var(--border); }
        .filters { display: flex; gap: 6px; padding: 14px 16px; flex-wrap: wrap; border-bottom: 1px solid var(--border); }
        .chip { padding: 5px 11px; font-size: 12px; border: 1px solid var(--border); color: var(--text-dim); cursor: pointer; background: transparent; }
        .chip.active { color: var(--text); border-color: var(--accent); background: rgba(95,143,191,0.12); }

        .asset-row { display: flex; align-items: center; gap: 12px; padding: 13px 16px; border-bottom: 1px solid var(--border); cursor: pointer; }
        .asset-row:hover { background: var(--panel); }
        .asset-row.selected { background: var(--panel-2); }
        .status-bar { width: 3px; align-self: stretch; border-radius: 1px; }
        .asset-row .info { flex: 1; min-width: 0; }
        .asset-row .tail { font-family: 'IBM Plex Mono', monospace; font-size: 12px; color: var(--text-dim); }
        .asset-row .name { font-size: 13.5px; margin-top: 1px; }
        .asset-row .days { font-size: 11px; color: var(--text-faint); margin-top: 3px; }

        .pill { font-size: 10.5px; padding: 3px 8px; border: 1px solid; border-radius: 2px; white-space: nowrap; }

        .detail { padding: 22px 26px; }
        .detail-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; margin-bottom: 22px; flex-wrap: wrap; }
        .detail-head h2 { font-family: 'Barlow Condensed', sans-serif; font-size: 24px; font-weight: 600; margin: 0 0 4px; }
        .detail-head .sub { color: var(--text-faint); font-size: 12.5px; }

        .section-label { font-size: 12px; color: var(--text-faint); margin: 26px 0 10px; letter-spacing: 0.3px; }
        .section-label:first-of-type { margin-top: 0; }

        .comp-card { border: 1px solid var(--border); background: var(--panel); padding: 13px 15px; margin-bottom: 8px; display: flex; align-items: center; gap: 14px; }
        .comp-card .cinfo { flex: 1; min-width: 0; }
        .comp-card .cname { font-size: 13.5px; }
        .comp-card .cmeta { font-size: 11.5px; color: var(--text-faint); margin-top: 2px; font-family: 'IBM Plex Mono', monospace; }

        .issue-card { border-left: 2px solid var(--critical); background: var(--panel); padding: 13px 15px; margin-bottom: 8px; }
        .issue-card.watch { border-left-color: var(--watch); }
        .issue-card .ihead { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
        .issue-card .iname { font-size: 13.5px; }
        .issue-card p { font-size: 12.5px; color: var(--text-dim); line-height: 1.55; margin: 0; }

        .empty { color: var(--text-faint); font-size: 13px; padding: 14px 0; }

        .plan-row { display: grid; grid-template-columns: 34px 1fr auto auto; gap: 14px; align-items: center; padding: 13px 16px; border-bottom: 1px solid var(--border); }
        .plan-row .rank { font-family: 'Barlow Condensed', sans-serif; font-size: 18px; color: var(--text-faint); }
        .plan-row .who { font-size: 13.5px; }
        .plan-row .what { font-size: 12px; color: var(--text-dim); margin-top: 2px; }
        .plan-row .due { font-family: 'IBM Plex Mono', monospace; font-size: 12px; text-align: right; }
        .plan-head { padding: 20px 26px 6px; }
        .plan-head h2 { font-family: 'Barlow Condensed', sans-serif; font-size: 22px; font-weight: 600; margin: 0 0 4px; }
        .plan-head p { color: var(--text-faint); font-size: 12.5px; margin: 0; }
      `}</style>

      <div className="topbar">
        <div className="brand">
          <span className="mark" />
          <div>
            <h1>Bob — Mission Readiness &amp; Predictive Maintenance</h1>
            <p>Defense &amp; Aerospace · Fleet Copilot</p>
          </div>
        </div>
        <div className="summary">
          <div className="stat">
            <div className="num" style={{ color: "var(--ok)" }}>{readyCount}/{fleet.length}</div>
            <div className="lbl">Mission Ready</div>
          </div>
          <div className="stat">
            <div className="num" style={{ color: "var(--watch)" }}>{riskCount}</div>
            <div className="lbl">At Risk</div>
          </div>
          <div className="stat">
            <div className="num" style={{ color: "var(--critical)" }}>{nmcCount}</div>
            <div className="lbl">Non-Mission-Capable</div>
          </div>
        </div>
      </div>

      <div className="tabs">
        <div className={`tab ${tab === "fleet" ? "active" : ""}`} onClick={() => setTab("fleet")}>Fleet Dashboard</div>
        <div className={`tab ${tab === "plan" ? "active" : ""}`} onClick={() => setTab("plan")}>Prioritized Maintenance Plan ({maintenancePlan.length})</div>
      </div>

      {tab === "fleet" && (
        <div className="body">
          <div className="list-col">
            <div className="filters">
              {["all", "aircraft", "ground", "equipment"].map((c) => (
                <button key={c} className={`chip ${catFilter === c ? "active" : ""}`} onClick={() => setCatFilter(c)}>
                  {c === "all" ? "All Assets" : CATEGORY_LABEL[c]}
                </button>
              ))}
            </div>
            <div>
              {filtered.map((a) => {
                const meta = STATUS_META[a.status];
                return (
                  <div
                    key={a.id}
                    className={`asset-row ${selected && selected.id === a.id ? "selected" : ""}`}
                    onClick={() => setSelectedId(a.id)}
                  >
                    <div className="status-bar" style={{ background: meta.color }} />
                    <div className="info">
                      <div className="tail">{a.tail}</div>
                      <div className="name">{a.name}</div>
                      <div className="days">
                        {a.status === "ready"
                          ? `Next mission T+${a.missionWindowDays}d · clear`
                          : `Flagged component in ${a.minDays === 9999 ? "—" : a.minDays + "d"}`}
                      </div>
                    </div>
                    <Pill color={meta.color}>{meta.label}</Pill>
                  </div>
                );
              })}
            </div>
          </div>

          {selected && (
            <div className="detail">
              <div className="detail-head">
                <div>
                  <h2>{selected.name}</h2>
                  <div className="sub mono">{selected.tail} · {CATEGORY_LABEL[selected.category]} · Next mission window T+{selected.missionWindowDays}d</div>
                </div>
                <Pill color={STATUS_META[selected.status].color}>{STATUS_META[selected.status].label}</Pill>
              </div>

              <div className="section-label">COMPONENT HEALTH</div>
              {selected.components.map((c) => {
                const meta = COMP_STATUS_META[c.status];
                return (
                  <div className="comp-card" key={c.key}>
                    <Sparkline data={c.history} color={meta.color} />
                    <div className="cinfo">
                      <div className="cname">{c.name}</div>
                      <div className="cmeta">
                        {c.metric} {c.current}{c.unit} / {c.threshold}{c.unit} limit · serviced {c.lastServiceDaysAgo}d ago
                      </div>
                    </div>
                    <Pill color={meta.color}>{meta.label}</Pill>
                  </div>
                );
              })}

              <div className="section-label">READINESS ISSUES — EXPLAINED</div>
              {selected.components.filter((c) => c.status !== "ok").length === 0 ? (
                <div className="empty">No flagged components. All systems within threshold.</div>
              ) : (
                selected.components
                  .filter((c) => c.status !== "ok")
                  .map((c) => (
                    <div className={`issue-card ${c.status}`} key={c.key}>
                      <div className="ihead">
                        <div className="iname">{c.name}</div>
                        <Pill color={COMP_STATUS_META[c.status].color}>{COMP_STATUS_META[c.status].label}</Pill>
                      </div>
                      <p>{explainComponent(c, selected.missionWindowDays)}</p>
                    </div>
                  ))
              )}
            </div>
          )}
        </div>
      )}

      {tab === "plan" && (
        <div>
          <div className="plan-head">
            <h2>Fleet-Wide Prioritized Maintenance Plan</h2>
            <p>Every flagged component across the fleet, ranked by days until it crosses its threshold.</p>
          </div>
          <div>
            {maintenancePlan.map((item, i) => {
              const meta = COMP_STATUS_META[item.component.status];
              const dueText = item.component.days === Infinity ? "—" : `${item.component.days}d`;
              return (
                <div className="plan-row" key={`${item.assetId}-${item.component.key}`}>
                  <div className="rank">{String(i + 1).padStart(2, "0")}</div>
                  <div>
                    <div className="who">{item.component.action} <span className="mono" style={{ color: "var(--text-faint)" }}>— {item.tail}</span></div>
                    <div className="what">{item.name} · {item.component.name}</div>
                  </div>
                  <Pill color={meta.color}>{meta.label}</Pill>
                  <div className="due" style={{ color: meta.color }}>{dueText}</div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
