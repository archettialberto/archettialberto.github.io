import { base } from './config';
import { cv } from './data/cv';

export type Lang = 'en' | 'it';
export const LANGS: Lang[] = ['en', 'it'];
export const langPath = (lang: Lang) => (lang === 'en' ? base : `${base}it/`);

const UI = {
  en: {
    nav: { about: 'About', news: 'News', publications: 'Publications', experience: 'Experience', teaching: 'Teaching' },
    downloadCv: 'Download CV',
    contact: 'Get in touch',
    news: 'News',
    publications: 'Publications',
    kind: { journal: 'Journal', conference: 'Conference', workshop: 'Workshop', preprint: 'Preprint' },
    citations: (n: number) => `${n} citations`,
    cite: 'BibTeX',
    copied: 'Copied',
    experience: 'Experience & Education',
    work: 'Work',
    education: 'Education',
    thesis: 'Thesis',
    interests: 'Research interests',
    projects: 'Research projects',
    project: 'project',
    teaching: 'Teaching & Mentoring',
    courses: 'Courses',
    coursesMeta: (n: number, h: number) => `${n} courses · ${h} h`,
    editions: (n: number) => `${n} editions`,
    supervision: 'Thesis supervision',
    supervisionMeta: (n: number) => `${n} theses`,
    talksAwards: 'Talks & Awards',
    talks: 'Talks',
    talksMeta: (n: number, c: number) => `${n} talks · ${c} countries`,
    awards: 'Awards',
    showAll: 'Show all',
    showFewer: 'Show fewer',
    present: 'present',
    menu: 'Menu',
    theme: 'Toggle dark mode',
    otherLang: 'Leggi in italiano',
  },
  it: {
    nav: { about: 'Chi sono', news: 'News', publications: 'Pubblicazioni', experience: 'Percorso', teaching: 'Didattica' },
    downloadCv: 'Scarica il CV',
    contact: 'Contattami',
    news: 'News',
    publications: 'Pubblicazioni',
    kind: { journal: 'Rivista', conference: 'Conferenza', workshop: 'Workshop', preprint: 'Preprint' },
    citations: (n: number) => `${n} citazioni`,
    cite: 'BibTeX',
    copied: 'Copiato',
    experience: 'Esperienza e formazione',
    work: 'Lavoro',
    education: 'Formazione',
    thesis: 'Tesi',
    interests: 'Interessi di ricerca',
    projects: 'Progetti di ricerca',
    project: 'progetto',
    teaching: 'Didattica e tutoraggio',
    courses: 'Corsi',
    coursesMeta: (n: number, h: number) => `${n} corsi · ${h} ore`,
    editions: (n: number) => `${n} edizioni`,
    supervision: 'Tesi seguite',
    supervisionMeta: (n: number) => `${n} tesi`,
    talksAwards: 'Interventi e premi',
    talks: 'Interventi',
    talksMeta: (n: number, c: number) => `${n} interventi · ${c} paesi`,
    awards: 'Premi',
    showAll: 'Mostra tutto',
    showFewer: 'Mostra meno',
    present: 'oggi',
    menu: 'Menu',
    theme: 'Attiva/disattiva tema scuro',
    otherLang: 'Read in English',
  },
} as const;

export function useTranslations(lang: Lang) {
  const ui = UI[lang];
  // Data text: Italian from the data layer's i18n map, English as fallback.
  const tr = <T extends string | null | undefined>(s: T): T =>
    lang === 'it' && s ? ((cv.i18n[s] ?? s) as T) : s;
  const period = (start: number, end: number | 'present') =>
    end === 'present' ? `${start} – ${ui.present}` : start === end ? `${start}` : `${start} – ${end}`;
  const month = new Intl.DateTimeFormat(lang, { month: 'short', year: 'numeric' });
  // "2026-06" -> "Jun 2026"; a bare year stays as is.
  const date = (d: string) => (d.length > 4 ? month.format(new Date(`${d}-01T12:00:00`)) : d);
  return { ui, tr, period, date };
}
