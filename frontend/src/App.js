import React, { useState, useRef } from "react";

function App() {
  const [file, setFile] = useState(null);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => setFile(e.target.files[0]);

  const handleFileButtonClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const formData = new FormData();
      if (file) formData.append("file", file);
      if (text) formData.append("text", text);

      const res = await fetch("http://127.0.0.1:5000/process", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error("Error:", err);
    }
    setLoading(false);
  };

  const handleDownloadReport = async () => {
    if (!result) return;
    try {
      const res = await fetch("http://127.0.0.1:5000/download_report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(result),
      });
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "compliance_report.pdf";
      a.click();
    } catch (err) {
      console.error("Download error:", err);
    }
  };

  return (
    <div
      style={{
        fontFamily: "Arial, sans-serif",
        backgroundColor: "#f9f9fb",
        minHeight: "100vh",
        padding: "2rem",
      }}
    >
      <div
        style={{
          maxWidth: "1000px",
          margin: "auto",
          background: "white",
          padding: "2rem",
          borderRadius: "10px",
          boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
        }}
      >
        <h1
          style={{
            textAlign: "center",
            marginBottom: "1.5rem",
            color: "#007bff",
          }}
        >
          Smart Compliance Copilot
        </h1>

        {/* Upload Section */}
        <div style={{ marginBottom: "1rem" }}>
          <input
            type="file"
            ref={fileInputRef}
            style={{ display: "none" }}
            onChange={handleFileChange}
          />
          <button
            onClick={handleFileButtonClick}
            style={{
              backgroundColor: "#007bff",
              color: "white",
              padding: "10px 20px",
              border: "none",
              borderRadius: "5px",
              cursor: "pointer",
              marginRight: "10px",
            }}
          >
            {file ? `📂 ${file.name}` : "Choose File"}
          </button>
        </div>

        <div style={{ marginBottom: "1rem" }}>
          <label>
            <strong>Or Enter Text:</strong>
          </label>
          <textarea
            rows="4"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste your text here..."
            style={{
              width: "100%",
              padding: "10px",
              borderRadius: "6px",
              border: "1px solid #ccc",
              marginTop: "5px",
            }}
          />
        </div>

        <button
          onClick={handleSubmit}
          disabled={loading}
          style={{
            backgroundColor: "#007bff",
            color: "white",
            padding: "10px 20px",
            border: "none",
            borderRadius: "5px",
            cursor: "pointer",
            marginRight: "10px",
          }}
        >
          {loading ? "Processing..." : "Analyze Document"}
        </button>

        {result && (
          <div style={{ marginTop: "2rem" }}>
            {/* Summary */}
            <div style={{ marginBottom: "1.5rem" }}>
              <h2 style={{ borderBottom: "2px solid #007bff", paddingBottom: "5px" }}>
                Summary
              </h2>
              <p>{result.summary}</p>
            </div>

            {/* Risk Analysis Table */}
            <div style={{ marginBottom: "1.5rem" }}>
              <h2 style={{ borderBottom: "2px solid #007bff", paddingBottom: "5px" }}>
                Risk Analysis
              </h2>
              {result.risk_analysis && result.risk_analysis.length > 0 ? (
                <div style={{ overflowX: "auto" }}>
                  <table
                    style={{
                      width: "100%",
                      borderCollapse: "collapse",
                      fontSize: "14px",
                    }}
                  >
                    <thead>
                      <tr style={{ backgroundColor: "#f2f2f2" }}>
                        <th style={{ border: "1px solid #ddd", padding: "8px" }}>Clause Number</th>
                        <th style={{ border: "1px solid #ddd", padding: "8px" }}>Clause Text</th>
                        <th style={{ border: "1px solid #ddd", padding: "8px" }}>Risk Level</th>
                        <th style={{ border: "1px solid #ddd", padding: "8px" }}>Reason</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.risk_analysis.map((r, i) => (
                        <tr
                          key={i}
                          style={{
                            backgroundColor:
                              r.risk_level === "High"
                                ? "#f8d7da"
                                : r.risk_level === "Medium"
                                ? "#fff3cd"
                                : "#d4edda",
                          }}
                        >
                          <td
                            style={{
                              border: "1px solid #ddd",
                              padding: "6px",
                              fontWeight: "bold",
                            }}
                          >
                            {r.clause_number}
                          </td>
                          <td
                            style={{
                              border: "1px solid #ddd",
                              padding: "6px",
                              textAlign: "left",
                            }}
                          >
                            {r.clause}
                          </td>
                          <td style={{ border: "1px solid #ddd", padding: "6px" }}>
                            {r.risk_level}
                          </td>
                          <td style={{ border: "1px solid #ddd", padding: "6px" }}>
                            {r.reason}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p>No structured risk data available.</p>
              )}
            </div>

            {/* Risk Counts */}
            <div style={{ marginBottom: "1.5rem" }}>
              <h2 style={{ borderBottom: "2px solid #007bff", paddingBottom: "5px" }}>
                Risk Counts
              </h2>
              <ul>
                <li>
                  <strong>High:</strong> {result.risk_counts.High}
                </li>
                <li>
                  <strong>Medium:</strong> {result.risk_counts.Medium}
                </li>
                <li>
                  <strong>Low:</strong> {result.risk_counts.Low}
                </li>
              </ul>
            </div>

            {/* Risk Chart */}
            {result.risk_chart_base64 && (
              <div style={{ marginBottom: "2rem" }}>
                <h2 style={{ borderBottom: "2px solid #007bff", paddingBottom: "5px" }}>
                  Risk Chart
                </h2>
                <img
                  alt="Risk Chart"
                  src={`data:image/png;base64,${result.risk_chart_base64}`}
                  style={{
                    maxWidth: "400px",
                    height: "auto",
                    border: "1px solid #eee",
                  }}
                />
              </div>
            )}

            {/* Divider */}
            <hr style={{ margin: "2rem 0", border: "none", borderTop: "2px solid #eee" }} />

            {/* Download Report Button */}
            <div style={{ textAlign: "center", marginTop: "1rem" }}>
              <button
                onClick={handleDownloadReport}
                style={{
                  backgroundColor: "#28a745",
                  color: "white",
                  padding: "12px 25px",
                  fontSize: "16px",
                  fontWeight: "bold",
                  border: "none",
                  borderRadius: "6px",
                  cursor: "pointer",
                  boxShadow: "0 4px 10px rgba(0,0,0,0.15)",
                }}
              >
                Download Compliance Report
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
