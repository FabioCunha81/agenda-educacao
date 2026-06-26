import os

file_path = r"d:\agenda_eventos_ols\frontend\src\pages\StatisticsPage.jsx"

content = """import { useEffect, useMemo, useState } from "react";
import { api } from "../api/client.js";

function formatNumber(value) {
  return Number(value || 0).toLocaleString("pt-BR");
}

export default function StatisticsPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  
  const [annualData, setAnnualData] = useState(null);
  const [monthlyData, setMonthlyData] = useState(null);

  const today = new Date();
  const currentYear = today.getFullYear();
  const prevYear = currentYear - 1;
  const elapsedMonths = Math.max(today.getMonth() + 1, 1);
  
  useEffect(() => {
    setLoading(true);
    setError("");
    
    // Busca do ano inteiro
    const ytdFilter = `date_from=${currentYear}-01-01&date_to=${today.toISOString().slice(0, 10)}`;
    
    // Busca do mês atual
    const firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 1).toISOString().slice(0, 10);
    const mtdFilter = `date_from=${firstDayOfMonth}&date_to=${today.toISOString().slice(0, 10)}`;
    
    Promise.all([
      api(`/education-reports/statistics/?${ytdFilter}`),
      api(`/education-reports/statistics/?${mtdFilter}`)
    ])
      .then(([ytdStats, mtdStats]) => {
        setAnnualData(ytdStats);
        setMonthlyData(mtdStats);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [currentYear]);

  const comparisonFields = [
    { key: "approach", label: "Total de abordagens" },
    { key: "approached_lectures", label: "Abordados em palestras" },
    { key: "approached_actions", label: "Abordados em ações" },
  ];
  
  const table1Data = useMemo(() => {
    if (!annualData?.comparison) return [];
    const comparisonMap = Object.fromEntries(annualData.comparison.map(item => [item.key, item]));
    
    return comparisonFields.map(field => {
      const cmp = comparisonMap[field.key] || { current: 0, previous: 0 };
      const current = cmp.current;
      const previous = cmp.previous;
      const difference = current - previous;
      const pct = previous > 0 ? (difference / previous) * 100 : (current > 0 ? 100 : 0);
      const projection = Math.round((current / elapsedMonths) * 12);
      
      return {
        ...field,
        current,
        previous,
        difference,
        percentage: pct.toFixed(1),
        projection
      };
    });
  }, [annualData, elapsedMonths]);

  const table2Data = useMemo(() => {
    if (!monthlyData?.totals) return [];
    const totalsMap = Object.fromEntries(monthlyData.totals.map(item => [item.key, Number(item.value || 0)]));
    
    return comparisonFields.map(field => ({
      ...field,
      total: totalsMap[field.key] || 0
    }));
  }, [monthlyData]);
  
  const currentMonthName = today.toLocaleDateString('pt-BR', { month: 'long' });

  return (
    <section className="page dashboard-page">
      <div className="dashboard-hero">
        <div>
          <span>Relatórios dos chefes</span>
          <h1>Estatísticas</h1>
          <p>Indicadores consolidados a partir dos relatórios técnicos.</p>
        </div>
      </div>

      {loading ? (
        <div className="dashboard-skeleton"><span /><span /><span /></div>
      ) : error ? (
        <div className="alert">Não foi possível carregar as estatísticas: {error}</div>
      ) : (
        <>
          <div className="chart-card comparison-board-card" style={{ marginBottom: 32 }}>
            <div className="section-heading">
              <div>
                <h2>Comparação {currentYear} vs {prevYear}</h2>
                <p>Análise de abordagens no período e projeção para o final do ano.</p>
              </div>
            </div>
            <div className="target-table-wrap">
              <table className="target-table comparison-table">
                <thead>
                  <tr>
                    <th>Indicador</th>
                    <th>{prevYear} (Total)</th>
                    <th>{currentYear} (Acumulado)</th>
                    <th>Diferença</th>
                    <th>Variação %</th>
                    <th>Projeção {currentYear}</th>
                  </tr>
                </thead>
                <tbody>
                  {table1Data.map((row) => {
                    const pct = Number(row.percentage);
                    const pctLabel = pct > 0 ? `+${pct}%` : `${pct}%`;
                    const pctClass = pct > 0 ? "pct-up" : pct < 0 ? "pct-down" : "pct-neutral";
                    return (
                      <tr key={row.key}>
                        <td><strong>{row.label}</strong></td>
                        <td>{formatNumber(row.previous)}</td>
                        <td>{formatNumber(row.current)}</td>
                        <td>{formatNumber(row.difference)}</td>
                        <td><span className={`pct-badge ${pctClass}`}>{pctLabel}</span></td>
                        <td>{formatNumber(row.projection)}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          <div className="chart-card target-board-card">
            <div className="section-heading">
              <div>
                <h2 style={{ textTransform: 'capitalize' }}>Resultados de {currentMonthName}</h2>
                <p>Indicadores registrados somente no mês atual.</p>
              </div>
            </div>
            <div className="target-table-wrap">
              <table className="target-table">
                <thead>
                  <tr>
                    <th>Indicador</th>
                    <th>Total Mês Vigente</th>
                  </tr>
                </thead>
                <tbody>
                  {table2Data.map((row) => (
                    <tr key={row.key}>
                      <td><strong>{row.label}</strong></td>
                      <td style={{ fontSize: 16, fontWeight: 700, color: 'var(--primary)' }}>{formatNumber(row.total)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </section>
  );
}
"""

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated StatisticsPage.jsx")
