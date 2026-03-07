import React from "react";
import { LucideIcon } from "lucide-react";

interface StatsCardProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  trend?: string;
  trendUp?: boolean;
}

export default function StatsCard({ label, value, icon: Icon, trend, trendUp }: StatsCardProps) {
  return (
    <div className="glass border border-slate-800/50 p-6 rounded-2xl flex flex-col gap-4 relative overflow-hidden group">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-slate-400">{label}</span>
        <div className="w-10 h-10 rounded-xl bg-slate-800/50 flex items-center justify-center group-hover:scale-110 transition-transform">
          <Icon className="w-5 h-5 text-[#00E5FF]" />
        </div>
      </div>
      
      <div className="flex items-end justify-between">
        <span className="text-3xl font-bold text-white tracking-tight">{value}</span>
        {trend && (
          <span className={`text-xs font-semibold px-2 py-1 rounded-full ${trendUp ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'}`}>
            {trend}
          </span>
        )}
      </div>

      {/* Subtle Decorator */}
      <div className="absolute -bottom-6 -right-6 w-24 h-24 bg-[#00E5FF]/5 rounded-full blur-3xl" />
    </div>
  );
}
