'use client';
import { useRouter } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function LoginPage() {
  const router = useRouter();

  const handleDevLogin = () => {
    localStorage.setItem('khokho_token', 'dev_mock_jwt_token_12345');
    router.push('/dashboard/servers');
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
          onClick={handleDevLogin}
          className="w-full py-3.5 px-4 rounded-xl bg-discord-blurple hover:bg-discord-blurple/90 text-white font-semibold text-sm transition flex items-center justify-center gap-3 shadow-lg shadow-discord-blurple/30 mb-4"
        >
          <span>Continue with Discord</span>
        </button>

        <Link href="/" className="inline-flex items-center gap-2 text-xs text-slate-400 hover:text-white transition">
          <ArrowLeft className="w-3.5 h-3.5" /> Back to Home
        </Link>
      </div>
    </div>
  );
}