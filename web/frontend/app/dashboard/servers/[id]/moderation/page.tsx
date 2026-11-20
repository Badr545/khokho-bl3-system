'use client';
import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { ShieldAlert, Trash2 } from 'lucide-react';
import { apiClient } from '@/lib/api';

export default function ModerationPage() {
  const params = useParams();
  const guildId = params?.id as string;
  const [warnings, setWarnings] = useState<any[]>([]);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!guildId) return;
    apiClient.get('/guilds/' + guildId + '/moderation/warnings')
      .then((res) => {
        setWarnings(res.data.warnings || []);
      })
      .catch(() => setError('Could not load warnings. Check your login and API connection.'));
  }, [guildId]);

  const handleRevoke = async (warnId: string) => {
    setError('');
    try {
      await apiClient.post('/guilds/' + guildId + '/moderation/warnings/' + warnId + '/revoke');
      setWarnings((current) => current.filter((warning) => warning.id !== warnId));
    } catch {
      setError('Could not revoke this warning. Verify that the bot is online and try again.');
    }
  };

  return (
    <div className="space-y-6 max-w-5xl">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Moderation & Warnings</h2>
          <p className="text-xs text-slate-400">View and revoke active warnings issued by your staff team.</p>
        </div>
      </div>

      <div className="p-6 rounded-2xl border border-white/5 glass">
        <h3 className="font-bold text-sm mb-4">Active Infractions Log</h3>
        {error && <p role="alert" className="mb-4 text-xs text-red-400">{error}</p>}
        <div className="space-y-2">
          {warnings.length === 0 ? (
            <p className="text-xs text-slate-500 py-4">No warnings found for this server. All clear!</p>
          ) : (
            warnings.map((w) => (
              <div key={w.id} className="p-3.5 rounded-xl border border-white/5 bg-[#12141c] flex items-center justify-between text-xs">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-white">User: {w.user_id}</span>
                    <span className="text-slate-500">• Mod: {w.moderator_id}</span>
                  </div>
                  <p className="text-slate-400 mt-1">{w.reason}</p>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-slate-500">{w.timestamp}</span>
                  <button
                    onClick={() => handleRevoke(w.id)}
                    className="p-1.5 rounded-lg text-discord-red hover:bg-discord-red/10 transition"
                    title="Revoke Warning"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}