import sys

with open('frontend/src/pages/DashboardPage.jsx', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace(
    'import {\n  CalendarCheck,\n  CalendarClock,\n  CheckCircle2,\n  Clock3,',
    'import {\n  CalendarCheck,\n  CalendarClock,\n  CheckCircle2,\n  CheckCheck,\n  Clock3,'
)

cardConfig_old = """const cardConfig = [
  { key: "approved", label: "Aprovadas", icon: CheckCircle2, tone: "green", status: "APPROVED" },
  { key: "pending", label: "Pendentes", icon: Clock3, tone: "amber", status: "PENDING" },
  { key: "cancelled", label: "Canceladas", icon: XCircle, tone: "red", status: "CANCELLED" },
  { key: "upcoming", label: "Próximas agendas", icon: CalendarClock, tone: "violet" },
  { key: "today_total", label: "Agendas de hoje", icon: CalendarCheck, tone: "blue" },
  { key: "today_agents", label: "Agentes escalados hoje", icon: Users, tone: "cyan" },
  { key: "in_progress", label: "Em andamento", icon: PauseCircle, tone: "teal" },
];"""

cardConfig_new = """const cardConfig = [
  { key: "approved", label: "Aprovadas", icon: CheckCircle2, tone: "green", status: "APPROVED", color: "#00b894", gradient: "linear-gradient(135deg, #00b894, #009472)" },
  { key: "pending", label: "Pendentes", icon: Clock3, tone: "amber", status: "PENDING", color: "#fdcb6e", gradient: "linear-gradient(135deg, #fdcb6e, #e1b12c)" },
  { key: "cancelled", label: "Canceladas", icon: XCircle, tone: "red", status: "CANCELLED", color: "#d63031", gradient: "linear-gradient(135deg, #d63031, #b33939)" },
  { key: "completed", label: "Concluídas", icon: CheckCheck, tone: "emerald", status: "COMPLETED", color: "#0984e3", gradient: "linear-gradient(135deg, #0984e3, #0762a8)" },
  { key: "upcoming", label: "Próximas agendas", icon: CalendarClock, tone: "violet", color: "#6c5ce7", gradient: "linear-gradient(135deg, #6c5ce7, #5345b5)" },
  { key: "today_total", label: "Agendas de hoje", icon: CalendarCheck, tone: "blue", color: "#74b9ff", gradient: "linear-gradient(135deg, #74b9ff, #5798d6)" },
  { key: "today_agents", label: "Agentes de hoje", icon: Users, tone: "cyan", color: "#00cec9", gradient: "linear-gradient(135deg, #00cec9, #00a4a1)" },
  { key: "in_progress", label: "Em andamento", icon: PauseCircle, tone: "teal", color: "#e84393", gradient: "linear-gradient(135deg, #e84393, #c23979)" },
];"""

c = c.replace(cardConfig_old, cardConfig_new)

dashboardCard_old = """function DashboardCard({ active, config, data, onClick }) {
  const Icon = config.icon;
  return (
    <button
      className={`metric-card ${config.tone} ${active ? "active" : ""}`}
      onClick={onClick}
      type="button"
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        textAlign: "center",
        transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
        boxShadow: active ? "0 10px 20px -5px rgba(0, 72, 215, 0.3)" : "none",
        transform: active ? "translateY(-4px)" : "none",
      }}
    >
      <span className="metric-icon" style={{ borderRadius: "10px", padding: "8px", margin: "0 auto 8px" }}>
        <Icon size={20} />
      </span>
      <span style={{ fontSize: "13px", fontWeight: "600", color: "var(--text-soft)", display: "block" }}>{config.label}</span>
      <strong style={{ fontSize: "28px", fontWeight: "800", marginTop: "4px", display: "block" }}>{data?.value ?? 0}</strong>
    </button>
  );
}"""

dashboardCard_new = """function DashboardCard({ active, config, data, onClick }) {
  const Icon = config.icon;
  return (
    <button
      onClick={onClick}
      type="button"
      style={{
        background: active ? "var(--surface)" : "var(--surface)",
        borderRadius: "16px",
        padding: "20px",
        border: active ? `2px solid ${config.color}` : "1px solid var(--line)",
        boxShadow: active ? `0 8px 24px ${config.color}33` : "0 4px 12px rgba(0,0,0,0.02)",
        display: "flex",
        flexDirection: "column",
        gap: "12px",
        position: "relative",
        overflow: "hidden",
        transition: "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
        transform: active ? "translateY(-4px)" : "none",
        cursor: "pointer",
        textAlign: "left",
      }}
      onMouseEnter={e => {
        if (!active) {
          e.currentTarget.style.transform = "translateY(-2px)";
          e.currentTarget.style.boxShadow = `0 8px 24px ${config.color}22`;
        }
      }}
      onMouseLeave={e => {
        if (!active) {
          e.currentTarget.style.transform = "none";
          e.currentTarget.style.boxShadow = "0 4px 12px rgba(0,0,0,0.02)";
        }
      }}
    >
      <div style={{ position: "absolute", top: -20, right: -20, width: 80, height: 80, borderRadius: "50%", background: config.color, opacity: active ? 0.1 : 0.04 }} />
      <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
        <div style={{ width: "36px", height: "36px", borderRadius: "10px", display: "flex", alignItems: "center", justifyContent: "center", background: config.gradient, color: "#fff", boxShadow: `0 4px 12px ${config.color}44` }}>
          <Icon size={18} />
        </div>
        <span style={{ fontSize: "12px", fontWeight: "700", color: "var(--text-soft)", textTransform: "uppercase", letterSpacing: "0.5px" }}>{config.label}</span>
      </div>
      <strong style={{ fontSize: "32px", fontWeight: "800", color: "var(--text)", lineHeight: "1" }}>{data?.value ?? 0}</strong>
    </button>
  );
}"""

c = c.replace(dashboardCard_old, dashboardCard_new)

with open('frontend/src/pages/DashboardPage.jsx', 'w', encoding='utf-8') as f:
    f.write(c)
