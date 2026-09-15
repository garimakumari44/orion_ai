import { useState } from 'react';
import { Settings as SettingsIcon, User, Bell, Database, Palette, Keyboard } from 'lucide-react';
import { cn, Divider } from '../../components/ui';

export function SettingsPage() {
  const [section, setSection] = useState('profile');
  const [notifications, setNotifications] = useState(true);
  const [autoResearch, setAutoResearch] = useState(true);
  const [streaming, setStreaming] = useState(true);

  const sections = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'data', label: 'Data & Sources', icon: Database },
    { id: 'appearance', label: 'Appearance', icon: Palette },
    { id: 'shortcuts', label: 'Keyboard Shortcuts', icon: Keyboard },
  ];

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-3xl mx-auto px-8 py-8 animate-fade-in">
        <div className="flex items-center gap-2.5 mb-1">
          <SettingsIcon className="w-5 h-5 text-text-faint" />
          <h1 className="text-xl font-semibold text-text-primary">Settings</h1>
        </div>
        <p className="text-sm text-text-muted mb-6">Manage your account, preferences, and data sources.</p>

        <div className="flex gap-8">
          <nav className="w-44 shrink-0">
            <div className="space-y-0.5">
              {sections.map((s) => {
                const Icon = s.icon;
                return (
                  <button
                    key={s.id}
                    onClick={() => setSection(s.id)}
                    className={cn(
                      'w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-md text-sm transition-colors',
                      section === s.id
                        ? 'bg-bg-hover text-text-primary'
                        : 'text-text-muted hover:text-text-secondary hover:bg-bg-hover/50',
                    )}
                  >
                    <Icon className={cn('w-3.5 h-3.5', section === s.id ? 'text-accent' : 'text-text-faint')} />
                    {s.label}
                  </button>
                );
              })}
            </div>
          </nav>

          <div className="flex-1 min-w-0">
            {section === 'profile' && (
              <div className="space-y-5 animate-fade-in">
                <div>
                  <label className="text-xs text-text-muted block mb-1.5">Display Name</label>
                  <input
                    defaultValue="John Doe"
                    className="w-full bg-bg-surface border border-border rounded-lg px-3 py-2 text-sm text-text-primary outline-none focus:border-border-hover transition-colors"
                  />
                </div>
                <div>
                  <label className="text-xs text-text-muted block mb-1.5">Email</label>
                  <input
                    defaultValue="john.doe@researchcanvas.com"
                    className="w-full bg-bg-surface border border-border rounded-lg px-3 py-2 text-sm text-text-primary outline-none focus:border-border-hover transition-colors"
                  />
                </div>
                <div>
                  <label className="text-xs text-text-muted block mb-1.5">Organization</label>
                  <input
                    defaultValue="Canvas Capital Management"
                    className="w-full bg-bg-surface border border-border rounded-lg px-3 py-2 text-sm text-text-primary outline-none focus:border-border-hover transition-colors"
                  />
                </div>
                <div>
                  <label className="text-xs text-text-muted block mb-1.5">Role</label>
                  <select className="w-full bg-bg-surface border border-border rounded-lg px-3 py-2 text-sm text-text-primary outline-none focus:border-border-hover transition-colors">
                    <option>Portfolio Manager</option>
                    <option>Equity Analyst</option>
                    <option>Research Associate</option>
                    <option>Investment Director</option>
                  </select>
                </div>
                <button className="px-4 py-2 rounded-lg bg-accent/10 border border-accent/20 text-accent text-sm font-medium hover:bg-accent/15 transition-colors">
                  Save Changes
                </button>
              </div>
            )}

            {section === 'notifications' && (
              <div className="space-y-1 animate-fade-in">
                <ToggleRow
                  label="Research Updates"
                  description="Get notified when new research is completed"
                  value={notifications}
                  onChange={setNotifications}
                />
                <Divider />
                <ToggleRow
                  label="Price Alerts"
                  description="Alert when stocks hit fair value targets"
                  value={true}
                  onChange={() => {}}
                />
                <Divider />
                <ToggleRow
                  label="News Digest"
                  description="Daily summary of relevant news for watchlist"
                  value={true}
                  onChange={() => {}}
                />
                <Divider />
                <ToggleRow
                  label="Weekly Report"
                  description="Weekly summary of research activity"
                  value={false}
                  onChange={() => {}}
                />
              </div>
            )}

            {section === 'data' && (
              <div className="space-y-1 animate-fade-in">
                <ToggleRow
                  label="Auto-Research New Companies"
                  description="Automatically start research when a new company is added"
                  value={autoResearch}
                  onChange={setAutoResearch}
                />
                <Divider />
                <ToggleRow
                  label="Streaming Updates"
                  description="Stream research progress updates in real time"
                  value={streaming}
                  onChange={setStreaming}
                />
                <Divider />
                <div className="py-3">
                  <div className="text-sm text-text-primary mb-1">Data Sources</div>
                  <div className="text-xs text-text-muted mb-3">Connected sources for research data</div>
                  <div className="space-y-2">
                    {['SEC EDGAR', 'Bloomberg API', 'Refinitiv', 'Alpha Vantage'].map((src) => (
                      <div key={src} className="flex items-center justify-between bg-bg-surface border border-border rounded-lg px-3 py-2">
                        <span className="text-sm text-text-secondary">{src}</span>
                        <span className="text-[10px] font-mono text-success uppercase tracking-wider">Connected</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {section === 'appearance' && (
              <div className="space-y-5 animate-fade-in">
                <div>
                  <label className="text-xs text-text-muted block mb-2">Theme</label>
                  <div className="flex gap-2">
                    <button className="px-3 py-2 rounded-lg bg-bg-hover border border-border text-sm text-text-primary">Dark</button>
                    <button className="px-3 py-2 rounded-lg border border-border text-sm text-text-muted hover:text-text-secondary transition-colors">System</button>
                  </div>
                </div>
                <div>
                  <label className="text-xs text-text-muted block mb-2">Accent Color</label>
                  <div className="flex gap-2">
                    {['#3B82F6', '#22C55E', '#F59E0B', '#EF4444'].map((c) => (
                      <button
                        key={c}
                        className={cn(
                          'w-8 h-8 rounded-lg border-2 transition-colors',
                          c === '#3B82F6' ? 'border-text-primary' : 'border-transparent',
                        )}
                        style={{ backgroundColor: c }}
                      />
                    ))}
                  </div>
                </div>
                <div>
                  <label className="text-xs text-text-muted block mb-2">Font Size</label>
                  <select className="bg-bg-surface border border-border rounded-lg px-3 py-2 text-sm text-text-primary outline-none focus:border-border-hover transition-colors">
                    <option>Small</option>
                    <option>Medium (Default)</option>
                    <option>Large</option>
                  </select>
                </div>
              </div>
            )}

            {section === 'shortcuts' && (
              <div className="space-y-1 animate-fade-in">
                {[
                  { keys: 'Ctrl K', action: 'Open search' },
                  { keys: 'Esc', action: 'Close modal / Cancel' },
                  { keys: 'G H', action: 'Go to Home' },
                  { keys: 'G W', action: 'Go to AI Workspace' },
                  { keys: 'G R', action: 'Go to Research' },
                  { keys: 'G L', action: 'Go to Library' },
                  { keys: 'G P', action: 'Go to Reports' },
                  { keys: '1', action: 'Overview tab' },
                  { keys: '2', action: 'Analysis tab' },
                  { keys: '3', action: 'Evidence tab' },
                  { keys: '4', action: 'Documents tab' },
                  { keys: '5', action: 'Report tab' },
                ].map((s) => (
                  <div key={s.keys} className="flex items-center justify-between py-2.5">
                    <span className="text-sm text-text-secondary">{s.action}</span>
                    <kbd className="font-mono text-xs text-text-muted bg-bg-surface border border-border px-2 py-1 rounded">
                      {s.keys}
                    </kbd>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function ToggleRow({
  label,
  description,
  value,
  onChange,
}: {
  label: string;
  description: string;
  value: boolean;
  onChange: (v: boolean) => void;
}) {
  return (
    <div className="flex items-center justify-between py-3">
      <div>
        <div className="text-sm text-text-primary">{label}</div>
        <div className="text-xs text-text-muted mt-0.5">{description}</div>
      </div>
      <button
        onClick={() => onChange(!value)}
        className={cn(
          'relative w-9 h-5 rounded-full transition-colors',
          value ? 'bg-accent' : 'bg-border',
        )}
      >
        <span
          className={cn(
            'absolute top-0.5 w-4 h-4 rounded-full bg-white transition-transform',
            value ? 'translate-x-4' : 'translate-x-0.5',
          )}
        />
      </button>
    </div>
  );
}
