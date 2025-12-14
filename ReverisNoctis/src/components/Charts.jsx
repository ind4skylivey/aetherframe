import {
    Bar,
    BarChart,
    CartesianGrid,
    Cell,
    Legend,
    Line,
    LineChart,
    Pie,
    PieChart,
    PolarAngleAxis,
    PolarGrid,
    PolarRadiusAxis,
    Radar,
    RadarChart,
    ResponsiveContainer,
    Tooltip,
    XAxis, YAxis
} from 'recharts';

// Severity Distribution Pie Chart
export function SeverityDistribution({ findings }) {
  if (!findings || findings.length === 0) return null;

  const severityCount = findings.reduce((acc, finding) => {
    acc[finding.severity] = (acc[finding.severity] || 0) + 1;
    return acc;
  }, {});

  const data = Object.entries(severityCount).map(([severity, count]) => ({
    name: severity,
    value: count,
  }));

  const COLORS = {
    critical: '#ff3366',
    high: '#ff6b6b',
    medium: '#ffd93d',
    low: '#6bcf7f',
    info: '#6af0ff',
  };

  return (
    <div className="chart-container">
      <h3 className="chart-title">Severity Distribution</h3>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, value }) => `${name}: ${value}`}
            outerRadius={100}
            fill="#8884d8"
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[entry.name]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: '#0c1324',
              border: '1px solid #1b2640',
              borderRadius: '8px',
            }}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

// Category Breakdown Bar Chart
export function CategoryBreakdown({ findings }) {
  if (!findings || findings.length === 0) return null;

  const categoryCount = findings.reduce((acc, finding) => {
    acc[finding.category] = (acc[finding.category] || 0) + 1;
    return acc;
  }, {});

  const data = Object.entries(categoryCount).map(([category, count]) => ({
    category: category.replace(/_/g, ' '),
    count,
  }));

  return (
    <div className="chart-container">
      <h3 className="chart-title">Findings by Category</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1b2640" />
          <XAxis
            dataKey="category"
            stroke="#9fb0d0"
            tick={{ fill: '#9fb0d0' }}
            angle={-15}
            textAnchor="end"
            height={80}
          />
          <YAxis stroke="#9fb0d0" tick={{ fill: '#9fb0d0' }} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#0c1324',
              border: '1px solid #1b2640',
              borderRadius: '8px',
            }}
          />
          <Bar dataKey="count" fill="#6af0ff" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

// Job Timeline Chart
export function JobTimeline({ jobs }) {
  if (!jobs || jobs.length === 0) return null;

  // Group jobs by date
  const jobsByDate = jobs.reduce((acc, job) => {
    const date = new Date(job.created_at).toLocaleDateString();
    if (!acc[date]) {
      acc[date] = { date, total: 0, completed: 0, failed: 0, running: 0 };
    }
    acc[date].total++;
    acc[date][job.status]++;
    return acc;
  }, {});

  const data = Object.values(jobsByDate).sort((a, b) =>
    new Date(a.date) - new Date(b.date)
  );

  return (
    <div className="chart-container">
      <h3 className="chart-title">Job Execution Timeline</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1b2640" />
          <XAxis dataKey="date" stroke="#9fb0d0" tick={{ fill: '#9fb0d0' }} />
          <YAxis stroke="#9fb0d0" tick={{ fill: '#9fb0d0' }} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#0c1324',
              border: '1px solid #1b2640',
              borderRadius: '8px',
            }}
          />
          <Legend />
          <Line type="monotone" dataKey="total" stroke="#6af0ff" strokeWidth={2} />
          <Line type="monotone" dataKey="completed" stroke="#22c55e" strokeWidth={2} />
          <Line type="monotone" dataKey="failed" stroke="#f87171" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

// Threat Radar Chart
export function ThreatRadar({ findings }) {
  if (!findings || findings.length === 0) return null;

  const categories = [
    'anti_debug',
    'anti_vm',
    'anti_frida',
    'packing',
    'timing_check',
    'obfuscation',
  ];

  const categoryScores = categories.map((category) => {
    const categoryFindings = findings.filter((f) => f.category === category);
    const score = categoryFindings.reduce((sum, f) => {
      const severityWeight = {
        critical: 100,
        high: 75,
        medium: 50,
        low: 25,
        info: 10,
      };
      return sum + (severityWeight[f.severity] || 0) * f.confidence;
    }, 0);

    return {
      category: category.replace(/_/g, ' '),
      score: Math.min(score, 100),
    };
  });

  return (
    <div className="chart-container">
      <h3 className="chart-title">Threat Vector Analysis</h3>
      <ResponsiveContainer width="100%" height={350}>
        <RadarChart data={categoryScores}>
          <PolarGrid stroke="#1b2640" />
          <PolarAngleAxis dataKey="category" stroke="#9fb0d0" tick={{ fill: '#9fb0d0' }} />
          <PolarRadiusAxis stroke="#9fb0d0" tick={{ fill: '#9fb0d0' }} />
          <Radar
            name="Threat Score"
            dataKey="score"
            stroke="#ff3366"
            fill="#ff3366"
            fillOpacity={0.6}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#0c1324',
              border: '1px solid #1b2640',
              borderRadius: '8px',
            }}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}

// Risk Score Trend
export function RiskScoreTrend({ jobs }) {
  if (!jobs || jobs.length === 0) return null;

  const jobsWithRisk = jobs
    .filter((j) => j.meta?.risk_score !== undefined)
    .map((j) => ({
      id: j.id,
      risk: (j.meta.risk_score * 100).toFixed(0),
      date: new Date(j.created_at).toLocaleDateString(),
    }))
    .reverse();

  if (jobsWithRisk.length === 0) return null;

  return (
    <div className="chart-container">
      <h3 className="chart-title">Risk Score Trend</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={jobsWithRisk}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1b2640" />
          <XAxis dataKey="id" stroke="#9fb0d0" tick={{ fill: '#9fb0d0' }} label={{ value: 'Job ID', fill: '#9fb0d0' }} />
          <YAxis stroke="#9fb0d0" tick={{ fill: '#9fb0d0' }} domain={[0, 100]} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#0c1324',
              border: '1px solid #1b2640',
              borderRadius: '8px',
            }}
          />
          <Line
            type="monotone"
            dataKey="risk"
            stroke="#ff3366"
            strokeWidth={3}
            dot={{ fill: '#ff3366', r: 5 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

// Confidence Score Distribution
export function ConfidenceDistribution({ findings }) {
  if (!findings || findings.length === 0) return null;

  const ranges = [
    { range: '0-20%', min: 0, max: 0.2 },
    { range: '20-40%', min: 0.2, max: 0.4 },
    { range: '40-60%', min: 0.4, max: 0.6 },
    { range: '60-80%', min: 0.6, max: 0.8 },
    { range: '80-100%', min: 0.8, max: 1.0 },
  ];

  const data = ranges.map(({ range, min, max }) => ({
    range,
    count: findings.filter((f) => f.confidence >= min && f.confidence < max).length,
  }));

  return (
    <div className="chart-container">
      <h3 className="chart-title">Confidence Distribution</h3>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1b2640" />
          <XAxis dataKey="range" stroke="#9fb0d0" tick={{ fill: '#9fb0d0' }} />
          <YAxis stroke="#9fb0d0" tick={{ fill: '#9fb0d0' }} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#0c1324',
              border: '1px solid #1b2640',
              borderRadius: '8px',
            }}
          />
          <Bar dataKey="count" fill="#9efc4f" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
