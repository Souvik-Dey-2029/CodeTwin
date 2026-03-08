"use client";

import React, { useEffect, useState, useCallback } from "react";
import DashboardLayout from "@/components/dashboard-layout";
import StatsCard from "@/components/stats-card";
import DependencyGraph from "@/components/dependency-graph";
import RiskHeatmap from "@/components/risk-heatmap";
import { Activity, Code, FileText, AlertCircle, TrendingUp, History, Loader2, HardDrive } from "lucide-react";
import { useParams } from "next/navigation";
import { api, Repository, AnalysisStatus } from "@/lib/api";

export default function RepositoryDashboard() {
  const { id } = useParams();
  const repoId = parseInt(id as string);

  const [repo, setRepo] = useState<Repository | null>(null);
  const [status, setStatus] = useState<AnalysisStatus | null>(null);
  const [graphData, setGraphData] = useState<any>(null);
  const [heatmapData, setHeatmapData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      const [repoData, statusData, graphRes, heatmapRes] = await Promise.all([
        api.getRepository(repoId),
        api.getAnalysisStatus(repoId),
        api.getRepositoryGraph(repoId),
        api.getRepositoryHeatmap(repoId)
      ]);
      setRepo(repoData);
      setStatus(statusData);
      setGraphData(graphRes);
      setHeatmapData(heatmapRes);
    } catch (error) {
      console.error("Failed to fetch dashboard data:", error);
    } finally {
      setLoading(false);
    }
  }, [repoId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Polling logic
  useEffect(() => {
    if (!status || status.status === "Done" || status.status === "Error") return;

    const interval = setInterval(async () => {
      try {
        const statusData = await api.getAnalysisStatus(repoId);
        setStatus(statusData);
        if (statusData.status === "Done") {
          fetchData(); // Final refresh
          clearInterval(interval);
        }
      } catch (error) {
        console.error("Polling error:", error);
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [status, repoId, fetchData]);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#020617]">
        <Loader2 className="w-10 h-10 text-[#00E5FF] animate-spin" />
      </div>
    );
  }

  const repoStats = [
    { label: "Health Score", value: repo?.health_score ? `${repo.health_score}/100` : "...", icon: Activity, trend: "+2.4%", trendUp: true },
    { label: "Status", value: status?.status || "Unknown", icon: History },
    { label: "Analysis ID", value: `#${status?.id || "..."}`, icon: Code },
    { label: "Predictive Risks", value: "12", icon: AlertCircle, trend: "Stable", trendUp: true },
  ];

  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header Section */}
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-3xl font-bold text-white tracking-tight leading-tight">
              Repo: <span className="text-[#00E5FF]">{repo?.github_url.split("/").slice(-2).join("/") || "Loading..."}</span>
            </h2>
            <p className="text-slate-400 mt-2 text-lg">Predictive Refactoring Analysis for <code className="bg-slate-800 px-2 py-0.5 rounded text-[#00E5FF]">{repo?.default_branch || "main"}</code> branch</p>
          </div>
          <button className="px-6 py-3 bg-[#00E5FF] text-[#020617] font-bold rounded-xl hover:shadow-[0_0_20px_rgba(0,229,255,0.4)] transition-all flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            Simulate Refactor
          </button>
        </div>
...

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {repoStats.map((stat) => (
            <StatsCard key={stat.label} {...stat} />
          ))}
        </div>

        {/* Intelligence Layer Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-12">
            <div className="glass border border-slate-800/50 p-6 rounded-2xl">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xl font-bold text-white flex items-center gap-2">
                        <HardDrive className="w-5 h-5 text-[#00E5FF]" />
                        Architectural Force-Graph
                    </h3>
                </div>
                {graphData ? <DependencyGraph data={graphData} /> : <div className="h-[400px] flex items-center justify-center text-slate-500 italic">Processing graph...</div>}
            </div>
            
            <div className="glass border border-slate-800/50 p-6 rounded-2xl">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xl font-bold text-white flex items-center gap-2">
                        <Loader2 className="w-5 h-5 text-[#00E5FF]" />
                        Deep Analysis Profile
                    </h3>
                </div>
                <div className="space-y-4">
                    <div className="p-4 bg-slate-800/20 rounded-xl border border-[#00E5FF]/10">
                        <p className="text-[#00E5FF] font-bold text-sm mb-1 uppercase tracking-wider">Predictive Observation</p>
                        <p className="text-slate-300 italic text-sm">"The system identifies `parser.py` as an architectural hub with high betweenness centrality (0.84). This indicates it is a major bottleneck."</p>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                           <p className="text-xs text-slate-500 uppercase font-bold">Avg Centrality</p>
                           <p className="text-xl font-bold text-white">0.42</p>
                        </div>
                        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                           <p className="text-xs text-slate-500 uppercase font-bold">PageRank Score</p>
                           <p className="text-xl font-bold text-white">0.68</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        {/* Risk Hotspots Section */}
        <div className="grid grid-cols-1 gap-8 mt-8">
            <div className="glass border border-slate-800/50 p-6 rounded-2xl">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xl font-bold text-white flex items-center gap-2">
                        <AlertCircle className="w-5 h-5 text-orange-400" />
                        Intelligence Risk Treemap
                    </h3>
                    <div className="flex gap-4 text-xs">
                        <span className="flex items-center gap-1 text-slate-400"><div className="w-2 h-2 rounded bg-[#ef4444]" /> Critical</span>
                        <span className="flex items-center gap-1 text-slate-400"><div className="w-2 h-2 rounded bg-[#f59e0b]" /> Warning</span>
                        <span className="flex items-center gap-1 text-slate-400"><div className="w-2 h-2 rounded bg-[#10b981]" /> Stable</span>
                    </div>
                </div>
                {heatmapData ? <RiskHeatmap data={heatmapData} /> : <div className="h-[400px] flex items-center justify-center text-slate-500 italic">Calculating hotspots...</div>}
            </div>
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
