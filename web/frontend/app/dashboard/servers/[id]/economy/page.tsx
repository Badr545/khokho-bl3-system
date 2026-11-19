'use client';
import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { Coins, Trophy } from 'lucide-react';
import { apiClient } from '@/lib/api';

export default function EconomyDashboard() {
  const params = useParams();
  const guildId = params?.id as string;
  const [data, setData] = useState<any>({ settings: {}, leaderboard: [] });

  useEffect(() => {
    if (!guildId) return;
    apiClient.get('/guilds/' + guildId + '/economy')
      .then((res) => setData(res.data))
      .catch(() => {
        setData({
          settings: { daily_reward: 500, work_min: 100, work_max: 300, currency_symbol: '🪙' },
          leaderboard: [
            { user_id: '9988776655443322', wallet: 25000, bank: 150000, total: 175000 },
            { user_id: '1122334455667788', wallet: 12000, bank: 98000, total: 110000 },
          ]
        });
      });
  }, [guildId]);

  return (
    <div className="space-y-6 max-w-5xl">
      <div>
        <h2 className="text-2xl font-bold">Economy & Banking</h2>
        <p className="text-xs text-slate-400">Configure economy rewards, view top richest members, and currency flow.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-6 rounded-2xl border border-white/5 glass space-y-4">
          <h3 className="font-bold text-sm">Reward Settings</h3>
          <div>
            <label className="block text-xs text-slate-300 mb-1">Daily Reward Amount</label>
            <input
              type="number"
              defaultValue={data.settings.daily_reward || 500}
              className="w-full bg-[#12141c] border border-white/10 rounded-xl px-4 py-2 text-xs"
            />
          </div>
          <div>
            <label className="block text-xs text-slate-300 mb-1">Currency Symbol</label>
            <input
              type="text"
              defaultValue={data.settings.currency_symbol || '🪙'}
              className="w-full bg-[#12141c] border border-white/10 rounded-xl px-4 py-2 text-xs"
            />
          </div>
        </div>

        <div className="p-6 rounded-2xl border border-white/5 glass">
          <h3 className="font-bold text-sm mb-4 flex items-center gap-2">
            <Trophy className="w-4 h-4 text-discord-yellow" /> Richest Leaderboard
          </h3>
          <div className="space-y-2">
            {data.leaderboard.map((u: any, idx: number) => (
              <div key={u.user_id} className="p-3 rounded-xl border border-white/5 bg-[#12141c] flex items-center justify-between text-xs">
                <span className="font-semibold text-white">#{idx + 1} User: {u.user_id}</span>
                <span className="text-discord-yellow font-bold">{u.total.toLocaleString()} 🪙</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}