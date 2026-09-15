import { LineChart } from 'lucide-react';

export default function Logo({ size = 32 }: { size?: number }) {
  return (
    <div className="flex items-center gap-2.5">
      <div
        className="flex items-center justify-center rounded-lg border border-border-default bg-surface"
        style={{ width: size, height: size }}
      >
        <LineChart className="h-5 w-5 text-accent" strokeWidth={2.25} />
      </div>
      <span className="text-base font-semibold tracking-tight text-text-primary">
        Research Canvas
      </span>
    </div>
  );
}
