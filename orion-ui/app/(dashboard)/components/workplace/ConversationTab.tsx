import { useState, useRef, useEffect } from 'react';
import { ArrowUp, RotateCcw, FileText, ExternalLink, Sparkles } from 'lucide-react';
import { cn } from '../../components/ui';
import type { ChatMessage, SuggestedQuestion } from "@/types";

interface ConversationTabProps {
  messages: ChatMessage[];
  suggestedQuestions: SuggestedQuestion[];
}

function MessageContent({ content }: { content: string }) {
  const lines = content.split('\n');
  return (
    <div className="space-y-2">
      {lines.map((line, i) => {
        if (line.trim() === '') return <div key={i} className="h-1" />;
        const numbered = /^\d+\.\s/.test(line);
        const boldMatch = line.match(/\*\*(.+?)\*\*/);
        if (boldMatch) {
          const parts = line.split(/\*\*(.+?)\*\*/);
          return (
            <p key={i} className={cn('text-sm leading-relaxed', numbered ? 'pl-4' : '')}>
              {parts.map((part, j) =>
                j % 2 === 1 ? (
                  <span key={j} className="font-semibold text-text-primary">{part}</span>
                ) : (
                  <span key={j} className="text-text-secondary">{part}</span>
                ),
              )}
            </p>
          );
        }
        return (
          <p key={i} className={cn('text-sm leading-relaxed text-text-secondary', numbered ? 'pl-4' : '')}>
            {line}
          </p>
        );
      })}
    </div>
  );
}

function MessageTable({
  title,
  rows,
}: {
  title: string;
  rows: string[][];
}) {
  return (
    <div className="mt-3">
      <div className="mb-2 text-[10px] font-mono uppercase tracking-wider text-text-faint">
        {title}
      </div>

      <div className="overflow-hidden rounded-lg border border-border">
        <table className="w-full border-collapse">
          <thead className="bg-bg-elevated">
            <tr>
              <th className="border-b border-border px-4 py-2 text-left text-xs font-semibold text-text-primary">
                Metric
              </th>
              <th className="border-b border-border px-4 py-2 text-left text-xs font-semibold text-text-primary">
                Value
              </th>
            </tr>
          </thead>

          <tbody>
            {rows.map((row, index) => (
              <tr
                key={`${row[0]}-${index}`}
                className="border-b border-border last:border-b-0"
              >
                <td className="px-4 py-2 text-sm text-text-secondary">
                  {row[0]}
                </td>

                <td className="px-4 py-2 text-sm font-medium text-text-primary">
                  {row[1]}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function ConversationTab({ messages, suggestedQuestions }: ConversationTabProps) {
  const [input, setInput] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="flex flex-col h-full">
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-6 py-6">
        <div className="max-w-3xl mx-auto space-y-6">
          {messages.map((msg) => (
            <div key={msg.id} className={cn('flex gap-3', msg.role === 'user' ? 'justify-end' : 'justify-start')}>
              {msg.role === 'assistant' && (
                <div className="w-7 h-7 rounded-lg bg-accent/10 border border-accent/20 flex items-center justify-center shrink-0 mt-0.5">
                  <Sparkles className="w-3.5 h-3.5 text-accent" />
                </div>
              )}
              <div className={cn('max-w-[80%]', msg.role === 'user' ? 'order-2' : '')}>
                {msg.role === 'user' ? (
                  <div className="bg-bg-hover rounded-lg px-4 py-2.5">
                    <p className="text-sm text-text-primary">{msg.content}</p>
                  </div>
                ) : (
                  <div className="bg-bg-surface border border-border rounded-lg px-4 py-3.5">
                    <MessageContent content={msg.content} />
                    {msg.tables?.map((t, i) => (
                      <MessageTable key={i} title={`Table ${i + 1}`} rows={t.rows} />
                    ))}
                    {msg.citations && msg.citations.length > 0 && (
                      <div className="flex items-center gap-2 mt-3 pt-3 border-t border-border-subtle">
                        <FileText className="w-3 h-3 text-text-faint" />
                        <span className="text-[10px] text-text-faint uppercase tracking-wider font-mono">Citations</span>
                        <div className="flex items-center gap-1.5">
                          {msg.citations.map((c, i) => (
                            <span
                              key={i}
                              className="inline-flex items-center gap-1 text-[11px] text-text-muted bg-bg-elevated border border-border rounded px-1.5 py-0.5"
                            >
                              {c.title ?? c.source ?? `Source ${i + 1}`}
                              <span className="text-text-faint">Â· {c.source}</span>
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
                <div className={cn('flex items-center gap-2 mt-1 px-1', msg.role === 'user' ? 'justify-end' : '')}>
                  <span className="text-[10px] text-text-faint font-mono">{msg.timestamp}</span>
                  {msg.role === 'assistant' && (
                    <button className="flex items-center gap-1 text-[10px] text-text-faint hover:text-text-muted transition-colors">
                      <RotateCcw className="w-2.5 h-2.5" />
                      Regenerate
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="border-t border-border px-6 py-4">
        <div className="max-w-3xl mx-auto">
          {suggestedQuestions.length > 0 && (
            <div className="flex items-center gap-2 mb-3 overflow-x-auto scrollbar-none">
              {suggestedQuestions.map((q) => (
                <button
                  key={q.id}
                  onClick={() => setInput(q.text)}
                  className="shrink-0 text-xs text-text-muted bg-bg-surface border border-border rounded-full px-3 py-1 hover:border-border-hover hover:text-text-secondary transition-colors"
                >
                  {q.text}
                </button>
              ))}
            </div>
          )}
          <div className="flex items-center gap-2 bg-bg-surface border border-border rounded-lg px-3 py-2.5 focus-within:border-border-hover transition-colors">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a follow-up question..."
              className="flex-1 bg-transparent text-sm text-text-primary placeholder:text-text-faint outline-none"
            />
            <button
              disabled={!input.trim()}
              className="w-7 h-7 flex items-center justify-center rounded-md bg-accent text-white disabled:opacity-30 disabled:cursor-not-allowed hover:bg-accent-hover transition-colors"
            >
              <ArrowUp className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}


