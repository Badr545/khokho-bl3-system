'use client';
import { useState } from 'react';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { apiClient } from '@/lib/api';

export default function LoginPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleDiscordLogin = async () => {
    setLoading(true);
    setError('');
    try {
      const { data } = await apiClient.get('/auth/discord/start');
      window.location.assign(data.authorization_url);
    } catch (loginError) {
      setError('Discord login is unavailable. Check the API and OAuth configuration.');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="p-8 rounded-2xl border border-white/10 glass max-w-md w-full text-center">
        <div className="w-12 h-12 rounded-xl bg-discord-blurple flex items-center justify-center font-bold text-2xl mx-auto mb-4">
          🤖
        </div>
        <h2 className="text-2xl font-bold mb-2">Login to Khokho Bl3</h2>
        <p className="text-sm text-slate-400 mb-8">Access and manage all your Discord servers seamlessly.</p>

        <button
          onClick={handleDiscordLogin}
          disabled={loading}
          className="w-full py-3.5 px-4 rounded-xl bg-discord-blurple hover:bg-discord-blurple/90 text-white font-semibold text-sm transition flex items-center justify-center gap-3 shadow-lg shadow-discord-blurple/30 mb-4"
        >
          <span>{loading ? 'Connecting to Discord...' : 'Continue with Discord'}</span>
        </button>
        {error && <p role="alert" className="mb-4 text-sm text-red-400">{error}</p>}

        <Link href="/" className="inline-flex items-center gap-2 text-xs text-slate-400 hover:text-white transition">
          <ArrowLeft className="w-3.5 h-3.5" /> Back to Home
        </Link>
      </div>
    </div>
  );
}