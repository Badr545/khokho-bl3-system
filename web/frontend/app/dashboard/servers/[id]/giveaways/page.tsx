'use client';
import { FormEvent, useCallback, useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { Gift } from 'lucide-react';
import { apiClient } from '@/lib/api';

type Giveaway = {
  message_id: string;
  channel_id: number;
  prize: string;
  winners: number;
  until: string;
  ended: boolean;
};

export default function GiveawaysPage() {
  const params = useParams();
  const guildId = params.id as string;
  const [giveaways, setGiveaways] = useState<Giveaway[]>([]);
  const [channelId, setChannelId] = useState('');
  const [prize, setPrize] = useState('');
  const [durationSeconds, setDurationSeconds] = useState(3600);
  const [winnersCount, setWinnersCount] = useState(1);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  const loadGiveaways = useCallback(async () => {
    const { data } = await apiClient.get(`/guilds/${guildId}/giveaways`);
    setGiveaways(data.giveaways || []);
  }, [guildId]);

  useEffect(() => {
    loadGiveaways().catch(() => setError('Could not load giveaways. Check your login and API connection.'));
  }, [loadGiveaways]);

  const createGiveaway = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setBusy(true);
    setError('');
    setNotice('');
    try {
      await apiClient.post(`/guilds/${guildId}/giveaways`, {
        channel_id: channelId.trim(),
        prize: prize.trim(),
        duration_seconds: durationSeconds,
        winners_count: winnersCount,
      });
      setPrize('');
      setNotice('Giveaway posted successfully.');
      await loadGiveaways();
    } catch {
      setError('Could not create giveaway. Check the channel ID, bot permissions, and Redis connection.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl">
      <div>
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <Gift className="w-6 h-6 text-discord-blurple" /> Giveaways
        </h2>
        <p className="text-xs text-slate-400">Create a giveaway through your Discord bot.</p>
      </div>

      <form onSubmit={createGiveaway} className="p-6 rounded-2xl border border-white/5 glass space-y-4">
        <h3 className="font-bold text-sm">Create giveaway</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <label className="text-xs text-slate-300">
            Text channel ID
            <input
              required
              inputMode="numeric"
              value={channelId}
              onChange={(event) => setChannelId(event.target.value)}
              className="mt-2 w-full bg-[#12141c] border border-white/10 rounded-xl px-4 py-2.5 text-sm"
              placeholder="Discord channel ID"
            />
          </label>
          <label className="text-xs text-slate-300">
            Prize
            <input
              required
              maxLength={256}
              value={prize}
              onChange={(event) => setPrize(event.target.value)}
              className="mt-2 w-full bg-[#12141c] border border-white/10 rounded-xl px-4 py-2.5 text-sm"
              placeholder="Giveaway prize"
            />
          </label>
          <label className="text-xs text-slate-300">
            Duration (seconds)
            <input
              required
              type="number"
              min={1}
              max={31536000}
              value={durationSeconds}
              onChange={(event) => setDurationSeconds(Number(event.target.value))}
              className="mt-2 w-full bg-[#12141c] border border-white/10 rounded-xl px-4 py-2.5 text-sm"
            />
          </label>
          <label className="text-xs text-slate-300">
            Number of winners
            <input
              required
              type="number"
              min={1}
              max={100}
              value={winnersCount}
              onChange={(event) => setWinnersCount(Number(event.target.value))}
              className="mt-2 w-full bg-[#12141c] border border-white/10 rounded-xl px-4 py-2.5 text-sm"
            />
          </label>
        </div>
        {error && <p role="alert" className="text-xs text-red-400">{error}</p>}
        {notice && <p role="status" className="text-xs text-emerald-400">{notice}</p>}
        <button
          disabled={busy}
          className="px-5 py-2.5 rounded-xl bg-discord-blurple disabled:opacity-50 text-white font-medium text-xs"
        >
          {busy ? 'Creating...' : 'Create and publish'}
        </button>
      </form>

      <section className="p-6 rounded-2xl border border-white/5 glass">
        <h3 className="font-bold text-sm mb-4">Giveaways</h3>
        {giveaways.length === 0 ? (
          <p className="text-xs text-slate-500">No giveaways found for this server.</p>
        ) : (
          <div className="space-y-2">
            {giveaways.map((giveaway) => (
              <div key={giveaway.message_id} className="p-3.5 rounded-xl border border-white/5 bg-[#12141c] text-xs">
                <p className="font-bold text-white">{giveaway.prize}</p>
                <p className="text-slate-400 mt-1">
                  Channel {giveaway.channel_id} · {giveaway.winners} winner(s) · {giveaway.ended ? 'Ended' : 'Active'}
                </p>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
