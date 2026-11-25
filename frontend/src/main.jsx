
import React, { useCallback, useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity,
  AlertCircle,
  ArrowRight,
  BookOpen,
  CheckCircle2,
  ChevronDown,
  FileText,
  Headphones,
  Inbox,
  Leaf,
  Mail,
  Menu,
  RefreshCw,
  Search,
  Settings,
  ShieldCheck,
  Sparkles,
  Ticket,
  X,
  Zap,
} from "lucide-react";
import "./styles.css";

const API = "/api";

async function apiRequest(endpoint, options = {}) {
  const response = await fetch(`${API}${endpoint}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed: ${response.status}`);
  }

  return response.json();
}

function getEmailId(email) {
  return email?.id || email?.email_id || "";
}

function getSender(email) {
  return (
    email?.from?.email ||
    email?.sender_email ||
    email?.customer_email ||
    email?.from ||
    "Unknown sender"
  );
}

function getName(email) {
  return (
    email?.from?.name ||
    email?.customer_name ||
    getSender(email).split("@")[0]
  );
}

function getSubject(email) {
  return email?.subject || "No subject";
}

function getBody(email) {
  return email?.body || email?.text || email?.message || "";
}

function getResultId(result) {
  return result?.email_id || result?.id || "";
}

function getIntent(result) {
  return (
    result?.classification?.intent ||
    result?.intent ||
    "Pending"
  );
}

function getConfidence(result) {
  const value =
    result?.classification?.confidence ??
    result?.confidence ??
    0;

  return Math.round(Number(value) * 100);
}

function getAction(result) {
  if (!result) return "Not processed";

  if (result?.ticket) return "Ticket Created";
  if (result?.needs_human) return "Needs Human";
  if (result?.action_taken === "log_only") return "Logged Only";
  if (result?.action_taken === "draft_reply") return "Draft Reply";

  return result?.action_taken || "Processed";
}

