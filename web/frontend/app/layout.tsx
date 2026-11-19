import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Khokho Bl3 V3 — Premium Discord Bot & SaaS Suite',
  description: 'The Ultimate Commercial Discord Bot: Banking, 19 Casino Games, AI AutoMod, Multi-Server Isolation & Web Dashboard.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-discord-dark text-slate-100 min-h-screen antialiased selection:bg-discord-blurple selection:text-white">
        {children}
      </body>
    </html>
  );
}