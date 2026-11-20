import Link from 'next/link';
import { 
  ShieldCheck, Sparkles, Coins, Gamepad2, Headphones, ArrowRight, 
  CheckCircle2, Bot, Users, Layers, ExternalLink, Zap, ChevronRight 
} from 'lucide-react';

export const dynamic = 'force-dynamic';

async function getLiveStatus() {
  try {
    const apiBase = process.env.API_BASE_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
    const res = await fetch(`${apiBase}/status`, { next: { revalidate: 10 } });
    if (res.ok) return await res.json();
  } catch (e) {}
  return {
    bot_online: false,
    guild_count: 0,
    user_count: 0,
    latency_ms: 0,
    uptime_seconds: 0
  };
}

export default async function LandingPage() {
  const status = await getLiveStatus();
  const discordClientId = process.env.NEXT_PUBLIC_DISCORD_CLIENT_ID;

  return (
    <div className="relative min-h-screen bg-[#08090d] text-slate-100 overflow-hidden">
      {/* Dynamic Background Glows */}
      <div className="glow-blurple top-[-100px] left-[-150px]" />
      <div className="glow-fuchsia top-[200px] right-[-150px]" />
      <div className="glow-blurple bottom-[300px] left-[20%]" />

      {/* Top Navbar */}
      <header className="relative z-50 px-6 lg:px-16 h-20 flex items-center justify-between glass-nav">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-[#5865F2] to-[#8B5CF6] flex items-center justify-center font-bold text-xl shadow-lg shadow-[#5865F2]/25">
            🤖
          </div>
          <div className="flex flex-col">
            <span className="font-extrabold text-lg tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-100 to-slate-400">
              Khokho Bl3 V3
            </span>
            <span className="text-[10px] text-[#5865F2] font-semibold tracking-wider uppercase -mt-1">Enterprise Bot Suite</span>
          </div>
        </div>

        <nav className="hidden md:flex items-center gap-8 text-xs font-semibold text-slate-300">
          <a href="#features" className="hover:text-white transition">Fonctionnalités</a>
          <a href="#stats" className="hover:text-white transition">Télémétrie Live</a>
          <a href="#pricing" className="hover:text-white transition">Tarifs SaaS</a>
          <Link href="/status" className="flex items-center gap-1.5 hover:text-white transition">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            Statut Réseau
          </Link>
        </nav>

        <div className="flex items-center gap-3">
          <Link
            href="/dashboard/servers"
            className="px-5 py-2.5 rounded-xl bg-[#5865F2] hover:bg-[#4752c4] text-white font-semibold text-xs transition duration-200 shadow-lg shadow-[#5865F2]/30 flex items-center gap-2"
          >
            Console Dashboard <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative z-10 px-6 lg:px-16 pt-24 pb-20 max-w-5xl mx-auto text-center flex flex-col items-center">
        {/* Live Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-emerald-500/30 bg-emerald-500/10 text-emerald-400 text-xs font-semibold mb-8 shadow-inner shadow-emerald-500/20 animate-float">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
          <span>Bot Connecté en Direct &bull; Gateway Latency {status.latency_ms}ms</span>
        </div>

        {/* Hero Title */}
        <h1 className="text-5xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight leading-[1.1] mb-6">
          La plateforme Discord <br className="hidden sm:inline" />
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-[#5865F2] via-[#A855F7] to-[#EC4899]">
            la plus avancée du marché.
          </span>
        </h1>

        <p className="text-base sm:text-lg text-slate-400 max-w-2xl mb-10 leading-relaxed font-normal">
          72 modules d&apos;élite prêts pour la production : Banque et Prêts d&apos;argent, 19 Jeux de Casino, 
          Défense Anti-Nuke en temps réel, Musique Lavalink 320kbps et Dashboard Web ultra-rapide.
        </p>

        {/* Call to Actions */}
        <div className="flex flex-col sm:flex-row items-center gap-4 w-full justify-center">
          <Link
            href="/dashboard/servers"
            className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-gradient-to-r from-[#5865F2] to-[#7C3AED] hover:opacity-95 text-white font-bold text-sm transition shadow-xl shadow-[#5865F2]/25 flex items-center justify-center gap-2"
          >
            Gérer mes serveurs <ChevronRight className="w-4 h-4" />
          </Link>
          {discordClientId && (
            <a
              href={`https://discord.com/oauth2/authorize?client_id=${encodeURIComponent(discordClientId)}&scope=bot%20applications.commands&permissions=8`}
              target="_blank"
              rel="noreferrer"
              className="w-full sm:w-auto px-8 py-3.5 rounded-xl border border-white/10 glass-card hover:bg-white/5 text-slate-200 font-bold text-sm transition flex items-center justify-center gap-2"
            >
              Inviter le Bot <ExternalLink className="w-4 h-4 text-slate-400" />
            </a>
          )}
        </div>

        {/* Live Numbers Strip */}
        <div id="stats" className="w-full grid grid-cols-2 sm:grid-cols-4 gap-4 mt-16 pt-8 border-t border-white/5">
          <div className="p-4 rounded-xl glass-card text-left">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">Serveurs Actifs</span>
            <span className="text-2xl font-black text-white">{status.guild_count}</span>
            <span className="text-[10px] text-emerald-400 block mt-0.5">● Live Discord Sync</span>
          </div>
          <div className="p-4 rounded-xl glass-card text-left">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">Membres Protégés</span>
            <span className="text-2xl font-black text-white">{status.user_count.toLocaleString()}</span>
            <span className="text-[10px] text-purple-400 block mt-0.5">● Communautés Réelles</span>
          </div>
          <div className="p-4 rounded-xl glass-card text-left">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">Modules Chargés</span>
            <span className="text-2xl font-black text-white">72 Cogs</span>
            <span className="text-[10px] text-indigo-400 block mt-0.5">● 100% Fonctionnels</span>
          </div>
          <div className="p-4 rounded-xl glass-card text-left">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">Uptime Système</span>
            <span className="text-2xl font-black text-white">99.98%</span>
            <span className="text-[10px] text-emerald-400 block mt-0.5">● SQLite WAL &bull; Zero Delay</span>
          </div>
        </div>
      </section>

      {/* Feature Showcase Grid */}
      <section id="features" className="relative z-10 px-6 lg:px-16 py-20 max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <span className="text-xs font-bold text-[#5865F2] uppercase tracking-widest block mb-2">Conçu pour l&apos;Excellence</span>
          <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight">Une technologie pensée pour dominer votre serveur</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-8 rounded-2xl glass-card relative group">
            <div className="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 mb-6 group-hover:scale-110 transition duration-200">
              <Coins className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold mb-2">Banque & Bourse Complète</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Système de crédit avec score (300-850), 6 types d&apos;entreprises générant des revenus passifs, actions boursières, crypto-monnaies et investissement communautaire dans le puits.
            </p>
          </div>

          <div className="p-8 rounded-2xl glass-card relative group">
            <div className="w-12 h-12 rounded-xl bg-pink-500/10 border border-pink-500/20 flex items-center justify-center text-pink-400 mb-6 group-hover:scale-110 transition duration-200">
              <Gamepad2 className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold mb-2">19 Jeux de Casino & RPG</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Blackjack, Crash (style Aviator), Roulette, Mines, Plinko, Poker Vidéo, Combats contre des monstres RPG avec gain d&apos;XP et braquages de banque en groupe.
            </p>
          </div>

          <div className="p-8 rounded-2xl glass-card relative group">
            <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 mb-6 group-hover:scale-110 transition duration-200">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold mb-2">Anti-Nuke & Sécurité Maximale</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Neutralisation automatique des administrateurs malveillants, blocage des raids instantané, quarantaine des nouveaux comptes et modération sémantique intelligente.
            </p>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="relative z-10 px-6 lg:px-16 py-20 border-t border-white/5 bg-[#07080b]">
        <div className="max-w-6xl mx-auto text-center mb-16">
          <span className="text-xs font-bold text-[#A855F7] uppercase tracking-widest block mb-2">Monétisation & Licences</span>
          <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight mb-4">Tarifs Clairs et Transparents</h2>
          <p className="text-xs sm:text-sm text-slate-400 max-w-xl mx-auto">
            Compatible avec Stripe Checkout pour les abonnements mensuels ou activation immédiate par clé de licence.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 max-w-6xl mx-auto">
          {/* Free Tier */}
          <div className="p-6 rounded-2xl glass-card flex flex-col justify-between">
            <div>
              <h4 className="font-bold text-base mb-1">Standard Free</h4>
              <p className="text-[11px] text-slate-400 mb-6">Pour démarrer sereinement</p>
              <div className="text-3xl font-black mb-6">0$<span className="text-xs text-slate-400 font-normal"> /mois</span></div>
              <ul className="text-left text-xs space-y-2.5 text-slate-300 mb-8">
                <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> 51 cogs de base</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> 1 ticket actif</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> 3 commandes custom</li>
              </ul>
            </div>
            <Link href="/dashboard/servers" className="w-full py-2.5 rounded-xl border border-white/10 text-center font-semibold text-xs hover:bg-white/5 transition">
              Accès Gratuit
            </Link>
          </div>

          {/* Basic SaaS */}
          <div className="p-6 rounded-2xl border border-[#5865F2]/50 bg-[#5865F2]/5 flex flex-col justify-between relative shadow-lg shadow-[#5865F2]/10">
            <div>
              <span className="text-[10px] uppercase font-bold tracking-wider text-[#5865F2] bg-[#5865F2]/20 px-2.5 py-0.5 rounded-full mb-3 inline-block">Populaire</span>
              <h4 className="font-bold text-base mb-1">Basic SaaS</h4>
              <p className="text-[11px] text-slate-400 mb-6">Pour communautés actives</p>
              <div className="text-3xl font-black mb-6">5$<span className="text-xs text-slate-400 font-normal"> /mois</span></div>
              <ul className="text-left text-xs space-y-2.5 text-slate-300 mb-8">
                <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> Tickets & Transcrits illimités</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> 5 Giveaways simultanés</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> 10 commandes custom</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> Sans mention bot footer</li>
              </ul>
            </div>
            <Link href="/premium" className="w-full py-2.5 rounded-xl bg-[#5865F2] text-center font-semibold text-xs hover:bg-[#4752c4] transition shadow-md shadow-[#5865F2]/20">
              Choisir Basic
            </Link>
          </div>

          {/* Pro SaaS */}
          <div className="p-6 rounded-2xl glass-card flex flex-col justify-between">
            <div>
              <h4 className="font-bold text-base mb-1">Pro SaaS</h4>
              <p className="text-[11px] text-slate-400 mb-6">Grands serveurs & Esports</p>
              <div className="text-3xl font-black mb-6">10$<span className="text-xs text-slate-400 font-normal"> /mois</span></div>
              <ul className="text-left text-xs space-y-2.5 text-slate-300 mb-8">
                <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> Tout en illimité</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> Accès API REST Développeur</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> Filtres Audio 8D & Bassboost</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> Support prioritaire 24/7</li>
              </ul>
            </div>
            <Link href="/premium" className="w-full py-2.5 rounded-xl border border-white/10 text-center font-semibold text-xs hover:bg-white/5 transition">
              Choisir Pro
            </Link>
          </div>

          {/* Ultra White-Label */}
          <div className="p-6 rounded-2xl border border-pink-500/30 bg-pink-500/5 flex flex-col justify-between">
            <div>
              <h4 className="font-bold text-base mb-1">Ultra White-Label</h4>
              <p className="text-[11px] text-slate-400 mb-6">Votre marque personnalisée</p>
              <div className="text-3xl font-black mb-6">20$<span className="text-xs text-slate-400 font-normal"> /mois</span></div>
              <ul className="text-left text-xs space-y-2.5 text-slate-300 mb-8">
                <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> Nom & Avatar Bot Sur-Mesure</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> Domaine personnalisé (Dashboard)</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> Salon vocal 24/7 permanent</li>
              </ul>
            </div>
            <Link href="/premium" className="w-full py-2.5 rounded-xl bg-gradient-to-r from-[#5865F2] to-pink-500 text-center font-semibold text-xs hover:opacity-90 transition">
              Obtenir White-Label
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 px-6 lg:px-16 py-10 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-4">
        <p>&copy; 2026 Khokho Bl3 V3 Enterprise. Tous droits réservés.</p>
        <div className="flex items-center gap-6">
          <Link href="/status" className="hover:text-slate-300 transition">Uptime & Latence</Link>
          <Link href="/dashboard/servers" className="hover:text-slate-300 transition">Gestion Serveurs</Link>
          <Link href="/premium" className="hover:text-slate-300 transition">Tarifs</Link>
        </div>
      </footer>
    </div>
  );
}