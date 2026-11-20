'use client';
import { useEffect, useState } from 'react';
import { 
  BarChart3, Users, MessageSquare, Zap, Shield, Trophy, 
  ArrowUpRight, Activity, TrendingUp, Sparkles, RefreshCw 
} from 'lucide-react';
import { apiClient } from '@/lib/api';

export default function DashboardOverviewPage() {
  const [stats, setStats] = useState({
    guild_count: 0,
    user_count: 0,
    latency_ms: 0,
    bot_online: false
  });
  const [topUsers, setTopUsers] = useState<any[]>([]);
  const [topLevels, setTopLevels] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient.get('/status')
      .then((res) => {
        if (res.data) setStats(res.data);
      })
      .catch(() => {});

    apiClient.get('/guilds')
      .then(async ({ data }) => {
        const guild = data.find((item: any) => item.has_bot);
        if (!guild) return;
        const [economy, levels] = await Promise.all([
          apiClient.get(`/guilds/${guild.id}/economy`),
          apiClient.get(`/guilds/${guild.id}/levels`),
        ]);
        if (economy.data?.leaderboard) setTopUsers(economy.data.leaderboard.slice(0, 5));
        if (levels.data?.leaderboard) setTopLevels(levels.data.leaderboard.slice(0, 5));
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-8 max-w-6xl">
      {/* Page Title */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-6 border-b border-white/5">
        <div>
          <h1 className="text-3xl font-black tracking-tight text-white mb-1.5 flex items-center gap-3">
            Vue d&apos;ensemble & Télémétrie
            <span className="text-xs bg-emerald-500/10 text-emerald-400 font-bold px-3 py-1 rounded-full border border-emerald-500/20">
              {stats.bot_online ? '● Bot connecté' : '● Bot hors ligne'}
            </span>
          </h1>
          <p className="text-xs sm:text-sm text-slate-400">
            Statistiques en direct extraites de votre base de données SQLite et de la passerelle Discord.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="px-3.5 py-1.5 rounded-xl glass-card flex items-center gap-2 text-xs">
            <span className={`w-2 h-2 rounded-full ${stats.bot_online ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'}`} />
            <span className="text-slate-300">Ping Gateway: <strong>{stats.latency_ms}ms</strong></span>
          </div>
        </div>
      </div>

      {/* Top 4 KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl glass-card flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 mb-3">
            <span className="text-xs font-bold uppercase tracking-wider">Serveurs Liés</span>
            <div className="w-8 h-8 rounded-lg bg-[#5865F2]/10 border border-[#5865F2]/20 flex items-center justify-center text-[#5865F2]">
              <Users className="w-4 h-4" />
            </div>
          </div>
          <div>
            <div className="text-3xl font-black text-white">{stats.guild_count}</div>
            <span className="text-[11px] text-emerald-400 font-medium flex items-center gap-1 mt-1">
              <TrendingUp className="w-3 h-3" /> Serveurs du bot
            </span>
          </div>
        </div>

        <div className="p-5 rounded-2xl glass-card flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 mb-3">
            <span className="text-xs font-bold uppercase tracking-wider">Membres Actifs</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <Activity className="w-4 h-4" />
            </div>
          </div>
          <div>
            <div className="text-3xl font-black text-white">{stats.user_count.toLocaleString()}</div>
            <span className="text-[11px] text-emerald-400 font-medium flex items-center gap-1 mt-1">
              {stats.bot_online ? '● Données Discord' : '● Indisponible'}
            </span>
          </div>
        </div>

        <div className="p-5 rounded-2xl glass-card flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 mb-3">
            <span className="text-xs font-bold uppercase tracking-wider">Modules Bot</span>
            <div className="w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
              <Zap className="w-4 h-4" />
            </div>
          </div>
          <div>
            <div className="text-3xl font-black text-white">72 Cogs</div>
            <span className="text-[11px] text-purple-400 font-medium flex items-center gap-1 mt-1">
              {stats.bot_online ? '● Bot joignable' : '● Bot hors ligne'}
            </span>
          </div>
        </div>

        <div className="p-5 rounded-2xl glass-card flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 mb-3">
            <span className="text-xs font-bold uppercase tracking-wider">Moteur Base</span>
            <div className="w-8 h-8 rounded-lg bg-pink-500/10 border border-pink-500/20 flex items-center justify-center text-pink-400">
              <Shield className="w-4 h-4" />
            </div>
          </div>
          <div>
            <div className="text-3xl font-black text-white">SQLite WAL</div>
            <span className="text-[11px] text-emerald-400 font-medium flex items-center gap-1 mt-1">
              ● SQLite
            </span>
          </div>
        </div>
      </div>

      {/* Real Live Leaderboards Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Economy Members */}
        <div className="p-6 rounded-2xl glass-card">
          <div className="flex items-center justify-between mb-5">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
                <Trophy className="w-4 h-4" />
              </div>
              <h3 className="font-extrabold text-white text-base">Top Riches (Économie Live)</h3>
            </div>
            <span className="text-[10px] text-slate-400 uppercase font-semibold">Portefeuille + Banque</span>
          </div>

          <div className="space-y-2.5">
            {topUsers.length === 0 ? (
              <p className="text-xs text-slate-400 py-4 text-center">Chargement des données économiques...</p>
            ) : (
              topUsers.map((u, i) => (
                <div
                  key={u.user_id}
                  className="p-3.5 rounded-xl border border-white/5 bg-[#0e111a] flex items-center justify-between"
                >
                  <div className="flex items-center gap-3">
                    <span className={`w-6 text-center font-black text-xs ${i === 0 ? 'text-amber-400' : i === 1 ? 'text-slate-300' : i === 2 ? 'text-amber-600' : 'text-slate-500'}`}>
                      #{i + 1}
                    </span>
                    {u.avatar_url ? (
                      <img src={u.avatar_url} alt="" className="w-9 h-9 rounded-full object-cover ring-1 ring-white/10" />
                    ) : (
                      <div className="w-9 h-9 rounded-full bg-slate-800 flex items-center justify-center text-xs font-bold text-slate-300">
                        {u.username.substring(0, 2).toUpperCase()}
                      </div>
                    )}
                    <div>
                      <span className="font-bold text-white text-xs block leading-tight">{u.username}</span>
                      <span className="text-[10px] text-slate-500 font-mono">ID: {u.user_id}</span>
                    </div>
                  </div>

                  <div className="text-right">
                    <span className="font-extrabold text-amber-400 text-xs block">
                      {u.total.toLocaleString()} 🪙
                    </span>
                    <span className="text-[10px] text-slate-500">
                      W: {u.wallet.toLocaleString()} &bull; B: {u.bank.toLocaleString()}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Top Levels & Activity */}
        <div className="p-6 rounded-2xl glass-card">
          <div className="flex items-center justify-between mb-5">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-[#5865F2]/10 border border-[#5865F2]/20 flex items-center justify-center text-[#5865F2]">
                <BarChart3 className="w-4 h-4" />
              </div>
              <h3 className="font-extrabold text-white text-base">Top Niveaux & XP (Live)</h3>
            </div>
            <span className="text-[10px] text-slate-400 uppercase font-semibold">XP & Messages</span>
          </div>

          <div className="space-y-2.5">
            {topLevels.length === 0 ? (
              <p className="text-xs text-slate-400 py-4 text-center">Chargement des données de niveaux...</p>
            ) : (
              topLevels.map((u, i) => (
                <div
                  key={u.user_id}
                  className="p-3.5 rounded-xl border border-white/5 bg-[#0e111a] flex items-center justify-between"
                >
                  <div className="flex items-center gap-3">
                    <span className={`w-6 text-center font-black text-xs ${i === 0 ? 'text-[#5865F2]' : 'text-slate-500'}`}>
                      #{i + 1}
                    </span>
                    {u.avatar_url ? (
                      <img src={u.avatar_url} alt="" className="w-9 h-9 rounded-full object-cover ring-1 ring-white/10" />
                    ) : (
                      <div className="w-9 h-9 rounded-full bg-slate-800 flex items-center justify-center text-xs font-bold text-slate-300">
                        {u.username.substring(0, 2).toUpperCase()}
                      </div>
                    )}
                    <div>
                      <span className="font-bold text-white text-xs block leading-tight">{u.username}</span>
                      <span className="text-[10px] text-slate-500">
                        {u.messages || 0} messages &bull; {u.voice_minutes || 0}m vocal
                      </span>
                    </div>
                  </div>

                  <div className="text-right">
                    <span className="font-extrabold text-purple-400 text-xs block">
                      Level {u.level || 1}
                    </span>
                    <span className="text-[10px] text-slate-500">
                      {(u.xp || 0).toLocaleString()} XP
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}