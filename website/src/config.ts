// Site-level config: metadata + navigation. Content comes from cv.ts (data-driven).
import { fullName, cv } from './data/cv';

// Astro's BASE_URL may or may not end in '/'; normalize so `${base}foo` works.
const rawBase = import.meta.env.BASE_URL;
const base = rawBase.endsWith('/') ? rawBase : `${rawBase}/`;

export const SITE = {
  name: fullName,
  title: `${fullName} — ${cv.profile.title}`,
  description: cv.profile.summary.trim(),
  // Base URL for links/assets, guaranteed to end with '/'.
  base,
};

// In-page anchor navigation. Each links to a <section id>.
export const NAV: { label: string; href: string }[] = [
  { label: 'About', href: '#about' },
  { label: 'Publications', href: '#publications' },
  { label: 'Experience', href: '#experience' },
  { label: 'Projects', href: '#projects' },
  { label: 'Teaching', href: '#teaching' },
];
