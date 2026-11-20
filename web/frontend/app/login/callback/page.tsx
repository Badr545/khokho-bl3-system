'use client';

import { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api';

export default function DiscordCallbackPage() {
  const router = useRouter();
  const started = useRef(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (started.current) return;
    started.current = true;

    const params = new URLSearchParams(window.location.search);
    const code = params.get('code');
    const state = params.get('state');
    if (!code || !state) {
      setError('Discord login was cancelled or returned an invalid response.');
      return;
    }

    apiClient.post('/auth/discord/callback', { code, state })
      .then(() => router.replace('/dashboard/servers'))
      .catch(() => setError('Discord login failed. Return to the login page and try again.'));
  }, [router]);

  return (
    <main className="min-h-screen flex items-center justify-center px-4">
      <div className="max-w-md text-center">
        {error ? (
          <>
            <h1 className="text-xl font-bold mb-3">Login failed</h1>
            <p role="alert" className="text-sm text-red-400">{error}</p>
            <a href="/login" className="inline-block mt-6 text-sm text-white underline">Try again</a>
          </>
        ) : (
          <p className="text-sm text-slate-300">Finishing Discord login...</p>
        )}
      </div>
    </main>
  );
}
