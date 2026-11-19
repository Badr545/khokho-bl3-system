import Link from 'next/link';
import { Server, Shield, Coins, BarChart3, Settings, LifeBuoy, ArrowLeft } from 'lucide-react';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen overflow-hidden bg-[#0a0c12]">
      {/* Sidebar */}
      <aside className="w-64 border-r border-white/5 glass flex flex-col justify-between p-4">
        <div>
          <div className="flex items-center gap-3 px-2 py-3 mb-6 border-b border-white/5">
            <div className="w-8 h-8 rounded-lg bg-discord-blurple flex items-center justify-center font-bold text-lg">
              🤖
            </div>
            <span className="font-bold text-sm tracking-tight text-white">Khokho Bl3 Console</span>
          </div>

          <nav className="space-y-1 text-sm font-medium">
            <Link
              href="/dashboard/servers"
              className="flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-white/5 text-slate-300 hover:text-white transition"
            >
              <Server className="w-4 h-4 text-discord-blurple" /> My Servers
            </Link>
            <Link
              href="/dashboard"
              className="flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-white/5 text-slate-300 hover:text-white transition"
            >
              <BarChart3 className="w-4 h-4 text-discord-green" /> Overview & Charts
            </Link>
            <Link
              href="/premium"
              className="flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-white/5 text-slate-300 hover:text-white transition"
            >
              <Shield className="w-4 h-4 text-discord-fuchsia" /> Subscriptions
            </Link>
          </nav>
        </div>

        <div className="border-t border-white/5 pt-4">
          <Link
            href="/"
            className="flex items-center gap-2 text-xs text-slate-400 hover:text-white px-2 py-1.5 transition"
          >
            <ArrowLeft className="w-3.5 h-3.5" /> Back to Website
          </Link>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto p-8">
        {children}
      </main>
    </div>
  );
}