function App() {
  const [page, setPage] = useState("Overview");
  const [emails, setEmails] = useState([]);
  const [results, setResults] = useState([]);
  const [tickets, setTickets] = useState([]);
  const [health, setHealth] = useState(null);
  const [selectedEmail, setSelectedEmail] = useState(null);

  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("All");
  const [mobileMenu, setMobileMenu] = useState(false);

  const loadDashboard = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const [emailData, resultData, ticketData, healthData] =
        await Promise.all([
          apiRequest("/emails"),
          apiRequest("/results"),
          apiRequest("/tickets"),
          apiRequest("/health"),
        ]);

      setEmails(emailData.emails || []);
      setResults(resultData.rows || []);
      setTickets(Array.isArray(ticketData.tickets) ? ticketData.tickets : Array.isArray(ticketData.rows) ? ticketData.rows : []);
      setHealth(healthData);
    } catch (err) {
      setError(
        `${err.message}. Check whether your FastAPI backend is running.`
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  const resultMap = useMemo(() => {
    const map = new Map();

    results.forEach((result) => {
      map.set(getResultId(result), result);
    });

    return map;
  }, [results]);

  const processedCount = results.length;

  const humanReviewCount = results.filter(
    (item) =>
      item.needs_human === true ||
      item.needs_human === "true" ||
      item.action_taken === "needs_human"
  ).length;

  const openTickets = tickets.filter(
    (ticket) => (ticket.status || "Open").toLowerCase() !== "closed"
  );

  const highPriority = tickets.filter(
    (ticket) => (ticket.priority || "").toLowerCase() === "high"
  ).length;

  const averageConfidence = processedCount
    ? Math.round(
        results.reduce((total, item) => total + getConfidence(item), 0) /
          processedCount
      )
    : 0;

  const actionCounts = {
    drafts: results.filter(
      (item) => getAction(item).toLowerCase() === "draft reply"
    ).length,
    tickets: results.filter((item) => item.ticket || item.ticket_id).length,
    human: humanReviewCount,
    logged: results.filter(
      (item) => item.action_taken === "log_only"
    ).length,
  };

  const filteredEmails = emails.filter((email) => {
    const result = resultMap.get(getEmailId(email));

    const searchText = [
      getName(email),
      getSender(email),
      getSubject(email),
      getBody(email),
      getEmailId(email),
    ]
      .join(" ")
      .toLowerCase();

    const matchesSearch = searchText.includes(search.toLowerCase());

    const action = getAction(result);
    const matchesFilter =
      filter === "All" ||
      action.toLowerCase() === filter.toLowerCase();

    return matchesSearch && matchesFilter;
  });

  async function processAllEmails() {
    if (processing) return;

    setProcessing(true);
    setError("");

    try {
      await apiRequest("/process-all", {
        method: "POST",
        body: JSON.stringify({}),
      });

      await loadDashboard();
    } catch (err) {
      setError(`Could not process emails: ${err.message}`);
    } finally {
      setProcessing(false);
    }
  }

  async function processSingleEmail(email) {
    setError("");

    try {
      await apiRequest("/process", {
        method: "POST",
        body: JSON.stringify(email),
      });

      await loadDashboard();
    } catch (err) {
      setError(`Could not process email: ${err.message}`);
    }
  }

  function navigate(destination) {
    setPage(destination);
    setMobileMenu(false);
  }

  function statusLabel(result) {
    const action = getAction(result);

    if (action === "Draft Reply") return "draft";
    if (action === "Ticket Created") return "ticket";
    if (action === "Needs Human") return "human";
    if (action === "Logged Only") return "logged";

    return "pending";
  }

  return (
    <div className="app-shell">
      <aside className={`sidebar ${mobileMenu ? "sidebar-open" : ""}`}>
        <div className="brand">
          <div className="brand-icon"><Leaf size={25} /></div>
          <div>
            <h2>kesar&co.</h2>
            <span>SUPPORT COPILOT</span>
          </div>
          <button
            className="mobile-close"
            onClick={() => setMobileMenu(false)}
            aria-label="Close menu"
          >
            <X size={20} />
          </button>
        </div>

        <div className="workspace-switch">
          <div className="workspace-letter">K</div>
          <div>
            <strong>Kesar & Co.</strong>
            <small>Customer operations</small>
          </div>
          <ChevronDown size={17} />
        </div>

        <div className="nav-label">WORKSPACE</div>

        <nav className="navigation">
          <NavItem icon={<Activity />} label="Overview" page={page} onClick={navigate} />
          <NavItem icon={<Inbox />} label="Inbox" page={page} onClick={navigate} />
          <NavItem
            icon={<Ticket />}
            label="Tickets"
            page={page}
            onClick={navigate}
            count={tickets.length}
          />

          <div className="nav-label insights-label">INSIGHTS</div>

          <NavItem icon={<FileText />} label="Audit log" page={page} onClick={navigate} />
          <NavItem icon={<BookOpen />} label="Knowledge base" page={page} onClick={navigate} />
        </nav>

        <div className="help-card">
          <div className="help-icon"><Headphones size={22} /></div>
          <strong>Need a hand?</strong>
          <p>Explore the setup guide and workflow tips.</p>
          <button onClick={() => navigate("Knowledge base")}>
            Open help center <ArrowRight size={16} />
          </button>
        </div>

        <button className="settings-link" onClick={() => navigate("Settings")}>
          <Settings size={20} /> Settings
        </button>

        <div className="profile">
          <div className="avatar">OS</div>
          <div>
            <strong>Support Admin</strong>
            <small>Workspace owner</small>
          </div>
        </div>
      </aside>

      {mobileMenu && (
        <button
          className="sidebar-overlay"
          onClick={() => setMobileMenu(false)}
          aria-label="Close navigation"
        />
      )}

      <main className="main-area">
        <header className="topbar">
          <button
            className="mobile-menu"
            onClick={() => setMobileMenu(true)}
            aria-label="Open menu"
          >
            <Menu size={22} />
          </button>

          <div className="breadcrumb">
            Workspace <span>›</span> <strong>{page}</strong>
          </div>

          <div className="topbar-right">
            <span className={`connection ${health ? "connected" : ""}`}>
              <i /> {health ? "API connected" : "API disconnected"}
            </span>
            <button className="icon-button" onClick={loadDashboard} title="Refresh data">
              <RefreshCw size={18} />
            </button>
            <div className="avatar">OS</div>
          </div>
        </header>

        <div className="content">
          {error && (
            <div className="error-banner">
              <AlertCircle size={18} />
              <span>{error}</span>
              <button onClick={() => setError("")}><X size={16} /></button>
            </div>
          )}

          {page === "Overview" && (
            <OverviewPage
              processedCount={processedCount}
              emailCount={emails.length}
              humanReviewCount={humanReviewCount}
              openTicketCount={openTickets.length}
              averageConfidence={averageConfidence}
              actionCounts={actionCounts}
              loading={loading}
              processing={processing}
              onProcess={processAllEmails}
              onNavigate={navigate}
            />
          )}

          {page === "Inbox" && (
            <InboxPage
              emails={filteredEmails}
              resultMap={resultMap}
              selectedEmail={selectedEmail}
              setSelectedEmail={setSelectedEmail}
              search={search}
              setSearch={setSearch}
              filter={filter}
              setFilter={setFilter}
              processEmail={processSingleEmail}
              statusLabel={statusLabel}
              loading={loading}
            />
          )}

          {page === "Tickets" && (
            <TicketsPage tickets={tickets} />
          )}

          {page === "Audit log" && (
            <AuditPage results={results} />
          )}

          {page === "Knowledge base" && (
            <KnowledgePage />
          )}

          {page === "Settings" && (
            <SettingsPage health={health} onRefresh={loadDashboard} />
          )}
        </div>
      </main>
    </div>
  );
}

function NavItem({ icon, label, page, onClick, count }) {
  return (
    <button
      className={`nav-item ${page === label ? "active" : ""}`}
      onClick={() => onClick(label)}
    >
      {React.cloneElement(icon, { size: 20 })}
      <span>{label}</span>
      {count > 0 && <small className="nav-count">{count}</small>}
    </button>
  );
}

function OverviewPage({
  processedCount,
  emailCount,
  humanReviewCount,
  openTicketCount,
  averageConfidence,
  actionCounts,
  loading,
  processing,
  onProcess,
  onNavigate,
}) {
  return (
    <>
      <div className="page-heading overview-heading">
        <div>
          <span className="eyebrow">ASSIGNMENT SCENARIO · SAMPLE DATA</span>
          <h1>Good evening, team 👋</h1>
          <p>Here’s what’s happening across your customer support today.</p>
        </div>

        <button className="primary-button" onClick={onProcess} disabled={processing || loading}>
          <Zap size={18} />
          {processing ? "Processing..." : "Process all emails"}
        </button>
      </div>

      <div className="welcome-banner">
        <div className="welcome-icon"><Sparkles size={23} /></div>
        <div>
          <strong>Your support copilot is ready.</strong>
          <p>Review incoming customer messages, generate grounded replies, and keep every case organized.</p>
        </div>
        <button onClick={() => onNavigate("Inbox")}>
          Go to inbox <ArrowRight size={17} />
        </button>
      </div>

      <div className="stats-grid">
        <StatCard
          label="Emails processed"
          value={loading ? "—" : processedCount}
          detail={`${emailCount} sample emails available`}
          icon={<Mail />}
          tone="green"
        />
        <StatCard
          label="Needs human review"
          value={loading ? "—" : humanReviewCount}
          detail="Requires team attention"
          icon={<Headphones />}
          tone="orange"
        />
        <StatCard
          label="Open tickets"
          value={loading ? "—" : openTicketCount}
          detail="Complaints & return requests"
          icon={<Ticket />}
          tone="blue"
        />
        <StatCard
          label="Avg. confidence"
          value={loading ? "—" : `${averageConfidence}%`}
          detail="Across processed emails"
          icon={<ShieldCheck />}
          tone="purple"
        />
      </div>

      <div className="overview-bottom">
        <section className="panel activity-panel">
          <div className="panel-heading">
            <div>
              <h3>Processing activity</h3>
              <p>Actions from the current processing run</p>
            </div>
            <span className="live-tag"><i /> Current sample run</span>
          </div>

          <div className="activity-total">
            <strong>{processedCount}</strong>
            <span>processed so far</span>
          </div>

          <div className="bar-chart">
            {[
              ["Draft replies", actionCounts.drafts],
              ["Ticket actions", actionCounts.tickets],
              ["Human review", actionCounts.human],
              ["Logged only", actionCounts.logged],
            ].map(([label, value]) => (
              <div className="bar-column" key={label}>
                <div
                  className="bar"
                  style={{
                    height: `${Math.max(
                      4,
                      processedCount ? (value / processedCount) * 100 : 0
                    )}%`,
                  }}
                  title={`${value} ${label}`}
                />
                <span>{label}: {value}</span>
              </div>
            ))}
          </div>

          <p className="chart-note">
            Counts are calculated from backend audit results, not historical analytics.
          </p>
        </section>

        <section className="panel quick-panel">
          <div className="panel-heading">
            <div>
              <h3>Quick actions</h3>
              <p>Keep your queue moving</p>
            </div>
            <Sparkles size={22} />
          </div>

          <QuickAction
            icon={<Inbox />}
            title="Review email inbox"
            description="Inspect and process customer emails"
            onClick={() => onNavigate("Inbox")}
          />
          <QuickAction
            icon={<Ticket />}
            title="Manage support tickets"
            description="Track complaints and return requests"
            onClick={() => onNavigate("Tickets")}
          />
          <QuickAction
            icon={<FileText />}
            title="View audit trail"
            description="See every processing decision"
            onClick={() => onNavigate("Audit log")}
          />
        </section>
      </div>
    </>
  );
}

function StatCard({ label, value, detail, icon, tone }) {
  return (
    <div className="stat-card">
      <div className="stat-top">
        <span>{label}</span>
        <div className={`stat-icon ${tone}`}>{icon}</div>
      </div>
      <strong className="stat-value">{value}</strong>
      <small>{detail}</small>
    </div>
  );
}

function QuickAction({ icon, title, description, onClick }) {
  return (
    <button className="quick-action" onClick={onClick}>
      <div className="quick-icon">{icon}</div>
      <div>
        <strong>{title}</strong>
        <small>{description}</small>
      </div>
      <ArrowRight size={18} />
    </button>
  );
}

function InboxPage({
  emails,
  resultMap,
  selectedEmail,
  setSelectedEmail,
  search,
  setSearch,
  filter,
  setFilter,
  processEmail,
  statusLabel,
  loading,
}) {
  const selectedResult = selectedEmail
    ? resultMap.get(getEmailId(selectedEmail))
    : null;

  return (
    <>
      <div className="page-heading">
        <div>
          <span className="eyebrow">CUSTOMER MESSAGES</span>
          <h1>Email inbox</h1>
          <p>Review customer messages and let your copilot prepare safe, policy-grounded responses.</p>
        </div>
        <span className="count-pill">{emails.length} messages shown</span>
      </div>

      <div className="inbox-layout">
        <section className="panel email-list-panel">
          <div className="email-search">
            <div className="search-box">
              <Search size={18} />
              <input
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Search emails..."
              />
            </div>
            <select value={filter} onChange={(event) => setFilter(event.target.value)}>
              <option>All</option>
              <option>Draft Reply</option>
              <option>Ticket Created</option>
              <option>Needs Human</option>
              <option>Logged Only</option>
            </select>
          </div>

          <div className="email-list">
            {loading ? (
              <EmptyState text="Loading emails..." />
            ) : emails.length === 0 ? (
              <EmptyState text="No matching emails found." />
            ) : (
              emails.map((email) => {
                const result = resultMap.get(getEmailId(email));

                return (
                  <button
                    className={`email-item ${
                      selectedEmail && getEmailId(selectedEmail) === getEmailId(email)
                        ? "selected"
                        : ""
                    }`}
                    key={getEmailId(email)}
                    onClick={() => setSelectedEmail(email)}
                  >
                    <div className="email-item-top">
                      <div className="avatar email-avatar">
                        {getName(email).slice(0, 2).toUpperCase()}
                      </div>
                      <div className="email-person">
                        <strong>{getName(email)}</strong>
                        <small>{getSender(email)}</small>
                      </div>
                      <small className="email-date">
                        {email.received_at || ""}
                      </small>
                    </div>
                    <strong className="email-subject">{getSubject(email)}</strong>
                    <p>{getBody(email).slice(0, 115)}...</p>
                    <div className="email-item-bottom">
                      <small>{getEmailId(email)}</small>
                      <span className={`status-pill ${statusLabel(result)}`}>
                        {getAction(result)}
                      </span>
                    </div>
                  </button>
                );
              })
            )}
          </div>
        </section>

        <section className="panel email-detail">
          {!selectedEmail ? (
            <EmptyState
              icon={<Mail size={27} />}
              title="Select an email"
              text="Choose a message from the inbox to review its contents and AI analysis."
            />
          ) : (
            <>
              <div className="detail-heading">
                <div>
                  <span className="eyebrow">MESSAGE DETAILS · {getEmailId(selectedEmail)}</span>
                  <h2>{getSubject(selectedEmail)}</h2>
                </div>
                <button
                  className="secondary-button"
                  onClick={() => processEmail(selectedEmail)}
                >
                  <Zap size={16} /> Process email
                </button>
              </div>

              <div className="sender-details">
                <div className="avatar">{getName(selectedEmail).slice(0, 2).toUpperCase()}</div>
                <div>
                  <strong>{getName(selectedEmail)}</strong>
                  <small>{getSender(selectedEmail)}</small>
                </div>
                <small>{selectedEmail.received_at || ""}</small>
              </div>

              <div className="message-body">{getBody(selectedEmail)}</div>

              <div className="analysis-section">
                <div className="analysis-title">
                  <div className="quick-icon"><Sparkles size={20} /></div>
                  <div>
                    <strong>Copilot analysis</strong>
                    <small>Classification and recommended action</small>
                  </div>
                </div>

                {selectedResult ? (
                  <>
                    <div className="analysis-grid">
                      <AnalysisValue label="Intent" value={getIntent(selectedResult)} />
                      <AnalysisValue label="Confidence" value={`${getConfidence(selectedResult)}%`} />
                      <AnalysisValue
                        label="Human review"
                        value={selectedResult.needs_human ? "Required" : "Not required"}
                      />
                      <AnalysisValue
                        label="Order found"
                        value={selectedResult.order_found ? "Yes" : "No"}
                      />
                    </div>

                    {selectedResult.human_reason && (
                      <div className="review-warning">
                        <AlertCircle size={18} />
                        <div>
                          <strong>Human review recommended</strong>
                          <p>{selectedResult.human_reason}</p>
                        </div>
                      </div>
                    )}

                    {selectedResult.draft_reply && (
                      <div className="draft-box">
                        <strong>AI draft reply</strong>
                        <p>{selectedResult.draft_reply}</p>
                      </div>
                    )}
                  </>
                ) : (
                  <EmptyState text="This email has not been processed yet." />
                )}
              </div>
            </>
          )}
        </section>
      </div>
    </>
  );
}

function AnalysisValue({ label, value }) {
  return (
    <div className="analysis-value">
      <small>{label}</small>
      <strong>{value ?? "—"}</strong>
    </div>
  );
}

function TicketsPage({ tickets }) {
  const [ticketFilter, setTicketFilter] = useState("All");

  const visibleTickets = tickets.filter((ticket) => {
    if (ticketFilter === "All") return true;
    return (ticket.status || "Open").toLowerCase() === ticketFilter.toLowerCase();
  });

  const openCount = tickets.filter(
    (ticket) => (ticket.status || "Open").toLowerCase() !== "closed"
  ).length;

  const highCount = tickets.filter(
    (ticket) => (ticket.priority || "").toLowerCase() === "high"
  ).length;

  return (
    <>
      <div className="page-heading">
        <div>
          <span className="eyebrow">CASE MANAGEMENT</span>
          <h1>Support tickets</h1>
          <p>A single place for customer complaints, returns, and refund requests.</p>
        </div>
        <span className="count-pill">{tickets.length} total tickets</span>
      </div>

      <div className="stats-grid ticket-stats">
        <StatCard label="All tickets" value={tickets.length} detail="Total cases" icon={<Ticket />} tone="green" />
        <StatCard label="Open" value={openCount} detail="Active cases" icon={<Activity />} tone="blue" />
        <StatCard label="High priority" value={highCount} detail="Needs attention" icon={<AlertCircle />} tone="orange" />
        <StatCard label="Closed" value={tickets.length - openCount} detail="Resolved cases" icon={<CheckCircle2 />} tone="purple" />
      </div>

      <section className="panel table-panel">
        <div className="panel-heading">
          <div>
            <h3>All support tickets</h3>
            <p>Ticket records generated by the support workflow</p>
          </div>
          <select value={ticketFilter} onChange={(e) => setTicketFilter(e.target.value)}>
            <option>All</option>
            <option>Open</option>
            <option>Closed</option>
          </select>
        </div>

        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>TICKET</th>
                <th>CUSTOMER</th>
                <th>ORDER</th>
                <th>TYPE</th>
                <th>PRIORITY</th>
                <th>STATUS</th>
                <th>UPDATED</th>
              </tr>
            </thead>
            <tbody>
              {visibleTickets.map((ticket, index) => (
                <tr key={ticket.ticket_id || index}>
                  <td>
                    <strong className="ticket-id">{ticket.ticket_id || `TKT-${index + 1}`}</strong>
                    <small>
                      {Array.isArray(ticket.email_ids)
                        ? ticket.email_ids.join(", ")
                        : typeof ticket.email_ids === "string"
                          ? ticket.email_ids.split(";").filter(Boolean).join(", ")
                          : "No linked emails"}
                    </small>
                  </td>
                  <td>{ticket.customer_email || ticket.sender_email || "—"}</td>
                  <td>{ticket.order_id || "—"}</td>
                  <td><span className="type-pill">{ticket.intent || ticket.type || "Support"}</span></td>
                  <td><span className={`priority ${String(ticket.priority || "Normal").toLowerCase()}`}>{ticket.priority || "Normal"}</span></td>
                  <td><span className="status-pill human">{ticket.status || "Open"}</span></td>
                  <td>{ticket.updated_at || ticket.created_at || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {visibleTickets.length === 0 && <EmptyState text="No tickets available." />}
        </div>
      </section>
    </>
  );
}

function AuditPage({ results }) {
  const [query, setQuery] = useState("");

  const rows = results.filter((item) =>
    [
      item.email_id,
      item.sender_email,
      item.intent,
      item.action_taken,
      item.notes,
    ]
      .join(" ")
      .toLowerCase()
      .includes(query.toLowerCase())
  );

  return (
    <>
      <div className="page-heading">
        <div>
          <span className="eyebrow">TRANSPARENCY & TRACEABILITY</span>
          <h1>Audit log</h1>
          <p>A record of email decisions, routing, and drafts created by the copilot.</p>
        </div>
        <span className="count-pill">{results.length} records</span>
      </div>

      <section className="panel table-panel">
        <div className="panel-heading">
          <div>
            <h3>Processing history</h3>
            <p>Searchable audit trail from the current run</p>
          </div>
          <div className="search-box audit-search">
            <Search size={17} />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search records..."
            />
          </div>
        </div>

        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>EMAIL ID</th>
                <th>SENDER</th>
                <th>INTENT</th>
                <th>CONFIDENCE</th>
                <th>ROUTING</th>
                <th>TICKET</th>
                <th>TIME</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((item, index) => (
                <tr key={`${item.email_id || "email"}-${index}`}>
                  <td><strong>{item.email_id || "—"}</strong></td>
                  <td>{item.sender_email || "—"}</td>
                  <td><span className="type-pill">{item.intent || "—"}</span></td>
                  <td>
                    <div className="confidence-cell">
                      <span className="confidence-track">
                        <i style={{ width: `${getConfidence(item)}%` }} />
                      </span>
                      {getConfidence(item)}%
                    </div>
                  </td>
                  <td><span className="status-pill">{item.action_taken || "—"}</span></td>
                  <td>{item.ticket_id || "—"}</td>
                  <td>{item.received_at || item.timestamp || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {rows.length === 0 && <EmptyState text="No audit records found." />}
        </div>
      </section>
    </>
  );
}

function KnowledgePage() {
  return (
    <>
      <div className="page-heading">
        <div>
          <span className="eyebrow">SUPPORT RESOURCES</span>
          <h1>Knowledge base</h1>
          <p>Reference material used by the copilot to prepare grounded responses.</p>
        </div>
      </div>

      <div className="knowledge-grid">
        <div className="panel knowledge-card">
          <div className="quick-icon"><BookOpen size={22} /></div>
          <h3>Frequently asked questions</h3>
          <p>Product, delivery, return, and refund information used during response drafting.</p>
          <span>Source: data/faq.md</span>
        </div>
        <div className="panel knowledge-card">
          <div className="quick-icon"><Leaf size={22} /></div>
          <h3>Brand voice</h3>
          <p>Guidelines for polite, clear, and customer-friendly communication.</p>
          <span>Source: data/brand_voice.md</span>
        </div>
        <div className="panel knowledge-card">
          <div className="quick-icon"><ShieldCheck size={22} /></div>
          <h3>Order and policy data</h3>
          <p>Order records and return eligibility rules used by the backend.</p>
          <span>Source: data/orders.json and policy engine</span>
        </div>
      </div>
    </>
  );
}

function SettingsPage({ health, onRefresh }) {
  return (
    <>
      <div className="page-heading">
        <div>
          <span className="eyebrow">WORKSPACE CONFIGURATION</span>
          <h1>Settings</h1>
          <p>Backend connection and application status.</p>
        </div>
      </div>
      <section className="panel settings-panel">
        <h3>Backend connection</h3>
        <p>
          Status: <strong>{health ? "Connected" : "Not connected"}</strong>
        </p>
        <p>API endpoint: <code>/api</code></p>
        <button className="primary-button" onClick={onRefresh}>
          <RefreshCw size={17} /> Check connection
        </button>
      </section>
    </>
  );
}

function EmptyState({ icon, title, text }) {
  return (
    <div className="empty-state">
      {icon && <div className="empty-icon">{icon}</div>}
      {title && <strong>{title}</strong>}
      <p>{text}</p>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);
