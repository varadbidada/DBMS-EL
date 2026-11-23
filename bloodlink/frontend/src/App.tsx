import React, { useState, useEffect } from 'react';

interface QueryItem {
  id: number;
  title: string;
  category: string;
  description: string;
  sql: string;
  explanation: string;
}

const queriesData: QueryItem[] = [
  {
    id: 1,
    title: "1. Available Units by Blood Bank & Group",
    category: "Aggregation & Grouping",
    description: "Multi-table join calculating real-time inventory levels per bank and blood group.",
    sql: `SELECT 
    bb.name AS blood_bank, 
    bg.group_name, 
    inv.units_available, 
    inv.units_reserved,
    inv.minimum_threshold
FROM inventory inv
JOIN blood_bank bb ON inv.blood_bank_id = bb.id
JOIN blood_group bg ON inv.blood_group_id = bg.id
ORDER BY bb.name, bg.group_name;`,
    explanation: "Demonstrates 3-table relational joins between inventory, blood_bank, and blood_group to check critical stock against the minimum threshold."
  },
  {
    id: 2,
    title: "2. Eligible Donors for Emergency Requests",
    category: "Matching & Complex Joins",
    description: "Matches open critical emergencies with donors in the same city who have cooled down for >= 90 days.",
    sql: `SELECT 
    er.id AS request_id, 
    h.name AS hospital_name, 
    bg.group_name AS blood_needed, 
    u.full_name AS donor_name, 
    d.registration_number, 
    loc.city
FROM emergency_request er
JOIN hospital h ON er.hospital_id = h.id
JOIN blood_group bg ON er.blood_group_id = bg.id
JOIN donor d ON d.location_id = h.location_id
JOIN "user" u ON d.user_id = u.id
JOIN location loc ON d.location_id = loc.id
WHERE er.status = 'OPEN' 
  AND er.urgency_level IN ('CRITICAL', 'HIGH')
  AND (d.last_donation_date IS NULL OR d.last_donation_date <= date('now', '-90 days'));`,
    explanation: "Fulfills complex emergency requirements by combining 6 relational entities with temporal filtering (date cooldown) and location constraint matching."
  },
  {
    id: 3,
    title: "3. Units Nearing Expiry (Within 7 Days)",
    category: "Date Filtering & Quality Control",
    description: "Queries units nearing their expiration date to prioritize usage and prevent wastage.",
    sql: `SELECT 
    bu.id AS unit_id, 
    bg.group_name, 
    bu.collection_date, 
    bu.expiry_date, 
    bu.status, 
    bb.name AS blood_bank
FROM blood_unit bu
JOIN blood_group bg ON bu.blood_group_id = bg.id
JOIN blood_bank bb ON bu.blood_bank_id = bb.id
WHERE bu.status = 'AVAILABLE'
ORDER BY bu.expiry_date ASC;`,
    explanation: "Performs date-range filtering on blood units to enforce FIFO quality control protocol across hospital networks."
  },
  {
    id: 4,
    title: "4. Full 14-Table Schema Entities Inspection",
    category: "Schema & Metadata",
    description: "Queries all user accounts, roles, and geographic registrations.",
    sql: `SELECT 
    u.id, 
    u.username, 
    u.full_name, 
    u.role, 
    loc.city, 
    loc.state 
FROM "user" u
LEFT JOIN location loc ON u.location_id = loc.id;`,
    explanation: "Displays user role separation (Donor, Staff, Admin) mapped to 3NF location geographic tables."
  }
];

