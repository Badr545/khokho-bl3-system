'use client';
import { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, CheckCircle2, Sparkles } from 'lucide-react';
import { apiClient } from '@/lib/api';

export default function PremiumPricingPage() {
  const [loadingTier, setLoadingTier] = useState<string | null>(null);

  const handleCheckout = (tier: string) => {
    setLoadingTier(tier);
    apiClient.post('/premium/checkout', {
      guild_id: '112233445566778899',
      tier: tier,
      success_url: window.location.origin + '/dashboard/servers',
      cancel_url: window.location.origin + '/premium'
    }).then((res) => {
      if (res.data.checkout_url) {
        window.location.href = res.data.checkout_url;
      }
    }).finally(() => setLoadingTier(null));
  };

  return (
    <div className="min-h-screen px-6 lg:px-12 py-12 max-w-6xl mx-auto">
      <Link href="/" className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white mb-8 transition">
        <ArrowLeft className="w-4 h-4" /> Back to Home
      </Link>

      <div className="text-center mb-16">
        <h1 className="text-4xl font-extrabold tracking-tight mb-3">Commercial SaaS Pricing</h1>
        <p className="text-slate-400 text-sm">Choose your recurring subscription or upgrade with instant Stripe Checkout.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Basic */}
        <div className="p-8 rounded-2xl border border-white/10 glass flex flex-col justify-between">
          <div>
            <h3 className="font-bold text-xl mb-1">Basic SaaS</h3>
            <p className="text-xs text-slate-400 mb-6">Growing gaming servers</p>
            <div className="text-4xl font-black mb-6"><span className="text-xs text-slate-400">/mo</span></div>
            <ul className="text-xs space-y-3 text-slate-300 mb-8">
              <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-discord-green" /> Unlimited tickets & transcripts</li>
              <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-discord-green" /> 5 concurrent giveaways</li>
              <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-discord-green" /> 10 custom commands</li>
            </ul>
          </div>
          <button
            onClick={() => handleCheckout('basic')}
            disabled={loadingTier === 'basic'}
            className="w-full py-3 rounded-xl bg-discord-blurple text-center font-medium text-xs hover:bg-discord-blurple/90 transition"
          >
            {loadingTier === 'basic' ? 'Redirecting...' : 'Checkout /mo'}
          </button>
        </div>

        {/* Pro */}
        <div className="p-8 rounded-2xl border border-discord-blurple/40 bg-discord-blurple/5 flex flex-col justify-between relative">
          <div>
            <span className="text-[10px] uppercase font-bold tracking-wider text-discord-blurple bg-discord-blurple/20 px-2.5 py-1 rounded-full mb-3 inline-block">Best Value</span>
            <h3 className="font-bold text-xl mb-1">Pro SaaS</h3>
            <p className="text-xs text-slate-400 mb-6">Large esports & clans</p>
            <div className="text-4xl font-black mb-6"><span className="text-xs text-slate-400">/mo</span></div>
            <ul className="text-xs space-y-3 text-slate-300 mb-8">
              <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-discord-green" /> Unlimited everything</li>
              <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-discord-green" /> REST API Developer access</li>
              <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-discord-green" /> 50 custom commands</li>
              <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-discord-green" /> 8D/Bassboost Music Filters</li>
            </ul>
          </div>
          <button
            onClick={() => handleCheckout('pro')}
            disabled={loadingTier === 'pro'}
            className="w-full py-3 rounded-xl bg-discord-blurple text-center font-medium text-xs hover:bg-discord-blurple/90 transition shadow-lg shadow-discord-blurple/25"
          >
            {loadingTier === 'pro' ? 'Redirecting...' : 'Checkout /mo'}
          </button>
        </div>

        {/* Ultra */}
        <div className="p-8 rounded-2xl border border-discord-fuchsia/40 bg-discord-fuchsia/5 flex flex-col justify-between">
          <div>
            <h3 className="font-bold text-xl mb-1">Ultra White-Label</h3>
            <p className="text-xs text-slate-400 mb-6">Full brand takeover</p>
            <div className="text-4xl font-black mb-6"><span className="text-xs text-slate-400">/mo</span></div>
            <ul className="text-xs space-y-3 text-slate-300 mb-8">
              <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-discord-green" /> Custom bot name & avatar</li>
              <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-discord-green" /> Custom domain dashboard</li>
              <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-discord-green" /> 24/7 dedicated voice room</li>
            </ul>
          </div>
          <button
            onClick={() => handleCheckout('ultra')}
            disabled={loadingTier === 'ultra'}
            className="w-full py-3 rounded-xl bg-gradient-to-r from-discord-blurple to-discord-fuchsia text-center font-medium text-xs hover:opacity-90 transition"
          >
            {loadingTier === 'ultra' ? 'Redirecting...' : 'Checkout /mo'}
          </button>
        </div>
      </div>
    </div>
  );
}