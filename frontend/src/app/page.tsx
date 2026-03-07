import Link from "next/link";
import { Github, Zap, Layout, Search, Sparkles, Binary } from "lucide-react";

export default function Home() {
  return (
    <div className="relative min-h-screen overflow-hidden selection:bg-cyan-500/30">
      {/* Dynamic Background Elements */}
      <div className="absolute top-0 left-0 w-full h-full -z-10 bg-[#09090b]">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-cyan-500/10 blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-blue-500/10 blur-[120px]" />
      </div>

      {/* Navigation */}
      <nav className="flex items-center justify-between px-8 py-6 max-w-7xl mx-auto">
        <div className="flex items-center gap-2 group cursor-pointer">
          <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/20 group-hover:border-cyan-500/50 transition-colors">
            <Binary className="w-6 h-6 text-cyan-400" />
          </div>
          <span className="text-xl font-bold tracking-tight text-white">CODETWIN</span>
        </div>
        <div className="hidden md:flex items-center gap-8">
          <Link href="#features" className="text-sm font-medium text-zinc-400 hover:text-white transition-colors">Features</Link>
          <Link href="#how-it-works" className="text-sm font-medium text-zinc-400 hover:text-white transition-colors">How it Works</Link>
          <a href="https://github.com" className="p-2 rounded-full hover:bg-zinc-800 transition-colors">
            <Github className="w-5 h-5 text-zinc-400" />
          </a>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="relative z-10 px-6 pt-20 pb-24 mx-auto max-w-7xl text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 mb-8 rounded-full border border-cyan-500/20 bg-cyan-500/5 text-xs font-semibold text-cyan-400 animate-pulse">
          <Sparkles className="w-3 h-3" />
          <span>Next-Gen Code Intelligence is here</span>
        </div>
        
        <h1 className="mb-6 text-5xl md:text-7xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-b from-white to-zinc-500">
          Digital Twin for your <br />
          <span className="text-cyan-400">Software Architecture</span>
        </h1>
        
        <p className="mb-12 text-lg md:text-xl text-zinc-400 max-w-2xl mx-auto leading-relaxed">
          Analyze, simulate, and refactor with precision. CodeTwin maps your codebase's DNA to predict risks and guide your next architectural evolution.
        </p>

        {/* Input Field */}
        <div className="relative max-w-2xl mx-auto mb-20 group">
          <div className="absolute -inset-1 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-2xl blur opacity-20 group-hover:opacity-40 transition duration-1000 group-hover:duration-200"></div>
          <div className="relative flex items-center p-2 rounded-xl bg-zinc-900 border border-zinc-800 focus-within:border-cyan-500/50 transition-all shadow-2xl">
            <div className="flex items-center flex-1 pl-4">
              <Search className="w-5 h-5 text-zinc-500" />
              <input 
                type="text" 
                placeholder="Paste a GitHub repository link (e.g., https://github.com/facebook/react)"
                className="w-full bg-transparent border-none focus:ring-0 text-zinc-200 placeholder:text-zinc-600 px-4 py-3 outline-none"
              />
            </div>
            <button className="px-6 py-3 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-zinc-950 font-bold transition-all transform active:scale-95 flex items-center gap-2">
              Analyze Twin
              <Zap className="w-4 h-4" />
            </button>
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
