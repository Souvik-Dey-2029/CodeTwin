"use client";

import React, { useState } from "react";
import { Github, ArrowRight, Activity, ShieldCheck, Zap, Globe, Layout, Sparkles } from "lucide-react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

export default function LandingPage() {
  const [url, setUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) return;
    
    setIsLoading(true);
    try {
      const repo = await api.submitRepository(url);
      router.push(`/dashboard/${repo.id}`);
    } catch (error) {
      console.error("Submission failed:", error);
      alert("Failed to initialize Digital Twin. Please check the URL.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#020617] text-slate-200 selection:bg-[#00E5FF]/30 selection:text-white font-sans overflow-x-hidden">
      {/* Dynamic Background */}
      <div className="fixed inset-0 z-0">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-[#00E5FF]/10 rounded-full blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-[#006064]/20 rounded-full blur-[120px]" />
        <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: 'radial-gradient(#94a3b8 1px, transparent 1px)', backgroundSize: '40px 40px' }} />
      </div>

      {/* Navigation */}
      <nav className="relative z-10 flex items-center justify-between px-8 py-6 max-w-7xl mx-auto">
        <div className="flex items-center gap-2 group cursor-pointer">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#00E5FF] to-[#006064] flex items-center justify-center group-hover:shadow-[0_0_20px_rgba(0,229,255,0.5)] transition-all">
            <span className="text-white font-bold text-2xl">C</span>
          </div>
          <span className="text-2xl font-bold tracking-tight text-white">CODETWIN</span>
        </div>
        <div className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-400">
          <a href="#" className="hover:text-[#00E5FF] transition-colors">Features</a>
          <a href="#" className="hover:text-[#00E5FF] transition-colors">How it works</a>
          <a href="#" className="hover:text-white transition-colors flex items-center gap-2">
            <Github className="w-4 h-4" />
            GitHub
          </a>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="relative z-10 pt-20 pb-32 px-6 max-w-5xl mx-auto text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800/50 border border-slate-700/50 text-[#00E5FF] text-xs font-bold tracking-widest uppercase mb-8 animate-fade-in">
          <div className="w-1.5 h-1.5 rounded-full bg-[#00E5FF] animate-pulse" />
          v0.1.0 Experimental Engine
        </div>

        <h1 className="text-6xl md:text-8xl font-bold text-white tracking-tighter mb-8 leading-[1.1]">
          Map Your Codebase's <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#00E5FF] to-[#00838F]">Future Twin</span>
        </h1>

        <p className="text-slate-400 text-lg md:text-xl max-w-2xl mx-auto mb-12 leading-relaxed">
          The first AI Digital Twin for software architecture. Predict structural decay, map dependencies, and simulate refactors before they happen.
        </p>

        {/* Input Area */}
        <div className="max-w-2xl mx-auto mb-20">
          <form onSubmit={handleSubmit} className="relative group">
            <div className="absolute inset-0 bg-gradient-to-r from-[#00E5FF] to-[#00838F] rounded-2xl blur-lg opacity-20 group-hover:opacity-40 transition-opacity" />
            <div className="relative flex p-2 bg-slate-900/80 border border-slate-700/50 rounded-2xl backdrop-blur-xl">
              <input 
                type="text" 
                placeholder="Paste GitHub Repository URL..." 
                className="flex-1 bg-transparent px-6 py-4 text-white placeholder:text-slate-500 focus:outline-none text-lg"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                disabled={isLoading}
              />
              <button 
                type="submit"
                className="bg-[#00E5FF] text-[#020617] px-8 rounded-xl font-bold flex items-center gap-2 hover:bg-white transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={isLoading}
              >
                {isLoading ? "Initializing..." : "Clone Twin"}
                <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          </form>
          <div className="flex gap-4 mt-6 justify-center text-xs text-slate-500 font-medium tracking-wide">
            <span className="flex items-center gap-1.5"><Globe className="w-3.5 h-3.5" /> Public Repos Only</span>
            <span className="flex items-center gap-1.5 text-slate-400">🔥 Supported: Python, JS, TS</span>
          </div>
        </div>

        {/* Feature Grid Skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
          {[
            { icon: Layout, title: "Dependency Graph", desc: "Interactive force-directed maps of your system's skeleton." },
            { icon: Zap, title: "Risk Prediction", desc: "Identify complexity hotspots before they become technical debt." },
            { icon: Sparkles, title: "AI Refactor", desc: "Get semantic modularization suggestions powered by LLMs." }
          ].map((feature, i) => (
            <div key={i} className="p-8 rounded-2xl border border-zinc-900 bg-zinc-900/50 hover:bg-zinc-800/50 hover:border-zinc-700 transition-all text-left">
              <feature.icon className="w-8 h-8 text-cyan-400 mb-4" />
              <h3 className="text-lg font-bold text-white mb-2">{feature.title}</h3>
              <p className="text-sm text-zinc-500 leading-relaxed">{feature.desc}</p>
            </div>
          ))}
        </div>
      </main>

      {/* Footer Decoration */}
      <div className="absolute bottom-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-zinc-800 to-transparent"></div>
    </div>
  );
}
