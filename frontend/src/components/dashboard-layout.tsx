import React from "react";
import Link from "next/link";
import { LayoutDashboard, ShieldAlert, GitBranch, Settings, HelpCircle, HardDrive } from "lucide-react";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const navItems = [
    { icon: LayoutDashboard, label: "Overview", href: "#" },
    { icon: GitBranch, label: "Dependencies", href: "#" },
    { icon: ShieldAlert, label: "Risk Center", href: "#" },
    { icon: HardDrive, label: "Code Map", href: "#" },
  ];

  return (
    <div className="flex h-screen bg-[#020617] text-slate-200 overflow-hidden font-sans">
      {/* Sidebar */}
      <aside className="w-64 border-r border-slate-800 bg-[#020617] flex flex-col">
        <div className="p-6">
          <Link href="/" className="flex items-center gap-2 group">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#00E5FF] to-[#006064] flex items-center justify-center group-hover:shadow-[0_0_15px_rgba(0,229,255,0.5)] transition-all">
              <span className="text-white font-bold text-xl">C</span>
            </div>
            <span className="text-xl font-bold tracking-tight text-white">CODETWIN</span>
          </Link>
        </div>

        <nav className="flex-1 px-4 space-y-1">
          {navItems.map((item) => (
            <Link
              key={item.label}
              href={item.href}
              className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-800 transition-colors group"
            >
              <item.icon className="w-5 h-5 text-slate-400 group-hover:text-[#00E5FF]" />
              <span className="text-sm font-medium">{item.label}</span>
            </Link>
          ))}
        </nav>

        <div className="p-4 border-t border-slate-800 mt-auto">
          <Link href="#" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-800 transition-colors">
            <Settings className="w-5 h-5 text-slate-400" />
            <span className="text-sm font-medium">Settings</span>
          </Link>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto relative custom-scrollbar">
        {/* Top Header */}
        <header className="h-16 border-b border-slate-800 flex items-center justify-between px-8 sticky top-0 bg-[#020617]/80 backdrop-blur-md z-10">
          <h1 className="text-sm font-medium text-slate-400 uppercase tracking-widest">Digital Twin Status: <span className="text-[#00E5FF]">Active</span></h1>
          <div className="flex items-center gap-4">
            <div className="flex -space-x-2">
              <div className="w-8 h-8 rounded-full border-2 border-slate-800 bg-slate-700 flex items-center justify-center text-[10px]">SD</div>
            </div>
          </div>
        </header>

        <div className="p-8">
          {children}
        </div>
      </main>
    </div>
  );
}
