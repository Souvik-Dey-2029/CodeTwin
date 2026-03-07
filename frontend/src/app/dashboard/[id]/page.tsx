import React from "react";
import DashboardLayout from "@/components/dashboard-layout";
import StatsCard from "@/components/stats-card";
import { Activity, Code, FileText, AlertCircle, TrendingUp, History } from "lucide-react";

export default function RepositoryDashboard() {
  // Mock Data (To be replaced with real API data)
  const repoStats = [
    { label: "Health Score", value: "84/100", icon: Activity, trend: "+2.4%", trendUp: true },
    { label: "Total Files", value: "1,248", icon: FileText },
    { label: "Cyclomatic Complexity", value: "A (Avg 4.2)", icon: Code, trend: "-1.1%", trendUp: true },
    { label: "Predictive Risks", value: "12", icon: AlertCircle, trend: "Stable", trendUp: true },
  ];

  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header Section */}
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-3xl font-bold text-white tracking-tight leading-tight">
              Repo: <span className="text-[#00E5FF]">facebook/react</span>
            </h2>
            <p className="text-slate-400 mt-2 text-lg">Predictive Refactoring Analysis for <code className="bg-slate-800 px-2 py-0.5 rounded text-[#00E5FF]">main</code> branch</p>
          </div>
          <button className="px-6 py-3 bg-[#00E5FF] text-[#020617] font-bold rounded-xl hover:shadow-[0_0_20px_rgba(0,229,255,0.4)] transition-all flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            Simulate Refactor
          </button>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {repoStats.map((stat) => (
            <StatsCard key={stat.label} {...stat} />
          ))}
        </div>

        {/* Content Tabs / Sections */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mt-12">
          {/* File structure / Analysis List */}
          <div className="lg:col-span-2 space-y-6">
            <div className="glass border border-slate-800/50 p-6 rounded-2xl relative overflow-hidden">
                <div className="flex items-center justify-between mb-6">
                    <h3 className="text-xl font-bold text-white">Files High-Risk Profiles</h3>
                    <button className="text-sm font-medium text-[#00E5FF]">View Map →</button>
                </div>
                
                <div className="space-y-4">
                    {[1, 2, 3].map((item) => (
                        <div key={item} className="flex items-center justify-between p-4 rounded-xl bg-slate-900/50 border border-slate-800 hover:border-slate-700 transition-all cursor-pointer group">
                             <div className="flex items-center gap-4">
                                <div className="w-10 h-10 rounded-lg bg-orange-500/10 flex items-center justify-center">
                                    <AlertCircle className="w-5 h-5 text-orange-400" />
                                </div>
                                <div>
                                    <h4 className="text-sm font-bold text-white group-hover:text-[#00E5FF] transition-colors">src/reconciler/ReactFiberWorkLoop.py</h4>
                                    <p className="text-xs text-slate-500 mt-1">High Coupling • 842 LOC • 12 dependencies</p>
                                </div>
                             </div>
                             <div className="text-right">
                                <span className="text-sm font-bold text-slate-300">Score: 82</span>
                                <div className="w-24 h-1 bg-slate-800 rounded-full mt-2">
                                    <div className="w-[82%] h-full bg-orange-400 rounded-full" />
                                </div>
                             </div>
                        </div>
                    ))}
                </div>
            </div>
          </div>

          {/* Right Sidebar / Meta info */}
          <div className="space-y-6">
            <div className="glass border border-slate-800/50 p-6 rounded-2xl">
                <h3 className="text-lg font-bold text-white mb-4">Analysis Timeline</h3>
                <div className="space-y-6">
                    <div className="flex items-start gap-3 relative">
                        <div className="w-2 h-2 rounded-full bg-[#00E5FF] mt-2 shadow-[0_0_8px_rgba(0,229,255,0.8)]" />
                        <div className="absolute left-[3px] top-4 w-px h-10 bg-slate-800" />
                        <div>
                            <p className="text-sm font-bold text-white">Latest Analysis Completed</p>
                            <p className="text-xs text-slate-500">2 minutes ago</p>
                        </div>
                    </div>
                    <div className="flex items-start gap-4">
                        <div className="w-2 h-2 rounded-full bg-slate-700 mt-2" />
                        <div>
                            <p className="text-sm font-medium text-slate-400">Deep Parsing (Phase 2)</p>
                            <p className="text-xs text-slate-500">1 hour ago</p>
                        </div>
                    </div>
                    <div className="flex items-start gap-4">
                        <div className="w-2 h-2 rounded-full bg-slate-700 mt-2" />
                        <div>
                            <p className="text-sm font-medium text-slate-400">Repository Ingested</p>
                            <p className="text-xs text-slate-500">2 hours ago</p>
                        </div>
                    </div>
                </div>
            </div>

            <div className="bg-gradient-to-br from-[#00E5FF]/10 to-transparent border border-[#00E5FF]/20 p-6 rounded-2xl">
                <h3 className="text-lg font-bold text-[#00E5FF] mb-2 flex items-center gap-2">
                    <History className="w-5 h-5" />
                    Predictive Edge
                </h3>
                <p className="text-sm text-slate-300 leading-relaxed italic">
                    "This codebase is showing early signs of structural regression in the Reconciler module. We recommend refactoring the logic in <code className="text-[#00E5FF]">ReactFiberWorkLoop.py</code> to reduce coupling."
                </p>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