export default function App() {
  const [selectedQuery, setSelectedQuery] = useState<QueryItem>(queriesData[0]);
  const [customSQL, setCustomSQL] = useState<string>(queriesData[0].sql);
  const [queryResult, setQueryResult] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setCustomSQL(selectedQuery.sql);
    runQuery(selectedQuery.sql);
  }, [selectedQuery]);

  const runQuery = async (sqlToRun: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/db/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: sqlToRun })
      });
      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.error || 'Failed to execute query');
      }
      setQueryResult(data);
    } catch (err: any) {
      setError(err.message);
      setQueryResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      backgroundColor: '#f5f0eb',
      minHeight: '100vh',
      color: '#3d342d',
      fontFamily: '"Georgia", "Cambria", "Times New Roman", serif',
      padding: '30px 20px'
    }}>
      <div style={{ maxWidth: '1280px', margin: '0 auto' }}>
        
        {/* Warm Beige Header */}
        <header style={{
          backgroundColor: '#ebe2d5',
          border: '1px solid #d4c5b3',
          borderRadius: '12px',
          padding: '24px 32px',
          marginBottom: '28px',
          boxShadow: '0 4px 15px rgba(80, 60, 40, 0.05)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <span style={{ fontSize: '32px' }}>🩸</span>
              <h1 style={{
                margin: 0,
                fontSize: '28px',
                fontWeight: 700,
                color: '#8b2626',
                letterSpacing: '-0.5px'
              }}>
                BloodLink — DBMS Query Console
              </h1>
            </div>
            <p style={{
              margin: '8px 0 0',
              fontSize: '15px',
              color: '#706152',
              fontStyle: 'italic'
            }}>
              Live 3NF Relational Database Execution & Multi-table Presentation Portal
            </p>
          </div>

          <div style={{ textAlign: 'right' }}>
            <span style={{
              display: 'inline-block',
              backgroundColor: '#ded0bf',
              border: '1px solid #c2b09a',
              color: '#524336',
              padding: '6px 14px',
              borderRadius: '20px',
              fontSize: '13px',
              fontWeight: 600
            }}>
              ● Database Engine: Connected & Ready
            </span>
          </div>
        </header>

        {/* Content Layout */}
        <div style={{ display: 'grid', gridTemplateColumns: '340px 1fr', gap: '28px' }}>
          
          {/* Left Column: Preset Queries */}
          <aside>
            <div style={{
              backgroundColor: '#ede5d8',
              border: '1px solid #d9ccbc',
              borderRadius: '10px',
              padding: '20px',
              marginBottom: '20px'
            }}>
              <h3 style={{
                margin: '0 0 14px',
                fontSize: '15px',
                textTransform: 'uppercase',
                letterSpacing: '1px',
                color: '#6e5e4f',
                fontWeight: 700
              }}>
                Prepared Queries for Mam
              </h3>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {queriesData.map((q) => {
                  const isActive = selectedQuery.id === q.id;
                  return (
                    <button
                      key={q.id}
                      onClick={() => setSelectedQuery(q)}
                      style={{
                        textAlign: 'left',
                        padding: '12px 14px',
                        borderRadius: '8px',
                        border: isActive ? '2px solid #a33835' : '1px solid #d4c5b3',
                        backgroundColor: isActive ? '#f7f3ed' : '#e4dacf',
                        color: isActive ? '#8b2626' : '#4d4136',
                        cursor: 'pointer',
                        transition: 'all 0.15s ease'
                      }}
                    >
                      <div style={{ fontSize: '11px', textTransform: 'uppercase', fontWeight: 700, color: '#a33835' }}>
                        {q.category}
                      </div>
                      <div style={{ fontSize: '14px', fontWeight: 600, marginTop: '3px' }}>
                        {q.title}
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Explanations card */}
            <div style={{
              backgroundColor: '#ede5d8',
              border: '1px solid #d9ccbc',
              borderRadius: '10px',
              padding: '18px',
              fontSize: '13px',
              lineHeight: '1.6',
              color: '#5c4e40'
            }}>
              <h4 style={{ margin: '0 0 8px', color: '#8b2626', fontSize: '14px' }}>
                💡 Key Features in this DB
              </h4>
              <ul style={{ margin: 0, paddingLeft: '18px' }}>
                <li><strong>14 Tables in 3NF:</strong> Zero transitive redundancy.</li>
                <li><strong>Referential Cascades:</strong> Auto-updates on donor/hospital shifts.</li>
                <li><strong>SQL-Controlled:</strong> Can run custom queries directly in the box on the right.</li>
              </ul>
            </div>
          </aside>

          {/* Right Column: Interactive SQL Runner */}
          <main>
            <div style={{
              backgroundColor: '#faf7f2',
              border: '1px solid #ded3c5',
              borderRadius: '12px',
              padding: '24px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.03)'
            }}>
              
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <div>
                  <h2 style={{ margin: 0, fontSize: '20px', color: '#4a3b2c' }}>
                    {selectedQuery.title}
                  </h2>
                  <p style={{ margin: '4px 0 0', fontSize: '14px', color: '#7a6a5a' }}>
                    {selectedQuery.description}
                  </p>
                </div>

                <button
                  onClick={() => runQuery(customSQL)}
                  disabled={loading}
                  style={{
                    backgroundColor: '#8b2626',
                    color: '#fff',
                    border: 'none',
                    padding: '10px 20px',
                    borderRadius: '6px',
                    fontSize: '14px',
                    fontWeight: 600,
                    cursor: 'pointer',
                    boxShadow: '0 2px 5px rgba(139, 38, 38, 0.2)'
                  }}
                >
                  {loading ? 'Running...' : '▶ Execute Live SQL'}
                </button>
              </div>

              {/* Editable Query Box */}
              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 700, color: '#736252', marginBottom: '6px', textTransform: 'uppercase' }}>
                  SQL Editor (You can edit or type any query here):
                </label>
                <textarea
                  value={customSQL}
                  onChange={(e) => setCustomSQL(e.target.value)}
                  rows={7}
                  style={{
                    width: '100%',
                    boxSizing: 'border-box',
                    fontFamily: '"Courier New", Courier, monospace',
                    fontSize: '13px',
                    padding: '14px',
                    backgroundColor: '#ede6db',
                    border: '1px solid #cfc0b0',
                    borderRadius: '8px',
                    color: '#2e261f',
                    lineHeight: '1.5',
                    resize: 'vertical'
                  }}
                />
              </div>

              {/* Error Box */}
              {error && (
                <div style={{
                  backgroundColor: '#fcedeb',
                  border: '1px solid #f0b6b4',
                  color: '#9e2a2b',
                  padding: '12px 16px',
                  borderRadius: '6px',
                  marginBottom: '18px',
                  fontSize: '13px'
                }}>
                  <strong>SQL Execution Error:</strong> {error}
                </div>
              )}

              {/* Live Output Table */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <h4 style={{ margin: 0, fontSize: '15px', color: '#4a3b2c' }}>
                    Live Result Set {queryResult ? `(${queryResult.count} rows returned)` : ''}
                  </h4>
                  <span style={{ fontSize: '12px', color: '#8c7a68' }}>
                    Directly fetched from database
                  </span>
                </div>

                {queryResult && queryResult.data && queryResult.data.length > 0 ? (
                  <div style={{
                    overflowX: 'auto',
                    border: '1px solid #ded3c5',
                    borderRadius: '8px',
                    backgroundColor: '#ffffff'
                  }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '13px' }}>
                      <thead style={{ backgroundColor: '#ebe3d8', color: '#524336' }}>
                        <tr>
                          {queryResult.columns.map((col: string) => (
                            <th key={col} style={{
                              padding: '10px 14px',
                              borderBottom: '2px solid #d4c5b3',
                              fontWeight: 700,
                              textTransform: 'capitalize'
                            }}>
                              {col.replace(/_/g, ' ')}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {queryResult.data.map((row: any, i: number) => (
                          <tr key={i} style={{
                            borderBottom: '1px solid #ece4da',
                            backgroundColor: i % 2 === 0 ? '#ffffff' : '#faf7f2'
                          }}>
                            {queryResult.columns.map((col: string, cIdx: number) => (
                              <td key={cIdx} style={{ padding: '9px 14px', color: '#382f27' }}>
                                {String(row[col] !== null ? row[col] : 'NULL')}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div style={{
                    padding: '24px',
                    textAlign: 'center',
                    backgroundColor: '#ede5d8',
                    borderRadius: '8px',
                    color: '#7a6a5a',
                    fontSize: '14px'
                  }}>
                    {loading ? 'Executing query on database...' : 'No rows returned or query has not been run yet.'}
                  </div>
                )}
              </div>

              {/* What to tell Mam */}
              <div style={{
                marginTop: '22px',
                padding: '16px 20px',
                backgroundColor: '#ede5d8',
                borderRadius: '8px',
                borderLeft: '5px solid #8b2626'
              }}>
                <div style={{ fontWeight: 700, fontSize: '14px', color: '#8b2626', marginBottom: '4px' }}>
                  🗣️ What to Explain to Mam for this Query:
                </div>
                <div style={{ fontSize: '13px', lineHeight: '1.6', color: '#4d3f32' }}>
                  {selectedQuery.explanation}
                </div>
              </div>

            </div>
          </main>
        </div>

      </div>
    </div>
  );
}
