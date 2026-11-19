# 📖 Documentation Châmila dyal Projet: Khokho Bl3 V3 🤖

Had l-ficher fih char7 mofassal b Darija o b deqqa l ga3 l-ajza2 dyal l-projet dyalek: L-mimarriya (Architecture), les fichiers asasya, ga3 les Cogs (51 cogs), Qawa3id l-bayarat (Database), w kifach t-configuri w tkhdem l-bot.

---

## 📑 Fehris l-Mo7tawayat
1. [Nabdha 3amma 3la l-Projet (Overview)](#1-nabdha-3amma-3la-l-projet)
2. [L-Binya dyal l-Milaffat (Project Structure)](#2-l-binya-dyal-l-milaffat)
3. [L-Milaffat l-Asasya (Core Files)](#3-l-milaffat-l-asasya)
4. [Nidham Qawa3id l-Bayanat (Database Architecture)](#4-nidham-qawa3id-l-bayanat)
5. [Char7 l-Kamel l-ga3 les Cogs (51 Modules)](#5-char7-l-kamel-l-ga3-les-cogs)
   - [A. Idara & Modération (Admin & Moderation)](#a-idara--modération)
   - [B. Himaya & Sécurité (Security & Anti-Raid)](#b-himaya--sécurité)
   - [C. Iqtisad & Banque (Economy & Banking)](#c-iqtisad--banque)
   - [D. Al3ab & Casino (Games & Gambling)](#d-al3ab--casino)
   - [E. Mostawayat & Tafa3ol (Levels & Social)](#e-mostawayat--tafa3ol)
   - [F. Idarat l-Voice & Channels (Voice & Setup)](#f-idarat-l-voice--channels)
   - [G. Khadamate l-A3da2 & Tickets (Tickets & Utilities)](#g-khadamate-l-a3da2--tickets)
6. [Qawa3id l-Prefix w l-Awamir (Prefix System)](#6-qawa3id-l-prefix-w-l-awamir)
7. [Kifach tkhdem l-Bot w t-déployih (Setup & Running)](#7-kifach-tkhdem-l-bot-w-t-déployih)

---

## 1. Nabdha 3amma 3la l-Projet
**Khokho Bl3 V3** howa bot Discord kbir w motatawwir masno3 b **Python (discord.py 2.x)**.
- **150+ Awamir** (Prefix commands + Slash commands).
- **Multi-Server Ready**: Kaykhedem f servers bzzaf bla ma yetkheltou les données m3a ba3dyathoum.
- **Hybride Data Layer**: Kheddam b **SQLite (WAL mode)** bch ykon sré3 w safe, m3a **JSON storage** l b3d les configs s-sghira.
- **Système d'Embeds dki**: Kulchi kaywsel f embeds zwinin w mlowana 3la hsab l-7ala (Khdar = Najah, 7mer = Khata2, Limoni = Tahdir).

---

## 2. L-Binya dyal l-Milaffat

```text
khokho bl3 V3/
├── app.py                  # Nuqtat l-bidaya (Main entrypoint)
├── botconfig.py            # Central Configuration w qrayat l-.env
├── config_manager.py       # Idarat les configurations par serveur
├── data_manager.py         # Gestionnaire central dyal SQLite & JSON
├── fix_zwsp.py             # Script dyal tnqiyat les caractères mkhfyin (Zero Width Space)
├── requirements.txt        # Les bibliothèques Python li khasin
├── Dockerfile              # Docker image build
├── docker-compose.yml      # Docker container config
├── .env                    # Tokens, Keys w Roles IDs
│
├── database/               # Moteur dyal SQLite
│   ├── engine.py           # Thread-safe SQLite Connection & Wal mode
│   ├── schema.py           # Les tables SQLite (Economy, Levels, Bir, Warnings...)
│   ├── store.py            # Key-Value & ORM-like Stores
│   └── migrate.py          # Auto-migration mn JSON l-SQLite
│
├── utils/                  # Okhshab w adawat mosa3ida
│   ├── context.py          # Custom EmbedContext (Auto-Embed sender)
│   ├── checks.py           # Vérification des rôles w les permissions
│   └── confirm.py          # Interactive Yes/No UI buttons
│
├── cogs/                   # 51 Modules w Extensions
│   ├── admin.py, economy.py, levels.py, gambling.py...
│
└── data/                   # Fichiers dyal l-bayanat w l-backups
    ├── bot.db              # SQLite Database file
    ├── guild_configs.json  # Config dyal kola serveur
    ├── backups/            # Backups automatiques
    └── transcripts/        # Ticket HTML/text transcripts
```

---

## 3. L-Milaffat l-Asasya

### 🔹 `app.py`
- L-qelb n-nabid dyal l-bot: Kay-initié l-instance dyal `commands.Bot`.
- Kay-activé ga3 l-**Intents** l-khasin (Message Content, Members, Presences, Voice States).
- Fih l-mikanizm dyal **Global Prefix Check**:
  - Les commandes d'administration khas-hom darori prefix `+` wla `-`.
  - Les commandes dyal l-a3da2 (Public) khas-hom prefix `&`.
  - Awamir b7al `help` w `myperms` khedamin bihom bjouj.
- Fih `setup_hook()` li kaychargi ga3 les 51 cogs w kaydir `tree.sync()` l slash commands.

### 🔹 `botconfig.py`
- Kayqra ga3 l-motaghayyirat mn l-milaf `.env`.
- Fih l-id dyal Owner (`BOT_OWNER_ID`), les rôles l-khasin b l-idara (`ADMIN_ROLES`, `MODERATOR_ROLES`), les salons dyal les logs (`LOG_CHANNEL_ID`, `VOICE_LOG_CHANNEL_ID`), etc.
- Safe type-casting (`_int`, `_str`, `_bool`) bach l-bot ma yetplantach ila kan chi var khawi.

### 🔹 `config_manager.py`
- Kay3ti li kola serveur l-istiqlaliya dyalo (Multi-guild isolation).
- Kaykhzen f `data/guild_configs.json` chkon houma les rôles w les salons w chmen miza (feature) m-activya wla m-désactivya f kola serveur.
- Thread-safe w Async-safe (kaysta3mel `threading.RLock`).

### 🔹 `data_manager.py`
- Kaydir l-liaison bin l-code w l-base de données.
- Kay-initialiser `init_schema()` w kaydir `auto_migrate_if_needed()`.
- Kay-exporter des objets prêt-à-l'emploi: `ECONOMY`, `LEVELS`, `BIR`, `WARNINGS`, `BANKING`.

### 🔹 `utils/context.py`
- `EmbedContext`: Ay `ctx.send("message")` kay7wlo otonomiyan l Embed mziwna b les couleurs monasiba bla ma t3awed tktb `discord.Embed(...)` kola merra.

---

## 4. Nidham Qawa3id l-Bayanat (Database)

L-bot kheddam b système hybride:
1. **SQLite (`data/bot.db`)**: 
   - Kheddam b mode **WAL (Write-Ahead Logging)** li kaykhlli l-qraya w l-ktaba ykono f nafs l-waqt bla blocage.
   - **Tables Asasya**:
     - `economy`: Koul user f serveur 3ndo wallet, bank, last_daily, inventory, net_worth...
     - `banking`: Qrod (Loans), Charikat (Businesses), As-hom (Stocks), Crypto, 7isab twfir (Savings).
     - `levels`: XP, Level, messages_count, voice_minutes.
     - `bir`: Système l-bir l-khass b l-arba7 w l-akhd.
     - `warnings`: Sijill l-inidarat dyal kola user.
     - `kv`: Table dynamique Key-Value l ay 7aja jdida.
2. **JSON Files (`data/*.json`)**:
   - Mkhliya l-7wayej l-kfifa w l-istatiqiya b7al: `clans.json`, `tickets.json`, `antiraid.json`, `automod.json`.

---

## 5. Char7 l-Kamel l-ga3 les Cogs (51 Modules)

### A. Idara & Modération (Admin & Moderation)
1. **`admin.py`**: Awamir l-idara: Kick, Ban, Unban, Softban, Timeout, Jail/Unjail, Purge (ms7 les messages), Slowmode, Lock/Unlock channels.
2. **`moderation_cases.py`**: Système complet dyal les cases (`+case <id>`, `+cases @user`, modlog auto).
3. **`tempban.py`**: Ban mo2aqqat b waqt mo7addad (kaytsala l-waqt kay-unbanni bo7do).
4. **`temproles.py`**: I3ta2 role mo2aqqat l wa7ed l-modda (b7al VIP 7 ayam) w kay7yed bo7do.
5. **`roles.py`**: I3ta2 w se7b les rôles (`giverole`, `removerole`, `massrole`).
6. **`roleconfig.py`**: Configuration dyal les rôles li 3ndhom ssofyat f l-bot.
7. **`permsmanager.py`**: Tahqiq w idarat les permissions dyal les membres w les rôles.
8. **`channelmanager.py`**: Idarat les salons (khedma fihom: khleq, ms7, bedel smiya, bedel permissions).

### B. Himaya & Sécurité (Security & Anti-Raid)
9. **`antiraid.py`**: 
   - Protection ded l-hwayech: Auto-kick l les comptes li 3ad tfta7o jdad (Account Age limit).
   - Join lockdown f 7alat ila dkhlo bzzaf dyal les comptes f daqiqa we7da.
10. **`automod.py`**: 
    - Anti-Spam (khedam b ratelimit).
    - Anti-Links (kay7bes les liens d-Discord wla les liens mam3rofash).
    - Anti-Caps (kay7bs li kaykteb gha b l-majuscule).
    - Badwords filter (kayms7 l-kass w l-kalam l-khayeb).
11. **`verification.py`**: Système dyal Captcha / Boutons bach l-a3da2 jdad y-vérifiw rashom 3ad ydkholo l-server.
12. **`tempverifvc.py`**: Salon vocal dyal l-vérification: Khas l-3odw ydkhol l voice bach y-vérifiyih admin.

### C. Iqtisad & Banque (Economy & Banking)
13. **`economy.py`**: 
    - Balance, Bank deposit, Withdraw.
    - Daily rewards, Work, Crime, Rob, Rich leaderboard.
14. **`shop.py`**: Magasin dyal l-bot: Chri rôles, items, badges b l-flous dyal l-bot.
15. **`bir.py`**: Miza khassa b l-bot (Bir l-flous / Wells): L-a3da2 kaylo7o flous wla kay-jbdou menno arba7.
16. **`clans.py`**: Système l-3achair (Clans/Guilds): Khleq clan, dkhl a3da2, 7ot flous f clan bank, w clan wars/leaderboard.

### D. Al3ab & Casino (Games & Gambling)
17. **`gambling.py`**: 19+ Lu3ba dyal l-qmar w l-khatir:
    - Coinflip (Pila wla Wjeh), Dice (Zar), Roulette, Slots (Machine à sous).
    - Blackjack, High-Low, Mines, Crash (B7al Aviator).
    - Baccarat, Video Poker, Plinko, Wheel of fortune.
18. **`games.py`**: Al3ab jam3iya w khfifa (Trivia, Tic-Tac-Toe, Connect4, RPS...).
19. **`adventure.py`**: Système RPG Mini-Adventure: Mchi f moghamara, dreb l-wo7oush (Monsters), rbe7 l-XP w l-Gold.
20. **`heist.py`**: Serqa jam3iya: L-a3da2 kaytjm3o bach yserqo la banque d-Discord, ila nj7o kayqsmo l-flous, ila khasro kaymchiw l-jail.
21. **`gamerequests.py`**: Talabat l-li3b bin l-a3da2 (Challenge user l lu3ba mo3ayyana).
22. **`tournaments.py`**: Tndhim boutoulat (Tournaments) bin les clans wla l-a3da2 b les brackets.

### E. Mostawayat & Tafa3ol (Levels & Social)
23. **`levels.py`**: 
    - Koul risala wla daqiqa f voice kat3ti XP.
    - Level-up notifications w Role rewards (role kayt3ta otonomiyan f level 5, 10, 20...).
24. **`rankcard.py`**: Tswira (PNG) katgenerasa b **Pillow (PIL)** fiha avatar, rank, level, w progress bar.
25. **`leaderboard.py`**: Top 10 dyal les riches, l-levels, l-voix, w l-clans.
26. **`activity.py`**: Tetebbo3 nachat l-a3da2 f les salons textuels w les vocals b stats daqiqa.
27. **`social.py`**: Reputations (+rep), bio, Zawaj/Talaq (Marry/Divorce), profile card.

### F. Idarat l-Voice & Channels (Voice & Setup)
28. **`voice.py`**: Idarat les salons vocaux, calcul dyal waqt l-istiqrar f l-voice.
29. **`tempvoice.py`**: Salons vocaux mo2aqqata (Join-to-Create): Dkhol l salon kaytft7 lik salon dyalek bo7dek t-thkkem fih (lock, limit, kick).
30. **`server_setup.py`**: Auto-setup dyal server: Kaycreyi les catégories, les salons w les rôles automatiquement.
31. **`setup.py`**: Configuration guide interactif l kola miza f l-bot.
32. **`serverstats.py`**: Counters f les salons vocaux (Total Members, Online, Bots...).

### G. Khadamate l-A3da2 & Tickets (Tickets & Utilities)
33. **`tickets.py`**: Système complet dyal support: Fte7 ticket b boutona, modal li kaytloub sabab, gestion par le staff.
34. **`transcripts.py`**: Kay-enregstri l-hadra li dazt f ticket kamla f HTML/Text file qbel ma yetms7 l-salon.
35. **`giveaway.py`**: Qor3a interactive b buttons, waqt mo7addad, w khtiyar l-fa2izin otonomiyan.
36. **`reactionroles.py`**: Akhd les rôles b les réactions wla les buttons.
37. **`selfroles.py`**: Menus déroulants (Select Menus) bach l-3odw ykhtar les rôles dyalo (ex: Al3ab, Dawla, Age).
38. **`auto_responses.py`**: Ajwiba otonomiya melli chi wa7ed kaykteb kalimat mo3ayyana.
39. **`announcements.py`**: Nchr i3lanat mzewqa b embeds f salons mo7addada.
40. **`embedbuilder.py`**: Builder interactif bach t-qad Embed custom b l-alwan, tswira, fields w boutons.
41. **`backup_restore.py`**: Akhd nuskha i7tiyatiya (Backup) l les salons w les rôles dyal l-server w rjja3ha f ay waqt.
42. **`welcome.py`**: Rissalat tar7ib f l-khas (DM) wla f salon dyal welcome m3a tswira wla embed.
43. **`logs.py`**: Sijill l-a7dat: Chkon dkhl, chkon khrej, chkon bdl smito, chkon ms7 risala.
44. **`scheduled.py`**: Awamir w rassa2il kaytsifto f waqt mbarmej (Cron-like scheduler).
45. **`status_rotation.py`**: Tbdel l-activity/status dyal l-bot kola modda (Playing, Watching, Streaming).
46. **`basic.py`**: Awamir 3amma b7al `ping`, `uptime`, `say`.
47. **`info.py`**: Ma3loumat 3la l-user, l-server, l-avatar, l-banner.
48. **`utility.py`**: Adawat mosa3ida: Calculatrice, Reminders (fekkarni), Polls (sondage).
49. **`sysinfo.py`**: Ma3loumat 3la l-vps w l-machine (CPU, RAM, OS, Python version).
50. **`guild_join.py`**: Gestion dyal dkhoul l-bot l servers jdad w t-sawyeb l-configs dyalhom.
51. **`help.py`**: Menu l-mosa3ada l-kamel categorisé b boutons w menus interactifs.

---

## 6. Qawa3id l-Prefix w l-Awamir (Prefix System)

L-bot fih séparation wad7a f les préfixes bach maykounch tadakhol:

| No3 l-Amr | L-Prefix l-Maqbol | Amthila |
|---|---|---|
| **Awamir l-Idara (Admin)** | `+` aw `-` | `+ban`, `+kick`, `+mute`, `+clear`, `+setup`, `+jail` |
| **Awamir l-A3da2 (Public)** | `&` | `&balance`, `&daily`, `&profile`, `&rank`, `&work`, `&bir` |
| **Awamir Mochtaraka (Dual)** | `+`, `-`, `&` | `help`, `cmds`, `myperms` |
| **Slash Commands** | `/` | `/help`, `/rank`, `/balance`, `/ticket`, etc. |

---

## 7. Kifach tkhdem l-Bot w t-déployih

### 1. Requirements
Khas ykoun 3ndek **Python 3.10+** (Rak m-instali Python 3.14 li kheddam mzyan).
Instali les bibliothèques:
```powershell
pip install -r requirements.txt
```

### 2. Configuration dyal `.env`
Khas t-3mer l-milaf `.env` b les informations dyalek:
```env
DISCORD_TOKEN=your_bot_token_here
BOT_OWNER_ID=your_discord_id
ROLE_FOUNDER=role_id
ROLE_ADMINISTRATOR=role_id
ROLE_MODERATOR=role_id
LOG_CHANNEL_ID=channel_id
```

### 3. T-lanci l-Bot
```powershell
python app.py
```

---
*Had l-milaf tsawab b deqqa bach ykon marja3 kamel l-koul khedma w code f Khokho Bl3 V3.*