'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { Shield, Coins, BarChart2, Bell, Lock, Terminal, Sparkles, Save, Check, Settings } from 'lucide-react';
import { apiClient } from '@/lib/api';

export default function ServerGeneralSettings() {
  const params = useParams();
  const guildId = params?.id as string;

  const [config, setConfig] = useState<any>({
    prefix: '&',
    language: 'darija',
    features: {
      welcome: true,
      auto_mod: true,
      logging: true,
      tickets: true,
      economy: true,
      levels: true
    }
  });
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!guildId) return;
    apiClient.get('/guilds/' + guildId)
      .then((res) => {
        if (res.data) setConfig(res.data);
      })
      .catch(() => setError('Could not load server settings. Check your login and API connection.'));
  }, [guildId]);

  const handleSave = async () => {
    setError('');
    try {
      await apiClient.patch('/guilds/' + guildId, {
        prefix: config.prefix,
        language: config.language
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    } catch {
      setError('Settings could not be synchronized. Check that the bot and API are connected to Redis.');
    }
  };

  const navItems = [
    { name: 'General', href: '/dashboard/servers/' + guildId, icon: Settings },
    { name: 'Moderation', href: '/dashboard/servers/' + guildId + '/moderation', icon: Shield },
    { name: 'Economy', href: '/dashboard/servers/' + guildId + '/economy', icon: Coins },
    { name: 'Levels', href: '/dashboard/servers/' + guildId + '/levels', icon: BarChart2 },
    { name: 'Tickets', href: '/dashboard/servers/' + guildId + '/tickets', icon: Bell },
    { name: 'Anti-Nuke', href: '/dashboard/servers/' + guildId + '/antinuke', icon: Lock },
    { name: 'Custom Cmds', href: '/dashboard/servers/' + guildId + '/custom_commands', icon: Terminal },
    { name: 'Premium', href: '/dashboard/servers/' + guildId + '/premium', icon: Sparkles },
  ];

  return (
    <div className="space-y-8 max-w-5xl">
      <div className="p-6 rounded-2xl border border-white/5 glass">
        <h2 className="text-2xl font-bold mb-1">Server Management</h2>
        <p className="text-xs text-slate-400 mb-6">Server ID: {guildId}</p>

        <div className="flex flex-wrap gap-2 text-xs">
          {navItems.map((item) => (
            <Link
              key={item.name}
              href={item.href}
              className="px-3.5 py-2 rounded-xl border border-white/5 bg-white/5 hover:bg-discord-blurple hover:text-white transition flex items-center gap-2"
            >
              <item.icon className="w-3.5 h-3.5" /> {item.name}
            </Link>
          ))}
        </div>
      </div>

      <div className="p-6 rounded-2xl border border-white/5 glass space-y-6">
        {error && <p role="alert" className="text-xs text-red-400">{error}</p>}
        <h3 className="text-lg font-bold">Bot Prefix & Localization</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-2">Public Command Prefix</label>
            <input
              type="text"
              value={config.prefix || '&'}
              onChange={(e) => setConfig({ ...config, prefix: e.target.value })}
              className="w-full bg-[#12141c] border border-white/10 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-discord-blurple"
            />
            <span className="text-[11px] text-slate-500 mt-1 block">Default is &apos;&amp;&apos; (Admin commands always use &apos;+&apos; or &apos;-&apos;)</span>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-2">Bot Language (i18n)</label>
            <select
              value={config.language || 'darija'}
              onChange={(e) => setConfig({ ...config, language: e.target.value })}
              className="w-full bg-[#12141c] border border-white/10 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-discord-blurple"
            >
              <option value="darija">Darija (Moroccan Arabic)</option>
              <option value="en">English (US)</option>
              <option value="fr">Français (French)</option>
              <option value="ar">العربية الفصحى (Arabic)</option>
            </select>
          </div>
        </div>

        <div className="pt-4 flex justify-end">
          <button
            onClick={handleSave}
            className="px-6 py-2.5 rounded-xl bg-discord-blurple hover:bg-discord-blurple/90 text-white font-medium text-sm transition flex items-center gap-2 shadow-lg shadow-discord-blurple/25"
          >
            {saved ? <Check className="w-4 h-4" /> : <Save className="w-4 h-4" />}
            {saved ? 'Saved Successfully!' : 'Save Settings'}
          </button>
        </div>
      </div>
    </div>
  );
}