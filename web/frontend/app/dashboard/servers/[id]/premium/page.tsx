'use client';
import { useState } from 'react';
import { useParams } from 'next/navigation';
import { Sparkles, Key, Check } from 'lucide-react';
import { apiClient } from '@/lib/api';

export default function ServerPremiumManagement() {
  const params = useParams();
  const guildId = params.id as string;

  const [key, setKey] = useState('');
  const [msg, setMsg] = useState('');

  const handleActivate = () => {
    apiClient.post('/premium/activate', { guild_id: guildId, key })
      .then((res) => {
        setMsg(res.data.message);
      })
      .catch((err) => {
        setMsg(err.response?.data?.detail || 'Activation error.');
      });
  };

  return (
    <div className="space-y-8 max-w-4xl">
      <div>
        <h2 className="text-2xl font-bold mb-1">Server Premium Licensing</h2>
        <p className="text-xs text-slate-400">Unlock Pro & White-Label features for Server ID: {guildId}</p>
      </div>

      <div className="p-6 rounded-2xl border border-discord-blurple/30 bg-discord-blurple/5 space-y-4">
        <h3 className="text-base font-bold flex items-center gap-2">
          <Key className="w-4 h-4 text-discord-blurple" /> Redeem Commercial License Key
        </h3>
        <p className="text-xs text-slate-300">Enter your purchased KHOKHO-XXXX-XXXX-XXXX key below:</p>

        <div className="flex gap-3">
          <input
            type="text"
            placeholder="KHOKHO-XXXX-XXXX-XXXX"
            value={key}
            onChange={(e) => setKey(e.target.value)}
            className="flex-1 bg-[#12141c] border border-white/10 rounded-xl px-4 py-2 text-sm focus:outline-none focus:border-discord-blurple uppercase font-mono"
          />
          <button
            onClick={handleActivate}
            className="px-6 py-2.5 rounded-xl bg-discord-blurple hover:bg-discord-blurple/90 text-white font-medium text-xs transition shadow-md shadow-discord-blurple/20"
          >
            Activate Key
          </button>
        </div>

        {msg && <p className="text-xs font-semibold text-discord-green mt-2">{msg}</p>}
      </div>
    </div>
  );
}