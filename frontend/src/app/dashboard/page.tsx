"use client";

import React, { useEffect, useState, useCallback } from "react";
import DashboardLayout from "@/components/dashboard-layout";
import StatsCard from "@/components/stats-card";
import DependencyGraph from "@/components/dependency-graph";
import RiskHeatmap from "@/components/risk-heatmap";
import RefactorAdvisor from "@/components/refactor-advisor";
import { Activity, Code, AlertCircle, TrendingUp, History, Loader2, HardDrive, Zap, RefreshCw, Clock } from "lucide-react";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";
import { api, Repository, AnalysisStatus } from "@/lib/api";

function DashboardContent() {
  const searchParams = useSearchParams();
  const id = searchParams.get("id");
  const repoId = id ? parseInt(id) : 1;

  const [repo, setRepo] = useState<Repository | null>(null);
  const [summary, setSummary] = useState<any>(null);
  const [status, setStatus] = useState<AnalysisStatus | null>(null);
  const [graphData, setGraphData] = useState<any>(null);
  const [heatmapData, setHeatmapData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [isReanalyzing, setIsReanalyzing] = useState(false);

  const fetchData = useCallback(async () => {
    try {
      const [repoData, summaryData, statusData, graphRes, heatmapRes] = await Promise.all([
        api.getRepository(repoId),
        api.getDashboardSummary(repoId),
        api.getAnalysisStatus(repoId),
        api.getRepositoryGraph(repoId),
        api.getRepositoryHeatmap(repoId)
      ]);
      setRepo(repoData);
      setSummary(summaryData);
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
          fetchData();
          clearInterval(interval);
        }
      } catch (error) {
        console.error("Polling error:", error);
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [status, repoId, fetchData]);

  const handleReanalyze = async () => {
    setIsReanalyzing(true);
    try {
      await api.reanalyzeRepository(repoId);
      // Set status to queue to trigger polling
      setStatus({ id: 0, repo_id: repoId, status: "Queue" });
      setLoading(true);
      // Wait a moment then start polling
      setTimeout(() => {
        setLoading(false);
      }, 2000);
    } catch (error) {
      console.error("Reanalysis failed:", error);
    } finally {
      setIsReanalyzing(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#020617]">
        <div className="text-center space-y-4">
          <Loader2 className="w-10 h-10 text-[#00E5FF] animate-spin mx-auto" />
          <p className="text-slate-400 text-sm animate-pulse">Building Digital Twin...</p>
        </div>
      </div>
    );
  }

  // Compute derived metrics
  const avgCentrality = graphData?.nodes?.length
    ? (graphData.nodes.reduce((acc: number, n: any) => acc + (n.centrality || 0), 0) / graphData.nodes.length).toFixed(2)
    : "0.00";

  const topNode = graphData?.nodes?.length
    ? [...graphData.nodes].sort((a: any, b: any) => (b.centrality || 0) - (a.centrality || 0))[0]
    : null;

  const repoStats = [
    { label: "Health Score", value: summary ? `${summary.health_score}/100` : "...", icon: Activity, trend: summary?.risk_level || "...", trendUp: summary?.risk_level === "Low" },
    { label: "Status", value: summary?.status || status?.status || "Unknown", icon: Clock },
    { label: "Architectural Debt", value: summary ? `${summary.god_object_count} God Objects` : "...", icon: Zap, trend: summary?.risk_level === "High" ? "Critical" : "Stable", trendUp: summary?.risk_level !== "High" },
    { label: "System Size", value: summary ? `${summary.total_files} Files` : "...", icon: Code },
  ];

  return (
    <DashboardLayout>
      <div id="overview" className="max-w-7xl mx-auto space-y-8">
        {/* Header Section */}
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div>
            <h2 className="text-3xl font-bold text-white tracking-tight leading-tight">
              Repo: <span className="text-[#00E5FF]">{repo?.github_url.split("/").slice(-2).join("/") || "Loading..."}</span>
            </h2>
            <p className="text-slate-400 mt-2 text-lg">Predictive Refactoring Analysis for <code className="bg-slate-800 px-2 py-0.5 rounded text-[#00E5FF]">{repo?.default_branch || "main"}</code> branch</p>
          </div>
          <div className="flex items-center gap-3">
            <button 
              onClick={handleReanalyze}
              disabled={isReanalyzing || status?.status === "Active" || status?.status === "Queue"}
              className="px-4 py-3 bg-slate-800 text-slate-300 font-semibold rounded-xl hover:bg-slate-700 transition-all flex items-center gap-2 border border-slate-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <RefreshCw className={`w-4 h-4 ${isReanalyzing ? "animate-spin" : ""}`} />
              Re-analyze
            </button>
            <button 
              onClick={() => document.getElementById('refactor-section')?.scrollIntoView({ behavior: 'smooth' })}
              className="px-6 py-3 bg-[#00E5FF] text-[#020617] font-bold rounded-xl hover:shadow-[0_0_20px_rgba(0,229,255,0.4)] transition-all flex items-center gap-2"
            >
              <TrendingUp className="w-5 h-5" />
              Simulate Refactor
            </button>
          </div>
        </div>

        {/* In-progress Banner */}
        {status && (status.status === "Active" || status.status === "Queue") && (
          <div className="flex items-center gap-3 p-4 rounded-xl bg-cyan-500/10 border border-cyan-500/20 animate-pulse">
            <Loader2 className="w-5 h-5 text-cyan-400 animate-spin" />
            <span className="text-cyan-300 font-medium text-sm">Analysis is {status.status === "Queue" ? "queued" : "running"}... Dashboard will refresh automatically when complete.</span>
          </div>
        )}

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
                    <span className="text-xs text-slate-500">{graphData?.nodes?.length || 0} nodes · {graphData?.links?.length || 0} edges</span>
                </div>
                {graphData && graphData.nodes?.length > 0 ? <DependencyGraph data={graphData} /> : <div className="h-[400px] flex items-center justify-center text-slate-500 italic">No graph data available. Try re-analyzing.</div>}
            </div>
            
            <div className="glass border border-slate-800/50 p-6 rounded-2xl">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xl font-bold text-white flex items-center gap-2">
                        <Activity className="w-5 h-5 text-[#00E5FF]" />
                        Deep Analysis Profile
                    </h3>
                </div>
                <div className="space-y-4">
                    <div className="p-4 bg-slate-800/20 rounded-xl border border-[#00E5FF]/10">
                        <p className="text-[#00E5FF] font-bold text-sm mb-1 uppercase tracking-wider">Predictive Observation</p>
                        <p className="text-slate-300 italic text-sm">
                          {summary?.risk_level === "High" 
                            ? `Architectural hotspots detected — ${summary?.god_object_count} God Objects are exerting significant pressure on the system core with ${summary?.total_dependencies} dependency links.`
                            : summary?.risk_level === "Medium"
                            ? `Moderate structural pressure detected across ${summary?.total_files} files. Some modules may benefit from decomposition.`
                            : `Stable architectural state. Dependency coupling is within healthy parameters across ${summary?.total_files || 0} files.`}
                        </p>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                           <p className="text-xs text-slate-500 uppercase font-bold">Avg Centrality</p>
                           <p className="text-xl font-bold text-white">{avgCentrality}</p>
                        </div>
                        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                           <p className="text-xs text-slate-500 uppercase font-bold">Nodes Connected</p>
                           <p className="text-xl font-bold text-white">{graphData?.nodes?.length || 0}</p>
                        </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                           <p className="text-xs text-slate-500 uppercase font-bold">Dependencies</p>
                           <p className="text-xl font-bold text-white">{summary?.total_dependencies || 0}</p>
                        </div>
                        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                           <p className="text-xs text-slate-500 uppercase font-bold">God Objects</p>
                           <p className="text-xl font-bold text-white">{summary?.god_object_count || 0}</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        {/* Risk Hotspots Section */}
        <div id="risk-center" className="grid grid-cols-1 gap-8 mt-8">
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
                {heatmapData && heatmapData.children?.length > 0 ? <RiskHeatmap data={heatmapData} /> : <div className="h-[300px] flex items-center justify-center text-slate-500 italic">No heatmap data available.</div>}
            </div>
        </div>

        {/* AI Refactor Advisor Section */}
        <div className="grid grid-cols-1 gap-8 mt-12 pb-12">
            <div id="refactor-section" className="glass border border-slate-800/50 p-6 rounded-2xl">
                <div className="flex items-center justify-between mb-8">
                    <h3 className="text-xl font-bold text-white flex items-center gap-2">
                        <Zap className="w-5 h-5 text-cyan-400" />
                        AI Refactor Advisor & Impact Simulator
                    </h3>
                    <div className="px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-400 text-[10px] font-bold uppercase tracking-widest border border-cyan-500/20">
                        Gemini 1.5 Flash Active
                    </div>
                </div>
                <RefactorAdvisor repoId={repoId} />
            </div>
        </div>

        {/* Content Tabs / Sections */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mt-12">
          {/* File structure / Analysis List */}
          <div className="lg:col-span-2 space-y-6">
            <div className="glass border border-slate-800/50 p-6 rounded-2xl relative overflow-hidden">
                <div className="flex items-center justify-between mb-6">
                    <h3 className="text-xl font-bold text-white">Files High-Risk Profiles</h3>
                    <span className="text-xs text-slate-500 font-medium">{graphData?.nodes?.length || 0} total files</span>
                </div>
                
                <div className="space-y-4 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
                    {(graphData?.nodes ? [...graphData.nodes] : []).sort((a: any, b: any) => (b.centrality || 0) - (a.centrality || 0)).slice(0, 8).map((node: any) => (
                        <div key={node.id} className="flex items-center justify-between p-4 rounded-xl bg-slate-900/50 border border-slate-800 hover:border-slate-700 transition-all cursor-pointer group">
                             <div className="flex items-center gap-4">
                                <div className={`w-10 h-10 rounded-lg ${(node.centrality || 0) > 0.5 ? "bg-orange-500/10" : (node.centrality || 0) > 0.2 ? "bg-amber-500/10" : "bg-blue-500/10"} flex items-center justify-center`}>
                                    <AlertCircle className={`w-5 h-5 ${(node.centrality || 0) > 0.5 ? "text-orange-400" : (node.centrality || 0) > 0.2 ? "text-amber-400" : "text-blue-400"}`} />
                                </div>
                                <div className="max-w-[280px]">
                                    <h4 className="text-sm font-bold text-white group-hover:text-[#00E5FF] transition-colors truncate">{node.name || node.id}</h4>
                                    <p className="text-xs text-slate-500 mt-1 truncate">{node.id} · Complexity: {node.complexity || 0}</p>
                                </div>
                             </div>
                             <div className="text-right">
                                <span className="text-sm font-bold text-slate-300">Centrality: {(node.centrality || 0).toFixed(2)}</span>
                                <div className="w-24 h-1 bg-slate-800 rounded-full mt-2">
                                    <div 
                                      className="h-full rounded-full transition-all duration-1000" 
                                      style={{ 
                                        width: `${Math.min(Math.round((node.centrality || 0) * 100), 100)}%`,
                                        backgroundColor: (node.centrality || 0) > 0.5 ? "#fb923c" : (node.centrality || 0) > 0.2 ? "#fbbf24" : "#38bdf8"
                                      }} 
                                    />
                                </div>
                             </div>
                        </div>
                    ))}
                    {(!graphData?.nodes || graphData.nodes.length === 0) && (
                      <div className="text-center py-10 text-slate-500 italic">No node profiles available yet. Submit a repository to generate.</div>
                    )}
                </div>
            </div>
          </div>

          {/* Right Sidebar / Meta info */}
          <div className="space-y-6">
            <div className="glass border border-slate-800/50 p-6 rounded-2xl">
                <h3 className="text-lg font-bold text-white mb-4">Analysis Timeline</h3>
                <div className="space-y-6">
                    <div className="flex items-start gap-3 relative">
                        <div className={`w-2 h-2 rounded-full mt-2 ${status?.status === "Done" ? "bg-[#00E5FF] shadow-[0_0_8px_rgba(0,229,255,0.8)]" : "bg-amber-400 animate-pulse"}`} />
                        <div className="absolute left-[3px] top-4 w-px h-10 bg-slate-800" />
                        <div>
                            <p className="text-sm font-bold text-white">
                              {status?.status === "Done" ? "Analysis Complete" : status?.status === "Active" ? "Analysis Running..." : status?.status === "Queue" ? "Queued for Analysis" : "Error in Analysis"}
                            </p>
                            <p className="text-xs text-slate-500">{status?.runtime_ms ? `${(status.runtime_ms / 1000).toFixed(1)}s runtime` : "Processing..."}</p>
                        </div>
                    </div>
                    <div className="flex items-start gap-4">
                        <div className="w-2 h-2 rounded-full bg-slate-700 mt-2" />
                        <div>
                            <p className="text-sm font-medium text-slate-400">Repository Cloned & Parsed</p>
                            <p className="text-xs text-slate-500">{summary?.total_files || 0} files indexed</p>
                        </div>
                    </div>
                    <div className="flex items-start gap-4">
                        <div className="w-2 h-2 rounded-full bg-slate-700 mt-2" />
                        <div>
                            <p className="text-sm font-medium text-slate-400">Graph Model Built</p>
                            <p className="text-xs text-slate-500">{summary?.total_dependencies || 0} dependencies mapped</p>
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
                  {topNode && topNode.centrality > 0.1
                    ? `"This codebase shows structural pressure in '${topNode.name}' (centrality: ${topNode.centrality.toFixed(2)}). Consider decomposing this module to reduce coupling risk."`
                    : `"The codebase architecture is well-distributed with no single dominant hub. Continue monitoring for emerging complexity."`
                  }
                </p>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}

export default function RepositoryDashboard() {
  return (
    <Suspense fallback={<div className="flex h-screen items-center justify-center bg-[#020617]"><Loader2 className="w-10 h-10 text-[#00E5FF] animate-spin" /></div>}>
      <DashboardContent />
    </Suspense>
  );
}
