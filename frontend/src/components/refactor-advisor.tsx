"use client";

import React, { useState, useEffect } from "react";
import { api, RefactorProposal, ImpactSimulation } from "@/lib/api";
import { AlertTriangle, Zap, ArrowRight, ShieldCheck, Search } from "lucide-react";

export default function RefactorAdvisor({ repoId }: { repoId: number }) {
  const [proposals, setProposals] = useState<RefactorProposal[]>([]);
  const [selectedProposal, setSelectedProposal] = useState<RefactorProposal | null>(null);
  const [impact, setImpact] = useState<ImpactSimulation | null>(null);
  const [codeContent, setCodeContent] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadProposals() {
      try {
        const data = await api.getRefactorProposals(repoId);
        setProposals(data);
        if (data.length > 0) setSelectedProposal(data[0]);
      } catch (err) {
        console.error("Failed to load proposals", err);
      } finally {
        setLoading(false);
      }
    }
    loadProposals();
  }, [repoId]);

  const simulateBlastRadius = async (filePath: string) => {
    try {
      const data = await api.simulateImpact(repoId, filePath);
      setImpact(data);
    } catch (err) {
      console.error("Simulation failed", err);
    }
  };

  const fetchCode = async (filePath: string) => {
    try {
      const data = await api.getFileContent(repoId, filePath);
      setCodeContent(data.content);
    } catch (err) {
      console.error("Failed to fetch code", err);
      setCodeContent("// Error: Failed to fetch source code content.");
    }
  };

  useEffect(() => {
    if (selectedProposal) {
      simulateBlastRadius(selectedProposal.file_path);
      fetchCode(selectedProposal.file_path);
    }
  }, [selectedProposal]);

  if (loading) return <div className="p-8 text-center text-gray-400">Analyzing for refactor opportunities...</div>;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[700px]">
      {/* Sidebar - Proposal List */}
      <div className="lg:col-span-1 bg-gray-900/50 border border-white/10 rounded-xl overflow-hidden flex flex-col">
        <div className="p-4 border-b border-white/10 bg-black/20 font-semibold flex items-center gap-2">
          <Zap className="w-4 h-4 text-cyan-400" />
          Refactor Proposals
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {proposals.map((p) => (
            <button
              key={p.file_path}
              onClick={() => setSelectedProposal(p)}
              className={`w-full text-left p-4 rounded-lg border transition-all ${
                selectedProposal?.file_path === p.file_path
                  ? "bg-cyan-500/10 border-cyan-500/50"
                  : "bg-black/40 border-white/5 hover:border-white/20"
              }`}
            >
              <div className="text-sm font-medium text-white mb-1 truncate">{p.file_path.split("/").pop()}</div>
              <div className="text-xs text-gray-500 mb-2 truncate">{p.file_path}</div>
              <div className="flex items-center gap-3">
                <span className="text-[10px] px-2 py-0.5 rounded bg-red-500/10 text-red-400 border border-red-500/20">
                  Complexity: {p.complexity}
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
                  Centrality: {p.centrality}
                </span>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Main Content - Refactor Details & Simulation */}
      <div className="lg:col-span-2 space-y-6 flex flex-col h-full overflow-hidden">
        {selectedProposal && (
          <>
            {/* Recommendation Header */}
            <div className="bg-gradient-to-r from-cyan-900/20 to-transparent border border-cyan-500/20 rounded-xl p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-bold text-white mb-1">Impact Analysis & Proposal</h3>
                  <p className="text-sm text-cyan-400/80">{selectedProposal.file_path}</p>
                </div>
                <div className="flex flex-col items-end">
                  <span className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">Blast Radius Score</span>
                  <div className="text-2xl font-black text-cyan-400">{impact?.impact_score || 0}%</div>
                </div>
              </div>
              <div className="bg-black/40 rounded-lg p-4 border border-white/5">
                <div className="flex gap-2 text-sm text-gray-300">
                  <Search className="w-4 h-4 text-cyan-500 shrink-0 mt-0.5" />
                  <div>
                    <span className="text-cyan-400 font-semibold italic">Recommendation: </span>
                    {selectedProposal.suggested_action}
                  </div>
                </div>
              </div>
            </div>

            {/* Split View */}
            <div className="flex-1 grid grid-cols-2 gap-4 min-h-0">
              {/* Blast Radius Visualizer */}
              <div className="bg-black/50 border border-white/10 rounded-xl p-4 flex flex-col min-h-0">
                <div className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-4 flex items-center justify-between">
                  Blast Radius Graph
                  <span className="text-red-400 flex items-center gap-1">
                    <AlertTriangle className="w-3 h-3" />
                    High Dependency Risk
                  </span>
                </div>
                <div className="flex-1 overflow-y-auto space-y-3 pr-2">
                  {impact?.affected_nodes.map((node) => (
                    <div key={node.id} className="flex items-center justify-between p-2 rounded bg-white/5 border border-white/5">
                      <div className="flex items-center gap-3 overflow-hidden">
                        <div className={`w-2 h-2 rounded-full ${node.distance === 0 ? "bg-cyan-400" : node.distance === 1 ? "bg-amber-400" : "bg-gray-600"}`} />
                        <span className="text-xs text-gray-300 truncate">{node.id.split("/").pop()}</span>
                      </div>
                      <div className="text-[10px] text-gray-500">Degree: {node.distance}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Simplified Diff Preview */}
              <div className="bg-[#0d1117] border border-white/10 rounded-xl overflow-hidden flex flex-col">
                <div className="px-4 py-2 border-b border-white/10 bg-black/40 text-[10px] uppercase tracking-widest text-gray-500 flex justify-between">
                  Refactor Preview
                  <span className="text-emerald-400">Target State</span>
                </div>
                <div className="flex-1 p-4 font-mono text-[11px] overflow-auto leading-relaxed scrollbar-thin scrollbar-thumb-white/10">
                  <div className="text-gray-500 mb-2 truncate">// Original Module: {selectedProposal.file_path.split("/").pop()}</div>
                  {codeContent ? (
                    <div className="whitespace-pre text-gray-300">
                      {codeContent.split("\n").slice(0, 100).map((line, i) => (
                        <div key={i} className="flex gap-4 group hover:bg-white/5 px-1 truncate">
                          <span className="text-gray-600 w-8 select-none text-right">{i + 1}</span>
                          <span>{line || " "}</span>
                        </div>
                      ))}
                      {codeContent.split("\n").length > 100 && (
                        <div className="text-gray-600 mt-2 italic px-8">... and {codeContent.split("\n").length - 100} more lines</div>
                      )}
                    </div>
                  ) : (
                    <div className="flex flex-col items-center justify-center h-full text-gray-600 gap-2">
                      <div className="w-4 h-4 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
                      Loading source content...
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex justify-end gap-3 pt-2">
              <button className="px-5 py-2 rounded-lg bg-white/5 border border-white/10 text-sm font-medium text-white hover:bg-white/10 transition-colors">
                Ignore Proposal
              </button>
              <button className="px-5 py-2 rounded-lg bg-cyan-600 text-sm font-bold text-white hover:bg-cyan-500 transition-shadow shadow-lg shadow-cyan-900/20 flex items-center gap-2">
                Simulate Impact <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
