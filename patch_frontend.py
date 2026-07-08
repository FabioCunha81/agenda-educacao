import sys

with open('frontend/src/components/AppLayout.jsx', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace(
'''    if (user && canAccessRoute(user, ["ADMIN", "MANAGER", "SUPERVISOR"])) {
      Promise.all([
        api("/agendas/?page_size=1000&reportable=true"),
        api("/education-reports/?page_size=1000"),
      ])
        .then(([agendasData, reportsData]) => {
          const agendas = agendasData.results || agendasData;
          const reports = reportsData.results || reportsData;
          const completedAgendaIds = new Set(reports.map((report) => String(report.agenda)));
          setPendingTechnicalReports(
            agendas.filter((agenda) => !completedAgendaIds.has(String(agenda.id))).length
          );
        });
    }''',
'''    if (user && canAccessRoute(user, ["ADMIN", "MANAGER", "SUPERVISOR"])) {
      api("/dashboard/")
        .then((data) => {
          setPendingTechnicalReports(data.pending_technical_reports_count || 0);
        })
        .catch(() => {});
    }'''
)

with open('frontend/src/components/AppLayout.jsx', 'w', encoding='utf-8') as f:
    f.write(c)
