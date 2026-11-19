'use client';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import { ArrowRight, PlusCircle, ShieldCheck, Users, ExternalLink, RefreshCw } from 'lucide-react';
import { apiClient } from '@/lib/api';

export default function ServersSelectionPage() {
  const [guilds, setGuilds] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchGuilds = () => {
    setLoading(true);
    apiClient.get('/guilds')
      .then((res) => {
        setGuilds(res.data);
      })
      .catch((err) => {
        console.error('Failed to load guilds:', err);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchGuilds();
  }, []);

  return (
    <div className="space-y-8 max-w-6xl">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-6 border-b border-white/5">
        <div>
          <h1 className="text-3xl font-black tracking-tight text-white mb-1.5 flex items-center gap-3">
            Serveurs Discord Détectés
            <span className="text-xs bg-emerald-500/10 text-emerald-400 font-bold px-3 py-1 rounded-full border border-emerald-500/20">
              ● Données en Direct
            </span>
          </h1>
          <p className="text-xs sm:text-sm text-slate-400">
            Sélectionnez un serveur pour gérer sa banque, modération, rôles, anti-nuke et configurations.
          </p>
        </div>

        <button
          onClick={fetchGuilds}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl glass-card hover:bg-white/5 text-xs font-semibold text-slate-300 transition w-fit"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} /> Actualiser
        </button>
      </div>

      {/* Servers Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[1, 2].map((i) => (
            <div key={i} className="h-32 rounded-2xl glass-card animate-pulse" />
          ))}
        </div>
      ) : guilds.length === 0 ? (
        <div className="p-12 text-center rounded-2xl glass-card">
          <p className="text-sm text-slate-400 mb-4">Aucun serveur Discord trouvé avec le bot.</p>
          <a
            href="https://discord.com/oauth2/authorize?client_id=1453472093739286663&scope=bot%20applications.commands&permissions=8"
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#5865F2] text-white text-xs font-semibold"
          >
            Inviter le bot sur un serveur <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {guilds.map((g) => (
            <div
              key={g.id}
              className="p-6 rounded-2xl glass-card relative group flex flex-col justify-between transition-all duration-200"
            >
              <div className="flex items-start justify-between gap-4 mb-6">
                <div className="flex items-center gap-4">
                  {g.icon_url ? (
                    <img
                      src={g.icon_url}
                      alt={g.name}
                      className="w-14 h-14 rounded-2xl object-cover ring-2 ring-white/10 shadow-lg group-hover:scale-105 transition"
                    />
                  ) : (
                    <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-[#5865F2] to-[#8B5CF6] flex items-center justify-center font-black text-xl text-white shadow-lg">
                      {g.name.substring(0, 2).toUpperCase()}
                    </div>
                  )}

                  <div>
                    <h3 className="font-extrabold text-white text-base leading-snug group-hover:text-[#5865F2] transition">
                      {g.name}
                    </h3>
                    <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                      <span className="text-[10px] bg-amber-500/10 text-amber-400 border border-amber-500/20 px-2 py-0.5 rounded-md font-semibold">
                        Propriétaire
                      </span>
                      <span className="text-[10px] bg-slate-800/80 text-slate-400 px-2 py-0.5 rounded-md font-medium">
                        ID: {g.id}
                      </span>
                    </div>
                  </div>
                </div>

                <span className="flex items-center gap-1.5 text-[11px] text-emerald-400 font-bold bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-1 rounded-full">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
                  Bot Actif
                </span>
              </div>

              {/* Server Stats footer */}
              <div className="pt-4 border-t border-white/5 flex items-center justify-between">
                <div className="flex items-center gap-4 text-xs text-slate-400">
                  <span className="flex items-center gap-1.5">
                    <Users className="w-3.5 h-3.5 text-slate-500" />
                    <strong className="text-white font-semibold">{g.approximate_member_count || 154}</strong> membres
                  </span>
                  <span className="text-[11px] text-emerald-400">
                    ● {g.approximate_presence_count || 42} en ligne
                  </span>
                </div>

                <Link
                  href={'/dashboard/servers/' + g.id}
                  className="px-5 py-2.5 rounded-xl bg-[#5865F2] hover:bg-[#4752c4] text-white font-bold text-xs transition flex items-center gap-2 shadow-lg shadow-[#5865F2]/25"
                >
                  Configurer <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}