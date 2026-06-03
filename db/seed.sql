-- ============================================================================
-- Content Empire OS  --  Seed data: the 10 niches + 1 channel each + schedule
-- ----------------------------------------------------------------------------
-- Idempotent via ON CONFLICT. Run AFTER schema.sql:
--   psql "$SUPABASE_DB_URL" -f db/seed.sql
--
-- edge-tts voices chosen for tone; change freely in the dashboard later.
-- (Verify available voices on the VM with:  edge-tts --list-voices)
-- ============================================================================

-- ---------------------------------------------------------------------------
-- NICHES
-- ---------------------------------------------------------------------------
insert into niches (slug, display_name, platform, category, tone, audience,
  visual_style, tts_voice, tts_rate, tts_pitch, remotion_template, style_props,
  target_rpm_usd, cadence, required_disclaimers, banned_framings, topics)
values
-- ====================== YOUTUBE (faceless) ================================
('quiet-capital', 'Quiet Capital', 'youtube',
 'Personal Finance & Investing Education',
 'kalme, autoritaire stem', 'beginnende en gevorderde beleggers',
 'Donker navy + goud, animated charts',
 'en-US-GuyNeural', '-5%', '-2Hz', 'FinanceTemplate',
 '{"bg":"#0a1f3c","accent":"#d4af37","font":"Georgia","mood":"calm"}',
 12.50, 'daily',
 array['This is not financial advice. Do your own research.'],
 array['get rich quick','guaranteed returns','double your money'],
 array['compound interest explained','index funds vs stocks','dollar cost averaging','reading a balance sheet','inflation and your savings']),

('leverage-lab', 'Leverage Lab', 'youtube',
 'AI Tools & Productivity',
 'energieke, praktische stem', 'makers, freelancers, solo-founders',
 'Screen recordings, neon-op-zwart',
 'en-US-AndrewNeural', '+8%', '+0Hz', 'TechTemplate',
 '{"bg":"#000000","accent":"#39ff14","font":"Inter","mood":"energetic"}',
 11.00, 'daily',
 array[]::text[],
 array['this one weird trick','you wont believe'],
 array['automate your inbox with AI','best AI note apps','build a workflow with no code','prompt engineering basics','AI for research']),

('plain-law', 'Plain Law', 'youtube',
 'Legal & Civic Explainers',
 'neutraal-gezaghebbend', 'algemeen publiek, studenten',
 'Flat-design animatie',
 'en-GB-RyanNeural', '-2%', '+0Hz', 'LegalTemplate',
 '{"bg":"#f4f1ea","accent":"#1f3a5f","font":"Source Serif Pro","mood":"neutral"}',
 10.50, 'daily',
 array['This is general information, not legal advice. Consult a qualified lawyer.'],
 array['sue them','easy money lawsuit'],
 array['how a bill becomes law','your rights when stopped by police','small claims court explained','what is due process','tenant rights basics']),

('coherent', 'Coherent', 'youtube',
 'Health & Mind-Body Science',
 'rustgevende, zachte stem', 'gezondheidsbewuste volwassenen, senioren',
 'Zachte anatomische animaties',
 'en-US-AvaNeural', '-8%', '-1Hz', 'HealthTemplate',
 '{"bg":"#0f2e2e","accent":"#7fd1c1","font":"Nunito","mood":"calm"}',
 9.00, 'daily',
 array['This is educational content, not medical advice. Talk to your doctor.'],
 array['cure','miracle','instant results','medical breakthrough you must try'],
 array['how sleep affects memory','the science of breathing','what stress does to the body','staying mobile after 60','the gut-brain connection']),

('lights-off', 'Lights Off', 'youtube',
 'Horror / Scary Story Narration',
 'diepe, langzame verteltoon', 'horror- en verhaalliefhebbers',
 'Donkere cinematische stills, mist, ambient',
 'en-US-ChristopherNeural', '-12%', '-3Hz', 'HorrorTemplate',
 '{"bg":"#050505","accent":"#8b0000","font":"Cormorant","mood":"eerie"}',
 10.00, 'daily',
 array[]::text[],
 array['real footage','100% true (claim)'],
 array['the cabin at the end of the road','night shift at the morgue','the last voicemail','something in the walls','the hiker who never came back']),

-- ====================== INSTAGRAM (faceless) ==============================
('the-quiet-ascent', '@thequietascent', 'instagram',
 'Mental Health, Mindset & Self-Improvement',
 'reflectief, ingehouden', 'jongvolwassenen die aan zichzelf werken',
 'Donkere moody typografie over trage B-roll, one-liners',
 'en-US-JennyNeural', '-6%', '-1Hz', 'IGQuoteTemplate',
 '{"bg":"#111111","accent":"#e8e2d6","font":"Playfair Display","mood":"moody"}',
 0.00, 'daily',
 array[]::text[],
 array['fix yourself overnight','toxic positivity'],
 array['discipline over motivation','sitting with discomfort','the cost of comparison','small habits compounding','letting go of control']),

('the-primed-body', '@theprimedbody', 'instagram',
 'Health & Supplements',
 'clean, klinisch, to-the-point', 'fitness- en gezondheidsbewusten',
 'Clean klinisch, text-overlay tips',
 'en-US-AndrewNeural', '+0%', '+0Hz', 'IGTipTemplate',
 '{"bg":"#f7f9fb","accent":"#0aa6b8","font":"Inter","mood":"clinical"}',
 0.00, 'daily',
 array['Educational only, not medical advice. Consult a professional.'],
 array['miracle supplement','cure','fat-burning hack'],
 array['magnesium and sleep','protein timing myths','creatine basics','hydration and performance','reading a supplement label']),

('build-quiet-brands', '@buildquietbrands', 'instagram',
 'Digital Marketing & Personal Branding',
 'bold, hook-gedreven', 'creators, kleine ondernemers',
 'Bold typografie, hook-gedreven carrousels',
 'en-US-AndrewNeural', '+5%', '+0Hz', 'IGCarouselTemplate',
 '{"bg":"#0d0d0d","accent":"#ffd400","font":"Archivo Black","mood":"bold"}',
 0.00, 'daily',
 array[]::text[],
 array['get rich quick','guaranteed viral'],
 array['hooks that stop the scroll','build authority without showing your face','content repurposing system','the 3-second rule','niche down to grow']),

('the-attachment-lab', '@theattachmentlab', 'instagram',
 'Love & Dating Psychology',
 'warm, inzichtelijk', 'mensen geinteresseerd in relaties',
 'Gedempte cinematische B-roll, psychologie-tekst',
 'en-US-JennyNeural', '-4%', '+0Hz', 'IGQuoteTemplate',
 '{"bg":"#1a1417","accent":"#caa0a8","font":"Cormorant","mood":"intimate"}',
 0.00, 'daily',
 array['Educational, not therapy. Seek a professional for personal issues.'],
 array['manipulate your ex','make them obsessed'],
 array['attachment styles explained','anxious vs avoidant','secure communication','the chase paradox','rebuilding trust']),

('quiet-cashflow', '@quietcashflow', 'instagram',
 'Make Money / Entrepreneurship',
 'dynamisch, bold hooks', 'aspirant-ondernemers',
 'Dynamisch, bold hooks',
 'en-US-AndrewNeural', '+6%', '+0Hz', 'IGCarouselTemplate',
 '{"bg":"#0a0a0a","accent":"#00e08f","font":"Archivo Black","mood":"bold"}',
 0.00, 'daily',
 array['Not financial advice. Results vary; most ventures fail.'],
 array['get rich quick','passive income guaranteed','quit your job today'],
 array['validate before you build','first 10 customers','pricing without fear','one offer one audience','cashflow vs profit'])
on conflict (slug) do update set
  display_name = excluded.display_name,
  tone = excluded.tone,
  visual_style = excluded.visual_style,
  tts_voice = excluded.tts_voice,
  style_props = excluded.style_props,
  target_rpm_usd = excluded.target_rpm_usd,
  required_disclaimers = excluded.required_disclaimers,
  banned_framings = excluded.banned_framings,
  topics = excluded.topics,
  updated_at = now();

-- ---------------------------------------------------------------------------
-- CHANNELS  --  one starter channel per niche (handle = niche display_name).
--   Credentials are left null; fill them via the dashboard form after you
--   create the GCP projects / IG Business accounts.
-- ---------------------------------------------------------------------------
insert into channels (niche_id, platform, handle, target_rpm_usd)
select n.id, n.platform, n.display_name, n.target_rpm_usd
from niches n
on conflict (platform, handle) do nothing;

-- ---------------------------------------------------------------------------
-- PUBLISH SCHEDULE  --  one daily slot per channel, throttled to 1/day.
--   Staggered hours so uploads spread across the day (anti rate-limit).
-- ---------------------------------------------------------------------------
insert into publish_schedule (channel_id, cron_expr, daily_cap)
select c.id,
       -- stagger: minute 0, hour = 8 + (row number mod 12), UTC
       format('0 %s * * *', 8 + (row_number() over (order by c.created_at) % 12)),
       1
from channels c
on conflict do nothing;

-- ---------------------------------------------------------------------------
-- Verify
-- ---------------------------------------------------------------------------
do $$
declare nc int; cc int; sc int;
begin
  select count(*) into nc from niches;
  select count(*) into cc from channels;
  select count(*) into sc from publish_schedule;
  raise notice 'Seed complete: % niches, % channels, % schedules', nc, cc, sc;
end $$;
